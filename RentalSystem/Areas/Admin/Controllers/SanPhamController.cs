using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Areas.Admin.Controllers
{
    // Quản lý danh mục sản phẩm thiết bị
    [Area("Admin")]
    [Authorize(Roles = "Admin,KinhDoanh,KyThuat")]
    public class SanPhamController : Controller
    {
        private readonly ApplicationDbContext _context;

        public SanPhamController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Danh sách sản phẩm và thống kê số lượng thiết bị trong kho
        public async Task<IActionResult> Index()
        {
            var sanPhams = await _context.SanPhams.Include(s => s.LoaiThietBi).ToListAsync();
            ViewBag.Categories = await _context.LoaiThietBis.ToListAsync();

            // Thống kê số lượng máy theo từng trạng thái
            var devices = await _context.ThietBis.ToListAsync();
            ViewBag.TotalMap = devices.GroupBy(t => t.MaSanPham).ToDictionary(g => g.Key, g => g.Count());
            ViewBag.AvailableMap = devices.Where(t => !_context.ChiTietHopDongs.Any(c => c.MaThietBi == t.MaThietBi && c.HopDong.TrangThai != 2 && c.HopDong.TrangThai != 3 && c.HopDong.NgayKetThuc > DateTime.Now)).GroupBy(t => t.MaSanPham).ToDictionary(g => g.Key, g => g.Count());
            ViewBag.RentedMap = devices.Where(t => t.TrangThai == 1).GroupBy(t => t.MaSanPham).ToDictionary(g => g.Key, g => g.Count());

            return View(sanPhams);
        }

        // Xem thông số kỹ thuật, cấu hình phần cứng và linh kiện tương thích
        public async Task<IActionResult> Details(int id)
        {
            var sp = await _context.SanPhams
                .Include(s => s.LoaiThietBi)
                .FirstOrDefaultAsync(m => m.MaSanPham == id);

            if (sp == null) return NotFound();

            // Danh sách máy vật lý thuộc dòng này trong kho
            ViewBag.Devices = await _context.ThietBis
                .Where(t => t.MaSanPham == id)
                .OrderBy(t => t.SoSerial)
                .ToListAsync();

            return View(sp);
        }

        // Form thêm sản phẩm mới
        [Authorize(Roles = "Admin,KinhDoanh")]
        public IActionResult Create()
        {
            ViewBag.MaLoai = new SelectList(_context.LoaiThietBis, "MaLoai", "TenLoai");
            return View();
        }

        // Lưu sản phẩm mới
        [Authorize(Roles = "Admin,KinhDoanh")]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create(SanPham sp)
        {
            ModelState.Remove("LoaiThietBi");
            ModelState.Remove("HinhAnh");
            ModelState.Remove("CauHinh");
            ModelState.Remove("MoTa");

            sp.HinhAnh = sp.HinhAnh ?? "";
            sp.CauHinh = sp.CauHinh ?? "";
            sp.MoTa = sp.MoTa ?? "";

            if (ModelState.IsValid)
            {
                _context.Add(sp);
                await _context.SaveChangesAsync();
                TempData["Success"] = "Đã thêm Sản phẩm mới vào hệ thống!";
                return RedirectToAction(nameof(Index));
            }
            ViewBag.MaLoai = new SelectList(_context.LoaiThietBis, "MaLoai", "TenLoai", sp.MaLoai);
            return View(sp);
        }

        // Form chỉnh sửa thông tin sản phẩm
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> Edit(int id)
        {
            var sp = await _context.SanPhams.FindAsync(id);
            if (sp == null) return NotFound();
            ViewBag.MaLoai = new SelectList(_context.LoaiThietBis, "MaLoai", "TenLoai", sp.MaLoai);
            return View(sp);
        }

        // Cập nhật thông tin sản phẩm
        [Authorize(Roles = "Admin,KinhDoanh")]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(int id, SanPham sp)
        {
            if (id != sp.MaSanPham) return NotFound();

            ModelState.Remove("LoaiThietBi");
            ModelState.Remove("HinhAnh");
            ModelState.Remove("CauHinh");
            ModelState.Remove("MoTa");

            sp.HinhAnh = sp.HinhAnh ?? "";
            sp.CauHinh = sp.CauHinh ?? "";
            sp.MoTa = sp.MoTa ?? "";

            if (ModelState.IsValid)
            {
                _context.Update(sp);
                await _context.SaveChangesAsync();
                TempData["Success"] = "Đã cập nhật thông tin sản phẩm thành công!";
                return RedirectToAction(nameof(Index));
            }
            ViewBag.MaLoai = new SelectList(_context.LoaiThietBis, "MaLoai", "TenLoai", sp.MaLoai);
            return View(sp);
        }

        // Xác nhận xóa sản phẩm
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> Delete(int id)
        {
            var sp = await _context.SanPhams.Include(s => s.LoaiThietBi).FirstOrDefaultAsync(m => m.MaSanPham == id);
            if (sp == null) return NotFound();

            bool hasDevices = await _context.ThietBis.AnyAsync(t => t.MaSanPham == id);
            if (hasDevices)
            {
                TempData["Error"] = "Không thể xóa: Dòng sản phẩm này đang có các thiết bị (Serial) trong kho!";
                return RedirectToAction(nameof(Index));
            }

            return View(sp);
        }

        // Xóa sản phẩm khỏi hệ thống
        [Authorize(Roles = "Admin,KinhDoanh")]
        [HttpPost, ActionName("Delete")]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DeleteConfirmed(int id)
        {
            var sp = await _context.SanPhams.FindAsync(id);
            if (sp != null)
            {
                bool hasDevices = await _context.ThietBis.AnyAsync(t => t.MaSanPham == id);
                if (hasDevices)
                {
                    TempData["Error"] = "KHÔNG THỂ XÓA: Sản phẩm này đang có thiết bị trong kho. Vui lòng xóa hết thiết bị trước!";
                    return RedirectToAction(nameof(Index));
                }
                
                _context.SanPhams.Remove(sp);
                await _context.SaveChangesAsync();
                TempData["Success"] = "Đã xóa sản phẩm thành công!";
            }
            return RedirectToAction(nameof(Index));
        }
    }
}
