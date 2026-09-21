using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Areas.Admin.Controllers
{
    // Controller quản lý tiếp nhận, điều phối và xử lý sự cố thiết bị (Bảo trì).
    // Hỗ trợ phân công kỹ thuật viên, cập nhật trạng thái sửa chữa và tính phí bồi thường nếu khách làm hỏng.
    [Area("Admin")]
    [Authorize]
    public class BaoTriController : Controller
    {
        private readonly ApplicationDbContext _context;

        public BaoTriController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Danh sách toàn bộ phiếu yêu cầu bảo trì, sự cố thiết bị được gửi từ khách hàng hoặc nội bộ.
        public async Task<IActionResult> Index()
        {
            var data = await _context.PhieuBaoTris
                .Include(p => p.HopDong)
                .Include(p => p.ThietBi)
                .Include(p => p.KyThuatVien)
                .OrderByDescending(p => p.NgayBaoLoi)
                .ToListAsync();
            return View(data);
        }

        // Xem chi tiết phiếu bảo trì, thông tin thiết bị lỗi, hợp đồng liên quan và phân công kỹ thuật viên.
        public async Task<IActionResult> Details(int id)
        {
            var phieu = await _context.PhieuBaoTris
                .Include(p => p.HopDong).ThenInclude(h => h.KhachHang)
                .Include(p => p.ThietBi).ThenInclude(t => t.SanPham)
                .Include(p => p.KyThuatVien)
                .FirstOrDefaultAsync(p => p.MaPhieu == id);

            if (phieu == null) return NotFound();

            // Nạp danh sách nhân viên có vai trò Kỹ Thuật (KyThuat) để phân công phụ trách
            ViewData["MaKyThuatVien"] = new SelectList(
                await _context.NguoiDungs.Where(n => n.VaiTro.TenVaiTro == "KyThuat").ToListAsync(), 
                "MaNguoiDung", "HoTen", phieu.MaKyThuatVien);

            return View(phieu);
        }

        // Cập nhật tiến độ sửa chữa: 1=Mới tiếp nhận, 2=Đang sửa chữa, 3=Đã sửa xong, 4=Hỏng không thể khắc phục.
        // Cho phép ghi chú kỹ thuật và bổ sung phí đền bù hư hỏng (nếu lỗi do khách hàng).
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> UpdateStatus(int id, int status, int? maKtv, string ghiChu, decimal phiDenBu)
        {
            var phieu = await _context.PhieuBaoTris.FindAsync(id);
            if (phieu == null) return NotFound();

            phieu.TrangThai = status;
            phieu.GhiChuSuaChua = ghiChu;
            phieu.PhiDenBu = phiDenBu;
            
            if (maKtv.HasValue)
            {
                phieu.MaKyThuatVien = maKtv.Value;
            }

            await _context.SaveChangesAsync();
            TempData["Success"] = "Cập nhật tiến độ bảo trì thành công!";
            return RedirectToAction(nameof(Details), new { id = id });
        }
    }
}
