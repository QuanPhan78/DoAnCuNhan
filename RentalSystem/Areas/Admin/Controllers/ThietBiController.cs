using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Areas.Admin.Controllers
{
    // Controller quản lý từng máy vật lý cụ thể (Định danh theo Số Serial).
    // Áp dụng các ràng buộc nghiệp vụ toàn vẹn dữ liệu: Không cho sửa/xóa máy đang cho thuê.
    [Area("Admin")]
    [Authorize(Roles = "Admin,KinhDoanh")]
    public class ThietBiController : Controller
    {
        private readonly ApplicationDbContext _context;

        public ThietBiController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Danh sách toàn bộ các thiết bị vật lý trong hệ thống kèm trạng thái (Sẵn sàng, Đang thuê, Bảo trì, Giữ chỗ).
        public async Task<IActionResult> Index()
        {
            var data = await _context.ThietBis.Include(t => t.SanPham).ToListAsync();
            return View(data);
        }

        // Mở form nhập thiết bị (Serial) mới vào kho.
        public IActionResult Create()
        {
            ViewBag.MaSanPham = new SelectList(_context.SanPhams, "MaSanPham", "TenSanPham");
            return View();
        }

        // Thêm máy mới: Kiểm tra trùng lặp Số Serial để tránh nhập trùng thiết bị.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create(ThietBi tb)
        {
            ModelState.Remove("SanPham");
            ModelState.Remove("TinhTrangMay");
            
            if (string.IsNullOrEmpty(tb.TinhTrangMay)) 
            {
                tb.TinhTrangMay = "Mới 100%"; 
            }

            if (ModelState.IsValid)
            {
                bool isExist = await _context.ThietBis.AnyAsync(x => x.SoSerial == tb.SoSerial);
                if (isExist)
                {
                    ModelState.AddModelError("SoSerial", "Số Serial này đã tồn tại trong hệ thống. Vui lòng kiểm tra lại!");
                    ViewBag.MaSanPham = new SelectList(_context.SanPhams, "MaSanPham", "TenSanPham", tb.MaSanPham);
                    return View(tb);
                }

                _context.Add(tb);
                await _context.SaveChangesAsync();
                TempData["Success"] = "Đã nhập thêm thiết bị (Serial) mới vào kho!";
                return RedirectToAction(nameof(Index));
            }
            ViewBag.MaSanPham = new SelectList(_context.SanPhams, "MaSanPham", "TenSanPham", tb.MaSanPham);
            return View(tb);
        }

        // Mở form chỉnh sửa thông tin máy vật lý.
        public async Task<IActionResult> Edit(int id)
        {
            var tb = await _context.ThietBis.FindAsync(id);
            if (tb == null) return NotFound();
            ViewBag.MaSanPham = new SelectList(_context.SanPhams, "MaSanPham", "TenSanPham", tb.MaSanPham);
            return View(tb);
        }

        // Cập nhật thông tin thiết bị:
        // Ràng buộc bảo mật: Nghiêm cấm chỉnh sửa khi máy đang được khách thuê (TrangThai = 1).
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(int id, ThietBi tb)
        {
            if (id != tb.MaThietBi) return NotFound();

            ModelState.Remove("SanPham");
            ModelState.Remove("TinhTrangMay");
            
            if (string.IsNullOrEmpty(tb.TinhTrangMay)) 
            {
                tb.TinhTrangMay = "Mới 100%"; 
            }

            if (ModelState.IsValid)
            {
                var oldTb = await _context.ThietBis.AsNoTracking().FirstOrDefaultAsync(x => x.MaThietBi == id);
                if (oldTb != null && oldTb.TrangThai == 1)
                {
                    TempData["Error"] = "BẢO MẬT: Máy đang được khách thuê, nghiêm cấm chỉnh sửa thông tin để tránh sai lệch Hợp đồng!";
                    return RedirectToAction(nameof(Index));
                }

                if (oldTb != null && oldTb.SoSerial != tb.SoSerial)
                {
                    bool isExist = await _context.ThietBis.AnyAsync(x => x.SoSerial == tb.SoSerial);
                    if (isExist)
                    {
                        ModelState.AddModelError("SoSerial", "Số Serial này đã được gán cho máy khác!");
                        ViewBag.MaSanPham = new SelectList(_context.SanPhams, "MaSanPham", "TenSanPham", tb.MaSanPham);
                        return View(tb);
                    }
                }

                _context.Update(tb);
                await _context.SaveChangesAsync();
                TempData["Success"] = "Đã cập nhật thông tin thiết bị thành công!";
                return RedirectToAction(nameof(Index));
            }
            ViewBag.MaSanPham = new SelectList(_context.SanPhams, "MaSanPham", "TenSanPham", tb.MaSanPham);
            return View(tb);
        }

        // Mở màn hình xác nhận xóa thiết bị khỏi hệ thống.
        public async Task<IActionResult> Delete(int id)
        {
            var tb = await _context.ThietBis.Include(t => t.SanPham).FirstOrDefaultAsync(m => m.MaThietBi == id);
            if (tb == null) return NotFound();
            return View(tb);
        }

        // Thực hiện xóa thiết bị:
        // Ràng buộc toàn vẹn: Không cho phép xóa máy đang cho thuê hoặc máy đã từng gắn liền với hợp đồng lịch sử.
        [HttpPost, ActionName("Delete")]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DeleteConfirmed(int id)
        {
            var tb = await _context.ThietBis.FindAsync(id);
            if (tb != null)
            {
                if (tb.TrangThai == 1)
                {
                    TempData["Error"] = "KHÔNG THỂ XÓA: Thiết bị này đang được cho thuê!";
                    return RedirectToAction(nameof(Index));
                }

                bool hasHistory = await _context.ChiTietHopDongs.AnyAsync(c => c.MaThietBi == id);
                if (hasHistory)
                {
                    TempData["Error"] = "KHÔNG THỂ XÓA: Thiết bị này đã có dữ liệu trong hợp đồng lịch sử. Hãy chuyển trạng thái sang Bảo trì hoặc Ngưng sử dụng!";
                    return RedirectToAction(nameof(Index));
                }

                _context.ThietBis.Remove(tb);
                await _context.SaveChangesAsync();
                TempData["Success"] = "Đã xóa thiết bị khỏi hệ thống thành công!";
            }
            return RedirectToAction(nameof(Index));
        }
    }
}
