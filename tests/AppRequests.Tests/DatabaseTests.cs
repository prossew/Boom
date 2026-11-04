using System;
using System.Collections.Generic;
using System.IO;
using Xunit;
using AppRequests.Models;

namespace AppRequests.Tests
{
    public class DatabaseTests : IDisposable
    {
        private readonly string dbPath;

        public DatabaseTests()
        {
            dbPath = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString("N") + ".db3");
        }

        public void Dispose()
        {
            if (File.Exists(dbPath)) File.Delete(dbPath);
        }

        [Fact]
        public void CreateTable_DoesNotThrowAndGetAllDataEmpty()
        {
            using var db = new MyDatabase(dbPath);
            var data = db.GetAllData();
            Assert.NotNull(data);
            Assert.Empty(data);
        }

        [Fact]
        public void AddData_GetAllDataReturnsRecordWithCorrectFields()
        {
            using var db = new MyDatabase(dbPath);
            db.AddData("Тестовая программа", "79123456789", "8 ГБ", "Windows", "Не запускается");

            var all = db.GetAllData();
            Assert.Single(all);
            Assert.Equal("Тестовая программа", all[0].Name);
            Assert.Equal("79123456789", all[0].Phone);
            Assert.Equal("8 ГБ", all[0].Memory);
            Assert.Equal("Windows", all[0].Platform);
            Assert.Equal("Не запускается", all[0].Text);
        }

        [Fact]
        public void AddData_IdAutoincrements()
        {
            using var db = new MyDatabase(dbPath);
            db.AddData("Prog1", "79123456789", "8 ГБ", "Windows", "t1");
            db.AddData("Prog2", "79123456788", "16 ГБ", "Linux", "t2");

            var all = db.GetAllData();
            Assert.Equal(2, all.Count);
            Assert.Equal(1, all[0].ID);
            Assert.Equal(2, all[1].ID);
        }

        [Fact]
        public void DeleteData_RemovesOnlySelectedRecord()
        {
            using var db = new MyDatabase(dbPath);
            db.AddData("Prog1", "79123456789", "8 ГБ", "Windows", "t1");
            db.AddData("Prog2", "79123456788", "16 ГБ", "Linux", "t2");

            db.DeleteData(1);
            var all = db.GetAllData();
            Assert.Single(all);
            Assert.Equal(2, all[0].ID);
            Assert.Equal("Prog2", all[0].Name);
        }

        [Fact]
        public void DeleteData_NonExistentId_DoesNotThrow()
        {
            using var db = new MyDatabase(dbPath);
            db.AddData("Prog1", "79123456789", "8 ГБ", "Windows", "t1");

            // не должно кидать исключение
            db.DeleteData(999);
            var all = db.GetAllData();
            Assert.Single(all);
        }

        [Fact]
        public void DataPersistsAcrossDatabaseInstances()
        {
            using (var db1 = new MyDatabase(dbPath))
            {
                db1.AddData("Prog1", "79123456789", "8 ГБ", "Windows", "t1");
            }

            using (var db2 = new MyDatabase(dbPath))
            {
                var all = db2.GetAllData();
                Assert.Single(all);
                Assert.Equal("Prog1", all[0].Name);
            }
        }
    }
}
