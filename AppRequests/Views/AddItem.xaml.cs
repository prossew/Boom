using System;
using AppRequests.Models;
using AppRequests.Services;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace AppRequests.Views
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class AddItem : ContentPage
    {
        private MyDatabase database;

        public AddItem()
        {
            InitializeComponent();
            string dbPath = System.IO.Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "mydata.db3");
            database = new MyDatabase(dbPath);
        }

        async void AddButton_Clicked(object sender, EventArgs e)
        {
            // 1) все поля обязательны
            if (string.IsNullOrWhiteSpace(nameEntry.Text) ||
                string.IsNullOrWhiteSpace(phoneEntry.Text) ||
                string.IsNullOrWhiteSpace(memoryEntry.Text) ||
                string.IsNullOrWhiteSpace(platformEntry.Text) ||
                string.IsNullOrWhiteSpace(textEntry.Text))
            {
                await DisplayAlert("Ошибка", "Заполните все поля", "OK");
                return;
            }

            // 2) валидация телефона
            if (!PhoneValidator.TryNormalize(phoneEntry.Text, out string normalizedPhone))
            {
                await DisplayAlert("Ошибка", "Введите полный Российский номер телефона!", "OK");
                return;
            }

            try
            {
                // 3) сохранение
                database.AddData(nameEntry.Text, normalizedPhone, memoryEntry.Text,
                    platformEntry.Text, textEntry.Text);

                nameEntry.Text = string.Empty;
                phoneEntry.Text = string.Empty;
                memoryEntry.Text = string.Empty;
                platformEntry.Text = string.Empty;
                textEntry.Text = string.Empty;

                await DisplayAlert("Уведомление", "Заявка успешно подана", "OK");
            }
            catch (Exception ex)
            {
                await DisplayAlert("Ошибка базы данных", ex.Message, "OK");
            }
        }
    }
}
