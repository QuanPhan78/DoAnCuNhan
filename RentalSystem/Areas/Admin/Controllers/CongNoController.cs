using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Areas.Admin.Controllers
{
    // Controller quản lý công nợ khách hàng trong phân hệ Quản trị (Admin).
    // Cho phép các bộ phận Admin, Kinh doanh và Kế toán theo dõi tiến độ thanh toán,
    // các hợp đồng còn thiếu tiền hoặc sắp đến hạn thanh toán các kỳ.
    [Area("Admin")]
    [Authorize(Roles = "Admin,KinhDoanh,KeToan")]
    public class CongNoController : Controller
    {
        private readonly ApplicationDbContext _context;

        public CongNoController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Hiển thị danh sách công nợ của toàn bộ hệ thống.
        // Nghiệp vụ: Chỉ lấy các hợp đồng chưa trả đủ tiền (TrangThaiThanhToan != 2)
        // và loại trừ các đơn đã bị hủy (TrangThai != 3).
        public async Task<IActionResult> Index()
        {
            var hopDongs = await _context.HopDongs
                .Include(h => h.KhachHang)
                .Include(h => h.KyHanThanhToans)
                .Where(h => h.TrangThaiThanhToan != 2 && h.TrangThai != 3) // Loại trừ đơn đã tất toán hoặc đã hủy
                .OrderByDescending(h => h.NgayBatDau) // Sắp xếp theo ngày bắt đầu mới nhất
                .ToListAsync();

            return View(hopDongs);
        }
    }
}
