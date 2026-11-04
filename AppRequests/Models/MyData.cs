using SQLite;

namespace AppRequests.Models
{
    public class MyData
    {
        [PrimaryKey, AutoIncrement]
        public int ID { get; set; }

        [NotNull, MaxLength(30)]
        public string Name { get; set; }

        [NotNull, MaxLength(11)]
        public string Phone { get; set; }

        [NotNull, MaxLength(20)]
        public string Memory { get; set; }

        [NotNull, MaxLength(50)]
        public string Platform { get; set; }

        [NotNull, MaxLength(200)]
        public string Text { get; set; }
    }
}
