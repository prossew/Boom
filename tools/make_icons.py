#!/usr/bin/env python3
"""Генерация простых PNG-иконок (72x72) без внешних зависимостей (только zlib)."""
import os
import struct
import zlib

PURPLE = (0x99, 0x21, 0x96, 0xFE)  # цвет приложения #992196fe
WHITE = (0xFF, 0xFF, 0xFF, 0xFF)


def write_png(path, width, height, pixels):
    """pixels: список строк, каждая строка — список кортежей RGBA."""
    raw = b""
    for row in pixels:
        raw += b"\x00"  # фильтр "None" для строки
        for r, g, b, a in row:
            raw += bytes((r, g, b, a))
    compressed = zlib.compress(raw, 6)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    ihdr_crc = zlib.crc32(b"IHDR" + ihdr) & 0xFFFFFFFF
    idat_crc = zlib.crc32(b"IDAT" + compressed) & 0xFFFFFFFF
    iend_crc = zlib.crc32(b"IEND") & 0xFFFFFFFF
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(struct.pack(">I", 13) + b"IHDR" + ihdr + struct.pack(">I", ihdr_crc))
        f.write(struct.pack(">I", len(compressed)) + b"IDAT" + compressed + struct.pack(">I", idat_crc))
        f.write(struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc))


def make_icon(size, draw):
    px = [[PURPLE for _ in range(size)] for _ in range(size)]
    draw(px, size)
    return px


def circle(px, size, cx, cy, r, color):
    r2 = r * r
    for y in range(size):
        for x in range(size):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                px[y][x] = color


def rect(px, x0, y0, x1, y1, color):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px[y][x] = color


def draw_about(px, size):
    r = size // 2 - 4
    circle(px, size, size // 2, size // 2, r, WHITE)
    circle(px, size, size // 2, size // 2, r - 6, PURPLE)
    # точка под кружком (как у буквы "i" / инфо)
    dot = max(2, size // 14)
    rect(px, size // 2 - dot // 2, int(size * 0.68), size // 2 + dot // 2, int(size * 0.68) + dot - 1, WHITE)


def draw_feed(px, size):
    r = size // 2 - 4
    circle(px, size, size // 2, size // 2, r, WHITE)
    circle(px, size, size // 2, size // 2, r - 6, PURPLE)
    # знак плюс
    w = max(4, size // 8)
    half = w // 2
    cx = cy = size // 2
    rect(px, cx - half, cy - r // 2 + 2, cx + half, cy + r // 2 - 2, PURPLE)
    rect(px, cx - r // 2 + 2, cy - half, cx + r // 2 - 2, cy + half, PURPLE)


root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
drawable = os.path.join(root, "AppRequests.Android", "Resources", "drawable")
os.makedirs(drawable, exist_ok=True)

write_png(os.path.join(drawable, "icon_about.png"), 72, 72, make_icon(72, draw_about))
write_png(os.path.join(drawable, "icon_feed.png"), 72, 72, make_icon(72, draw_feed))

# Лаунчерная иконка icon.png для всех плотностей
for density, size in [("mipmap-ldpi", 36), ("mipmap-mdpi", 48), ("mipmap-hdpi", 72),
                      ("mipmap-xhdpi", 96), ("mipmap-xxhdpi", 144), ("mipmap-xxxhdpi", 192)]:
    d = os.path.join(root, "AppRequests.Android", "Resources", density)
    os.makedirs(d, exist_ok=True)
    write_png(os.path.join(d, "icon.png"), size, size, make_icon(size, draw_feed))

print("Icons created:")
for d, _, files in os.walk(os.path.join(root, "AppRequests.Android", "Resources")):
    for f in sorted(files):
        print(" ", os.path.join(d, f))
