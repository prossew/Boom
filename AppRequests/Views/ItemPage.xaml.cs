using System;
using AppRequests.Models;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace AppRequests.Views
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class ItemPage : ContentPage
    {
        private MyDatabase database;

        public ItemPage()
        {
            InitializeComponent();
            string dbPath = System.IO.Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "mydata.db3");
            database = new MyDatabase(dbPath);
            dataList.ItemsSource = database.GetAllData();
            UpdateEmptyLabel();
        }

        protected override void OnAppearing()
        {
            base.OnAppearing();
            dataList.ItemsSource = database.GetAllData();
            UpdateEmptyLabel();
        }

        void UpdateEmptyLabel()
        {
            var list = dataList.ItemsSource as System.Collections.IList;
            bool empty = list == null || list.Count == 0;
            emptyLabel.IsVisible = empty;
            dataList.IsVisible = !empty;
        }

        async void DeleteButton_Clicked(object sender, EventArgs e)
        {
            var data = dataList.SelectedItem as Models.MyData;
            if (data == null)
            {
                await DisplayAlert("Внимание", "Выберите заявку для удаления", "OK");
                return;
            }

            bool confirm = await DisplayAlert("Удаление", "Удалить выбранную заявку?", "Да", "Нет");
            if (!confirm) return;

            database.DeleteData(data.ID);
            dataList.ItemsSource = database.GetAllData();
            UpdateEmptyLabel();
        }

        void UpdateButton_Clicked(object sender, EventArgs e)
        {
            dataList.ItemsSource = database.GetAllData();
            UpdateEmptyLabel();
        }
    }
}
