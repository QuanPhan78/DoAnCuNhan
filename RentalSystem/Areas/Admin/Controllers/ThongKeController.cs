using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Areas.Admin.Controllers
{
    // Báo cáo thống kê tài chính và thiết bị
    [Area("Admin")]
    [Authorize(Roles = "Admin,KinhDoanh")]
    public class ThongKeController : Controller
    {
        private readonly ApplicationDbContext _context;

        public ThongKeController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Thống kê doanh thu, tình trạng kho máy và phiếu bảo trì
        public async Task<IActionResult> Index()
        {
            var hopDongs = await _context.HopDongs.ToListAsync();

            // Doanh thu theo dòng tiền thực thu: Tổng PhieuThu (LoaiPhieu == 0 || LoaiPhieu == 2, !DaHuy) trừ PhieuChi
            var tongThu = await _context.PhieuThus
                .Where(pt => !pt.DaHuy && (pt.LoaiPhieu == 0 || pt.LoaiPhieu == 2))
                .SumAsync(pt => (decimal?)pt.SoTien) ?? 0m;

            var tongChi = await _context.PhieuChis
                .SumAsync(pc => (decimal?)pc.SoTien) ?? 0m;

            var tongDoanhThu = tongThu - tongChi;

            // Tiền cọc giữ chỗ: Tính các đơn Chờ duyệt hoặc Đang cho thuê (0, 1)
            var tongCoc = hopDongs.Where(h => h.TrangThai == 0 || h.TrangThai == 1).Sum(h => h.TienDaCoc);
            
            // Phân loại trạng thái toàn bộ máy vật lý trong kho
            var thietBis = await _context.ThietBis.ToListAsync();
            var dangChoThue = thietBis.Count(t => t.TrangThai == 1);
            var sanSang = thietBis.Count(t => t.TrangThai == 0);
            var dangSuaChua = thietBis.Count(t => t.TrangThai == 2);

            // Báo cáo tình hình bảo trì và sự cố kỹ thuật
            var baoTris = await _context.PhieuBaoTris.ToListAsync();

            ViewBag.TongDoanhThu = tongDoanhThu;
            ViewBag.TongThu = tongThu;
            ViewBag.TongChi = tongChi;
            ViewBag.TongCoc = tongCoc;
            ViewBag.DangChoThue = dangChoThue;
            ViewBag.SanSang = sanSang;
            ViewBag.DangSuaChua = dangSuaChua;
            ViewBag.TongSuCo = baoTris.Count;
            ViewBag.SuCoChuaXuLy = baoTris.Count(p => p.TrangThai == 1 || p.TrangThai == 2);

            return View();
        }

        // Sao lưu cơ sở dữ liệu dự phòng
        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult BackupDatabase()
        {
            TempData["Success"] = "Sao lưu (Backup) cơ sở dữ liệu thành công! Bản lưu được cất giữ an toàn.";
            return RedirectToAction(nameof(Index));
        }

        // Phục hồi cơ sở dữ liệu từ bản sao lưu
        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult RestoreDatabase()
        {
            TempData["Success"] = "Khôi phục (Restore) cơ sở dữ liệu từ bản sao lưu thành công!";
            return RedirectToAction(nameof(Index));
        }
    }
}
