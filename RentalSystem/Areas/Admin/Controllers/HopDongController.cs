using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Areas.Admin.Controllers
{
    [Area("Admin")]
    [Authorize(Roles = "Admin,KinhDoanh")]
    public class HopDongController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly Microsoft.AspNetCore.Hosting.IWebHostEnvironment _env;

        public HopDongController(ApplicationDbContext context, Microsoft.AspNetCore.Hosting.IWebHostEnvironment env)
        {
            _context = context;
            _env = env;
        }

        public async Task<IActionResult> Index()
        {
            var data = await _context.HopDongs
                .Include(h => h.KhachHang)
                .OrderByDescending(h => h.NgayBatDau)
                .ToListAsync();
            
            var overdue = await _context.KyHanThanhToans
                .Where(k => k.TrangThai == 0 && k.NgayDenHan.Date < DateTime.Now.Date && (k.HopDong.TrangThai == 1 || k.HopDong.TrangThai == 0))
                .Select(k => k.MaHopDong)
                .Distinct()
                .ToListAsync();
            
            ViewBag.Overdue = overdue;
            return View(data);
        }

        public async Task<IActionResult> Details(int id, string returnUrl = null)
        {
            ViewBag.ReturnUrl = returnUrl;
            var hd = await _context.HopDongs
                .Include(h => h.KhachHang)
                .Include(h => h.NhanVien)
                .FirstOrDefaultAsync(h => h.MaHopDong == id);
                
            if (hd == null) return NotFound();

            var chiTiets = await _context.ChiTietHopDongs
                .Include(c => c.ThietBi)
                .ThenInclude(t => t.SanPham)
                .Where(c => c.MaHopDong == id)
                .ToListAsync();
            
            var kyHans = await _context.KyHanThanhToans
                .Where(k => k.MaHopDong == id)
                .OrderBy(k => k.SoKyHan)
                .ToListAsync();

            var phieuThus = await _context.PhieuThus
                .Where(p => p.MaHopDong == id)
                .OrderByDescending(p => p.NgayGiaoDich)
                .ToListAsync();

            ViewBag.ChiTiets = chiTiets;
            ViewBag.KyHans = kyHans;
            ViewBag.PhieuThus = phieuThus;
            return View(hd);
        }

        public async Task<IActionResult> Create()
        {
            var khachHangs = await _context.NguoiDungs.Where(u => u.VaiTro.TenVaiTro == "KhachHang").ToListAsync();
            
            var sanPhams = await _context.SanPhams.Select(sp => new {
                sp.MaSanPham,
                sp.TenSanPham,
                sp.GiaThueNgay,
                TonKho = _context.ThietBis.Count(t => t.MaSanPham == sp.MaSanPham && t.TrangThai == 0)
            }).ToListAsync();

            ViewBag.KhachHangs = khachHangs;
            ViewBag.SanPhams = sanPhams;
            return View();
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Giao diện dành cho Admin/Nhân viên tạo đơn trực tiếp tại quầy. 
        // Hỗ trợ tìm hoặc tạo mới khách hàng, thiết lập số kỳ hạn trả góp và thu cọc tức thời.
        public async Task<IActionResult> Create(string KhachHang_HoTen, string KhachHang_SoDienThoai, string KhachHang_Email, string KhachHang_DiaChi, DateTime NgayBatDau, DateTime NgayKetThuc, decimal TienDaCoc, int HinhThucCoc, int SoKyHan, int[] SanPhamIds, int[] SoLuongs, string GhiChu)
        {
            if (NgayKetThuc.Date < NgayBatDau.Date)
            {
                TempData["Error"] = "Ngày trả máy không thể nhỏ hơn ngày nhận máy!";
                return RedirectToAction(nameof(Create));
            }

            if (SanPhamIds == null || SanPhamIds.Length == 0 || SoLuongs == null || !SoLuongs.Any(s => s > 0))
            {
                TempData["Error"] = "Vui lòng nhập số lượng cho ít nhất 1 sản phẩm để cho thuê!";
                return RedirectToAction(nameof(Create));
            }

            if (SoLuongs.Length != SanPhamIds.Length)
            {
                TempData["Error"] = "Dữ liệu giỏ hàng bị lệch!";
                return RedirectToAction(nameof(Create));
            }

            for (int i = 0; i < SanPhamIds.Length; i++)
            {
                if (SoLuongs[i] > 0)
                {
                    int spId = SanPhamIds[i];
                    int slNeed = SoLuongs[i];
                    int slKho = await _context.ThietBis.CountAsync(t => t.MaSanPham == spId && t.TrangThai == 0);
                    
                    if (slKho < slNeed)
                    {
                        var tenSp = (await _context.SanPhams.FindAsync(spId))?.TenSanPham;
                        TempData["Error"] = $"Sản phẩm '{tenSp}' không đủ số lượng trong kho (Chỉ còn {slKho}).";
                        return RedirectToAction(nameof(Create));
                    }
                }
            }

            var days = (NgayKetThuc - NgayBatDau).TotalDays;
            if (days <= 0) days = 1;
            decimal totalMoney = 0;

            int adminId = 1;
            var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (claim != null && int.TryParse(claim.Value, out int parsedId))
            {
                adminId = parsedId;
            }

            // Xử lý tạo mới hoặc tái sử dụng Khách Hàng
            var khachHang = await _context.NguoiDungs
                .FirstOrDefaultAsync(u => u.SoDienThoai == KhachHang_SoDienThoai || (!string.IsNullOrEmpty(KhachHang_Email) && u.Email == KhachHang_Email));

            if (khachHang == null)
            {
                var vaiTroKhachHang = await _context.VaiTros.FirstOrDefaultAsync(v => v.TenVaiTro == "KhachHang");
                khachHang = new NguoiDung
                {
                    HoTen = KhachHang_HoTen,
                    SoDienThoai = KhachHang_SoDienThoai,
                    Email = KhachHang_Email ?? "",
                    DiaChi = KhachHang_DiaChi ?? "",
                    MaVaiTro = vaiTroKhachHang?.MaVaiTro ?? 4,
                    MatKhau = KhachHang_SoDienThoai, // Default password is phone number
                    CCCD = "",
                    TrangThai = true
                };
                _context.NguoiDungs.Add(khachHang);
                await _context.SaveChangesAsync();
            }
            else
            {
                // Cập nhật lại thông tin mới nhất
                khachHang.HoTen = KhachHang_HoTen;
                if (!string.IsNullOrEmpty(KhachHang_Email)) khachHang.Email = KhachHang_Email;
                if (!string.IsNullOrEmpty(KhachHang_DiaChi)) khachHang.DiaChi = KhachHang_DiaChi;
                await _context.SaveChangesAsync();
            }

            var hd = new HopDong
            {
                MaKhachHang = khachHang.MaNguoiDung,
                MaNhanVien = adminId,
                NgayBatDau = NgayBatDau,
                NgayKetThuc = NgayKetThuc,
                TienDaCoc = TienDaCoc,
                TrangThai = 0, // Chờ duyệt
                NgayKy = null,
                ChuKyKhachHang = "",
                ChuKyNhanVien = "",
                AnhCMND = "",
                TrangThaiThanhToan = 0,
                GhiChu = GhiChu ?? "",
                TongTien = 0
            };

            _context.HopDongs.Add(hd);
            await _context.SaveChangesAsync();

            for (int i = 0; i < SanPhamIds.Length; i++)
            {
                if (SoLuongs[i] > 0)
                {
                    int spId = SanPhamIds[i];
                    int slNeed = SoLuongs[i];
                    
                    var spInfo = await _context.SanPhams.FindAsync(spId);
                    if (spInfo == null) continue;
                    
                    decimal giaThue = spInfo.GiaThueNgay * (decimal)days;
                    
                    var devices = await _context.ThietBis
                        .Where(t => t.MaSanPham == spId && t.TrangThai == 0)
                        .Take(slNeed)
                        .ToListAsync();

                    foreach (var dev in devices)
                    {
                        var ct = new ChiTietHopDong
                        {
                            MaHopDong = hd.MaHopDong,
                            MaThietBi = dev.MaThietBi,
                            GiaChotThu = giaThue
                        };
                        _context.ChiTietHopDongs.Add(ct);
                        
                        // FIXED RACECONDITION: Đánh dấu thiết bị đang được giữ chỗ (3)
                        dev.TrangThai = 3;
                        totalMoney += giaThue;
                    }
                }
            }
            
            hd.TongTien = totalMoney;
            
            // Tự động tạo Phiếu Thu cho Tiền Cọc (nếu có)
            if (hd.TienDaCoc > 0)
            {
                var phieuCoc = new PhieuThu
                {
                    MaHopDong = hd.MaHopDong,
                    LoaiPhieu = 1, // Thu cọc
                    SoTien = hd.TienDaCoc,
                    NgayGiaoDich = DateTime.Now,
                    HinhThucThanhToan = HinhThucCoc, // Tiền mặt hoặc Chuyển khoản theo chọn lựa
                    GhiChu = "Thu tiền cọc khi tạo đơn"
                };
                _context.PhieuThus.Add(phieuCoc);
            }

            // Lưu số kỳ hạn vào GhiChu tạm để dùng khi Giao máy
            if (SoKyHan > 1)
            {
                hd.GhiChu = (string.IsNullOrEmpty(hd.GhiChu) ? "" : hd.GhiChu + " | ") + $"[SoKy:{SoKyHan}]";
            }

            await _context.SaveChangesAsync();
            
            TempData["Success"] = "Đã tạo hợp đồng mới thành công (Đang chờ duyệt)!";
            return RedirectToAction(nameof(Index));
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Đóng vai trò là cỗ máy điều hướng toàn bộ vòng đời của Hợp đồng và Thiết bị.
        // Khi duyệt (1): Tự sinh lịch trả góp, đổi trạng thái máy thành Đang thuê.
        // Khi hủy/hoàn tất (2,3): Giải phóng thiết bị trả về kho.
        public async Task<IActionResult> UpdateStatus(int id, int status, string returnUrl = null)
        {
            if (status < 0 || status > 3)
            {
                TempData["Error"] = "Trạng thái không hợp lệ!";
                return RedirectToAction(nameof(Index));
            }

            var hopDong = await _context.HopDongs.FindAsync(id);
            if (hopDong == null) return NotFound();

            if ((hopDong.TrangThai == 2 || hopDong.TrangThai == 3) && (status == 0 || status == 1))
            {
                TempData["Error"] = "Hợp đồng đã đóng (Hoàn tất/Hủy) không thể chuyển ngược lại trạng thái đang hoạt động! (Tránh lỗi thất thoát kho)";
                return RedirectToAction(nameof(Index));
            }

            var chiTiets = await _context.ChiTietHopDongs.Where(c => c.MaHopDong == id).ToListAsync();

            if (status == 1) // Giao máy & Cho thuê -> Chuyển máy sang 1 (Đang cho thuê)
            {
                foreach (var ct in chiTiets)
                {
                    var tb = await _context.ThietBis.FindAsync(ct.MaThietBi);
                    if (tb != null)
                    {
                        tb.TrangThai = 1; // Đang cho thuê
                    }
                }

                // NGHIỆP VỤ TÀI CHÍNH: Tự động chia lịch trả góp theo số kỳ đã chọn.
                // Khoảng cách ngày giữa các kỳ được chia đều theo tổng thời gian thuê.
                // Số tiền mỗi kỳ = (Tổng tiền - Tiền cọc) / Số kỳ
                bool hasInstallments = await _context.KyHanThanhToans.AnyAsync(k => k.MaHopDong == id);
                if (!hasInstallments)
                {
                    // Đọc số kỳ từ GhiChu (nếu Admin đã chỉ định lúc tạo đơn)
                    int soKy = 1;
                    var ghiChu = hopDong.GhiChu ?? "";
                    var match = System.Text.RegularExpressions.Regex.Match(ghiChu, @"\[SoKy:(\d+)\]");
                    if (match.Success && int.TryParse(match.Groups[1].Value, out int parsedSoKy) && parsedSoKy > 0)
                    {
                        soKy = parsedSoKy;
                    }
                    else
                    {
                        // Nếu không chỉ định → tự chia theo 30 ngày
                        var totalDays = (hopDong.NgayKetThuc - hopDong.NgayBatDau).TotalDays;
                        soKy = (int)Math.Ceiling(totalDays / 30.0);
                        if (soKy <= 0) soKy = 1;
                    }

                    decimal tienMoiKy = (hopDong.TongTien - hopDong.TienDaCoc) / soKy;
                    if (tienMoiKy < 0) tienMoiKy = 0;

                    // Tính ngày đến hạn đều nhau theo số kỳ
                    var totalContractDays = (hopDong.NgayKetThuc - hopDong.NgayBatDau).TotalDays;
                    if (totalContractDays <= 0) totalContractDays = 1;
                    double daysPerKy = totalContractDays / soKy;

                    for (int i = 1; i <= soKy; i++)
                    {
                        var kyHan = new KyHanThanhToan
                        {
                            MaHopDong = hopDong.MaHopDong,
                            SoKyHan = i,
                            NgayDenHan = hopDong.NgayBatDau.AddDays(Math.Round(i * daysPerKy)),
                            SoTienPhai = tienMoiKy,
                            SoTienDaTra = 0,
                            TrangThai = 0,
                            GhiChu = ""
                        };
                        _context.KyHanThanhToans.Add(kyHan);
                    }
                }
            }
            else if (status == 0) // Chờ duyệt -> Máy đang giữ chỗ
            {
                foreach (var ct in chiTiets)
                {
                    var tb = await _context.ThietBis.FindAsync(ct.MaThietBi);
                    if (tb != null && (tb.TrangThai == 1 || tb.TrangThai == 0))
                    {
                        tb.TrangThai = 3; // Giữ chỗ (Pending)
                    }
                }
            }
            else if (status == 2 || status == 3) // Hoàn tất hoặc Hủy -> Trả máy về kho 0 (Sẵn sàng)
            {
                foreach (var ct in chiTiets)
                {
                    var tb = await _context.ThietBis.FindAsync(ct.MaThietBi);
                    if (tb != null)
                    {
                        tb.TrangThai = 0; // Sẵn sàng
                    }
                }
            }

            hopDong.TrangThai = status;
            await _context.SaveChangesAsync();

            TempData["Success"] = "Đã cập nhật trạng thái đơn hàng và Hệ thống Kho thành công!";
            return RedirectToAction(nameof(Details), new { id = id });
        }
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> AdminSign(int id, string signatureData, string returnUrl = null)
        {
            var hopDong = await _context.HopDongs.FindAsync(id);
            if (hopDong == null) return NotFound();

            if (!string.IsNullOrEmpty(signatureData) && signatureData.StartsWith("data:image/png;base64,"))
            {
                var base64Data = signatureData.Substring("data:image/png;base64,".Length);
                var imageBytes = Convert.FromBase64String(base64Data);
                string sigFileName = $"nv_{hopDong.MaHopDong}_{DateTime.Now.Ticks}.png";
                string sigPath = System.IO.Path.Combine(_env.WebRootPath, "uploads", "signatures", sigFileName);
                await System.IO.File.WriteAllBytesAsync(sigPath, imageBytes);
                
                hopDong.ChuKyNhanVien = $"/uploads/signatures/{sigFileName}";
                hopDong.NgayKy = DateTime.Now;
                
                var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
                if (claim != null && int.TryParse(claim.Value, out int adminId))
                {
                    hopDong.MaNhanVien = adminId;
                }

                await _context.SaveChangesAsync();
                TempData["Success"] = "Đã ký đối chiếu thành công!";
            }
            else
            {
                TempData["Error"] = "Chữ ký không hợp lệ.";
            }

            return RedirectToAction(nameof(Details), new { id = id });
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Ghi nhận thu tiền từng kỳ hạn. Kiểm tra thu đủ, thu thiếu hay trả thừa.
        // Tự động sinh Biên lai (Phiếu Thu) lưu lại lịch sử giao dịch.
        public async Task<IActionResult> ConfirmPayment(int maKyHan, decimal soTienThucThu, int hinhThuc, string ghiChu, string returnUrl = null)
        {
            var kyHan = await _context.KyHanThanhToans.Include(k => k.HopDong).FirstOrDefaultAsync(k => k.MaKyHan == maKyHan);
            if (kyHan == null) return NotFound();

            if (kyHan.TrangThai != 1)
            {
                kyHan.SoTienDaTra += soTienThucThu;
                kyHan.NgayThanhToan = DateTime.Now;
                
                string ghiChuKyHan = "";
                if (kyHan.SoTienDaTra >= kyHan.SoTienPhai)
                {
                    kyHan.TrangThai = 1; // Đã trả
                    if (kyHan.SoTienDaTra > kyHan.SoTienPhai)
                    {
                        var traThua = kyHan.SoTienDaTra - kyHan.SoTienPhai;
                        ghiChuKyHan = $" (Trả thừa {traThua:N0}đ)";
                    }
                }
                else
                {
                    kyHan.TrangThai = 0; // Vẫn tính là chưa trả (trả thiếu)
                }
                
                if (!string.IsNullOrEmpty(ghiChuKyHan))
                {
                    kyHan.GhiChu = (kyHan.GhiChu + ghiChuKyHan).Trim();
                }

                // Create PhieuThu
                var phieuThu = new PhieuThu
                {
                    MaHopDong = kyHan.MaHopDong,
                    LoaiPhieu = 0, // Thu thuê kỳ hạn
                    SoTien = soTienThucThu,
                    NgayGiaoDich = DateTime.Now,
                    HinhThucThanhToan = hinhThuc,
                    GhiChu = string.IsNullOrEmpty(ghiChu) ? $"Thu tiền kỳ {kyHan.SoKyHan}" : ghiChu,
                    MaKyHan = kyHan.MaKyHan
                };
                _context.PhieuThus.Add(phieuThu);

                // Update HopDong payment status
                var allKyHan = await _context.KyHanThanhToans.Where(k => k.MaHopDong == kyHan.MaHopDong).ToListAsync();
                if (allKyHan.All(k => k.TrangThai == 1))
                {
                    kyHan.HopDong.TrangThaiThanhToan = 2; // Đã trả đủ
                }
                else
                {
                    kyHan.HopDong.TrangThaiThanhToan = 1; // Còn nợ
                }

                await _context.SaveChangesAsync();
                TempData["Success"] = $"Đã ghi nhận thu {soTienThucThu:N0}đ cho kỳ {kyHan.SoKyHan}!";
            }

            return RedirectToAction(nameof(Details), new { id = kyHan.MaHopDong, returnUrl = returnUrl });
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Thu thêm tiền cọc bổ sung cho hợp đồng đang hoạt động.
        // Hệ thống sẽ tự động cân bằng lại công nợ: giảm trừ số tiền nợ còn lại và
        // chia lại đều số tiền phải đóng cho các kỳ hạn tương lai.
        public async Task<IActionResult> ThemTienCoc(int maHopDong, decimal soTienCoc, int hinhThuc, string ghiChu, string returnUrl = null)
        {
            var hopDong = await _context.HopDongs.FindAsync(maHopDong);
            if (hopDong == null) return NotFound();

            if (soTienCoc <= 0)
            {
                TempData["Error"] = "Số tiền cọc phải lớn hơn 0!";
                return RedirectToAction(nameof(Details), new { id = maHopDong, returnUrl = returnUrl });
            }

            // Cộng tiền cọc vào hợp đồng
            hopDong.TienDaCoc += soTienCoc;

            // Tạo phiếu thu tiền cọc bổ sung
            var phieuCoc = new PhieuThu
            {
                MaHopDong = maHopDong,
                LoaiPhieu = 1, // Thu cọc
                SoTien = soTienCoc,
                NgayGiaoDich = DateTime.Now,
                HinhThucThanhToan = hinhThuc,
                GhiChu = string.IsNullOrEmpty(ghiChu) ? "Thu tiền cọc bổ sung" : ghiChu
            };
            _context.PhieuThus.Add(phieuCoc);

            // Cập nhật lại các kỳ hạn nếu đã có (tái tính lại tiền còn nợ)
            var kyHans = await _context.KyHanThanhToans
                .Where(k => k.MaHopDong == maHopDong && k.TrangThai == 0)
                .ToListAsync();

            if (kyHans.Any())
            {
                // Tính lại tổng đã trả
                decimal tongDaTra = await _context.KyHanThanhToans
                    .Where(k => k.MaHopDong == maHopDong)
                    .SumAsync(k => k.SoTienDaTra);

                decimal conNo = hopDong.TongTien - hopDong.TienDaCoc - tongDaTra;
                if (conNo < 0) conNo = 0;

                decimal moiKy = conNo / kyHans.Count;
                foreach (var k in kyHans)
                {
                    k.SoTienPhai = moiKy;
                }
            }

            await _context.SaveChangesAsync();
            TempData["Success"] = $"Đã ghi nhận thu cọc bổ sung {soTienCoc:N0}đ thành công!";
            return RedirectToAction(nameof(Details), new { id = maHopDong, returnUrl = returnUrl });
        }
    }
}
