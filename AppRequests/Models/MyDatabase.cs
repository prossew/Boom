using System;
using System.Collections.Generic;
using System.IO;
using SQLite;

namespace AppRequests.Models
{
    public class MyDatabase : IDisposable
    {
        private SQLiteConnection database;

        public MyDatabase(string dbPath)
        {
            database = new SQLiteConnection(dbPath);
            database.CreateTable<MyData>();
        }

        public List<MyData> GetAllData() => database.Table<MyData>().ToList();

        public void AddData(string name, string phone, string memory, string platform, string text)
        {
            var data = new MyData
            {
                Name = name,
                Phone = phone,
                Memory = memory,
                Platform = platform,
                Text = text
            };
            database.Insert(data);
        }

        public void DeleteData(int id) => database.Delete<MyData>(id);

        public void Dispose()
        {
            database?.Dispose();
        }
    }
}
