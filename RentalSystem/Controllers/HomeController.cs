using Microsoft.AspNetCore.Mvc;

namespace RentalSystem.Controllers
{
    // Controller Trang chủ phía giao diện Khách Hàng.
    // Giới thiệu dịch vụ cho thuê thiết bị công nghệ, banner quảng bá và quy trình thuê máy.
    public class HomeController : Controller
    {
        // Hiển thị giao diện Landing Page trang chủ.
        public IActionResult Index()
        {
            return View();
        }
    }
}
