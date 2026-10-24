using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Controllers
{
    // Controller hỗ trợ Khách hàng báo hỏng / yêu cầu bảo trì thiết bị đang thuê,
    // theo dõi tiến độ sửa chữa, nghiệm thu và đánh giá chất lượng dịch vụ.
    [Authorize]
    public class BaoTriController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly IWebHostEnvironment _env;

        public BaoTriController(ApplicationDbContext context, IWebHostEnvironment env)
        {
            _context = context;
            _env = env;
        }

        // Mở giao diện tạo phiếu báo hỏng thiết bị.
        // Chỉ cho phép khách hàng tạo yêu cầu đối với hợp đồng đang có hiệu lực thuê
        [HttpGet]
        public async Task<IActionResult> TaoPhieu(int hopDongId)
        {
            var userIdStr = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
            {
                return Challenge();
            }

            var hopDong = await _context.HopDongs
                .Include(h => h.KhachHang)
                .FirstOrDefaultAsync(h => h.MaHopDong == hopDongId && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            // Kiểm tra trạng thái hợp đồng trước khi tiếp nhận yêu cầu
            if (hopDong.TrangThai != 1)
            {
                TempData["Error"] = "Chỉ có thể gửi yêu cầu bảo trì cho hợp đồng đang trong thời gian cho thuê (Đang thuê)!";
                return RedirectToAction("MyContracts", "Cart");
            }

            var thietBis = await _context.ChiTietHopDongs
                .Include(c => c.ThietBi)
                .ThenInclude(t => t.SanPham)
                .Where(c => c.MaHopDong == hopDongId)
                .ToListAsync();

            ViewBag.HopDong = hopDong;
            ViewBag.ThietBis = thietBis;

            return View();
        }

        [HttpGet]
        [ActionName("TaoYeuCau")]
        public async Task<IActionResult> TaoYeuCau(int hopDongId)
        {
            return await TaoPhieu(hopDongId);
        }

        // Tiếp nhận yêu cầu báo hỏng và lưu Phiếu Bảo Trì vào hệ thống.
        // Tải lên tệp đính kèm hình ảnh/video sự cố và xác định thời hạn cam kết xử lý
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> TaoPhieu(
            int maHopDong, 
            int maThietBi, 
            string moTaLoi,
            IFormFile? hinhAnhLoi = null,
            IFormFile? videoLoi = null,
            List<IFormFile>? hinhAnhSuCo = null,
            int? mucDoKhanCap = 1)
        {
            var userIdStr = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
            {
                return Challenge();
            }

            // Kiểm tra hợp đồng thuộc quyền sở hữu của khách hàng đang đăng nhập
            var hopDong = await _context.HopDongs
                .FirstOrDefaultAsync(h => h.MaHopDong == maHopDong && h.MaKhachHang == userId);

            if (hopDong == null)
            {
                TempData["Error"] = "Không tìm thấy hợp đồng hoặc bạn không có quyền gửi yêu cầu cho hợp đồng này!";
                return RedirectToAction("MyContracts", "Cart");
            }

            // Chặn nếu hợp đồng không ở trạng thái đang thuê
            if (hopDong.TrangThai != 1)
            {
                TempData["Error"] = "Chỉ có thể gửi yêu cầu bảo trì cho hợp đồng đang trong thời gian cho thuê (Đang thuê)!";
                return RedirectToAction("MyContracts", "Cart");
            }

            // Kiểm tra thiết bị có nằm trong danh mục máy đã thuê hay không
            bool isDeviceInContract = await _context.ChiTietHopDongs
                .AnyAsync(c => c.MaHopDong == maHopDong && c.MaThietBi == maThietBi);

            if (!isDeviceInContract)
            {
                TempData["Error"] = "Thiết bị không thuộc danh mục của hợp đồng này!";
                return RedirectToAction("MyContracts", "Cart");
            }

            // Chặn tạo trùng yêu cầu bảo trì nếu thiết bị đang có phiếu xử lý dang dở
            bool hasActiveTicket = await _context.PhieuBaoTris
                .AnyAsync(p => p.MaThietBi == maThietBi && (p.TrangThai == 1 || p.TrangThai == 2));
            if (hasActiveTicket)
            {
                TempData["Error"] = "Thiết bị này đang có một phiếu bảo trì đang được xử lý. Không thể tạo thêm yêu cầu trùng lặp!";
                return RedirectToAction(nameof(MyTickets));
            }

            if (string.IsNullOrWhiteSpace(moTaLoi))
            {
                TempData["Error"] = "Vui lòng nhập mô tả lỗi chi tiết!";
                return RedirectToAction(nameof(TaoPhieu), new { hopDongId = maHopDong });
            }

            // Xử lý upload ảnh và video bằng chứng lỗi
            string? savedImagePath = null;
            string? savedVideoPath = null;
            string uploadFolder = Path.Combine(_env.WebRootPath, "uploads", "baotri");
            if (!Directory.Exists(uploadFolder))
            {
                Directory.CreateDirectory(uploadFolder);
            }

            var allowedImageExtensions = new[] { ".jpg", ".jpeg", ".png", ".webp" };
            var allowedVideoExtensions = new[] { ".mp4", ".mov", ".avi", ".webm", ".mkv" };

            // Gom tất cả các tệp tải lên
            var allUploads = new List<IFormFile>();
            if (hinhAnhLoi != null) allUploads.Add(hinhAnhLoi);
            if (videoLoi != null) allUploads.Add(videoLoi);
            if (hinhAnhSuCo != null && hinhAnhSuCo.Count > 0) allUploads.AddRange(hinhAnhSuCo);

            var savedImagePaths = new List<string>();
            var savedVideoPaths = new List<string>();

            foreach (var file in allUploads)
            {
                if (file.Length > 0)
                {
                    string ext = Path.GetExtension(file.FileName).ToLowerInvariant();
                    if (allowedImageExtensions.Contains(ext))
                    {
                        if (file.Length > 10 * 1024 * 1024)
                        {
                            TempData["Error"] = "Ảnh tải lên vượt quá dung lượng cho phép (tối đa 10MB)!";
                            return RedirectToAction(nameof(TaoPhieu), new { hopDongId = maHopDong });
                        }
                        string fileName = $"img_{DateTime.Now.Ticks}_{Guid.NewGuid().ToString("N")[..8]}{ext}";
                        string filePath = Path.Combine(uploadFolder, fileName);
                        using (var stream = new FileStream(filePath, FileMode.Create))
                        {
                            await file.CopyToAsync(stream);
                        }
                        savedImagePaths.Add($"/uploads/baotri/{fileName}");
                    }
                    else if (allowedVideoExtensions.Contains(ext))
                    {
                        if (file.Length > 50 * 1024 * 1024)
                        {
                            TempData["Error"] = "Video tải lên vượt quá dung lượng cho phép (tối đa 50MB)!";
                            return RedirectToAction(nameof(TaoPhieu), new { hopDongId = maHopDong });
                        }
                        string fileName = $"vid_{DateTime.Now.Ticks}_{Guid.NewGuid().ToString("N")[..8]}{ext}";
                        string filePath = Path.Combine(uploadFolder, fileName);
                        using (var stream = new FileStream(filePath, FileMode.Create))
                        {
                            await file.CopyToAsync(stream);
                        }
                        savedVideoPaths.Add($"/uploads/baotri/{fileName}");
                    }
                }
            }

            if (savedImagePaths.Count > 0) savedImagePath = string.Join(";", savedImagePaths);
            if (savedVideoPaths.Count > 0) savedVideoPath = string.Join(";", savedVideoPaths);

            int urgency = mucDoKhanCap ?? 1;
            DateTime deadline = DateTime.Now.AddHours(urgency == 2 ? 12 : (urgency == 3 ? 24 : 48));

            var phieu = new PhieuBaoTri
            {
                MaHopDong = maHopDong,
                MaThietBi = maThietBi,
                MoTaLoi = moTaLoi.Trim(),
                NgayBaoLoi = DateTime.Now,
                TrangThai = 1, // 1: Mới tiếp nhận
                GhiChuSuaChua = "",
                PhiDenBu = 0,
                ChiPhiSuaChua = 0,
                HinhAnhLoi = savedImagePath,
                VideoLoi = savedVideoPath,
                MucDoKhanCap = urgency,
                HanHoanThanh = deadline
            };

            _context.PhieuBaoTris.Add(phieu);
            await _context.SaveChangesAsync();

            // Ghi nhận nhật ký thiết bị
            _context.LichSuThietBis.Add(new LichSuThietBi
            {
                MaThietBi = maThietBi,
                HanhDong = $"Khách hàng gửi báo hỏng phiếu #{phieu.MaPhieu} theo HĐ #{maHopDong}. Lỗi: {moTaLoi.Trim()}",
                ThoiGian = DateTime.Now,
                MaNguoiThucHien = userId,
                GhiChu = $"Yêu cầu xử lý từ khách hàng. SLA hoàn thành: {deadline:dd/MM/yyyy HH:mm}"
            });
            await _context.SaveChangesAsync();

            TempData["Success"] = "Đã gửi yêu cầu bảo trì thành công! Nhân viên kỹ thuật sẽ liên hệ hỗ trợ bạn sớm.";
            return RedirectToAction("MyTickets");
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        [ActionName("TaoYeuCau")]
        public async Task<IActionResult> TaoYeuCau(int maHopDong, int maThietBi, string moTaLoi)
        {
            return await TaoPhieu(maHopDong, maThietBi, moTaLoi);
        }

        // Xem chi tiết tiến độ xử lý phiếu bảo trì
        [HttpGet]
        public async Task<IActionResult> ChiTiet(int id)
        {
            var userIdStr = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
            {
                return Challenge();
            }

            var phieu = await _context.PhieuBaoTris
                .Include(p => p.HopDong).ThenInclude(h => h.KhachHang)
                .Include(p => p.ThietBi).ThenInclude(t => t.SanPham)
                .Include(p => p.KyThuatVien)
                .FirstOrDefaultAsync(p => p.MaPhieu == id && p.HopDong != null && p.HopDong.MaKhachHang == userId);

            if (phieu == null) return NotFound();

            // Lấy số tiền đền bù đã thanh toán (nếu có)
            decimal daThanhToan = 0;
            if (phieu.MaHopDong.HasValue)
            {
                daThanhToan = await _context.PhieuThus
                    .Where(pt => pt.MaHopDong == phieu.MaHopDong.Value && pt.LoaiPhieu == 2 && !pt.DaHuy)
                    .SumAsync(pt => (decimal?)pt.SoTien) ?? 0m;
            }
            ViewBag.DaThanhToanPhiDenBu = daThanhToan;

            return View(phieu);
        }

        // Xem danh sách tất cả các yêu cầu bảo trì mà khách hàng này đã từng gửi đi kèm tiến độ xử lý.
        [HttpGet]
        public async Task<IActionResult> MyTickets()
        {
            var userIdStr = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
            {
                return Challenge();
            }

            var tickets = await _context.PhieuBaoTris
                .Include(p => p.HopDong)
                .Include(p => p.ThietBi)
                .ThenInclude(t => t.SanPham)
                .Include(p => p.KyThuatVien)
                .Where(p => p.HopDong != null && p.HopDong.MaKhachHang == userId)
                .OrderByDescending(p => p.NgayBaoLoi)
                .ToListAsync();

            return View(tickets);
        }

        // Khách hàng xác nhận nghiệm thu sau khi thiết bị sửa xong
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> NghiemThu(int maPhieu, bool dongY, string? yKien = null)
        {
            var userIdStr = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
            {
                return Challenge();
            }

            var phieu = await _context.PhieuBaoTris
                .Include(p => p.HopDong)
                .FirstOrDefaultAsync(p => p.MaPhieu == maPhieu && p.HopDong != null && p.HopDong.MaKhachHang == userId);

            if (phieu == null) return NotFound();

            if (phieu.TrangThai != 3 && phieu.TrangThai != 5)
            {
                TempData["Error"] = "Chỉ có thể nghiệm thu khi thiết bị đã được kỹ thuật viên sửa xong!";
                return RedirectToAction(nameof(ChiTiet), new { id = maPhieu });
            }

            if (dongY)
            {
                phieu.DaNghiemThu = true;
                phieu.NgayNghiemThu = DateTime.Now;
                phieu.YKienPhanHoi = yKien;
                phieu.TrangThai = 5; // 5: Khách đã nghiệm thu và đóng phiếu hoàn tất

                _context.LichSuThietBis.Add(new LichSuThietBi
                {
                    MaThietBi = phieu.MaThietBi,
                    HanhDong = $"Khách hàng xác nhận nghiệm thu máy phiếu #{phieu.MaPhieu} thành công",
                    ThoiGian = DateTime.Now,
                    MaNguoiThucHien = userId,
                    GhiChu = $"Ý kiến khách hàng: {yKien ?? "Hài lòng với kết quả sửa chữa"}"
                });

                TempData["Success"] = "Cảm ơn bạn đã xác nhận nghiệm thu thiết bị!";
            }
            else
            {
                phieu.DaNghiemThu = false;
                phieu.TrangThai = 2; // Đưa về trạng thái 2 (Đang sửa chữa / Cần kiểm tra lại)
                phieu.GhiChuSuaChua += $" [Khách yêu cầu xử lý lại: {yKien}]";

                _context.LichSuThietBis.Add(new LichSuThietBi
                {
                    MaThietBi = phieu.MaThietBi,
                    HanhDong = $"Khách từ chối nghiệm thu phiếu #{phieu.MaPhieu}, yêu cầu KTV xử lý lại",
                    ThoiGian = DateTime.Now,
                    MaNguoiThucHien = userId,
                    GhiChu = $"Lý do khách từ chối: {yKien}"
                });

                TempData["Success"] = "Đã gửi yêu cầu xử lý lại cho kỹ thuật viên!";
            }

            await _context.SaveChangesAsync();
            return RedirectToAction(nameof(ChiTiet), new { id = maPhieu });
        }

        // Đánh giá chất lượng dịch vụ bảo trì (Thang điểm 1 - 5 sao) sau khi kỹ thuật viên hoàn thành.
        // Ghi nhận phản hồi và đánh dấu nghiệm thu
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DanhGia(int maPhieu, int rating, string? yKienPhanHoi = null)
        {
            var userIdStr = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
            {
                return Challenge();
            }

            // Kiểm tra thang điểm hợp lệ từ 1 đến 5 sao
            if (rating < 1 || rating > 5)
            {
                TempData["Error"] = "Đánh giá chất lượng dịch vụ phải từ 1 đến 5 sao!";
                return RedirectToAction(nameof(MyTickets));
            }

            var phieu = await _context.PhieuBaoTris
                .Include(p => p.HopDong)
                .FirstOrDefaultAsync(p => p.MaPhieu == maPhieu && p.HopDong != null && p.HopDong.MaKhachHang == userId);

            if (phieu == null) return NotFound();

            if (phieu.TrangThai != 3 && phieu.TrangThai != 5)
            {
                TempData["Error"] = "Chỉ đánh giá được phiếu đã hoàn thành (sửa xong)!";
                return RedirectToAction("MyTickets");
            }

            phieu.DanhGiaSao = rating;
            if (!string.IsNullOrEmpty(yKienPhanHoi))
            {
                phieu.YKienPhanHoi = yKienPhanHoi;
            }
            phieu.DaNghiemThu = true;
            phieu.NgayNghiemThu ??= DateTime.Now;

            // Ghi nhận nhật ký đánh giá của khách hàng
            _context.LichSuThietBis.Add(new LichSuThietBi
            {
                MaThietBi = phieu.MaThietBi,
                HanhDong = $"Khách hàng gửi đánh giá {rating} sao cho phiếu bảo trì #{phieu.MaPhieu}",
                ThoiGian = DateTime.Now,
                MaNguoiThucHien = userId,
                GhiChu = $"Đánh giá: {rating} sao. Ý kiến: {yKienPhanHoi}"
            });

            await _context.SaveChangesAsync();

            TempData["Success"] = "Cảm ơn bạn đã gửi đánh giá chất lượng dịch vụ bảo trì!";
            return RedirectToAction(nameof(MyTickets));
        }
    }
}
