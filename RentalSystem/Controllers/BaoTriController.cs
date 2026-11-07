using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using RentalSystem.Services;

namespace RentalSystem.Controllers
{
    // Controller hỗ trợ Khách hàng báo hỏng / yêu cầu bảo trì thiết bị đang thuê,
    // theo dõi tiến độ sửa chữa, nghiệm thu và đánh giá chất lượng dịch vụ.
    [Authorize]
    public class BaoTriController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly IWebHostEnvironment _env;

        public BaoTriController(ApplicationDbContext context, IWebHostEnvironment env)
        {
            _context = context;
            _env = env;
        }

        // Mở giao diện tạo phiếu báo hỏng thiết bị.
        // Chỉ cho phép khách hàng tạo yêu cầu đối với hợp đồng đang có hiệu lực thuê
        [HttpGet]
        public async Task<IActionResult> TaoPhieu(int hopDongId)
        {
            var userIdStr = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
            {
                return Challenge();
            }

            var hopDong = await _context.HopDongs
                .Include(h => h.KhachHang)
                .FirstOrDefaultAsync(h => h.MaHopDong == hopDongId && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            // Kiểm tra trạng thái hợp đồng trước khi tiếp nhận yêu cầu
            if (hopDong.TrangThai != 1)
            {
                TempData["Error"] = "Chỉ có thể gửi yêu cầu bảo trì cho hợp đồng đang trong thời gian cho thuê (Đang thuê)!";
                return RedirectToAction("MyContracts", "Cart");
            }

            var thietBis = await _context.ChiTietHopDongs
                .Include(c => c.ThietBi)
                .ThenInclude(t => t.SanPham)
                .Where(c => c.MaHopDong == hopDongId)
                .ToListAsync();

            ViewBag.HopDong = hopDong;
            ViewBag.ThietBis = thietBis;

            return View();
        }

        [HttpGet]
        [ActionName("TaoYeuCau")]
        public async Task<IActionResult> TaoYeuCau(int hopDongId)
        {
            return await TaoPhieu(hopDongId);
        }

        // Tiếp nhận yêu cầu báo hỏng và lưu Phiếu Bảo Trì vào hệ thống.
        // Tải lên tệp đính kèm hình ảnh/video sự cố và xác định thời hạn cam kết xử lý
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> TaoPhieu(
            int maHopDong, 
            int maThietBi, 
            string moTaLoi,
            IFormFile? hinhAnhLoi = null,
            IFormFile? videoLoi = null,
            List<IFormFile>? hinhAnhSuCo = null,
            int? mucDoKhanCap = 1)
        {
            var userIdStr = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
            {
                return Challenge();
            }

            var files = new List<IFormFile>(hinhAnhSuCo ?? []);
            if (hinhAnhLoi != null) files.Add(hinhAnhLoi);
            if (videoLoi != null) files.Add(videoLoi);

            try
            {
                await CustomerMaintenance.ReportAsync(_context, _env.WebRootPath, userId, maHopDong,
                    maThietBi.ToString(), moTaLoi, mucDoKhanCap is 2 or 3 ? mucDoKhanCap.Value : 1,
                    files, allowVideo: true, HttpContext.RequestAborted);
            }
            catch (CustomerMaintenanceException error)
            {
                TempData["Error"] = error.Message;
                return error.StatusCode is 404 or 409
                    ? RedirectToAction(nameof(MyTickets))
                    : RedirectToAction(nameof(TaoPhieu), new { hopDongId = maHopDong });
            }

            TempData["Success"] = "Đã gửi yêu cầu bảo trì thành công! Nhân viên kỹ thuật sẽ liên hệ hỗ trợ bạn sớm.";
            return RedirectToAction("MyTickets");
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        [ActionName("TaoYeuCau")]
        public async Task<IActionResult> TaoYeuCau(int maHopDong, int maThietBi, string moTaLoi)
        {
            return await TaoPhieu(maHopDong, maThietBi, moTaLoi);
        }

        // Xem chi tiết tiến độ xử lý phiếu bảo trì
        [HttpGet]
        public async Task<IActionResult> ChiTiet(int id)
        {
            var userIdStr = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
            {
                return Challenge();
            }

            var phieu = await _context.PhieuBaoTris
                .Include(p => p.HopDong).ThenInclude(h => h!.KhachHang)
                .Include(p => p.ThietBi).ThenInclude(t => t.SanPham)
                .Include(p => p.KyThuatVien)
                .FirstOrDefaultAsync(p => p.MaPhieu == id && p.HopDong != null && p.HopDong.MaKhachHang == userId);

            if (phieu == null) return NotFound();

            // Lấy số tiền đền bù đã thanh toán (nếu có)
            decimal daThanhToan = 0;
            if (phieu.MaHopDong.HasValue)
            {
                daThanhToan = await _context.PhieuThus
                    .Where(pt => pt.MaHopDong == phieu.MaHopDong.Value && pt.LoaiPhieu == 2 && !pt.DaHuy)
                    .SumAsync(pt => (decimal?)pt.SoTien) ?? 0m;
            }
            ViewBag.DaThanhToanPhiDenBu = daThanhToan;

            return View(phieu);
        }

        // Xem danh sách tất cả các yêu cầu bảo trì mà khách hàng này đã từng gửi đi kèm tiến độ xử lý.
        [HttpGet]
        public async Task<IActionResult> MyTickets()
        {
            var userIdStr = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
            {
                return Challenge();
            }

            var tickets = await _context.PhieuBaoTris
                .Include(p => p.HopDong)
                .Include(p => p.ThietBi)
                .ThenInclude(t => t.SanPham)
                .Include(p => p.KyThuatVien)
                .Where(p => p.HopDong != null && p.HopDong.MaKhachHang == userId)
                .OrderByDescending(p => p.NgayBaoLoi)
                .ToListAsync();

            return View(tickets);
        }

        // Khách hàng xác nhận nghiệm thu sau khi thiết bị sửa xong
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> NghiemThu(int maPhieu, bool dongY, string? yKien = null)
        {
            var userIdStr = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
            {
                return Challenge();
            }

            return await ReviewAsync(userId, maPhieu, dongY, null, yKien);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DanhGia(int maPhieu, int rating, string? yKienPhanHoi = null)
        {
            var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (!int.TryParse(claim, out int userId)) return Challenge();
            return await ReviewAsync(userId, maPhieu, null, rating, yKienPhanHoi);
        }

        private async Task<IActionResult> ReviewAsync(int userId, int ticketId, bool? accepted, int? rating, string? feedback)
        {
            try
            {
                await CustomerMaintenance.ReviewAsync(_context, userId, ticketId, accepted, rating, feedback);
                TempData["Success"] = accepted switch
                {
                    true => "Đã xác nhận nghiệm thu.",
                    false => "Đã gửi yêu cầu xử lý lại.",
                    null => "Đã lưu đánh giá."
                };
            }
            catch (CustomerMaintenanceException error)
            {
                if (error.StatusCode == 404) return NotFound();
                TempData["Error"] = error.Message;
            }
            return RedirectToAction(nameof(ChiTiet), new { id = ticketId });
        }
    }
}
