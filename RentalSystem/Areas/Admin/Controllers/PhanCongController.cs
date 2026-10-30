using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Areas.Admin.Controllers
{
    [Area("Admin")]
    [Authorize(Roles = "Admin,KinhDoanh,KyThuat")]
    public class PhanCongController : Controller
    {
        private readonly ApplicationDbContext _context;

        public PhanCongController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Danh sách phân công công việc
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> Index(int? trangThai, int? maNhanVien, string? search)
        {
            var query = _context.PhanCongCongViecs
                .Include(p => p.NhanVien).ThenInclude(u => u.VaiTro)
                .Include(p => p.NguoiGiao)
                .Include(p => p.HopDong)!.ThenInclude(h => h!.KhachHang)
                .Include(p => p.PhieuBaoTri)!.ThenInclude(b => b!.ThietBi)!.ThenInclude(t => t!.SanPham)
                .AsQueryable();

            if (trangThai.HasValue)
            {
                query = query.Where(p => p.TrangThai == trangThai.Value);
            }

            if (maNhanVien.HasValue)
            {
                query = query.Where(p => p.MaNhanVien == maNhanVien.Value);
            }

            if (!string.IsNullOrWhiteSpace(search))
            {
                var s = search.Trim();
                query = query.Where(p => p.TieuDe.Contains(s) ||
                                         p.NoiDung.Contains(s) ||
                                         (p.NhanVien != null && p.NhanVien.HoTen.Contains(s)));
            }

            var list = await query.OrderByDescending(p => p.NgayGiao).ToListAsync();

            ViewBag.NhanViens = await _context.NguoiDungs
                .Include(u => u.VaiTro)
                .Where(u => u.VaiTro.TenVaiTro != "KhachHang")
                .OrderBy(u => u.HoTen)
                .ToListAsync();

            ViewBag.CurrentTrangThai = trangThai;
            ViewBag.CurrentMaNhanVien = maNhanVien;
            ViewBag.Search = search;

            // Thống kê số lượng theo trạng thái
            ViewBag.TotalTasks = await _context.PhanCongCongViecs.CountAsync();
            ViewBag.NewTasks = await _context.PhanCongCongViecs.CountAsync(p => p.TrangThai == 0);
            ViewBag.InProgressTasks = await _context.PhanCongCongViecs.CountAsync(p => p.TrangThai == 1);
            ViewBag.CompletedTasks = await _context.PhanCongCongViecs.CountAsync(p => p.TrangThai == 2);

            return View(list);
        }

        // Phân công công việc mới
        [HttpGet]
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> Create()
        {
            await PopulateDropDowns();
            var model = new PhanCongCongViec
            {
                NgayGiao = DateTime.Now,
                HanHoanThanh = DateTime.Now.AddDays(3),
                TrangThai = 0
            };
            return View(model);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> Create(PhanCongCongViec model)
        {
            if (string.IsNullOrWhiteSpace(model.TieuDe))
            {
                ModelState.AddModelError("TieuDe", "Vui lòng nhập tiêu đề công việc.");
            }
            if (string.IsNullOrWhiteSpace(model.NoiDung))
            {
                ModelState.AddModelError("NoiDung", "Vui lòng nhập nội dung công việc.");
            }
            if (model.MaNhanVien <= 0)
            {
                ModelState.AddModelError("MaNhanVien", "Vui lòng chọn nhân viên thực hiện.");
            }

            var staff = await _context.NguoiDungs.FindAsync(model.MaNhanVien);
            if (staff == null)
            {
                ModelState.AddModelError("MaNhanVien", "Nhân viên được chọn không tồn tại.");
            }

            if (ModelState.IsValid)
            {
                var claim = User.FindFirst(ClaimTypes.NameIdentifier);
                int? currentUserId = claim != null && int.TryParse(claim.Value, out int uid) ? uid : null;

                model.NgayGiao = DateTime.Now;
                model.TrangThai = 0; // Mới
                model.MaNguoiGiao = currentUserId;
                model.MaHopDong = (model.MaHopDong.HasValue && model.MaHopDong.Value > 0) ? model.MaHopDong : null;
                model.MaPhieuBaoTri = (model.MaPhieuBaoTri.HasValue && model.MaPhieuBaoTri.Value > 0) ? model.MaPhieuBaoTri : null;

                _context.PhanCongCongViecs.Add(model);
                await _context.SaveChangesAsync();

                TempData["Success"] = "Giao việc cho nhân viên thành công!";
                return RedirectToAction(nameof(Index));
            }

            await PopulateDropDowns(model.MaNhanVien, model.MaHopDong, model.MaPhieuBaoTri);
            return View(model);
        }

        // Cập nhật phân công công việc
        [HttpGet]
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> Edit(int id)
        {
            var task = await _context.PhanCongCongViecs.FindAsync(id);
            if (task == null)
            {
                TempData["Error"] = "Không tìm thấy công việc cần sửa.";
                return RedirectToAction(nameof(Index));
            }

            await PopulateDropDowns(task.MaNhanVien, task.MaHopDong, task.MaPhieuBaoTri);
            return View(task);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> Edit(int id, PhanCongCongViec model)
        {
            var task = await _context.PhanCongCongViecs.FindAsync(id);
            if (task == null)
            {
                TempData["Error"] = "Không tìm thấy công việc cần cập nhật.";
                return RedirectToAction(nameof(Index));
            }

            if (string.IsNullOrWhiteSpace(model.TieuDe))
            {
                ModelState.AddModelError("TieuDe", "Vui lòng nhập tiêu đề công việc.");
            }
            if (string.IsNullOrWhiteSpace(model.NoiDung))
            {
                ModelState.AddModelError("NoiDung", "Vui lòng nhập nội dung chi tiết.");
            }
            if (model.MaNhanVien <= 0)
            {
                ModelState.AddModelError("MaNhanVien", "Vui lòng chọn nhân viên.");
            }

            if (ModelState.IsValid)
            {
                task.TieuDe = model.TieuDe.Trim();
                task.NoiDung = model.NoiDung.Trim();
                task.MaNhanVien = model.MaNhanVien;
                task.MaHopDong = (model.MaHopDong.HasValue && model.MaHopDong.Value > 0) ? model.MaHopDong : null;
                task.MaPhieuBaoTri = (model.MaPhieuBaoTri.HasValue && model.MaPhieuBaoTri.Value > 0) ? model.MaPhieuBaoTri : null;
                task.HanHoanThanh = model.HanHoanThanh;
                task.GhiChuTienDo = model.GhiChuTienDo;

                if (model.TrangThai == 2 && task.TrangThai != 2)
                {
                    task.NgayHoanThanh = DateTime.Now;
                }
                else if (model.TrangThai != 2)
                {
                    task.NgayHoanThanh = null;
                }
                task.TrangThai = model.TrangThai;

                await _context.SaveChangesAsync();
                TempData["Success"] = "Cập nhật phân công công việc thành công!";
                return RedirectToAction(nameof(Index));
            }

            await PopulateDropDowns(model.MaNhanVien, model.MaHopDong, model.MaPhieuBaoTri);
            return View(model);
        }

        // Xóa phân công
        [HttpPost]
        [ValidateAntiForgeryToken]
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> Delete(int id)
        {
            var task = await _context.PhanCongCongViecs.FindAsync(id);
            if (task != null)
            {
                _context.PhanCongCongViecs.Remove(task);
                await _context.SaveChangesAsync();
                TempData["Success"] = "Đã xóa phân công công việc thành công!";
            }
            else
            {
                TempData["Error"] = "Không tìm thấy công việc để xóa.";
            }

            return RedirectToAction(nameof(Index));
        }

        // Danh sách công việc của nhân viên đang đăng nhập
        [HttpGet]
        [Authorize]
        public async Task<IActionResult> MyTasks(int? trangThai)
        {
            var claim = User.FindFirst(ClaimTypes.NameIdentifier);
            if (claim == null || !int.TryParse(claim.Value, out int currentUserId))
            {
                return RedirectToAction("Login", "Account", new { area = "" });
            }

            // Thống kê công việc của nhân viên
            int totalTasks = await _context.PhanCongCongViecs.CountAsync(p => p.MaNhanVien == currentUserId);
            int newTasks = await _context.PhanCongCongViecs.CountAsync(p => p.MaNhanVien == currentUserId && p.TrangThai == 0);
            int inProgressTasks = await _context.PhanCongCongViecs.CountAsync(p => p.MaNhanVien == currentUserId && p.TrangThai == 1);
            int completedTasks = await _context.PhanCongCongViecs.CountAsync(p => p.MaNhanVien == currentUserId && p.TrangThai == 2);

            var query = _context.PhanCongCongViecs
                .Include(p => p.NguoiGiao)
                .Include(p => p.HopDong)!.ThenInclude(h => h!.KhachHang)
                .Include(p => p.PhieuBaoTri)!.ThenInclude(b => b!.ThietBi)!.ThenInclude(t => t!.SanPham)
                .Where(p => p.MaNhanVien == currentUserId);

            if (trangThai.HasValue)
            {
                query = query.Where(p => p.TrangThai == trangThai.Value);
            }

            var list = await query.OrderByDescending(p => p.NgayGiao).ToListAsync();

            ViewBag.TotalTasks = totalTasks;
            ViewBag.NewTasks = newTasks;
            ViewBag.InProgressTasks = inProgressTasks;
            ViewBag.CompletedTasks = completedTasks;
            ViewBag.CurrentTrangThai = trangThai;

            return View(list);
        }

        // Cập nhật tiến độ và trạng thái công việc
        [HttpPost]
        [ValidateAntiForgeryToken]
        [Authorize]
        public async Task<IActionResult> UpdateStatus(int id, int status, string? ghiChu)
        {
            var task = await _context.PhanCongCongViecs.FindAsync(id);
            if (task == null)
            {
                if (IsAjaxRequest())
                {
                    return NotFound(new { success = false, message = "Không tìm thấy công việc." });
                }
                TempData["Error"] = "Không tìm thấy công việc.";
                return RedirectToAction(nameof(MyTasks));
            }

            var claim = User.FindFirst(ClaimTypes.NameIdentifier);
            int? currentUserId = claim != null && int.TryParse(claim.Value, out int uid) ? uid : null;
            bool isManager = User.IsInRole("Admin") || User.IsInRole("KinhDoanh");

            if (task.MaNhanVien != currentUserId && !isManager)
            {
                if (IsAjaxRequest())
                {
                    return StatusCode(403, new { success = false, message = "Bạn không có quyền cập nhật công việc này." });
                }
                TempData["Error"] = "Bạn không có quyền cập nhật công việc này.";
                return RedirectToAction(nameof(MyTasks));
            }

            if (status < 0 || status > 3)
            {
                if (IsAjaxRequest())
                {
                    return BadRequest(new { success = false, message = "Trạng thái không hợp lệ." });
                }
                TempData["Error"] = "Trạng thái không hợp lệ.";
                return RedirectToAction(nameof(MyTasks));
            }

            task.TrangThai = status;
            if (status == 2)
            {
                task.NgayHoanThanh = DateTime.Now;
            }
            else
            {
                task.NgayHoanThanh = null;
            }

            if (!string.IsNullOrWhiteSpace(ghiChu))
            {
                task.GhiChuTienDo = ghiChu.Trim();
            }

            await _context.SaveChangesAsync();

            if (IsAjaxRequest())
            {
                return Json(new
                {
                    success = true,
                    message = "Cập nhật tiến độ thành công!",
                    status = task.TrangThai,
                    statusText = GetStatusText(task.TrangThai),
                    ngayHoanThanh = task.NgayHoanThanh?.ToString("dd/MM/yyyy HH:mm"),
                    ghiChu = task.GhiChuTienDo
                });
            }

            TempData["Success"] = "Cập nhật trạng thái công việc thành công!";
            return RedirectToAction(nameof(MyTasks));
        }

        // Lấy chi tiết công việc
        [HttpGet]
        [Authorize]
        public async Task<IActionResult> Details(int id)
        {
            var task = await _context.PhanCongCongViecs
                .Include(p => p.NhanVien).ThenInclude(u => u.VaiTro)
                .Include(p => p.NguoiGiao)
                .Include(p => p.HopDong)!.ThenInclude(h => h!.KhachHang)
                .Include(p => p.PhieuBaoTri)!.ThenInclude(b => b!.ThietBi)!.ThenInclude(t => t!.SanPham)
                .FirstOrDefaultAsync(p => p.MaPhanCong == id);

            if (task == null) return NotFound();

            var claim = User.FindFirst(ClaimTypes.NameIdentifier);
            int? currentUserId = claim != null && int.TryParse(claim.Value, out int uid) ? uid : null;
            bool isManager = User.IsInRole("Admin") || User.IsInRole("KinhDoanh");
            if (task.MaNhanVien != currentUserId && !isManager)
            {
                return Forbid();
            }

            return Json(new
            {
                id = task.MaPhanCong,
                title = task.TieuDe,
                content = task.NoiDung,
                staff = task.NhanVien != null ? $"{task.NhanVien.HoTen} ({task.NhanVien.VaiTro?.TenVaiTro})" : "N/A",
                staffId = task.MaNhanVien,
                creator = task.NguoiGiao != null ? task.NguoiGiao.HoTen : "Hệ thống",
                assignedDate = task.NgayGiao.ToString("dd/MM/yyyy HH:mm"),
                dueDate = task.HanHoanThanh?.ToString("dd/MM/yyyy HH:mm") ?? "Không có",
                completedDate = task.NgayHoanThanh?.ToString("dd/MM/yyyy HH:mm") ?? "Chưa hoàn thành",
                status = task.TrangThai,
                statusText = GetStatusText(task.TrangThai),
                progressNote = task.GhiChuTienDo ?? "",
                contractId = task.MaHopDong,
                ticketId = task.MaPhieuBaoTri
            });
        }

        // Hàm hỗ trợ
        private async Task PopulateDropDowns(int? selectedNhanVien = null, int? selectedHopDong = null, int? selectedPhieuBaoTri = null)
        {
            var staff = await _context.NguoiDungs
                .Include(u => u.VaiTro)
                .Where(u => u.VaiTro.TenVaiTro != "KhachHang")
                .OrderBy(u => u.HoTen)
                .Select(u => new
                {
                    u.MaNguoiDung,
                    DisplayText = $"{u.HoTen} ({u.VaiTro.TenVaiTro}) - {u.SoDienThoai}"
                })
                .ToListAsync();
            ViewBag.NhanVienList = new SelectList(staff, "MaNguoiDung", "DisplayText", selectedNhanVien);

            var contracts = await _context.HopDongs
                .Include(h => h.KhachHang)
                .OrderByDescending(h => h.MaHopDong)
                .Take(50)
                .Select(h => new
                {
                    h.MaHopDong,
                    DisplayText = $"HĐ#{h.MaHopDong} - {(h.KhachHang != null ? h.KhachHang.HoTen : "Khách hàng")} ({h.TongTien:N0} đ)"
                })
                .ToListAsync();
            ViewBag.HopDongList = new SelectList(contracts, "MaHopDong", "DisplayText", selectedHopDong);

            var tickets = await _context.PhieuBaoTris
                .Include(t => t.ThietBi).ThenInclude(tb => tb.SanPham)
                .OrderByDescending(t => t.MaPhieu)
                .Take(50)
                .Select(t => new
                {
                    t.MaPhieu,
                    DisplayText = $"PBT#{t.MaPhieu} - {(t.ThietBi != null && t.ThietBi.SanPham != null ? t.ThietBi.SanPham.TenSanPham : "Thiết bị")} ({(t.MoTaLoi != null && t.MoTaLoi.Length > 30 ? t.MoTaLoi.Substring(0, 30) + "..." : (t.MoTaLoi ?? "Sự cố"))})"
                })
                .ToListAsync();
            ViewBag.PhieuBaoTriList = new SelectList(tickets, "MaPhieu", "DisplayText", selectedPhieuBaoTri);
        }

        private bool IsAjaxRequest()
        {
            return Request.Headers["X-Requested-With"] == "XMLHttpRequest" ||
                   Request.Headers.Accept.ToString().Contains("application/json");
        }

        private static string GetStatusText(int status) => status switch
        {
            0 => "Mới",
            1 => "Đang thực hiện",
            2 => "Hoàn thành",
            3 => "Đã hủy",
            _ => "Không xác định"
        };
    }
}
