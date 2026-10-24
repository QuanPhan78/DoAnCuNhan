using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Controllers
{
    // Xuất văn bản và in hợp đồng điện tử
    [Authorize]
    public class DocumentController : Controller
    {
        private readonly ApplicationDbContext _context;

        public DocumentController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Xem bản in hợp đồng thuê thiết bị
        [HttpGet]
        public async Task<IActionResult> InHopDong(int id)
        {
            var hopDong = await _context.HopDongs
                .Include(h => h.KhachHang)
                .Include(h => h.NhanVien)
                .FirstOrDefaultAsync(h => h.MaHopDong == id);

            if (hopDong == null) return NotFound();

            // Kiểm tra phân quyền truy cập hợp đồng
            if (!User.IsInRole("Admin") && !User.IsInRole("KinhDoanh") && !User.IsInRole("KyThuat"))
            {
                var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
                if (claim == null || !int.TryParse(claim.Value, out int userId) || hopDong.MaKhachHang != userId)
                {
                    return Unauthorized("BẢO MẬT: Bạn không có quyền xem bản in hợp đồng của khách hàng khác.");
                }
            }

            // Nạp danh sách thiết bị và sản phẩm chi tiết trong hợp đồng
            var chiTiets = await _context.ChiTietHopDongs
                .Include(c => c.ThietBi).ThenInclude(t => t.SanPham)
                .Where(c => c.MaHopDong == id)
                .ToListAsync();

            ViewBag.ChiTiets = chiTiets;
            return View(hopDong);
        }

        // Xem và in Biên bản bàn giao / thu hồi thiết bị
        [HttpGet]
        public async Task<IActionResult> InBienBanBanGiao(int id)
        {
            var bienBan = await _context.BienBanBanGiaos
                .Include(b => b.NhanVienLap)
                .Include(b => b.HopDong)
                    .ThenInclude(h => h.KhachHang)
                .Include(b => b.HopDong)
                    .ThenInclude(h => h.NhanVien)
                .FirstOrDefaultAsync(b => b.MaBienBan == id);

            if (bienBan == null) return NotFound();

            if (!User.IsInRole("Admin") && !User.IsInRole("KinhDoanh") && !User.IsInRole("KyThuat"))
            {
                var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
                if (claim == null || !int.TryParse(claim.Value, out int userId) || bienBan.HopDong == null || bienBan.HopDong.MaKhachHang != userId)
                {
                    return Unauthorized("BẢO MẬT: Bạn không có quyền xem biên bản bàn giao của khách hàng khác.");
                }
            }

            var chiTiets = await _context.ChiTietHopDongs
                .Include(c => c.ThietBi).ThenInclude(t => t.SanPham)
                .Where(c => c.MaHopDong == bienBan.MaHopDong)
                .ToListAsync();

            ViewBag.ChiTiets = chiTiets;
            return View(bienBan);
        }

        // Xem và in Phiếu thu tiền
        [HttpGet]
        public async Task<IActionResult> InPhieuThu(int id)
        {
            var phieuThu = await _context.PhieuThus
                .Include(p => p.NhanVienThu)
                .Include(p => p.KyHanThanhToan)
                .Include(p => p.HopDong)
                    .ThenInclude(h => h.KhachHang)
                .Include(p => p.HopDong)
                    .ThenInclude(h => h.NhanVien)
                .FirstOrDefaultAsync(p => p.MaPhieuThu == id);

            if (phieuThu == null) return NotFound("Không tìm thấy phiếu thu yêu cầu.");

            if (!User.IsInRole("Admin") && !User.IsInRole("KinhDoanh") && !User.IsInRole("KeToan"))
            {
                var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
                if (claim == null || !int.TryParse(claim.Value, out int userId) || phieuThu.HopDong == null || phieuThu.HopDong.MaKhachHang != userId)
                {
                    return Unauthorized("BẢO MẬT: Bạn không có quyền xem phiếu thu của khách hàng khác.");
                }
            }

            return View(phieuThu);
        }
    }
}
