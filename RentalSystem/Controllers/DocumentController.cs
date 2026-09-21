using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Controllers
{
    // Controller xuất văn bản, hóa đơn và in Hợp đồng điện tử.
    // Tích hợp tính năng bảo mật phân quyền xem hợp đồng theo đúng chủ sở hữu.
    [Authorize]
    public class DocumentController : Controller
    {
        private readonly ApplicationDbContext _context;

        public DocumentController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Xem bản in Hợp Đồng Thuê Thiết Bị chuẩn pháp lý:
        // Bao gồm điều khoản thuê, thông tin 2 bên, danh sách máy serial kèm chữ ký số điện tử Base64.
        // Bảo mật: Khách hàng thông thường chỉ được in hợp đồng của chính mình.
        [HttpGet]
        public async Task<IActionResult> InHopDong(int id)
        {
            var hopDong = await _context.HopDongs
                .Include(h => h.KhachHang)
                .Include(h => h.NhanVien)
                .FirstOrDefaultAsync(h => h.MaHopDong == id);

            if (hopDong == null) return NotFound();

            // Kiểm tra phân quyền truy cập hợp đồng
            var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (claim != null && int.TryParse(claim.Value, out int userId))
            {
                // Nếu người dùng không phải Admin hoặc Kinh Doanh, chỉ được phép xem hợp đồng của chính mình
                if (!User.IsInRole("Admin") && !User.IsInRole("KinhDoanh"))
                {
                    if (hopDong.MaKhachHang != userId)
                    {
                        return Unauthorized("BẢO MẬT: Bạn không có quyền xem bản in hợp đồng của khách hàng khác.");
                    }
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
    }
}
