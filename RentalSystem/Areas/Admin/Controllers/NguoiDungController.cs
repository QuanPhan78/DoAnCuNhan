using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Areas.Admin.Controllers
{
    // Quản lý tài khoản người dùng và phân quyền
    [Area("Admin")]
    [Authorize(Roles = "Admin")]
    public class NguoiDungController : Controller
    {
        private readonly ApplicationDbContext _context;

        public NguoiDungController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Danh sách tài khoản người dùng
        public async Task<IActionResult> Index()
        {
            var users = await _context.NguoiDungs.Include(n => n.VaiTro).ToListAsync();
            return View(users);
        }

        // Form thêm tài khoản mới
        public async Task<IActionResult> Create()
        {
            ViewData["MaVaiTro"] = new SelectList(await _context.VaiTros.ToListAsync(), "MaVaiTro", "TenVaiTro");
            return View();
        }

        // Lưu tài khoản mới
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

        // Form chỉnh sửa tài khoản
        public async Task<IActionResult> Edit(int? id)
        {
            if (id == null) return NotFound();

            var nguoiDung = await _context.NguoiDungs.FindAsync(id);
            if (nguoiDung == null) return NotFound();

            ViewData["MaVaiTro"] = new SelectList(await _context.VaiTros.ToListAsync(), "MaVaiTro", "TenVaiTro", nguoiDung.MaVaiTro);
            return View(nguoiDung);
        }

        // Cập nhật thông tin tài khoản
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

            var existingUser = await _context.NguoiDungs.AsNoTracking().FirstOrDefaultAsync(u => u.MaNguoiDung == id);
            if (existingUser != null)
            {
                if (string.IsNullOrEmpty(nguoiDung.MatKhau)) nguoiDung.MatKhau = existingUser.MatKhau;
                if (string.IsNullOrEmpty(nguoiDung.Email)) nguoiDung.Email = existingUser.Email;
                if (string.IsNullOrEmpty(nguoiDung.CCCD)) nguoiDung.CCCD = existingUser.CCCD;
                if (string.IsNullOrEmpty(nguoiDung.DiaChi)) nguoiDung.DiaChi = existingUser.DiaChi;
            }

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

        // Xác nhận xóa tài khoản
        public async Task<IActionResult> Delete(int? id)
        {
            if (id == null) return NotFound();

            var nguoiDung = await _context.NguoiDungs
                .Include(n => n.VaiTro)
                .FirstOrDefaultAsync(m => m.MaNguoiDung == id);
            if (nguoiDung == null) return NotFound();

            return View(nguoiDung);
        }

        // Xóa tài khoản người dùng
        [HttpPost, ActionName("Delete")]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DeleteConfirmed(int id)
        {
            var nguoiDung = await _context.NguoiDungs.FindAsync(id);
            if (nguoiDung != null)
            {
                bool hasContracts = await _context.HopDongs.AnyAsync(h => h.MaKhachHang == id || h.MaNhanVien == id);
                if (hasContracts)
                {
                    TempData["Error"] = "KHÔNG THỂ XÓA: Người dùng này đang liên kết với hợp đồng trong hệ thống. Vui lòng vô hiệu hóa tài khoản thay vì xóa!";
                    return RedirectToAction(nameof(Index));
                }
                
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
