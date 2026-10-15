using System.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using RentalSystem.Models;

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

        // Xử lý hiển thị trang thông báo lỗi
        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
    }
}

namespace RentalSystem.Models
{
    public class ErrorViewModel
    {
        public string? RequestId { get; set; }
        public bool ShowRequestId => !string.IsNullOrEmpty(RequestId);
    }
}
