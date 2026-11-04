#!/usr/bin/env python3
"""Проверка консистентности проекта AppRequests (Xamarin.Forms).
Проверяет XML-корректность файлов, соответствие x:Class/Clicked/x:Name,
существование классов ShellContent и наличие/валидность иконок.
"""
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT = os.path.join(ROOT, "AppRequests")
ANDROID = os.path.join(ROOT, "AppRequests.Android")

errors = []


def fail(msg):
    errors.append(msg)


def check_xml(path, label):
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        fail(f"{label}: некорректный XML — {exc}")


# 1. XML-корректность обязательных проектных файлов
xml_files = []
for dirpath, _, files in os.walk(ROOT):
    for f in files:
        if (f.endswith((".xaml", ".axml", ".csproj")) or
                f == "AndroidManifest.xml"):
            xml_files.append(os.path.join(dirpath, f))
for path in sorted(xml_files):
    check_xml(path, path)
print(f"[OK] XML-проверка: {len(xml_files)} файлов")


# 2. Сопутствующие пары xaml/xaml.cs
xaml_files = []
for dirpath, _, files in os.walk(PROJECT):
    for f in files:
        if f.endswith(".xaml"):
            xaml_files.append(os.path.join(dirpath, f))

for xaml_path in sorted(xaml_files):
    cs_path = xaml_path + ".cs"
    label = os.path.relpath(xaml_path, ROOT)
    if not os.path.exists(cs_path):
        fail(f"{label}: отсутствует code-behind {os.path.basename(cs_path)}")
        continue

    try:
        tree = ET.parse(xaml_path)
        root = tree.getroot()
    except ET.ParseError:
        continue

    # x:Class
    ns = {"x": "http://schemas.microsoft.com/winfx/2009/xaml"}
    xclass = root.get("{http://schemas.microsoft.com/winfx/2009/xaml}Class")
    if xclass:
        cs_content = open(cs_path, encoding="utf-8").read()
        namespace_match = re.search(
            r"\bnamespace\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)", cs_content)
        class_match = re.search(r"\bpartial\s+class\s+(\w+)", cs_content)
        if namespace_match and class_match:
            actual_class = namespace_match.group(1) + "." + class_match.group(1)
            if actual_class != xclass:
                fail(f"{label}: x:Class='{xclass}', а в .cs класс '{actual_class}'")
        else:
            fail(f"{label}: не найдены namespace и partial class в {os.path.basename(cs_path)}")

    # x:Name уникальность и использование в code-behind
    xnames = []
    for elem in root.iter():
        name = elem.get("{http://schemas.microsoft.com/winfx/2009/xaml}Name")
        if name:
            xnames.append(name)
    if len(xnames) != len(set(xnames)):
        for n in set([n for n in xnames if xnames.count(n) > 1]):
            fail(f"{label}: x:Name='{n}' дублируется")
    cs_content = open(cs_path, encoding="utf-8").read()
    for name in xnames:
        if not re.search(r"\b" + re.escape(name) + r"\b", cs_content):
            fail(f"{label}: x:Name='{name}' не используется в code-behind")

    # Clicked обработчики
    for elem in root.iter():
        for attr, value in elem.attrib.items():
            if attr.split("}")[-1] == "Clicked":
                handler = value
                if not re.search(r"\b" + re.escape(handler) + r"\s*\(", cs_content):
                    fail(f"{label}: Clicked='{handler}', но метода {handler}() нет в {os.path.basename(cs_path)}")

    print(f"[OK] {label}: x:Class={xclass}, имена={xnames}")


# 3. ShellContent ссылаются на существующие классы
mainpage_xaml = os.path.join(PROJECT, "MainPage.xaml")
if os.path.exists(mainpage_xaml):
    try:
        tree = ET.parse(mainpage_xaml)
        root = tree.getroot()
        xns = "http://xamarin.com/schemas/2014/forms"
        xaml_ns = "http://schemas.microsoft.com/winfx/2009/xaml"
        for elem in root.iter():
            if elem.tag.split("}")[-1] == "ShellContent":
                tmpl = elem.get("ContentTemplate", "")
                m = re.search(r"\{\s*DataTemplate\s+([\w]+):(\w+)\s*\}", tmpl)
                if m:
                    prefix, cls_name = m.groups()
                    expected_cs = os.path.join(PROJECT, "Views", cls_name + ".xaml.cs")
                    if prefix != "views" or not os.path.exists(expected_cs):
                        fail(f"MainPage.xaml: ShellContent ссылается на несуществующий класс {cls_name}")
                    else:
                        print(f"[OK] ShellContent -> {cls_name} существует")
                else:
                    fail("MainPage.xaml: ShellContent не содержит проверяемый ContentTemplate")
    except ET.ParseError:
        pass


# 4. Полная проверка PNG: структура, CRC, декодирование и заданный размер
for icon in ["icon_about.png", "icon_feed.png"]:
    path = os.path.join(ANDROID, "Resources", "drawable", icon)
    if not os.path.exists(path):
        fail(f"Иконка отсутствует: {path}")
        continue
    try:
        with open(path, "rb") as f:
            data = f.read()
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("неверная PNG-сигнатура")

        pos = 8
        image_header = None
        image_data = bytearray()
        saw_end = False
        while pos + 12 <= len(data):
            length = struct.unpack(">I", data[pos:pos + 4])[0]
            chunk_type = data[pos + 4:pos + 8]
            chunk_end = pos + 12 + length
            if chunk_end > len(data):
                raise ValueError("обрезанный чанк")
            chunk_data = data[pos + 8:pos + 8 + length]
            expected_crc = struct.unpack(">I", data[pos + 8 + length:chunk_end])[0]
            actual_crc = zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF
            if actual_crc != expected_crc:
                raise ValueError(f"неверная CRC чанка {chunk_type.decode('ascii')}")
            if chunk_type == b"IHDR":
                if image_header is not None or length != 13:
                    raise ValueError("некорректный IHDR")
                image_header = struct.unpack(">IIBBBBB", chunk_data)
            elif chunk_type == b"IDAT":
                image_data.extend(chunk_data)
            elif chunk_type == b"IEND":
                if length != 0:
                    raise ValueError("некорректный IEND")
                saw_end = True
                pos = chunk_end
                break
            pos = chunk_end

        if not saw_end or pos != len(data) or image_header is None:
            raise ValueError("неполная структура PNG")
        width, height, bit_depth, color_type, compression, filtering, interlace = image_header
        if (width, height) != (72, 72):
            raise ValueError(f"ожидался размер 72x72, получен {width}x{height}")
        if (bit_depth, color_type, compression, filtering, interlace) != (8, 6, 0, 0, 0):
            raise ValueError("ожидался PNG RGBA 8-bit без чересстрочной развертки")
        decoded = zlib.decompress(image_data)
        if len(decoded) != height * (1 + width * 4):
            raise ValueError("некорректный размер декодированных пикселей")
        if any(decoded[row * (1 + width * 4)] > 4 for row in range(height)):
            raise ValueError("неподдерживаемый фильтр строки")
        print(f"[OK] {icon}: PNG {width}x{height}, данные успешно декодированы")
    except (OSError, ValueError, zlib.error, struct.error) as exc:
        fail(f"{path}: некорректный PNG — {exc}")


print("\n" + "=" * 60)
if errors:
    print(f"ОШИБКИ ({len(errors)}):")
    for e in errors:
        print("  -", e)
if not errors:
    print("ВСЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО")
sys.exit(1 if errors else 0)
