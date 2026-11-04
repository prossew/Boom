using AppRequests.Views;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace AppRequests
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class MainPage : Shell
    {
        public MainPage()
        {
            InitializeComponent();
            Routing.RegisterRoute(nameof(AddItem), typeof(AddItem));
        }
    }
}
