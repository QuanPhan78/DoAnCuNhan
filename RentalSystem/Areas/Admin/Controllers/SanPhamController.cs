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
    // Controller quản lý Danh mục Sản phẩm (Model/Dòng máy) trong phân hệ Quản trị.
    // Quản lý giá thuê, cấu hình, hình ảnh đại diện và thống kê tồn kho theo từng dòng máy.
    [Area("Admin")]
    [Authorize(Roles = "Admin,KinhDoanh")]
    public class SanPhamController : Controller
    {
        private readonly ApplicationDbContext _context;

        public SanPhamController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Danh sách sản phẩm kèm theo thống kê số lượng máy vật lý:
        // Tổng số máy trong kho, số máy sẵn sàng cho thuê và số máy đang có khách thuê.
        public async Task<IActionResult> Index()
        {
            var sanPhams = await _context.SanPhams.Include(s => s.LoaiThietBi).ToListAsync();
            ViewBag.Categories = await _context.LoaiThietBis.ToListAsync();

            // Đồng bộ dữ liệu tồn kho thực tế từ bảng thiết bị con (ThietBi)
            var devices = await _context.ThietBis.ToListAsync();
            ViewBag.TotalMap = devices.GroupBy(t => t.MaSanPham).ToDictionary(g => g.Key, g => g.Count());
            ViewBag.AvailableMap = devices.Where(t => t.TrangThai == 0).GroupBy(t => t.MaSanPham).ToDictionary(g => g.Key, g => g.Count());
            ViewBag.RentedMap = devices.Where(t => t.TrangThai == 1).GroupBy(t => t.MaSanPham).ToDictionary(g => g.Key, g => g.Count());

            return View(sanPhams);
        }

        // Mở form thêm mới dòng sản phẩm.
        public IActionResult Create()
        {
            ViewBag.MaLoai = new SelectList(_context.LoaiThietBis, "MaLoai", "TenLoai");
            return View();
        }

        // Tiếp nhận dữ liệu lưu sản phẩm mới vào CSDL.
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

        // Mở form chỉnh sửa thông tin sản phẩm (giá thuê, tên máy, cấu hình).
        public async Task<IActionResult> Edit(int id)
        {
            var sp = await _context.SanPhams.FindAsync(id);
            if (sp == null) return NotFound();
            ViewBag.MaLoai = new SelectList(_context.LoaiThietBis, "MaLoai", "TenLoai", sp.MaLoai);
            return View(sp);
        }

        // Cập nhật thông tin sản phẩm sau khi sửa đổi.
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

        // Xác nhận xóa dòng sản phẩm.
        // Kiểm tra an toàn: Nếu đã có thiết bị con thuộc sản phẩm này thì không cho phép xóa.
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

        // Thực hiện xóa sản phẩm khỏi CSDL.
        [HttpPost, ActionName("Delete")]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DeleteConfirmed(int id)
        {
            var sp = await _context.SanPhams.FindAsync(id);
            if (sp != null)
            {
                _context.SanPhams.Remove(sp);
                await _context.SaveChangesAsync();
                TempData["Success"] = "Đã xóa sản phẩm thành công!";
            }
            return RedirectToAction(nameof(Index));
        }
    }
}
