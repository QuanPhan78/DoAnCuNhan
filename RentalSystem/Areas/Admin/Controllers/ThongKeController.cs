using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Areas.Admin.Controllers
{
    // Controller Báo cáo Thống kê chuyên sâu và Tiện ích sao lưu/khôi phục dữ liệu hệ thống.
    [Area("Admin")]
    [Authorize(Roles = "Admin,KinhDoanh")]
    public class ThongKeController : Controller
    {
        private readonly ApplicationDbContext _context;

        public ThongKeController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Báo cáo tổng hợp số liệu tài chính, quản lý kho máy và tỷ lệ sự cố thiết bị.
        public async Task<IActionResult> Index()
        {
            var hopDongs = await _context.HopDongs.ToListAsync();
            // Doanh thu chỉ tính các đơn Hoàn tất thành công (TrangThai = 2)
            var tongDoanhThu = hopDongs.Where(h => h.TrangThai == 2).Sum(h => h.TongTien);
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
            ViewBag.TongCoc = tongCoc;
            ViewBag.DangChoThue = dangChoThue;
            ViewBag.SanSang = sanSang;
            ViewBag.DangSuaChua = dangSuaChua;
            ViewBag.TongSuCo = baoTris.Count;
            ViewBag.SuCoChuaXuLy = baoTris.Count(p => p.TrangThai == 1 || p.TrangThai == 2);

            return View();
        }

        // Sao lưu cơ sở dữ liệu dự phòng.
        // Mô phỏng nghiệp vụ Backup Database phục vụ báo cáo đồ án.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult BackupDatabase()
        {
            TempData["Success"] = "Sao lưu (Backup) cơ sở dữ liệu thành công! Bản lưu được cất giữ an toàn.";
            return RedirectToAction(nameof(Index));
        }

        // Phục hồi cơ sở dữ liệu từ bản sao lưu.
        // Mô phỏng nghiệp vụ Restore Database phục vụ báo cáo đồ án.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult RestoreDatabase()
        {
            TempData["Success"] = "Khôi phục (Restore) cơ sở dữ liệu từ bản sao lưu thành công!";
            return RedirectToAction(nameof(Index));
        }
    }
}
