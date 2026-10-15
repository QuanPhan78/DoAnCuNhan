using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Areas.Admin.Controllers
{
    // Quản lý các chương trình và mã khuyến mãi
    [Area("Admin")]
    [Authorize(Roles = "Admin,KinhDoanh")]
    public class KhuyenMaiController : Controller
    {
        private readonly ApplicationDbContext _context;

        public KhuyenMaiController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Danh sách mã khuyến mãi
        public async Task<IActionResult> Index()
        {
            var list = await _context.KhuyenMais
                .OrderByDescending(k => k.MaKM)
                .ToListAsync();

            // Đếm số lần sử dụng của từng mã
            var usageCounts = await _context.HopDongs
                .Where(h => h.MaKhuyenMai != null)
                .GroupBy(h => h.MaKhuyenMai!.Value)
                .ToDictionaryAsync(g => g.Key, g => g.Count());

            ViewBag.UsageCounts = usageCounts;

            return View(list);
        }

        // Form tạo mã khuyến mãi
        public IActionResult Create()
        {
            var model = new KhuyenMai
            {
                NgayBatDau = DateTime.Today,
                NgayKetThuc = DateTime.Today.AddMonths(1),
                SoLuong = 50,
                PhanTramGiam = 10,
                KichHoat = true
            };
            return View(model);
        }

        // Lưu mã khuyến mãi mới
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create(KhuyenMai km)
        {
            km.Code = (km.Code ?? string.Empty).Trim().ToUpperInvariant();

            if (string.IsNullOrWhiteSpace(km.Code))
            {
                ModelState.AddModelError("Code", "Vui lòng nhập mã khuyến mãi!");
            }
            else
            {
                var isDuplicate = await _context.KhuyenMais.AnyAsync(k =>
                    k.Code.ToUpper() == km.Code.ToUpper() ||
                    (k.MaCode != null && k.MaCode.ToUpper() == km.Code.ToUpper()));

                if (isDuplicate)
                {
                    ModelState.AddModelError("Code", $"Mã khuyến mãi '{km.Code}' đã tồn tại trong hệ thống!");
                }
            }

            if (km.NgayKetThuc < km.NgayBatDau)
            {
                ModelState.AddModelError("NgayKetThuc", "Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu!");
            }

            if (km.PhanTramGiam < 1 || km.PhanTramGiam > 100)
            {
                ModelState.AddModelError("PhanTramGiam", "Phần trăm giảm phải nằm trong khoảng từ 1% đến 100%!");
            }

            if (km.SoLuong < 0)
            {
                ModelState.AddModelError("SoLuong", "Số lượng lượt sử dụng phải lớn hơn hoặc bằng 0!");
            }

            if (!ModelState.IsValid)
            {
                return View(km);
            }

            _context.KhuyenMais.Add(km);
            await _context.SaveChangesAsync();

            TempData["Success"] = $"Thêm mới mã khuyến mãi '{km.Code}' (giảm {km.PhanTramGiam}%) thành công!";
            return RedirectToAction(nameof(Index));
        }

        // Form chỉnh sửa mã khuyến mãi
        public async Task<IActionResult> Edit(int id)
        {
            var km = await _context.KhuyenMais.FindAsync(id);
            if (km == null)
            {
                TempData["Error"] = "Không tìm thấy mã khuyến mãi yêu cầu!";
                return RedirectToAction(nameof(Index));
            }

            return View(km);
        }

        // Cập nhật thông tin mã khuyến mãi
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(int id, KhuyenMai km)
        {
            if (id != km.MaKM)
            {
                return BadRequest();
            }

            km.Code = (km.Code ?? string.Empty).Trim().ToUpperInvariant();

            if (string.IsNullOrWhiteSpace(km.Code))
            {
                ModelState.AddModelError("Code", "Vui lòng nhập mã khuyến mãi!");
            }
            else
            {
                var isDuplicate = await _context.KhuyenMais.AnyAsync(k =>
                    k.MaKM != id &&
                    (k.Code.ToUpper() == km.Code.ToUpper() || (k.MaCode != null && k.MaCode.ToUpper() == km.Code.ToUpper())));

                if (isDuplicate)
                {
                    ModelState.AddModelError("Code", $"Mã khuyến mãi '{km.Code}' đã được sử dụng bởi chương trình khác!");
                }
            }

            if (km.NgayKetThuc < km.NgayBatDau)
            {
                ModelState.AddModelError("NgayKetThuc", "Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu!");
            }

            if (km.PhanTramGiam < 1 || km.PhanTramGiam > 100)
            {
                ModelState.AddModelError("PhanTramGiam", "Phần trăm giảm phải nằm trong khoảng từ 1% đến 100%!");
            }

            if (km.SoLuong < 0)
            {
                ModelState.AddModelError("SoLuong", "Số lượng lượt sử dụng phải lớn hơn hoặc bằng 0!");
            }

            if (!ModelState.IsValid)
            {
                return View(km);
            }

            var existing = await _context.KhuyenMais.FindAsync(id);
            if (existing == null)
            {
                TempData["Error"] = "Không tìm thấy mã khuyến mãi trong hệ thống!";
                return RedirectToAction(nameof(Index));
            }

            existing.Code = km.Code;
            existing.PhanTramGiam = km.PhanTramGiam;
            existing.NgayBatDau = km.NgayBatDau;
            existing.NgayKetThuc = km.NgayKetThuc;
            existing.SoLuong = km.SoLuong;
            existing.KichHoat = km.KichHoat;
            existing.MoTa = km.MoTa;

            await _context.SaveChangesAsync();

            TempData["Success"] = $"Cập nhật mã khuyến mãi '{existing.Code}' thành công!";
            return RedirectToAction(nameof(Index));
        }

        // Xóa mã khuyến mãi hoặc tắt kích hoạt nếu đã có hợp đồng sử dụng
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Delete(int id)
        {
            var km = await _context.KhuyenMais.FindAsync(id);
            if (km == null)
            {
                TempData["Error"] = "Không tìm thấy mã khuyến mãi để xóa!";
                return RedirectToAction(nameof(Index));
            }

            bool hasContracts = await _context.HopDongs.AnyAsync(h => h.MaKhuyenMai == id);
            if (hasContracts)
            {
                km.KichHoat = false;
                await _context.SaveChangesAsync();
                TempData["Success"] = $"Mã '{km.Code}' đã được áp dụng trong hợp đồng nên hệ thống chuyển trạng thái sang Tạm dừng/Ngừng kích hoạt để bảo toàn dữ liệu lịch sử.";
            }
            else
            {
                _context.KhuyenMais.Remove(km);
                await _context.SaveChangesAsync();
                TempData["Success"] = $"Xóa mã khuyến mãi '{km.Code}' thành công!";
            }

            return RedirectToAction(nameof(Index));
        }

        // Bật hoặc tắt trạng thái kích hoạt
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> ToggleStatus(int id)
        {
            var km = await _context.KhuyenMais.FindAsync(id);
            if (km == null)
            {
                TempData["Error"] = "Không tìm thấy mã khuyến mãi!";
                return RedirectToAction(nameof(Index));
            }

            km.KichHoat = !km.KichHoat;
            await _context.SaveChangesAsync();

            TempData["Success"] = $"Đã {(km.KichHoat ? "kích hoạt" : "tạm dừng")} mã khuyến mãi '{km.Code}'!";
            return RedirectToAction(nameof(Index));
        }

        // Phương thức hỗ trợ đổi trạng thái
        [HttpPost]
        [ValidateAntiForgeryToken]
        public Task<IActionResult> ToggleActive(int id) => ToggleStatus(id);
    }
}
