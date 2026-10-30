using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Areas.Admin.Controllers
{
    // Quản lý từng thiết bị theo số serial trong hệ thống
    [Area("Admin")]
    [Authorize(Roles = "Admin,KinhDoanh,KyThuat")]
    public class ThietBiController : Controller
    {
        private readonly ApplicationDbContext _context;

        public ThietBiController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Danh sách toàn bộ các thiết bị vật lý trong hệ thống kèm trạng thái và bộ lọc tìm kiếm
        public async Task<IActionResult> Index(int? status = null, string? search = null)
        {
            var allDevices = await _context.ThietBis.ToListAsync();
            ViewBag.CountAll = allDevices.Count;
            ViewBag.CountReady = allDevices.Count(t => t.TrangThai == 0);
            ViewBag.CountRenting = allDevices.Count(t => t.TrangThai == 1);
            ViewBag.CountMaintenance = allDevices.Count(t => t.TrangThai == 2);
            ViewBag.CountReserved = allDevices.Count(t => t.TrangThai == 3);
            ViewBag.CountDisposed = allDevices.Count(t => t.TrangThai == 4);
            ViewBag.CurrentStatus = status;
            ViewBag.CurrentSearch = search;

            var query = _context.ThietBis.Include(t => t.SanPham).AsQueryable();

            if (status.HasValue)
            {
                query = query.Where(t => t.TrangThai == status.Value);
            }

            if (!string.IsNullOrWhiteSpace(search))
            {
                var s = search.Trim();
                query = query.Where(t => t.SoSerial.Contains(s) || (t.SanPham != null && t.SanPham.TenSanPham.Contains(s)));
            }

            var data = await query.OrderByDescending(t => t.MaThietBi).ToListAsync();
            return View(data);
        }

        // Xem thông tin chi tiết thiết bị, thông số cấu hình và lịch sử vòng đời
        public async Task<IActionResult> Details(int id)
        {
            var tb = await _context.ThietBis
                .Include(t => t.SanPham).ThenInclude(s => s.LoaiThietBi)
                .Include(t => t.LichSuThietBis).ThenInclude(l => l.NguoiThucHien)
                .Include(t => t.PhieuBaoTris).ThenInclude(p => p.KyThuatVien)
                .FirstOrDefaultAsync(m => m.MaThietBi == id);

            if (tb == null) return NotFound();
            return View(tb);
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

        // Cập nhật thông tin thiết bị (không cho sửa máy đang có khách thuê)
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
                bool isBooked = await _context.ChiTietHopDongs.AnyAsync(c => c.MaThietBi == id && c.HopDong.TrangThai != 2 && c.HopDong.TrangThai != 3);
                if (oldTb != null && isBooked)
                {
                    TempData["Error"] = "BẢO MẬT: Máy đang được khách thuê hoặc đã được đặt trước, nghiêm cấm chỉnh sửa thông tin để tránh sai lệch Hợp đồng!";
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

                if (oldTb != null && oldTb.TrangThai != tb.TrangThai)
                {
                    int? currentUserId = null;
                    var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
                    if (claim != null && int.TryParse(claim.Value, out int uid))
                    {
                        currentUserId = uid;
                    }

                    string statusName(int st) => st switch
                    {
                        0 => "Sẵn sàng",
                        1 => "Đang cho thuê",
                        2 => "Bảo trì / Hỏng",
                        3 => "Đang giữ chỗ",
                        4 => "Hỏng thanh lý",
                        _ => $"Trạng thái {st}"
                    };

                    _context.LichSuThietBis.Add(new LichSuThietBi
                    {
                        MaThietBi = tb.MaThietBi,
                        HanhDong = $"Cập nhật trạng thái: {statusName(oldTb.TrangThai)} -> {statusName(tb.TrangThai)}",
                        ThoiGian = DateTime.Now,
                        MaNguoiThucHien = currentUserId,
                        GhiChu = $"Tình trạng máy: {tb.TinhTrangMay}"
                    });
                }

                _context.Update(tb);
                await _context.SaveChangesAsync();
                TempData["Success"] = "Đã cập nhật thông tin thiết bị thành công!";
                return RedirectToAction(nameof(Index));
            }
            ViewBag.MaSanPham = new SelectList(_context.SanPhams, "MaSanPham", "TenSanPham", tb.MaSanPham);
            return View(tb);
        }

        // Mở màn hình xác nhận xóa thiết bị khỏi hệ thống (Chỉ dành cho Admin)
        [Authorize(Roles = "Admin")]
        public async Task<IActionResult> Delete(int id)
        {
            var tb = await _context.ThietBis.Include(t => t.SanPham).FirstOrDefaultAsync(m => m.MaThietBi == id);
            if (tb == null) return NotFound();
            return View(tb);
        }

        // Xóa thiết bị khỏi hệ thống (kiểm tra không cho xóa máy đang thuê hoặc đã có lịch sử hợp đồng - Chỉ dành cho Admin)
        [Authorize(Roles = "Admin")]
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
