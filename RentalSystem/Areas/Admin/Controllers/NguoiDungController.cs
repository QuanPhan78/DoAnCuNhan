using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Areas.Admin.Controllers
{
    // Controller quản lý Người dùng và Phân quyền nội bộ (Admin, Kinh Doanh, Kế Toán, Kỹ Thuật, Khách Hàng).
    [Area("Admin")]
    [Authorize]
    public class NguoiDungController : Controller
    {
        private readonly ApplicationDbContext _context;

        public NguoiDungController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Danh sách toàn bộ tài khoản người dùng trong hệ thống kèm vai trò tương ứng.
        public async Task<IActionResult> Index()
        {
            var users = await _context.NguoiDungs.Include(n => n.VaiTro).ToListAsync();
            return View(users);
        }

        // Mở form tạo mới tài khoản người dùng / nhân viên.
        public async Task<IActionResult> Create()
        {
            ViewData["MaVaiTro"] = new SelectList(await _context.VaiTros.ToListAsync(), "MaVaiTro", "TenVaiTro");
            return View();
        }

        // Lưu tài khoản mới vào CSDL. Mặc định kích hoạt TrangThai = true.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create(NguoiDung nguoiDung)
        {
            ModelState.Remove("VaiTro");
            ModelState.Remove("Email");
            ModelState.Remove("MatKhau");
            ModelState.Remove("CCCD");
            ModelState.Remove("DiaChi");

            nguoiDung.Email = nguoiDung.Email ?? "";
            nguoiDung.MatKhau = nguoiDung.MatKhau ?? "";
            nguoiDung.CCCD = nguoiDung.CCCD ?? "";
            nguoiDung.DiaChi = nguoiDung.DiaChi ?? "";

            if (ModelState.IsValid)
            {
                nguoiDung.TrangThai = true;
                _context.Add(nguoiDung);
                await _context.SaveChangesAsync();
                TempData["Success"] = "Thêm người dùng thành công!";
                return RedirectToAction(nameof(Index));
            }
            ViewData["MaVaiTro"] = new SelectList(await _context.VaiTros.ToListAsync(), "MaVaiTro", "TenVaiTro", nguoiDung.MaVaiTro);
            return View(nguoiDung);
        }

        // Mở form chỉnh sửa thông tin người dùng (Đổi vai trò, khóa/mở tài khoản, cập nhật số điện thoại).
        public async Task<IActionResult> Edit(int? id)
        {
            if (id == null) return NotFound();

            var nguoiDung = await _context.NguoiDungs.FindAsync(id);
            if (nguoiDung == null) return NotFound();

            ViewData["MaVaiTro"] = new SelectList(await _context.VaiTros.ToListAsync(), "MaVaiTro", "TenVaiTro", nguoiDung.MaVaiTro);
            return View(nguoiDung);
        }

        // Cập nhật thông tin người dùng.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(int id, NguoiDung nguoiDung)
        {
            if (id != nguoiDung.MaNguoiDung) return NotFound();

            ModelState.Remove("VaiTro");
            ModelState.Remove("Email");
            ModelState.Remove("MatKhau");
            ModelState.Remove("CCCD");
            ModelState.Remove("DiaChi");

            nguoiDung.Email = nguoiDung.Email ?? "";
            nguoiDung.MatKhau = nguoiDung.MatKhau ?? "";
            nguoiDung.CCCD = nguoiDung.CCCD ?? "";
            nguoiDung.DiaChi = nguoiDung.DiaChi ?? "";

            if (ModelState.IsValid)
            {
                try
                {
                    _context.Update(nguoiDung);
                    await _context.SaveChangesAsync();
                    TempData["Success"] = "Cập nhật người dùng thành công!";
                }
                catch (DbUpdateConcurrencyException)
                {
                    if (!NguoiDungExists(nguoiDung.MaNguoiDung)) return NotFound();
                    else throw;
                }
                return RedirectToAction(nameof(Index));
            }
            ViewData["MaVaiTro"] = new SelectList(await _context.VaiTros.ToListAsync(), "MaVaiTro", "TenVaiTro", nguoiDung.MaVaiTro);
            return View(nguoiDung);
        }

        // Màn hình xác nhận xóa tài khoản người dùng.
        public async Task<IActionResult> Delete(int? id)
        {
            if (id == null) return NotFound();

            var nguoiDung = await _context.NguoiDungs
                .Include(n => n.VaiTro)
                .FirstOrDefaultAsync(m => m.MaNguoiDung == id);
            if (nguoiDung == null) return NotFound();

            return View(nguoiDung);
        }

        // Thực hiện xóa tài khoản khỏi hệ thống.
        [HttpPost, ActionName("Delete")]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DeleteConfirmed(int id)
        {
            var nguoiDung = await _context.NguoiDungs.FindAsync(id);
            if (nguoiDung != null)
            {
                _context.NguoiDungs.Remove(nguoiDung);
                await _context.SaveChangesAsync();
                TempData["Success"] = "Đã xóa người dùng thành công!";
            }
            return RedirectToAction(nameof(Index));
        }

        private bool NguoiDungExists(int id)
        {
            return _context.NguoiDungs.Any(e => e.MaNguoiDung == id);
        }
    }
}
