using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Controllers
{
    // Controller hỗ trợ Khách hàng báo hỏng / yêu cầu bảo trì thiết bị đang thuê
    // và đánh giá mức độ hài lòng về chất lượng dịch vụ sửa chữa.
    [Authorize]
    public class BaoTriController : Controller
    {
        private readonly ApplicationDbContext _context;

        public BaoTriController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Mở giao diện tạo phiếu báo hỏng thiết bị.
        // Chỉ cho phép khách hàng tạo phiếu trên đúng các hợp đồng thuê của chính mình.
        [HttpGet]
        public async Task<IActionResult> TaoPhieu(int hopDongId)
        {
            var userId = int.Parse(User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier).Value);

            var hopDong = await _context.HopDongs
                .Include(h => h.KhachHang)
                .FirstOrDefaultAsync(h => h.MaHopDong == hopDongId && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            var thietBis = await _context.ChiTietHopDongs
                .Include(c => c.ThietBi)
                .ThenInclude(t => t.SanPham)
                .Where(c => c.MaHopDong == hopDongId)
                .ToListAsync();

            ViewBag.HopDong = hopDong;
            ViewBag.ThietBis = thietBis;

            return View();
        }

        // Tiếp nhận yêu cầu báo hỏng và lưu Phiếu Bảo Trì vào hệ thống.
        // Trạng thái khởi tạo là 1 (Mới tiếp nhận) để kỹ thuật viên vào xử lý.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> TaoPhieu(int maHopDong, int maThietBi, string moTaLoi)
        {
            var userId = int.Parse(User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier).Value);

            var hopDong = await _context.HopDongs
                .FirstOrDefaultAsync(h => h.MaHopDong == maHopDong && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            var phieu = new PhieuBaoTri
            {
                MaHopDong = maHopDong,
                MaThietBi = maThietBi,
                MoTaLoi = moTaLoi,
                NgayBaoLoi = DateTime.Now,
                TrangThai = 1, // 1: Mới tiếp nhận
                GhiChuSuaChua = "",
                PhiDenBu = 0
            };

            _context.PhieuBaoTris.Add(phieu);
            await _context.SaveChangesAsync();

            TempData["Success"] = "Đã gửi yêu cầu bảo trì thành công! Nhân viên kỹ thuật sẽ liên hệ hỗ trợ bạn sớm.";
            return RedirectToAction("MyContracts", "Cart");
        }
        
        // Xem danh sách tất cả các yêu cầu bảo trì mà khách hàng này đã từng gửi đi kèm tiến độ xử lý.
        [HttpGet]
        public async Task<IActionResult> MyTickets()
        {
            var userId = int.Parse(User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier).Value);

            var tickets = await _context.PhieuBaoTris
                .Include(p => p.HopDong)
                .Include(p => p.ThietBi)
                .ThenInclude(t => t.SanPham)
                .Where(p => p.HopDong.MaKhachHang == userId)
                .OrderByDescending(p => p.NgayBaoLoi)
                .ToListAsync();

            return View(tickets);
        }

        // Đánh giá chất lượng dịch vụ bảo trì (Thang điểm 1 - 5 sao) sau khi kỹ thuật viên hoàn thành.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DanhGia(int maPhieu, int rating)
        {
            var userId = int.Parse(User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier).Value);

            var phieu = await _context.PhieuBaoTris
                .Include(p => p.HopDong)
                .FirstOrDefaultAsync(p => p.MaPhieu == maPhieu && p.HopDong.MaKhachHang == userId);

            if (phieu == null) return NotFound();

            if (phieu.TrangThai != 3)
            {
                TempData["Error"] = "Chỉ đánh giá được phiếu đã hoàn thành (sửa xong)!";
                return RedirectToAction("MyTickets");
            }

            phieu.DanhGiaSao = rating;
            await _context.SaveChangesAsync();

            TempData["Success"] = "Cảm ơn bạn đã gửi đánh giá chất lượng dịch vụ bảo trì!";
            return RedirectToAction("MyTickets");
        }
    }
}
