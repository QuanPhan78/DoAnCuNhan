using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using RentalSystem.Controllers;
using RentalSystem.Common;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Areas.Admin.Controllers
{
    [Area("Admin")]
    [Authorize(Roles = "Admin,KinhDoanh,KyThuat")]
    public class HopDongController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly Microsoft.AspNetCore.Hosting.IWebHostEnvironment _env;

        private static readonly SemaphoreSlim _paymentLock = new SemaphoreSlim(1, 1);
        public static SemaphoreSlim PaymentLock => _paymentLock;

        // Tự động cập nhật trễ hạn, phí phạt và phân loại tuổi nợ
        public static void CapNhatTreHanVaPhiPhat(IEnumerable<KyHanThanhToan> kyHans)
        {
            var today = DateTime.Now.Date;
            foreach (var k in kyHans)
            {
                if (k.TrangThai == 1 || k.TrangThai == 3) continue; // paid or cancelled
                if (today > k.NgayDenHan.Date)
                {
                    k.TrangThai = 2; // Trễ hạn
                    k.SoNgayTreHan = (int)(today - k.NgayDenHan.Date).TotalDays;
                    decimal unpaid = Math.Max(0m, k.SoTienPhai - k.SoTienDaTra);
                    k.TienPhat = DebtCalculationHelper.CalculateLateFee(unpaid, k.NgayDenHan, DateTime.Now);
                    k.PhiPhatTreHan = k.TienPhat;
                    k.NhomTuoiNo = DebtCalculationHelper.CalculateAgingTier(k.SoNgayTreHan);
                }
            }
        }

        // Đồng bộ trạng thái thanh toán hợp đồng bao gồm cả chi phí đền bù hư hại
        public static async Task SyncTrangThaiThanhToanHopDong(HopDong hopDong, ApplicationDbContext context)
        {
            var kyHans = await context.KyHanThanhToans
                .Where(k => k.MaHopDong == hopDong.MaHopDong && k.TrangThai != 3)
                .ToListAsync();

            decimal damages = await context.PhieuBaoTris
                .Where(p => p.MaHopDong == hopDong.MaHopDong)
                .SumAsync(p => (decimal?)p.PhiDenBu) ?? 0m;

            decimal paidDamages = await context.PhieuThus
                .Where(pt => pt.MaHopDong == hopDong.MaHopDong && pt.LoaiPhieu == 2 && !pt.DaHuy)
                .SumAsync(pt => (decimal?)pt.SoTien) ?? 0m;

            bool allInstallmentsPaid = kyHans.Count > 0 && kyHans.All(k => k.TrangThai == 1);
            bool damagesCleared = paidDamages >= damages;
            bool hasAnyInstallmentPaid = kyHans.Any(k => k.SoTienDaTra > 0 || k.TrangThai == 1);

            decimal totalReceivable = hopDong.TongTien + damages;
            decimal totalCollected = await context.PhieuThus
                .Where(p => p.MaHopDong == hopDong.MaHopDong && !p.DaHuy && (p.LoaiPhieu == 0 || p.LoaiPhieu == 2))
                .SumAsync(p => (decimal?)p.SoTien) ?? 0m;
            decimal remainingDebt = totalReceivable - totalCollected;

            if ((allInstallmentsPaid && damagesCleared) || remainingDebt <= 0)
            {
                hopDong.TrangThaiThanhToan = 3; // 3: Đã tất toán đủ
            }
            else if (hasAnyInstallmentPaid || (damages > paidDamages) || totalCollected > 0)
            {
                hopDong.TrangThaiThanhToan = 2; // 2: Còn nợ
            }
            else if (hopDong.TienDaCoc > 0 || hopDong.TienCocBaoDamMay > 0)
            {
                hopDong.TrangThaiThanhToan = 1; // 1: Đã đặt cọc
            }
            else
            {
                hopDong.TrangThaiThanhToan = 0; // 0: Chưa thanh toán
            }
        }

        public HopDongController(ApplicationDbContext context, Microsoft.AspNetCore.Hosting.IWebHostEnvironment env)
        {
            _context = context;
            _env = env;
        }

        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> Index(string? filter = null)
        {
            var query = _context.HopDongs
                .Include(h => h.KhachHang)
                .AsQueryable();

            if (filter == "overdue")
            {
                query = query.Where(h => h.TrangThai == 1 && h.NgayKetThuc.Date < DateTime.Now.Date);
            }
            else if (filter == "pending_cancel")
            {
                query = query.Where(h => h.TrangThai == 0 && h.YeuCauHuy);
            }
            else if (filter == "pending_extension")
            {
                query = query.Where(h => h.TrangThai == 1 && h.YeuCauGiaHan);
            }
            else if (filter == "pending_proof")
            {
                query = query.Where(h => h.KyHanThanhToans.Any(k => k.TrangThaiXacNhan == 1));
            }
            else if (filter == "renting")
            {
                query = query.Where(h => h.TrangThai == 1);
            }
            else if (filter == "pending")
            {
                query = query.Where(h => h.TrangThai == 0);
            }
            else if (filter == "completed")
            {
                query = query.Where(h => h.TrangThai == 2);
            }
            else if (filter == "cancelled")
            {
                query = query.Where(h => h.TrangThai == 3);
            }
            else if (filter == "returned_pending_settlement" || filter == "status_4")
            {
                query = query.Where(h => h.TrangThai == 4);
            }

            // Tự động đồng bộ trạng thái trễ hạn vào CSDL
            var overdueToUpdate = await _context.KyHanThanhToans
                .Where(k => (k.TrangThai == 0 || k.TrangThai == 2) && DateTime.Now.Date > k.NgayDenHan.Date)
                .ToListAsync();
            if (overdueToUpdate.Any())
            {
                CapNhatTreHanVaPhiPhat(overdueToUpdate);
                await _context.SaveChangesAsync();
            }

            var data = await query.OrderByDescending(h => h.NgayBatDau).ToListAsync();
            
            var overdueKyHan = await _context.KyHanThanhToans
                .Where(k => (k.TrangThai == 0 || k.TrangThai == 2) && k.NgayDenHan.Date < DateTime.Now.Date && (k.HopDong.TrangThai == 1 || k.HopDong.TrangThai == 0 || k.HopDong.TrangThai == 4))
                .Select(k => k.MaHopDong)
                .Distinct()
                .ToListAsync();

            var overdueHopDong = await _context.HopDongs
                .Where(h => h.TrangThai == 1 && h.NgayKetThuc.Date < DateTime.Now.Date)
                .Select(h => h.MaHopDong)
                .ToListAsync();
            
            ViewBag.Overdue = overdueKyHan;
            ViewBag.OverdueHopDong = overdueHopDong;
            ViewBag.CurrentFilter = filter;
            ViewBag.OverdueCount = overdueHopDong.Count;
            ViewBag.PendingCancelCount = await _context.HopDongs.CountAsync(h => h.TrangThai == 0 && h.YeuCauHuy);
            ViewBag.PendingExtensionCount = await _context.HopDongs.CountAsync(h => h.TrangThai == 1 && h.YeuCauGiaHan);
            ViewBag.PendingProofCount = await _context.KyHanThanhToans.CountAsync(k => k.TrangThaiXacNhan == 1);
            ViewBag.ReturnedPendingCount = await _context.HopDongs.CountAsync(h => h.TrangThai == 4);

            return View(data);
        }

        public async Task<IActionResult> Details(int id, string returnUrl = null)
        {
            ViewBag.ReturnUrl = returnUrl;
            var hd = await _context.HopDongs
                .Include(h => h.KhachHang)
                .Include(h => h.NhanVien)
                .Include(h => h.BienBanBanGiaos)
                .Include(h => h.PhieuChis)
                .Include(h => h.KyHanThanhToans)
                .Include(h => h.PhieuThus)
                .Include(h => h.PhieuBaoTris)
                .Include(h => h.DanhSachYeuCauGiaHan)
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

            CapNhatTreHanVaPhiPhat(kyHans);
            await SyncTrangThaiThanhToanHopDong(hd, _context);
            await _context.SaveChangesAsync();

            var phieuThus = await _context.PhieuThus
                .Include(p => p.NhanVienThu)
                .Where(p => p.MaHopDong == id)
                .OrderByDescending(p => p.NgayGiaoDich)
                .ToListAsync();

            var bienBanBanGiaos = await _context.BienBanBanGiaos
                .Include(b => b.NhanVienLap)
                .Where(b => b.MaHopDong == id)
                .OrderByDescending(b => b.NgayLap)
                .ToListAsync();

            var phieuChis = await _context.PhieuChis
                .Include(p => p.NhanVienChi)
                .Where(p => p.MaHopDong == id)
                .OrderByDescending(p => p.NgayChi)
                .ToListAsync();

            // Lịch sử bảo trì thiết bị trong hợp đồng
            var phieuBaoTris = await _context.PhieuBaoTris
                .Include(p => p.ThietBi).ThenInclude(t => t.SanPham)
                .Include(p => p.KyThuatVien)
                .Where(p => p.MaHopDong == id)
                .OrderByDescending(p => p.NgayBaoLoi)
                .ToListAsync();

            hd.KyHanThanhToans = kyHans;
            hd.PhieuThus = phieuThus;
            hd.PhieuBaoTris = phieuBaoTris;

            ViewBag.ChiTiets = chiTiets;
            ViewBag.KyHans = kyHans;
            ViewBag.PhieuThus = phieuThus;
            ViewBag.BienBanBanGiaos = bienBanBanGiaos;
            ViewBag.PhieuChis = phieuChis;
            ViewBag.PhieuBaoTris = phieuBaoTris;
            ViewBag.YeuCauGiaHans = await _context.YeuCauGiaHans
                .Include(y => y.NguoiDuyet)
                .Where(y => y.MaHopDong == id)
                .OrderByDescending(y => y.NgayYeuCau)
                .ToListAsync();
            return View(hd);
        }

        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> Create()
        {
            var khachHangs = await _context.NguoiDungs.Where(u => u.VaiTro.TenVaiTro == "KhachHang").ToListAsync();
            
            var sanPhams = await _context.SanPhams.Select(sp => new {
                sp.MaSanPham,
                sp.TenSanPham,
                sp.GiaThueNgay,
                TonKho = _context.ThietBis.Count(t => t.MaSanPham == sp.MaSanPham && t.TrangThai != 2 && !_context.ChiTietHopDongs.Any(c => c.MaThietBi == t.MaThietBi && c.HopDong.TrangThai != 2 && c.HopDong.TrangThai != 3 && c.HopDong.NgayKetThuc > DateTime.Now))
            }).ToListAsync();

            ViewBag.KhachHangs = khachHangs;
            ViewBag.SanPhams = sanPhams;

            var availableDevices = await _context.ThietBis
                .Include(t => t.SanPham)
                .Where(t => t.TrangThai == 0)
                .OrderBy(t => t.SanPham.TenSanPham)
                .ToListAsync();
            ViewBag.AvailableDevices = availableDevices;

            return View();
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Giao diện dành cho Admin/Nhân viên tạo đơn trực tiếp tại quầy. 
        // Hỗ trợ tìm hoặc tạo mới khách hàng, thiết lập số kỳ hạn trả góp và thu cọc tức thời.
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> Create(string KhachHang_HoTen, string KhachHang_SoDienThoai, string KhachHang_Email, string KhachHang_DiaChi, DateTime NgayBatDau, DateTime NgayKetThuc, decimal TienDaCoc, int HinhThucCoc, int SoKyHan, int[] SanPhamIds, int[] SoLuongs, string GhiChu)
        {
            // Đọc tiền cọc bảo đảm máy và tiền thuê trả trước từ Request.Form nếu có
            decimal depositBaoDam = 0m;
            decimal rentTraTruoc = 0m;
            try
            {
                if (Request?.HasFormContentType == true)
                {
                    if (Request.Form.ContainsKey("TienCocBaoDamMay") && decimal.TryParse(Request.Form["TienCocBaoDamMay"], out decimal parsedCoc))
                        depositBaoDam = parsedCoc;
                    if (Request.Form.ContainsKey("TienThueTraTruoc") && decimal.TryParse(Request.Form["TienThueTraTruoc"], out decimal parsedRent))
                        rentTraTruoc = parsedRent;
                }
            }
            catch { }

            if (depositBaoDam == 0 && rentTraTruoc == 0 && TienDaCoc > 0)
            {
                depositBaoDam = TienDaCoc;
            }

            // Kiểm tra tiền cọc và tiền thuê trả trước hợp lệ
            if (depositBaoDam < 0 || rentTraTruoc < 0 || TienDaCoc < 0)
            {
                TempData["Error"] = "Tiền đặt cọc và tiền thuê trả trước không thể là số âm!";
                return RedirectToAction(nameof(Create));
            }

            if (NgayKetThuc.Date < NgayBatDau.Date)
            {
                TempData["Error"] = "Ngày trả máy không thể nhỏ hơn ngày nhận máy!";
                return RedirectToAction(nameof(Create));
            }

            // Cảnh báo nếu ngày bắt đầu ở quá khứ
            if (NgayBatDau.Date < DateTime.Now.Date)
            {
                TempData["Warning"] = "Cảnh báo: Ngày bắt đầu ở trong quá khứ!";
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

            // Đồng bộ hóa kiểm tra tồn kho và cấp phát thiết bị
            await CartController.InventoryLock.WaitAsync();
            try
            {
                for (int i = 0; i < SanPhamIds.Length; i++)
                {
                    if (SoLuongs[i] > 0)
                    {
                        int spId = SanPhamIds[i];
                        int slNeed = SoLuongs[i];
                        int slKho = await _context.ThietBis.CountAsync(t => t.MaSanPham == spId && t.TrangThai != 2 && !_context.ChiTietHopDongs.Any(c => c.MaThietBi == t.MaThietBi && c.HopDong.TrangThai != 2 && c.HopDong.TrangThai != 3 && c.HopDong.NgayBatDau < NgayKetThuc && c.HopDong.NgayKetThuc > NgayBatDau));
                        
                        if (slKho < slNeed)
                        {
                            var tenSp = (await _context.SanPhams.FindAsync(spId))?.TenSanPham;
                            TempData["Error"] = $"Sản phẩm '{tenSp}' không đủ số lượng trong kho (Chỉ còn {slKho}).";
                            return RedirectToAction(nameof(Create));
                        }
                    }
                }

                var days = (NgayKetThuc.Date - NgayBatDau.Date).TotalDays;
                if (days <= 0) days = 1;
                decimal totalMoney = 0;

                for (int i = 0; i < SanPhamIds.Length; i++)
                {
                    if (SoLuongs[i] > 0)
                    {
                        var spInfo = await _context.SanPhams.FindAsync(SanPhamIds[i]);
                        if (spInfo != null)
                        {
                            totalMoney += spInfo.GiaThueNgay * (decimal)days * SoLuongs[i];
                        }
                    }
                }

                // Kiểm tra giới hạn tiền đặt cọc
                if (TienDaCoc < 0)
                {
                    TempData["Error"] = "Tiền đặt cọc không thể âm!";
                    return RedirectToAction(nameof(Create));
                }
                if (TienDaCoc > totalMoney)
                {
                    if (depositBaoDam <= 0)
                    {
                        TempData["Error"] = "Tiền đặt cọc không thể lớn hơn tổng giá trị hợp đồng!";
                        return RedirectToAction(nameof(Create));
                    }
                }

                // Tiền thuê trả trước không được lớn hơn tổng giá trị tiền thuê
                if (rentTraTruoc > totalMoney)
                {
                    TempData["Error"] = $"Tiền thuê trả trước ({rentTraTruoc:N0}đ) không thể lớn hơn tổng giá trị hợp đồng ({totalMoney:N0}đ)!";
                    return RedirectToAction(nameof(Create));
                }

                int adminId = 1;
                var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
                if (claim != null && int.TryParse(claim.Value, out int parsedId))
                {
                    adminId = parsedId;
                }

                // Kiểm tra hoặc tạo thông tin khách hàng, tránh ghi đè tài khoản nhân viên
                var existingUser = await _context.NguoiDungs
                    .Include(u => u.VaiTro)
                    .FirstOrDefaultAsync(u => u.SoDienThoai == KhachHang_SoDienThoai || (!string.IsNullOrEmpty(KhachHang_Email) && u.Email == KhachHang_Email));

                string? cccdFromForm = null;
                try
                {
                    if (Request?.HasFormContentType == true)
                    {
                        if (Request.Form.ContainsKey("KhachHang_CCCD"))
                            cccdFromForm = Request.Form["KhachHang_CCCD"].ToString()?.Trim();
                        else if (Request.Form.ContainsKey("CCCD"))
                            cccdFromForm = Request.Form["CCCD"].ToString()?.Trim();
                    }
                }
                catch
                {
                    // Bỏ qua nếu không đọc được từ form
                }

                NguoiDung khachHang;
                if (existingUser != null)
                {
                    if (existingUser.VaiTro != null && existingUser.VaiTro.TenVaiTro != "KhachHang")
                    {
                        TempData["Error"] = "Số điện thoại hoặc Email đã thuộc về tài khoản nhân viên nội bộ! Không thể sử dụng làm thông tin khách hàng.";
                        return RedirectToAction(nameof(Create));
                    }

                    string finalCccd = !string.IsNullOrWhiteSpace(cccdFromForm) ? cccdFromForm : (existingUser.CCCD ?? "");
                    if (string.IsNullOrWhiteSpace(finalCccd))
                    {
                        TempData["Error"] = "Khách hàng chưa có số CCCD/CMND! Vui lòng cập nhật số CCCD của khách hàng trước khi tạo hợp đồng.";
                        return RedirectToAction(nameof(Create));
                    }

                    // Cập nhật thông tin liên hệ cho khách hàng (không sửa mật khẩu, không nâng quyền)
                    existingUser.HoTen = KhachHang_HoTen;
                    if (!string.IsNullOrEmpty(KhachHang_Email)) existingUser.Email = KhachHang_Email;
                    if (!string.IsNullOrEmpty(KhachHang_DiaChi)) existingUser.DiaChi = KhachHang_DiaChi;
                    existingUser.CCCD = finalCccd;
                    await _context.SaveChangesAsync();
                    khachHang = existingUser;
                }
                else
                {
                    if (string.IsNullOrWhiteSpace(cccdFromForm))
                    {
                        TempData["Error"] = "Khách hàng chưa có số CCCD/CMND! Vui lòng cập nhật số CCCD của khách hàng trước khi tạo hợp đồng.";
                        return RedirectToAction(nameof(Create));
                    }

                    var vaiTroKhachHang = await _context.VaiTros.FirstOrDefaultAsync(v => v.TenVaiTro == "KhachHang");
                    khachHang = new NguoiDung
                    {
                        HoTen = KhachHang_HoTen,
                        SoDienThoai = KhachHang_SoDienThoai,
                        Email = KhachHang_Email ?? "",
                        DiaChi = KhachHang_DiaChi ?? "",
                        MaVaiTro = vaiTroKhachHang?.MaVaiTro ?? 4,
                        MatKhau = KhachHang_SoDienThoai,
                        CCCD = cccdFromForm,
                        TrangThai = true
                    };
                    _context.NguoiDungs.Add(khachHang);
                    await _context.SaveChangesAsync();
                }

                // Bắt buộc khách hàng phải có số CCCD/CMND khi tạo hợp đồng
                if (string.IsNullOrWhiteSpace(khachHang.CCCD))
                {
                    TempData["Error"] = "Khách hàng chưa có số CCCD/CMND! Vui lòng cập nhật số CCCD của khách hàng trước khi tạo hợp đồng.";
                    return RedirectToAction(nameof(Create));
                }

                decimal finalTotalDeposit = (depositBaoDam + rentTraTruoc) > 0 ? (depositBaoDam + rentTraTruoc) : TienDaCoc;

                var hd = new HopDong
                {
                    MaKhachHang = khachHang.MaNguoiDung,
                    MaNhanVien = adminId,
                    NgayBatDau = NgayBatDau,
                    NgayKetThuc = NgayKetThuc,
                    TienCocBaoDamMay = depositBaoDam,
                    TienThueTraTruoc = rentTraTruoc,
                    TienDaCoc = finalTotalDeposit,
                    TrangThai = 0, // Chờ duyệt
                    NgayKy = null,
                    ChuKyKhachHang = "",
                    ChuKyNhanVien = "",
                    AnhCMND = "",
                    TrangThaiThanhToan = 0,
                    GhiChu = GhiChu ?? "",
                    TongTien = totalMoney,
                    HanChotKy = DateTime.Now.AddHours(24)
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
                            .Where(t => t.MaSanPham == spId && t.TrangThai != 2 && !_context.ChiTietHopDongs.Any(c => c.MaThietBi == t.MaThietBi && c.HopDong.TrangThai != 2 && c.HopDong.TrangThai != 3 && c.HopDong.NgayBatDau < NgayKetThuc && c.HopDong.NgayKetThuc > NgayBatDau))
                            .Take(slNeed)
                            .ToListAsync();

                        if (devices.Count < slNeed)
                        {
                            TempData["Error"] = $"Sản phẩm '{spInfo.TenSanPham}' không đủ số lượng thực tế trong kho.";
                            return RedirectToAction(nameof(Create));
                        }

                        foreach (var dev in devices)
                        {
                            var ct = new ChiTietHopDong
                            {
                                MaHopDong = hd.MaHopDong,
                                MaThietBi = dev.MaThietBi,
                                GiaChotThu = giaThue
                            };
                            _context.ChiTietHopDongs.Add(ct);
                            
                            // Đánh dấu thiết bị đang được giữ chỗ (3)
                            dev.TrangThai = 3;
                        }
                    }
                }
                
                // Tự động tạo Phiếu Thu cho Tiền Cọc bảo đảm máy và Tiền thuê trả trước (nếu có)
                if (hd.TienCocBaoDamMay > 0)
                {
                    var phieuCoc = new PhieuThu
                    {
                        MaHopDong = hd.MaHopDong,
                        LoaiPhieu = 1, // Thu cọc
                        SoTien = hd.TienCocBaoDamMay,
                        NgayGiaoDich = DateTime.Now,
                        HinhThucThanhToan = HinhThucCoc,
                        GhiChu = "Thu tiền cọc bảo đảm máy khi tạo đơn",
                        MaNhanVienThu = adminId,
                        DaHuy = false
                    };
                    _context.PhieuThus.Add(phieuCoc);
                    hd.TrangThaiThanhToan = 1; // 1: Đã đặt cọc
                }

                if (hd.TienThueTraTruoc > 0)
                {
                    var phieuRent = new PhieuThu
                    {
                        MaHopDong = hd.MaHopDong,
                        LoaiPhieu = 0, // Thu tiền thuê
                        SoTien = hd.TienThueTraTruoc,
                        NgayGiaoDich = DateTime.Now,
                        HinhThucThanhToan = HinhThucCoc,
                        GhiChu = "Thu tiền thuê trả trước khi tạo đơn",
                        MaNhanVienThu = adminId,
                        DaHuy = false
                    };
                    _context.PhieuThus.Add(phieuRent);
                    hd.TrangThaiThanhToan = 2; // Còn nợ
                }
                else if (hd.TienCocBaoDamMay == 0 && hd.TienDaCoc > 0)
                {
                    var phieuCoc = new PhieuThu
                    {
                        MaHopDong = hd.MaHopDong,
                        LoaiPhieu = 1, // Thu cọc
                        SoTien = hd.TienDaCoc,
                        NgayGiaoDich = DateTime.Now,
                        HinhThucThanhToan = HinhThucCoc,
                        GhiChu = "Thu tiền cọc khi tạo đơn",
                        MaNhanVienThu = adminId,
                        DaHuy = false
                    };
                    _context.PhieuThus.Add(phieuCoc);
                    hd.TrangThaiThanhToan = 1; // 1: Đã đặt cọc
                }

                int maxInstallments = Math.Max(1, (int)Math.Floor(days / 7.0));
                if (SoKyHan < 1) SoKyHan = 1;
                if (SoKyHan > maxInstallments) SoKyHan = maxInstallments;
                hd.SoKyHan = SoKyHan;

                await _context.SaveChangesAsync();
                
                TempData["Success"] = "Đã tạo hợp đồng mới thành công (Đang chờ duyệt)!";
                return RedirectToAction(nameof(Index));
            }
            finally
            {
                CartController.InventoryLock.Release();
            }
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Cập nhật trạng thái hợp đồng và điều phối vòng đời thiết bị
        // (0: Chờ duyệt, 1: Đang thuê, 2: Hoàn tất, 3: Đã hủy, 4: Đã trả máy/Chờ quyết toán)
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> UpdateStatus(int id, int status, string returnUrl = null)
        {
            if (status < 0 || status > 4)
            {
                TempData["Error"] = "Trạng thái không hợp lệ!";
                return RedirectToAction(nameof(Index));
            }

            var hopDong = await _context.HopDongs
                .Include(h => h.KyHanThanhToans)
                .Include(h => h.PhieuBaoTris)
                .Include(h => h.PhieuThus)
                .FirstOrDefaultAsync(h => h.MaHopDong == id);
            if (hopDong == null) return NotFound();

            // Không cho đổi trạng thái khi hợp đồng đã hoàn tất hoặc đã hủy
            if ((hopDong.TrangThai == 2 || hopDong.TrangThai == 3) && (status != hopDong.TrangThai))
            {
                TempData["Error"] = "Hợp đồng đã đóng (Hoàn tất/Hủy) không thể chuyển đổi trạng thái!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            // Không cho chuyển ngược về Chờ duyệt
            if ((hopDong.TrangThai == 1 || hopDong.TrangThai == 4) && status == 0)
            {
                TempData["Error"] = "Hợp đồng đã bàn giao máy không thể chuyển ngược về trạng thái Chờ duyệt!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            // Không cho hủy hợp đồng khi máy đang cho thuê
            if (hopDong.TrangThai == 1 && status == 3)
            {
                TempData["Error"] = "Không thể hủy hợp đồng khi thiết bị đang trong quá trình cho thuê! Vui lòng thực hiện quy trình thu hồi máy.";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            // Chặn kết thúc hoặc hủy hợp đồng khi còn phiếu bảo trì chưa đóng
            if (status == 2 || status == 3)
            {
                bool coPhieuDangXuLy = await _context.PhieuBaoTris
                    .AnyAsync(p => p.MaHopDong == id && (p.TrangThai == 1 || p.TrangThai == 2));
                if (coPhieuDangXuLy)
                {
                    TempData["Error"] = "CẢNH BÁO RÀNG BUỘC: Hợp đồng còn phiếu bảo trì/sự cố đang trong quá trình xử lý dở dang (chưa đóng). Vui lòng hoàn tất hoặc đóng phiếu bảo trì trước khi kết thúc hợp đồng!";
                    return RedirectToAction(nameof(Details), new { id = id });
                }
            }

            var chiTiets = await _context.ChiTietHopDongs.Where(c => c.MaHopDong == id).ToListAsync();
            var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            int adminId = (claim != null && int.TryParse(claim.Value, out int aId)) ? aId : hopDong.MaNhanVien;

            if (status == 1) // Giao máy & Cho thuê -> Chuyển máy sang 1 (Đang cho thuê)
            {
                // Kiểm tra chữ ký khách hàng và ảnh CCCD trước khi bàn giao máy
                if (string.IsNullOrEmpty(hopDong.ChuKyKhachHang) || (string.IsNullOrEmpty(hopDong.AnhCMND) && string.IsNullOrEmpty(hopDong.AnhCCCD_Truoc)))
                {
                    TempData["Error"] = "CẢNH BÁO BẢO MẬT: Không thể giao máy khi hợp đồng chưa có chữ ký của khách hàng hoặc chưa có ảnh CCCD!";
                    return RedirectToAction(nameof(Details), new { id = id });
                }

                if (string.IsNullOrEmpty(hopDong.ChuKyNhanVien))
                {
                    TempData["Error"] = "Vui lòng hoàn tất Chữ ký nhân viên đối chiếu trước khi thực hiện bàn giao máy!";
                    return RedirectToAction(nameof(Details), new { id = id });
                }

                foreach (var ct in chiTiets)
                {
                    var tb = await _context.ThietBis.FindAsync(ct.MaThietBi);
                    if (tb != null)
                    {
                        tb.TrangThai = 1; // Đang cho thuê
                        _context.LichSuThietBis.Add(new LichSuThietBi
                        {
                            MaThietBi = tb.MaThietBi,
                            HanhDong = $"Xuất kho bàn giao thiết bị cho khách theo HĐ #{id} (TrangThai = 1)",
                            ThoiGian = DateTime.Now,
                            MaNguoiThucHien = adminId,
                            GhiChu = $"Bàn giao theo hợp đồng #{id}"
                        });
                    }
                }

                // Tự động tạo Biên bản bàn giao xuất kho nếu chưa có
                bool hasHandoverSlip = await _context.BienBanBanGiaos.AnyAsync(b => b.MaHopDong == id && b.LoaiBienBan == 0);
                if (!hasHandoverSlip)
                {
                    var bbGiao = new BienBanBanGiao
                    {
                        MaHopDong = id,
                        LoaiBienBan = 0, // Xuất kho bàn giao
                        NgayLap = DateTime.Now,
                        MaNhanVienLap = adminId,
                        PhuKienKemTheo = "Đầy đủ sạc nguồn, chuột, túi chống sốc theo tiêu chuẩn xuất kho",
                        TinhTrangNgoaiQuan = "Máy nguyên vẹn, ngoại quan hoạt động tốt",
                        GhiChu = "Tự động lập biên bản bàn giao khi duyệt xuất kho cho thuê"
                    };
                    _context.BienBanBanGiaos.Add(bbGiao);
                }

                // Phân chia kỳ hạn trả góp dựa trên số tiền thuê còn lại sau khi trừ tiền thuê trả trước
                bool hasInstallments = await _context.KyHanThanhToans.AnyAsync(k => k.MaHopDong == id);
                if (!hasInstallments)
                {
                    int soKy = hopDong.SoKyHan > 0 ? hopDong.SoKyHan : 1;
                    var totalContractDays = (hopDong.NgayKetThuc.Date - hopDong.NgayBatDau.Date).TotalDays;
                    if (totalContractDays <= 0) totalContractDays = 1;

                    int maxAllowedKy = Math.Max(1, (int)Math.Floor(totalContractDays / 7.0));
                    if (soKy > maxAllowedKy)
                    {
                        soKy = maxAllowedKy;
                        hopDong.SoKyHan = soKy;
                    }

                    decimal remainingRentToSplit = Math.Max(0m, hopDong.TongTien - hopDong.TienThueTraTruoc);
                    if (remainingRentToSplit > 0)
                    {
                        decimal tienMoiKy = Math.Round((remainingRentToSplit / soKy) / 1000m) * 1000m;
                        decimal tongDaPhanBo = 0m;

                        for (int i = 1; i <= soKy; i++)
                        {
                            decimal soTienPhai = (i == soKy) ? (remainingRentToSplit - tongDaPhanBo) : tienMoiKy;
                            tongDaPhanBo += soTienPhai;

                            // Kỳ 1 thu vào ngày bắt đầu nhận máy
                            DateTime ngayDenHan = (i == 1 || soKy == 1)
                                ? hopDong.NgayBatDau.Date
                                : hopDong.NgayBatDau.Date.AddDays(Math.Round((double)(i - 1) / (soKy - 1) * totalContractDays));

                            var kyHan = new KyHanThanhToan
                            {
                                MaHopDong = hopDong.MaHopDong,
                                SoKyHan = i,
                                NgayDenHan = ngayDenHan,
                                SoTienPhai = soTienPhai,
                                SoTienDaTra = 0,
                                TrangThai = 0,
                                GhiChu = (i == 1) ? "Kỳ 1 - Thanh toán đầu kỳ khi nhận máy" : $"Kỳ {i}"
                            };
                            _context.KyHanThanhToans.Add(kyHan);
                        }
                    }
                    else
                    {
                        hopDong.TrangThaiThanhToan = 3; // 3: Đã thanh toán đủ bằng tiền thuê trả trước
                    }
                    await SyncTrangThaiThanhToanHopDong(hopDong, _context);
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
            else if (status == 4) // Đã trả máy (Chờ quyết toán công nợ)
            {
                // Giải phóng toàn bộ thiết bị về kho (0: Ready) TRỪ thiết bị hỏng (4: Broken)
                foreach (var ct in chiTiets)
                {
                    var tb = await _context.ThietBis.FindAsync(ct.MaThietBi);
                    if (tb != null)
                    {
                        bool isBroken = tb.TrangThai == 4 || await _context.PhieuBaoTris.AnyAsync(p => p.MaThietBi == tb.MaThietBi && p.TrangThai == 4);
                        if (isBroken)
                        {
                            tb.TrangThai = 4;
                            tb.TinhTrangMay = "Hỏng không thể khắc phục (Thanh lý)";
                            _context.LichSuThietBis.Add(new LichSuThietBi
                            {
                                MaThietBi = tb.MaThietBi,
                                HanhDong = $"Thu hồi từ HĐ #{id}: Thiết bị hỏng không thể khắc phục, giữ nguyên trạng thái thanh lý (TrangThai = 4)",
                                ThoiGian = DateTime.Now,
                                MaNguoiThucHien = adminId,
                                GhiChu = $"Hợp đồng #{id} đã trả máy (chờ quyết toán nợ) nhưng thiết bị hỏng hoàn toàn"
                            });
                        }
                        else
                        {
                            tb.TrangThai = 0; // Sẵn sàng cho thuê
                            _context.LichSuThietBis.Add(new LichSuThietBi
                            {
                                MaThietBi = tb.MaThietBi,
                                HanhDong = $"Thu hồi nhập kho sẵn sàng cho thuê (TrangThai = 0) từ HĐ #{id}",
                                ThoiGian = DateTime.Now,
                                MaNguoiThucHien = adminId,
                                GhiChu = $"Hợp đồng #{id} đã trả máy (Chờ quyết toán công nợ)"
                            });
                        }
                    }
                }

                // Tự động tạo Biên bản thu hồi nhập kho nếu chưa có
                bool hasReturnSlip = await _context.BienBanBanGiaos.AnyAsync(b => b.MaHopDong == id && b.LoaiBienBan == 1);
                if (!hasReturnSlip)
                {
                    var bbThuHoi = new BienBanBanGiao
                    {
                        MaHopDong = id,
                        LoaiBienBan = 1, // Thu hồi nhập kho
                        NgayLap = DateTime.Now,
                        MaNhanVienLap = adminId,
                        PhuKienKemTheo = "Đầy đủ phụ kiện theo hợp đồng",
                        TinhTrangNgoaiQuan = "Đã kiểm tra thu hồi máy về kho (Chờ quyết toán công nợ)",
                        GhiChu = "Biên bản thu hồi máy vật lý về kho khi hợp đồng chuyển sang trạng thái Đã trả máy (Chờ quyết toán nợ)"
                    };
                    _context.BienBanBanGiaos.Add(bbThuHoi);
                }

                hopDong.TrangThai = 4;
                await SyncTrangThaiThanhToanHopDong(hopDong, _context);
                await _context.SaveChangesAsync();

                TempData["Success"] = "Đã tiếp nhận thu hồi thiết bị về kho thành công! Hợp đồng chuyển sang trạng thái 'Đã trả máy (Chờ quyết toán công nợ)'.";
                return RedirectToAction(nameof(Details), new { id = id });
            }
            else if (status == 2) // Hoàn tất / Thu hồi máy & Quyết toán cọc
            {
                decimal tienCoc = hopDong.TienCocBaoDamMay > 0 ? hopDong.TienCocBaoDamMay : hopDong.TienDaCoc;
                var unpaidKyHans = hopDong.KyHanThanhToans?
                    .Where(k => k.TrangThai != 1 && k.TrangThai != 3)
                    .OrderBy(k => k.SoKyHan)
                    .ToList() ?? new List<KyHanThanhToan>();
                decimal unpaidRent = unpaidKyHans.Sum(k => Math.Max(0m, k.SoTienPhai - k.SoTienDaTra + k.TienPhat));

                var totalDamages = await _context.PhieuBaoTris
                    .Where(p => p.MaHopDong == id)
                    .SumAsync(p => (decimal?)p.PhiDenBu) ?? 0m;

                var totalPaidDamages = await _context.PhieuThus
                    .Where(pt => pt.MaHopDong == id && pt.LoaiPhieu == 2 && !pt.DaHuy)
                    .SumAsync(pt => (decimal?)pt.SoTien) ?? 0m;

                decimal unpaidDamages = totalDamages > totalPaidDamages ? (totalDamages - totalPaidDamages) : 0m;

                var (refund, remainingDebt) = DebtCalculationHelper.CalculateDepositSettlement(hopDong, unpaidRent, unpaidDamages);

                if (refund < 0)
                {
                    // Nếu đang ở trạng thái 1 (Đang thuê), tự động chuyển sang 4 để giải phóng máy về kho
                    if (hopDong.TrangThai == 1)
                    {
                        foreach (var ct in chiTiets)
                        {
                            var tb = await _context.ThietBis.FindAsync(ct.MaThietBi);
                            if (tb != null)
                            {
                                bool isBroken = tb.TrangThai == 4 || await _context.PhieuBaoTris.AnyAsync(p => p.MaThietBi == tb.MaThietBi && p.TrangThai == 4);
                                tb.TrangThai = isBroken ? 4 : 0;
                                if (isBroken) tb.TinhTrangMay = "Hỏng không thể khắc phục (Thanh lý)";
                                _context.LichSuThietBis.Add(new LichSuThietBi
                                {
                                    MaThietBi = tb.MaThietBi,
                                    HanhDong = isBroken ? $"Thu hồi HĐ #{id}: Thiết bị hỏng không thể khắc phục (TrangThai = 4)" : $"Thu hồi nhập kho (TrangThai = 0) từ HĐ #{id}",
                                    ThoiGian = DateTime.Now,
                                    MaNguoiThucHien = adminId,
                                    GhiChu = $"Hợp đồng #{id} chuyển sang trạng thái 4 chờ quyết toán nợ"
                                });
                            }
                        }

                        bool hasReturnSlip = await _context.BienBanBanGiaos.AnyAsync(b => b.MaHopDong == id && b.LoaiBienBan == 1);
                        if (!hasReturnSlip)
                        {
                            _context.BienBanBanGiaos.Add(new BienBanBanGiao
                            {
                                MaHopDong = id,
                                LoaiBienBan = 1,
                                NgayLap = DateTime.Now,
                                MaNhanVienLap = adminId,
                                PhuKienKemTheo = "Đầy đủ phụ kiện theo hợp đồng",
                                TinhTrangNgoaiQuan = "Đã thu hồi máy về kho (Chờ quyết toán)",
                                GhiChu = "Biên bản thu hồi máy vật lý khi hợp đồng chuyển sang Chờ quyết toán nợ"
                            });
                        }

                        hopDong.TrangThai = 4;
                        await SyncTrangThaiThanhToanHopDong(hopDong, _context);
                        await _context.SaveChangesAsync();

                        TempData["Warning"] = $"Khách hàng còn nợ {remainingDebt:N0} đ (Nợ thuê: {unpaidRent:N0} đ, phí đền bù: {unpaidDamages:N0} đ). Đã giải phóng thiết bị về kho và chuyển hợp đồng sang trạng thái 'Đã trả máy (Chờ quyết toán công nợ)'!";
                        return RedirectToAction(nameof(Details), new { id = id });
                    }
                    else
                    {
                        TempData["Error"] = $"Không thể hoàn tất hợp đồng: Sau khi cấn trừ cọc, khách hàng vẫn còn nợ {remainingDebt:N0} đ (Nợ thuê: {unpaidRent:N0} đ, phí đền bù: {unpaidDamages:N0} đ). Vui lòng thu hồi khoản nợ này trước khi tất toán hợp đồng!";
                        return RedirectToAction(nameof(Details), new { id = id });
                    }
                }

                // Cấn trừ tiền nợ thuê từ cọc
                if (unpaidRent > 0)
                {
                    foreach (var k in unpaidKyHans)
                    {
                        k.SoTienDaTra = k.SoTienPhai;
                        k.TrangThai = 1;
                        k.NgayThanhToan = DateTime.Now;
                        k.PhiPhatTreHan = 0;
                        k.TienPhat = 0;
                        k.SoNgayTreHan = 0;
                        k.GhiChu = ((k.GhiChu ?? "") + " [Cấn trừ từ tiền cọc]").Trim();
                    }
                }
                hopDong.TrangThaiThanhToan = 3; // 3: Đã tất toán đủ

                // Cấn trừ phí bồi thường hư hại từ cọc
                if (unpaidDamages > 0)
                {
                    var phieuThuDenBu = new PhieuThu
                    {
                        MaHopDong = id,
                        LoaiPhieu = 2,
                        SoTien = unpaidDamages,
                        NgayGiaoDich = DateTime.Now,
                        HinhThucThanhToan = 2, // Cấn trừ cọc
                        GhiChu = "Cấn trừ phí đền bù hư hại từ tiền cọc của hợp đồng",
                        MaNhanVienThu = adminId,
                        DaHuy = false
                    };
                    _context.PhieuThus.Add(phieuThuDenBu);
                }

                // Tạo phiếu chi hoàn cọc nếu có số tiền cọc thực hoàn > 0
                if (refund > 0 && hopDong.TrangThaiHoanCoc == 0)
                {
                    var phieuChiHoanCoc = new PhieuChi
                    {
                        MaHopDong = id,
                        LoaiChi = 0, // Hoàn tiền cọc
                        SoTien = refund,
                        NgayChi = DateTime.Now,
                        HinhThucChi = 1, // Chuyển khoản hoàn cọc
                        MaNhanVienChi = adminId,
                        GhiChu = $"Hoàn trả tiền cọc sau khi quyết toán hợp đồng HD{hopDong.MaHopDong} (Cọc: {tienCoc:N0}đ, Nợ thuê: {unpaidRent:N0}đ, Phí BT: {unpaidDamages:N0}đ)"
                    };
                    _context.PhieuChis.Add(phieuChiHoanCoc);
                    hopDong.TrangThaiHoanCoc = 1;
                    hopDong.TienCocThucHoan = refund;
                    hopDong.NgayHoanCoc = DateTime.Now;
                    hopDong.GhiChuHoanCoc = phieuChiHoanCoc.GhiChu;
                }
                else if (tienCoc > 0 && refund == 0)
                {
                    hopDong.TrangThaiHoanCoc = 2; // Cấn trừ hết cọc
                    hopDong.TienCocThucHoan = 0;
                    hopDong.NgayHoanCoc = DateTime.Now;
                    hopDong.GhiChuHoanCoc = "Cọc đã được cấn trừ toàn bộ cho công nợ thuê và phí đền bù.";
                }

                // Giải phóng thiết bị về kho (giữ nguyên thiết bị hỏng ở trạng thái thanh lý)
                foreach (var ct in chiTiets)
                {
                    var tb = await _context.ThietBis.FindAsync(ct.MaThietBi);
                    if (tb != null)
                    {
                        bool isBroken = tb.TrangThai == 4 || await _context.PhieuBaoTris.AnyAsync(p => p.MaThietBi == tb.MaThietBi && p.TrangThai == 4);
                        if (isBroken)
                        {
                            tb.TrangThai = 4;
                            tb.TinhTrangMay = "Hỏng không thể khắc phục (Thanh lý)";
                            _context.LichSuThietBis.Add(new LichSuThietBi
                            {
                                MaThietBi = tb.MaThietBi,
                                HanhDong = $"Thu hồi từ HĐ #{id}: Thiết bị hỏng không thể khắc phục, giữ nguyên trạng thái thanh lý (TrangThai = 4)",
                                ThoiGian = DateTime.Now,
                                MaNguoiThucHien = adminId,
                                GhiChu = $"Hợp đồng #{id} hoàn tất nhưng thiết bị đã hỏng hoàn toàn"
                            });
                        }
                        else
                        {
                            tb.TrangThai = 0;
                            _context.LichSuThietBis.Add(new LichSuThietBi
                            {
                                MaThietBi = tb.MaThietBi,
                                HanhDong = $"Thu hồi nhập kho sẵn sàng cho thuê (TrangThai = 0) từ HĐ #{id}",
                                ThoiGian = DateTime.Now,
                                MaNguoiThucHien = adminId,
                                GhiChu = $"Hoàn tất hợp đồng #{id}"
                            });
                        }
                    }
                }

                // Tự động tạo Biên bản thu hồi nhập kho
                var bbThuHoi = new BienBanBanGiao
                {
                    MaHopDong = id,
                    LoaiBienBan = 1, // Thu hồi nhập kho
                    NgayLap = DateTime.Now,
                    MaNhanVienLap = adminId,
                    PhuKienKemTheo = "Đầy đủ phụ kiện theo hợp đồng",
                    TinhTrangNgoaiQuan = "Đã kiểm tra thu hồi máy về kho an toàn",
                    GhiChu = "Biên bản thu hồi tự động khi hoàn tất hợp đồng"
                };
                _context.BienBanBanGiaos.Add(bbThuHoi);
            }
            else if (status == 3) // Hủy hợp đồng (chỉ cho phép khi ở trạng thái 0)
            {
                var kyHans = await _context.KyHanThanhToans.Where(k => k.MaHopDong == id).ToListAsync();
                foreach (var k in kyHans)
                {
                    if (k.TrangThai != 1) k.TrangThai = 3; // 3 = Đã hủy
                }

                decimal totalCollected = await _context.PhieuThus.Where(p => p.MaHopDong == id).SumAsync(p => (decimal?)p.SoTien) ?? 0;
                if (hopDong.TienDaCoc > 0 || totalCollected > 0)
                {
                    decimal refundAmount = hopDong.TienDaCoc > 0 ? hopDong.TienDaCoc : totalCollected;
                    var phieuChiHuy = new PhieuChi
                    {
                        MaHopDong = id,
                        LoaiChi = 0,
                        SoTien = refundAmount,
                        NgayChi = DateTime.Now,
                        HinhThucChi = 1,
                        MaNhanVienChi = adminId,
                        GhiChu = $"Hoàn tiền khi hủy hợp đồng (Lý do: {hopDong.LyDoHuy ?? "Hủy đơn trước khi nhận máy"})"
                    };
                    _context.PhieuChis.Add(phieuChiHuy);
                    hopDong.TrangThaiHoanCoc = 1;
                    hopDong.TienCocThucHoan = refundAmount;
                    hopDong.NgayHoanCoc = DateTime.Now;
                }

                hopDong.YeuCauHuy = false;

                // Giải phóng thiết bị về kho khi hủy hợp đồng
                foreach (var ct in chiTiets)
                {
                    var tb = await _context.ThietBis.FindAsync(ct.MaThietBi);
                    if (tb != null)
                    {
                        bool isBroken = tb.TrangThai == 4 || await _context.PhieuBaoTris.AnyAsync(p => p.MaThietBi == tb.MaThietBi && p.TrangThai == 4);
                        if (isBroken)
                        {
                            tb.TrangThai = 4;
                            tb.TinhTrangMay = "Hỏng không thể khắc phục (Thanh lý)";
                            _context.LichSuThietBis.Add(new LichSuThietBi
                            {
                                MaThietBi = tb.MaThietBi,
                                HanhDong = $"Hủy HĐ #{id}: Thiết bị hỏng không thể khắc phục, giữ nguyên trạng thái thanh lý (TrangThai = 4)",
                                ThoiGian = DateTime.Now,
                                MaNguoiThucHien = adminId,
                                GhiChu = $"Hợp đồng #{id} bị hủy nhưng thiết bị đã hỏng hoàn toàn"
                            });
                        }
                        else
                        {
                            tb.TrangThai = 0;
                            _context.LichSuThietBis.Add(new LichSuThietBi
                            {
                                MaThietBi = tb.MaThietBi,
                                HanhDong = $"Hủy HĐ #{id}: Giải phóng thiết bị về kho (TrangThai = 0)",
                                ThoiGian = DateTime.Now,
                                MaNguoiThucHien = adminId,
                                GhiChu = $"Hủy hợp đồng #{id}"
                            });
                        }
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
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> CapNhatTrangThai(int id, int status, string returnUrl = null)
        {
            return await UpdateStatus(id, status, returnUrl);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> HuyHopDong(int id, string returnUrl = null)
        {
            return await UpdateStatus(id, 3, returnUrl);
        }
        [HttpPost]
        [ValidateAntiForgeryToken]
        // Kiểm tra tính hợp lệ của chữ ký điện tử nhân viên (định dạng ảnh Base64, dung lượng cho phép)
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> AdminSign(int id, string signatureData, string returnUrl = null)
        {
            var hopDong = await _context.HopDongs.FindAsync(id);
            if (hopDong == null) return NotFound();

            if (string.IsNullOrEmpty(signatureData))
            {
                TempData["Error"] = "Dữ liệu chữ ký không được để trống!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            // Giới hạn dung lượng chữ ký tối đa 256KB
            if (signatureData.Length > 256 * 1024)
            {
                TempData["Error"] = "Kích thước dữ liệu chữ ký vượt quá giới hạn cho phép (tối đa 256KB)!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            string base64Data = signatureData;
            if (signatureData.StartsWith("data:image/png;base64,", StringComparison.OrdinalIgnoreCase))
            {
                base64Data = signatureData.Substring("data:image/png;base64,".Length);
            }
            else if (signatureData.StartsWith("data:image/jpeg;base64,", StringComparison.OrdinalIgnoreCase))
            {
                base64Data = signatureData.Substring("data:image/jpeg;base64,".Length);
            }
            else if (signatureData.StartsWith("data:", StringComparison.OrdinalIgnoreCase))
            {
                TempData["Error"] = "Định dạng chữ ký không được hỗ trợ (yêu cầu ảnh PNG)!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            byte[] imageBytes;
            try
            {
                imageBytes = Convert.FromBase64String(base64Data);
            }
            catch (FormatException)
            {
                TempData["Error"] = "Dữ liệu chữ ký Base64 bị lỗi định dạng!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            // Kiểm tra định dạng ảnh PNG hợp lệ
            if (imageBytes.Length < 8 || imageBytes[0] != 0x89 || imageBytes[1] != 0x50 || imageBytes[2] != 0x4E || imageBytes[3] != 0x47)
            {
                TempData["Error"] = "Dữ liệu chữ ký không phải là ảnh PNG hợp lệ!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            string sigFolder = System.IO.Path.Combine(_env.WebRootPath, "uploads", "signatures");
            if (!System.IO.Directory.Exists(sigFolder))
            {
                System.IO.Directory.CreateDirectory(sigFolder);
            }

            string sigFileName = $"nv_{hopDong.MaHopDong}_{DateTime.Now.Ticks}.png";
            string sigPath = System.IO.Path.Combine(sigFolder, sigFileName);
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
            return RedirectToAction(nameof(Details), new { id = id });
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> LuuChuKy(int id, string signatureData, string returnUrl = null)
        {
            return await AdminSign(id, signatureData, returnUrl);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Xác nhận thu tiền kỳ hạn trả góp, xử lý trả thừa/trả thiếu và đồng bộ công nợ
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> ConfirmPayment(
            int maKyHan, 
            decimal soTienThucThu, 
            int hinhThuc, 
            string ghiChu, 
            string? maGiaoDichNganHang = null, 
            string? nganHangNhan = null, 
            DateTime? ngayHenTraTiepTheo = null, 
            string? ghiChuTraThieu = null, 
            string returnUrl = null)
        {
            await _paymentLock.WaitAsync();
            try
            {
                using var tx = await _context.Database.BeginTransactionAsync(System.Data.IsolationLevel.Serializable);
                try
                {
                    var kyHan = await _context.KyHanThanhToans
                        .Include(k => k.HopDong)
                        .FirstOrDefaultAsync(k => k.MaKyHan == maKyHan);

                    if (kyHan == null) return NotFound();

                    if (soTienThucThu <= 0)
                    {
                        TempData["Error"] = "Số tiền thu phải lớn hơn 0!";
                        return RedirectToAction(nameof(Details), new { id = kyHan.MaHopDong, returnUrl = returnUrl });
                    }

                    // Kiểm tra kỳ hạn đã thanh toán trước đó
                    if (kyHan.TrangThai == 1)
                    {
                        TempData["Error"] = "Kỳ hạn này đã được thanh toán hoàn tất trước đó!";
                        return RedirectToAction(nameof(Details), new { id = kyHan.MaHopDong, returnUrl = returnUrl });
                    }

                    // Lấy thông tin nhân viên đang đăng nhập
                    var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
                    int? adminId = (claim != null && int.TryParse(claim.Value, out int aId)) ? aId : null;

                    // Tạo phiếu thu
                    var phieuThu = new PhieuThu
                    {
                        MaHopDong = kyHan.MaHopDong,
                        LoaiPhieu = 0, // Thu thuê kỳ hạn
                        SoTien = soTienThucThu,
                        NgayGiaoDich = DateTime.Now,
                        HinhThucThanhToan = hinhThuc,
                        GhiChu = string.IsNullOrEmpty(ghiChu) ? $"Thu tiền kỳ {kyHan.SoKyHan}" : ghiChu,
                        MaKyHan = kyHan.MaKyHan,
                        MaNhanVienThu = adminId,
                        MaGiaoDichNganHang = maGiaoDichNganHang,
                        NganHangNhan = nganHangNhan,
                        DaHuy = false
                    };
                    _context.PhieuThus.Add(phieuThu);

                    decimal penalty = Math.Max(kyHan.TienPhat, kyHan.PhiPhatTreHan);
                    decimal conThieu = Math.Max(0m, (kyHan.SoTienPhai - kyHan.SoTienDaTra) + penalty);

                    if (soTienThucThu >= conThieu)
                    {
                        kyHan.SoTienDaTra = kyHan.SoTienPhai;
                        kyHan.TrangThai = 1; // Đã trả đủ
                        kyHan.NgayThanhToan = DateTime.Now;
                        kyHan.PhiPhatTreHan = 0;
                        kyHan.TienPhat = 0;
                        kyHan.SoNgayTreHan = 0;

                        decimal tienDu = soTienThucThu - conThieu;
                        if (tienDu > 0)
                        {
                            // Tự động phân bổ số tiền trả thừa sang các kỳ hạn tiếp theo
                            var futureKyHans = await _context.KyHanThanhToans
                                .Where(k => k.MaHopDong == kyHan.MaHopDong && (k.TrangThai == 0 || k.TrangThai == 2) && k.MaKyHan != kyHan.MaKyHan)
                                .OrderBy(k => k.SoKyHan)
                                .ToListAsync();

                            foreach (var nextKy in futureKyHans)
                            {
                                if (tienDu <= 0) break;
                                decimal nextPenalty = Math.Max(nextKy.TienPhat, nextKy.PhiPhatTreHan);
                                decimal nextUnpaid = Math.Max(0m, (nextKy.SoTienPhai - nextKy.SoTienDaTra) + nextPenalty);
                                if (nextUnpaid <= 0)
                                {
                                    nextKy.TrangThai = 1;
                                    nextKy.PhiPhatTreHan = 0;
                                    nextKy.TienPhat = 0;
                                    continue;
                                }

                                if (tienDu >= nextUnpaid)
                                {
                                    nextKy.SoTienDaTra = nextKy.SoTienPhai;
                                    nextKy.TrangThai = 1;
                                    nextKy.NgayThanhToan = DateTime.Now;
                                    nextKy.PhiPhatTreHan = 0;
                                    nextKy.TienPhat = 0;
                                    nextKy.SoNgayTreHan = 0;
                                    nextKy.GhiChu = ((nextKy.GhiChu ?? "") + $" [Cấn trừ {nextUnpaid:N0}đ từ trả thừa kỳ {kyHan.SoKyHan}]").Trim();
                                    tienDu -= nextUnpaid;
                                }
                                else
                                {
                                    nextKy.SoTienDaTra += tienDu;
                                    nextKy.GhiChu = ((nextKy.GhiChu ?? "") + $" [Cấn trừ {tienDu:N0}đ từ trả thừa kỳ {kyHan.SoKyHan}]").Trim();
                                    tienDu = 0;
                                    break;
                                }
                            }

                            if (tienDu > 0)
                            {
                                // Cấn trừ phí bồi thường hư hại bảo trì nếu còn tiền thừa
                                var phieuBaoTris = await _context.PhieuBaoTris
                                    .Where(p => p.MaHopDong == kyHan.MaHopDong)
                                    .ToListAsync();
                                decimal totalDamages = phieuBaoTris.Sum(b => b.PhiDenBu);
                                decimal paidDamages = await _context.PhieuThus
                                    .Where(p => p.MaHopDong == kyHan.MaHopDong && p.LoaiPhieu == 2 && !p.DaHuy)
                                    .SumAsync(p => (decimal?)p.SoTien) ?? 0m;
                                decimal unpaidDamages = Math.Max(0m, totalDamages - paidDamages);

                                if (unpaidDamages > 0)
                                {
                                    decimal damageToPay = Math.Min(tienDu, unpaidDamages);
                                    var phieuThuDamage = new PhieuThu
                                    {
                                        MaHopDong = kyHan.MaHopDong,
                                        LoaiPhieu = 2, // Thu phí đền bù bảo trì
                                        SoTien = damageToPay,
                                        NgayGiaoDich = DateTime.Now,
                                        HinhThucThanhToan = hinhThuc,
                                        GhiChu = $"Cấn trừ {damageToPay:N0}đ phí đền bù từ trả thừa kỳ {kyHan.SoKyHan}",
                                        MaNhanVienThu = adminId,
                                        DaHuy = false
                                    };
                                    _context.PhieuThus.Add(phieuThuDamage);
                                    tienDu -= damageToPay;
                                }

                                if (tienDu > 0)
                                {
                                    kyHan.HopDong.TienTraThua += tienDu;
                                    kyHan.HopDong.GhiChu = ((kyHan.HopDong.GhiChu ?? "") + $" [Khách trả thừa {tienDu:N0}đ cần hoàn trả]").Trim();
                                }
                            }
                        }
                    }
                    else
                    {
                        // Xử lý trường hợp thanh toán một phần (trả thiếu)
                        kyHan.SoTienDaTra += soTienThucThu;
                        kyHan.TrangThai = (kyHan.NgayDenHan.Date < DateTime.Now.Date) ? 2 : 0;
                        if (ngayHenTraTiepTheo.HasValue)
                        {
                            kyHan.NgayHenTraTiepTheo = ngayHenTraTiepTheo;
                            kyHan.GhiChuTraThieu = ghiChuTraThieu;
                            kyHan.GhiChu = ((kyHan.GhiChu ?? "") + $" [Thu {soTienThucThu:N0}đ, hẹn trả tiếp {ngayHenTraTiepTheo:dd/MM/yyyy}]").Trim();
                        }
                        else
                        {
                            kyHan.GhiChu = ((kyHan.GhiChu ?? "") + $" [Thu một phần: {soTienThucThu:N0}đ]").Trim();
                        }
                    }

                    // Đồng bộ lại trạng thái thanh toán của hợp đồng
                    await SyncTrangThaiThanhToanHopDong(kyHan.HopDong, _context);

                    await _context.SaveChangesAsync();
                    await tx.CommitAsync();

                    TempData["Success"] = $"Đã ghi nhận thu {soTienThucThu:N0}đ cho kỳ {kyHan.SoKyHan}!";
                    return RedirectToAction(nameof(Details), new { id = kyHan.MaHopDong, returnUrl = returnUrl });
                }
                catch (Exception)
                {
                    await tx.RollbackAsync();
                    throw;
                }
            }
            finally
            {
                _paymentLock.Release();
            }
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Hủy phiếu thu, hoàn tác công nợ kỳ hạn và đồng bộ trạng thái hợp đồng
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> HuyPhieuThu(int maPhieuThu, string lyDoHuy, string returnUrl = null)
        {
            if (string.IsNullOrWhiteSpace(lyDoHuy))
            {
                TempData["Error"] = "Vui lòng nhập lý do hủy phiếu thu!";
                return RedirectToAction(nameof(Index));
            }

            var pt = await _context.PhieuThus
                .Include(p => p.HopDong)
                .Include(p => p.KyHanThanhToan)
                .FirstOrDefaultAsync(p => p.MaPhieuThu == maPhieuThu);

            if (pt == null) return NotFound();

            if (pt.DaHuy)
            {
                TempData["Error"] = "Phiếu thu này đã bị hủy trước đó!";
                return RedirectToAction(nameof(Details), new { id = pt.MaHopDong, returnUrl = returnUrl });
            }

            pt.DaHuy = true;
            pt.LyDoHuy = lyDoHuy.Trim();
            pt.NgayHuy = DateTime.Now;

            // Hoàn tác số tiền đã thu
            if (pt.MaKyHan.HasValue && pt.KyHanThanhToan != null)
            {
                var kyHan = pt.KyHanThanhToan;
                kyHan.SoTienDaTra = Math.Max(0, kyHan.SoTienDaTra - pt.SoTien);
                if (kyHan.SoTienDaTra < kyHan.SoTienPhai)
                {
                    if (kyHan.NgayDenHan.Date < DateTime.Now.Date)
                    {
                        kyHan.TrangThai = 2; // Quá hạn
                        var days = (DateTime.Now.Date - kyHan.NgayDenHan.Date).Days;
                        kyHan.SoNgayTreHan = days;
                        if (days > 3)
                        {
                            kyHan.PhiPhatTreHan = Math.Round((kyHan.SoTienPhai - kyHan.SoTienDaTra) * 0.001m * days, 0);
                        }
                    }
                    else
                    {
                        kyHan.TrangThai = 0; // Chưa thanh toán
                    }
                    kyHan.NgayThanhToan = null;
                }
                kyHan.GhiChu = ((kyHan.GhiChu ?? "") + $" [Hủy phiếu #{maPhieuThu}: {lyDoHuy.Trim()}]").Trim();
            }
            else if (pt.LoaiPhieu == 1) // Thu cọc
            {
                pt.HopDong.TienDaCoc = Math.Max(0, pt.HopDong.TienDaCoc - pt.SoTien);
            }

            await SyncTrangThaiThanhToanHopDong(pt.HopDong, _context);
            await _context.SaveChangesAsync();

            TempData["Success"] = $"Đã hủy phiếu thu #{maPhieuThu} và hoàn tác công nợ thành công!";
            return RedirectToAction(nameof(Details), new { id = pt.MaHopDong, returnUrl = returnUrl });
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Tất toán sớm toàn bộ các kỳ hạn còn lại
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> TatToanSom(int maHopDong, int hinhThuc = 0, string ghiChu = null, string maGiaoDichNganHang = null, string returnUrl = null)
        {
            var hopDong = await _context.HopDongs
                .Include(h => h.KyHanThanhToans)
                .FirstOrDefaultAsync(h => h.MaHopDong == maHopDong);

            if (hopDong == null) return NotFound();

            var openKyHans = hopDong.KyHanThanhToans
                .Where(k => k.TrangThai != 1 && k.TrangThai != 3)
                .OrderBy(k => k.SoKyHan)
                .ToList();

            if (!openKyHans.Any())
            {
                TempData["Error"] = "Hợp đồng không còn kỳ hạn nào cần thanh toán!";
                return RedirectToAction(nameof(Details), new { id = maHopDong, returnUrl = returnUrl });
            }

            decimal tongConNo = openKyHans.Sum(k => (k.SoTienPhai - k.SoTienDaTra) + k.PhiPhatTreHan);
            if (tongConNo <= 0)
            {
                TempData["Error"] = "Số tiền còn nợ bằng 0, không cần tất toán!";
                return RedirectToAction(nameof(Details), new { id = maHopDong, returnUrl = returnUrl });
            }

            var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            int? adminId = (claim != null && int.TryParse(claim.Value, out int aId)) ? aId : null;

            var phieuThu = new PhieuThu
            {
                MaHopDong = maHopDong,
                LoaiPhieu = 0, // Thu thuê kỳ hạn
                SoTien = tongConNo,
                NgayGiaoDich = DateTime.Now,
                HinhThucThanhToan = hinhThuc,
                GhiChu = string.IsNullOrEmpty(ghiChu) ? "Tất toán sớm toàn bộ các kỳ hạn còn lại" : ghiChu,
                MaNhanVienThu = adminId,
                MaGiaoDichNganHang = maGiaoDichNganHang,
                DaHuy = false
            };
            _context.PhieuThus.Add(phieuThu);

            foreach (var k in openKyHans)
            {
                k.SoTienDaTra = k.SoTienPhai;
                k.TrangThai = 1;
                k.NgayThanhToan = DateTime.Now;
                k.PhiPhatTreHan = 0;
                k.SoNgayTreHan = 0;
                k.GhiChu = ((k.GhiChu ?? "") + " [Tất toán sớm]").Trim();
            }

            await SyncTrangThaiThanhToanHopDong(hopDong, _context);
            await _context.SaveChangesAsync();

            TempData["Success"] = $"Đã tất toán toàn bộ các kỳ hạn thành công với số tiền {tongConNo:N0}đ!";
            return RedirectToAction(nameof(Details), new { id = maHopDong, returnUrl = returnUrl });
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Điều chỉnh ngày đến hạn của kỳ hạn chưa thanh toán
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> DieuChinhKyHan(int maKyHan, DateTime ngayDenHanMoi, string lyDo, string returnUrl = null)
        {
            var kyHan = await _context.KyHanThanhToans.FindAsync(maKyHan);
            if (kyHan == null) return NotFound();

            if (kyHan.TrangThai == 1)
            {
                TempData["Error"] = "Không thể điều chỉnh kỳ hạn đã thanh toán hoàn tất!";
                return RedirectToAction(nameof(Details), new { id = kyHan.MaHopDong, returnUrl = returnUrl });
            }

            if (string.IsNullOrWhiteSpace(lyDo))
            {
                TempData["Error"] = "Vui lòng nhập lý do điều chỉnh hạn!";
                return RedirectToAction(nameof(Details), new { id = kyHan.MaHopDong, returnUrl = returnUrl });
            }

            kyHan.NgayDenHan = ngayDenHanMoi.Date;
            if (ngayDenHanMoi.Date >= DateTime.Now.Date)
            {
                kyHan.TrangThai = 0; // Hết quá hạn
                kyHan.PhiPhatTreHan = 0;
                kyHan.SoNgayTreHan = 0;
            }
            kyHan.GhiChu = ((kyHan.GhiChu ?? "") + $" [Dời hạn sang {ngayDenHanMoi:dd/MM/yyyy}: {lyDo.Trim()}]").Trim();

            await _context.SaveChangesAsync();
            TempData["Success"] = $"Đã cập nhật ngày đến hạn mới cho kỳ #{kyHan.SoKyHan} thành công!";
            return RedirectToAction(nameof(Details), new { id = kyHan.MaHopDong, returnUrl = returnUrl });
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Lập phiếu thu phí bảo trì / đền bù hư hỏng (LoaiPhieu = 2)
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> ThuPhiBaoTri(int maHopDong, decimal soTien, int hinhThuc = 0, string ghiChu = null, string returnUrl = null)
        {
            var hopDong = await _context.HopDongs.FindAsync(maHopDong);
            if (hopDong == null) return NotFound();

            // Kiểm tra số tiền hợp lệ
            if (soTien <= 0)
            {
                TempData["Error"] = "Số tiền thu phí bảo trì phải lớn hơn 0!";
                return RedirectToAction(nameof(Details), new { id = maHopDong, returnUrl = returnUrl });
            }

            var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            int? adminId = (claim != null && int.TryParse(claim.Value, out int aId)) ? aId : null;

            var phieuThu = new PhieuThu
            {
                MaHopDong = maHopDong,
                LoaiPhieu = 2, // 2: Thu phí BT / đền bù
                SoTien = soTien,
                NgayGiaoDich = DateTime.Now,
                HinhThucThanhToan = hinhThuc,
                GhiChu = string.IsNullOrEmpty(ghiChu) ? "Thu phí đền bù / sửa chữa thiết bị" : ghiChu,
                MaNhanVienThu = adminId,
                DaHuy = false
            };

            _context.PhieuThus.Add(phieuThu);
            await SyncTrangThaiThanhToanHopDong(hopDong, _context);
            await _context.SaveChangesAsync();

            TempData["Success"] = $"Đã lập phiếu thu {soTien:N0}đ phí bảo trì/đền bù thành công!";
            return RedirectToAction(nameof(Details), new { id = maHopDong, returnUrl = returnUrl });
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Thu thêm tiền cọc bổ sung cho hợp đồng đang hoạt động.
        // Khấu trừ dần vào các kỳ hạn nợ và sinh PhieuThu (LoaiPhieu = 0)
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> ThemTienCoc(int maHopDong, decimal soTienCoc, int hinhThuc, string ghiChu, string returnUrl = null)
        {
            var hopDong = await _context.HopDongs
                .Include(h => h.KyHanThanhToans)
                .Include(h => h.PhieuBaoTris)
                .Include(h => h.PhieuThus)
                .FirstOrDefaultAsync(h => h.MaHopDong == maHopDong);
            if (hopDong == null) return NotFound();

            if (soTienCoc <= 0)
            {
                TempData["Error"] = "Số tiền cọc phải lớn hơn 0!";
                return RedirectToAction(nameof(Details), new { id = maHopDong, returnUrl = returnUrl });
            }

            // Tính công nợ hợp đồng qua DebtCalculationHelper
            var (totalReceivable, totalCollected, remainingDebt) = DebtCalculationHelper.CalculateContractDebt(hopDong);
            decimal conLai = remainingDebt;
            if (conLai <= 0)
            {
                TempData["Error"] = "Hợp đồng đã được thanh toán đầy đủ, không thể thu thêm cọc!";
                return RedirectToAction(nameof(Details), new { id = maHopDong, returnUrl = returnUrl });
            }
            if (soTienCoc > conLai)
            {
                TempData["Error"] = $"Số tiền cọc bổ sung ({soTienCoc:N0}đ) vượt quá số tiền còn nợ ({conLai:N0}đ)!";
                return RedirectToAction(nameof(Details), new { id = maHopDong, returnUrl = returnUrl });
            }

            // Cộng tiền cọc vào hợp đồng
            hopDong.TienDaCoc += soTienCoc;

            var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            int? adminId = (claim != null && int.TryParse(claim.Value, out int aId)) ? aId : null;

            // Tạo phiếu thu tiền cọc bổ sung khấu trừ công nợ kỳ hạn (LoaiPhieu = 0)
            var phieuCoc = new PhieuThu
            {
                MaHopDong = maHopDong,
                LoaiPhieu = 0, // Thu tiền cọc bổ sung khấu trừ công nợ kỳ hạn
                SoTien = soTienCoc,
                NgayGiaoDich = DateTime.Now,
                HinhThucThanhToan = hinhThuc,
                GhiChu = string.IsNullOrEmpty(ghiChu) ? "Thu tiền cọc bổ sung" : ghiChu,
                MaNhanVienThu = adminId,
                DaHuy = false
            };
            _context.PhieuThus.Add(phieuCoc);

            // Cập nhật lại các kỳ hạn nợ (giữ nguyên số tiền phải thu ban đầu)
            var kyHans = await _context.KyHanThanhToans
                .Where(k => k.MaHopDong == maHopDong && (k.TrangThai == 0 || k.TrangThai == 2))
                .OrderBy(k => k.SoKyHan)
                .ToListAsync();

            if (kyHans.Any())
            {
                decimal remainingDeposit = soTienCoc;
                foreach (var k in kyHans)
                {
                    if (remainingDeposit <= 0) break;
                    decimal unpaidInPeriod = Math.Max(0m, k.SoTienPhai - k.SoTienDaTra);
                    if (unpaidInPeriod <= 0)
                    {
                        k.TrangThai = 1;
                        continue;
                    }

                    decimal allocatedDeposit = Math.Min(remainingDeposit, unpaidInPeriod);
                    k.SoTienDaTra += allocatedDeposit;
                    remainingDeposit -= allocatedDeposit;

                    if (k.SoTienDaTra >= k.SoTienPhai)
                    {
                        k.TrangThai = 1; // Đã thanh toán
                        k.NgayThanhToan = DateTime.Now;
                        k.PhiPhatTreHan = 0;
                        k.TienPhat = 0;
                        k.SoNgayTreHan = 0;
                    }
                    k.GhiChu = ((k.GhiChu ?? "") + $" (Cấn trừ từ cọc bổ sung: +{allocatedDeposit:N0} đ)").Trim();
                }

                await SyncTrangThaiThanhToanHopDong(hopDong, _context);
            }
            else if (hopDong.TienDaCoc >= hopDong.TongTien)
            {
                hopDong.TrangThaiThanhToan = 3; // Đã tất toán đủ
            }

            await _context.SaveChangesAsync();
            TempData["Success"] = $"Đã ghi nhận thu cọc bổ sung {soTienCoc:N0}đ thành công!";
            return RedirectToAction(nameof(Details), new { id = maHopDong, returnUrl = returnUrl });
        }

        [HttpGet]
        // Quản lý và duyệt yêu cầu gia hạn hợp đồng
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> YeuCauGiaHan(int? status)
        {
            var query = _context.YeuCauGiaHans
                .Include(y => y.HopDong)
                    .ThenInclude(h => h!.KhachHang)
                .Include(y => y.NguoiDuyet)
                .AsQueryable();

            if (status.HasValue)
            {
                query = query.Where(y => y.TrangThai == status.Value);
            }

            var list = await query.OrderByDescending(y => y.NgayYeuCau).ToListAsync();
            ViewBag.CurrentStatus = status;
            ViewBag.AllCount = await _context.YeuCauGiaHans.CountAsync();
            ViewBag.PendingCount = await _context.YeuCauGiaHans.CountAsync(y => y.TrangThai == 0);
            ViewBag.ApprovedCount = await _context.YeuCauGiaHans.CountAsync(y => y.TrangThai == 1);
            ViewBag.RejectedCount = await _context.YeuCauGiaHans.CountAsync(y => y.TrangThai == 2);
            return View(list);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Phê duyệt hoặc từ chối yêu cầu gia hạn hợp đồng
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> DuyetGiaHan(int id, bool chapNhan, string ghiChu = null, string returnUrl = null)
        {
            var hopDong = await _context.HopDongs.FindAsync(id);

            if (hopDong == null) return NotFound();

            if (hopDong.TrangThai != 1)
            {
                TempData["Error"] = "Chỉ có thể duyệt gia hạn cho hợp đồng đang cho thuê!";
                if (!string.IsNullOrEmpty(returnUrl) && Url.IsLocalUrl(returnUrl)) return Redirect(returnUrl);
                return RedirectToAction(nameof(Details), new { id = id });
            }

            // Tìm yêu cầu gia hạn chờ duyệt mới nhất cho hợp đồng này
            var pendingYc = await _context.YeuCauGiaHans
                .Where(y => y.MaHopDong == id && y.TrangThai == 0)
                .OrderByDescending(y => y.NgayYeuCau)
                .FirstOrDefaultAsync();

            int soNgayGiaHan = hopDong.SoNgayGiaHan ?? pendingYc?.SoNgayGiaHan ?? 0;

            if ((!hopDong.YeuCauGiaHan && pendingYc == null) || soNgayGiaHan <= 0)
            {
                TempData["Error"] = "Không tìm thấy yêu cầu gia hạn hợp lệ!";
                if (!string.IsNullOrEmpty(returnUrl) && Url.IsLocalUrl(returnUrl)) return Redirect(returnUrl);
                return RedirectToAction(nameof(Details), new { id = id });
            }

            var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            int? adminId = (claim != null && int.TryParse(claim.Value, out int aId)) ? aId : null;

            if (chapNhan)
            {
                DateTime extStart = hopDong.NgayKetThuc.Date;
                DateTime extEnd = hopDong.NgayKetThuc.Date.AddDays(soNgayGiaHan);

                // Kiểm tra trùng lịch thiết bị trong thời gian gia hạn
                var chiTiets = await _context.ChiTietHopDongs.Where(c => c.MaHopDong == id).ToListAsync();
                foreach (var ct in chiTiets)
                {
                    bool conflict = await _context.ChiTietHopDongs.AnyAsync(other =>
                        other.MaHopDong != id &&
                        other.MaThietBi == ct.MaThietBi &&
                        other.HopDong.TrangThai != 2 && other.HopDong.TrangThai != 3 &&
                        other.HopDong.NgayBatDau.Date < extEnd &&
                        other.HopDong.NgayKetThuc.Date > extStart);

                    if (conflict)
                    {
                        TempData["Error"] = $"Không thể gia hạn: Thiết bị #{ct.MaThietBi} đã có đơn hàng khác đặt trước trong khoảng thời gian gia hạn!";
                        if (!string.IsNullOrEmpty(returnUrl) && Url.IsLocalUrl(returnUrl)) return Redirect(returnUrl);
                        return RedirectToAction(nameof(Details), new { id = id });
                    }
                }

                int originalDays = Math.Max(1, (int)(hopDong.NgayKetThuc.Date - hopDong.NgayBatDau.Date).TotalDays);
                decimal dailyRate = hopDong.TongTien / originalDays;
                decimal additionalRent = Math.Round((dailyRate * soNgayGiaHan) / 1000m) * 1000m;

                hopDong.NgayKetThuc = extEnd;
                hopDong.TongTien += additionalRent;

                // Tạo kỳ hạn thanh toán mới cho phần tiền gia hạn
                int nextKy = (await _context.KyHanThanhToans.CountAsync(k => k.MaHopDong == id)) + 1;
                var newKyHan = new KyHanThanhToan
                {
                    MaHopDong = id,
                    SoKyHan = nextKy,
                    NgayDenHan = extStart,
                    SoTienPhai = additionalRent,
                    SoTienDaTra = 0,
                    TrangThai = 0,
                    GhiChu = $"Gia hạn thêm {soNgayGiaHan} ngày (Từ {extStart:dd/MM/yyyy} đến {extEnd:dd/MM/yyyy})"
                };
                _context.KyHanThanhToans.Add(newKyHan);

                hopDong.SoKyHan = nextKy;
                hopDong.TrangThaiThanhToan = 1; // Có công nợ mới
                hopDong.TrangThaiGiaHan = 1; // Đã duyệt
                hopDong.YeuCauGiaHan = false;
                if (!string.IsNullOrEmpty(ghiChu))
                {
                    hopDong.GhiChu = (hopDong.GhiChu ?? "") + $" [Duyệt gia hạn: {ghiChu}]";
                }

                if (pendingYc != null)
                {
                    pendingYc.TrangThai = 1; // 1: Đã duyệt
                    pendingYc.NgayDuyet = DateTime.Now;
                    pendingYc.MaNguoiDuyet = adminId;
                    pendingYc.ChiPhiPhatSinh = additionalRent;
                    pendingYc.GhiChuAdmin = ghiChu;
                }

                TempData["Success"] = $"Đã duyệt gia hạn thêm {soNgayGiaHan} ngày thành công! Sinh kỳ hạn thanh toán #{nextKy} với số tiền {additionalRent:N0} đ.";
            }
            else
            {
                hopDong.TrangThaiGiaHan = 2; // Từ chối
                hopDong.YeuCauGiaHan = false;
                if (!string.IsNullOrEmpty(ghiChu))
                {
                    hopDong.GhiChu = (hopDong.GhiChu ?? "") + $" [Từ chối gia hạn: {ghiChu}]";
                }

                if (pendingYc != null)
                {
                    pendingYc.TrangThai = 2; // 2: Từ chối
                    pendingYc.NgayDuyet = DateTime.Now;
                    pendingYc.MaNguoiDuyet = adminId;
                    pendingYc.GhiChuAdmin = ghiChu;
                }

                TempData["Success"] = "Đã từ chối yêu cầu gia hạn hợp đồng.";
            }

            await _context.SaveChangesAsync();
            if (!string.IsNullOrEmpty(returnUrl) && Url.IsLocalUrl(returnUrl)) return Redirect(returnUrl);
            return RedirectToAction(nameof(Details), new { id = id });
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Trả máy trước hạn và thanh lý hợp đồng sớm
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> TraMayTruocHan(int id, DateTime ngayTraThucTe, decimal phiPhatTraSom, int hinhThucHoanCoc = 1, string ghiChu = null)
        {
            var hopDong = await _context.HopDongs.FindAsync(id);
            if (hopDong == null) return NotFound();

            if (hopDong.TrangThai != 1)
            {
                TempData["Error"] = "Chỉ có thể thanh lý trước hạn hợp đồng đang cho thuê!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            // Chặn thanh lý sớm nếu còn phiếu bảo trì chưa đóng
            bool coPhieuDangXuLy = await _context.PhieuBaoTris
                .AnyAsync(p => p.MaHopDong == id && (p.TrangThai == 1 || p.TrangThai == 2));
            if (coPhieuDangXuLy)
            {
                TempData["Error"] = "CẢNH BÁO: Hợp đồng còn phiếu bảo trì chưa xử lý xong. Vui lòng hoàn tất phiếu bảo trì trước khi thanh lý sớm!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            if (ngayTraThucTe.Date < hopDong.NgayBatDau.Date)
            {
                TempData["Error"] = "Ngày trả thực tế không thể trước ngày bắt đầu thuê!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            if (ngayTraThucTe.Date > hopDong.NgayKetThuc.Date)
            {
                TempData["Error"] = "Ngày trả sớm không thể lớn hơn ngày kết thúc hợp đồng!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            if (phiPhatTraSom < 0) phiPhatTraSom = 0;

            int originalDays = Math.Max(1, (int)(hopDong.NgayKetThuc.Date - hopDong.NgayBatDau.Date).TotalDays);
            int actualDays = Math.Max(1, (int)(ngayTraThucTe.Date - hopDong.NgayBatDau.Date).TotalDays);

            decimal dailyRate = hopDong.TongTien / originalDays;
            decimal actualRentalFee = Math.Round((dailyRate * actualDays) / 1000m) * 1000m;
            decimal totalActualObligation = actualRentalFee + phiPhatTraSom;

            // Hủy các kỳ hạn chưa trả trong tương lai
            var futureKyHans = await _context.KyHanThanhToans
                .Where(k => k.MaHopDong == id && k.TrangThai != 1)
                .ToListAsync();
            foreach (var k in futureKyHans)
            {
                k.TrangThai = 3; // Hủy
                k.GhiChu = (k.GhiChu ?? "") + " [Hủy do thanh lý trước hạn]";
            }

            decimal rentPaid = await _context.PhieuThus
                .Where(p => p.MaHopDong == id && p.LoaiPhieu == 0)
                .SumAsync(p => (decimal?)p.SoTien) ?? 0m;

            decimal damages = await _context.PhieuBaoTris
                .Where(p => p.MaHopDong == id)
                .SumAsync(p => (decimal?)p.PhiDenBu) ?? 0m;
            decimal paidDamages = await _context.PhieuThus
                .Where(p => p.MaHopDong == id && p.LoaiPhieu == 2)
                .SumAsync(p => (decimal?)p.SoTien) ?? 0m;
            decimal unpaidDamages = damages > paidDamages ? (damages - paidDamages) : 0m;

            decimal totalCredits = rentPaid + hopDong.TienDaCoc;
            decimal netRefund = totalCredits - totalActualObligation - unpaidDamages;

            var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            int adminId = (claim != null && int.TryParse(claim.Value, out int aId)) ? aId : hopDong.MaNhanVien;

            if (netRefund > 0)
            {
                var phieuChi = new PhieuChi
                {
                    MaHopDong = id,
                    LoaiChi = 0,
                    SoTien = netRefund,
                    NgayChi = DateTime.Now,
                    HinhThucChi = hinhThucHoanCoc,
                    MaNhanVienChi = adminId,
                    GhiChu = $"Quyết toán thanh lý hợp đồng trước hạn ({actualDays}/{originalDays} ngày). Tiền thuê thực tế: {actualRentalFee:N0} đ, phạt sớm: {phiPhatTraSom:N0} đ, bồi thường: {unpaidDamages:N0} đ. {ghiChu}"
                };
                _context.PhieuChis.Add(phieuChi);
                hopDong.TrangThaiHoanCoc = 1;
                hopDong.TienCocThucHoan = netRefund;
                hopDong.NgayHoanCoc = DateTime.Now;
                hopDong.GhiChuHoanCoc = phieuChi.GhiChu;
            }
            else
            {
                hopDong.TrangThaiHoanCoc = 2; // Đã cấn trừ hết cọc
                hopDong.TienCocThucHoan = 0;
                hopDong.NgayHoanCoc = DateTime.Now;
                hopDong.GhiChuHoanCoc = "Cọc đã được cấn trừ toàn bộ cho chi phí thuê thực tế.";
            }

            hopDong.TongTien = totalActualObligation;
            hopDong.NgayKetThuc = ngayTraThucTe.Date;
            hopDong.TrangThai = 2; // Hoàn tất
            hopDong.TrangThaiThanhToan = 2;

            // Giải phóng thiết bị về kho (giữ nguyên thiết bị hỏng ở trạng thái thanh lý)
            var chiTiets = await _context.ChiTietHopDongs.Where(c => c.MaHopDong == id).ToListAsync();
            foreach (var ct in chiTiets)
            {
                var tb = await _context.ThietBis.FindAsync(ct.MaThietBi);
                if (tb != null)
                {
                    bool isBroken = tb.TrangThai == 4 || await _context.PhieuBaoTris.AnyAsync(p => p.MaThietBi == tb.MaThietBi && p.TrangThai == 4);
                    if (isBroken)
                    {
                        tb.TrangThai = 4;
                        tb.TinhTrangMay = "Hỏng không thể khắc phục (Thanh lý)";
                        _context.LichSuThietBis.Add(new LichSuThietBi
                        {
                            MaThietBi = tb.MaThietBi,
                            HanhDong = $"Thanh lý sớm HĐ #{id}: Thiết bị hỏng không thể khắc phục, giữ nguyên trạng thái thanh lý (TrangThai = 4)",
                            ThoiGian = DateTime.Now,
                            MaNguoiThucHien = adminId,
                            GhiChu = $"Thanh lý trước hạn HĐ #{id}"
                        });
                    }
                    else
                    {
                        tb.TrangThai = 0;
                        _context.LichSuThietBis.Add(new LichSuThietBi
                        {
                            MaThietBi = tb.MaThietBi,
                            HanhDong = $"Thanh lý sớm HĐ #{id}: Thu hồi nhập kho sẵn sàng cho thuê (TrangThai = 0)",
                            ThoiGian = DateTime.Now,
                            MaNguoiThucHien = adminId,
                            GhiChu = $"Thanh lý trước hạn HĐ #{id}"
                        });
                    }
                }
            }

            // Tự động lập biên bản thu hồi máy trước hạn
            var bbThuHoi = new BienBanBanGiao
            {
                MaHopDong = id,
                LoaiBienBan = 1,
                NgayLap = DateTime.Now,
                MaNhanVienLap = adminId,
                PhuKienKemTheo = "Đầy đủ phụ kiện thu hồi trước hạn",
                TinhTrangNgoaiQuan = "Đã kiểm tra thu hồi máy trước hạn an toàn",
                GhiChu = $"Thanh lý sớm ngày {ngayTraThucTe:dd/MM/yyyy}. {ghiChu}"
            };
            _context.BienBanBanGiaos.Add(bbThuHoi);

            await _context.SaveChangesAsync();
            TempData["Success"] = $"Đã thanh lý hợp đồng trước hạn thành công! Ngày thuê thực tế: {actualDays}/{originalDays} ngày. Hoàn lại cho khách: {Math.Max(0, netRefund):N0} đ.";
            return RedirectToAction(nameof(Details), new { id = id });
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Lập Biên bản bàn giao thiết bị xuất/nhập kho kèm ảnh chụp và phụ kiện
        public async Task<IActionResult> LapBienBanBanGiao(int maHopDong, int loaiBienBan, string phuKienKemTheo, string tinhTrangNgoaiQuan, string ghiChu, Microsoft.AspNetCore.Http.IFormFile hinhAnh1 = null, Microsoft.AspNetCore.Http.IFormFile hinhAnh2 = null, Microsoft.AspNetCore.Http.IFormFile hinhAnh3 = null, Microsoft.AspNetCore.Http.IFormFile hinhAnh4 = null)
        {
            var hopDong = await _context.HopDongs.FindAsync(maHopDong);
            if (hopDong == null) return NotFound();

            var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            int adminId = (claim != null && int.TryParse(claim.Value, out int aId)) ? aId : hopDong.MaNhanVien;

            string uploadFolder = System.IO.Path.Combine(_env.WebRootPath, "uploads", "bienban");
            if (!System.IO.Directory.Exists(uploadFolder)) System.IO.Directory.CreateDirectory(uploadFolder);

            async Task<string?> SavePhotoAsync(Microsoft.AspNetCore.Http.IFormFile? file, string suffix)
            {
                if (file == null || file.Length == 0) return null;
                var ext = System.IO.Path.GetExtension(file.FileName).ToLower();
                string fileName = $"bb_{maHopDong}_{suffix}_{DateTime.Now.Ticks}{ext}";
                string filePath = System.IO.Path.Combine(uploadFolder, fileName);
                using (var stream = new System.IO.FileStream(filePath, System.IO.FileMode.Create))
                {
                    await file.CopyToAsync(stream);
                }
                return $"/uploads/bienban/{fileName}";
            }

            var bb = new BienBanBanGiao
            {
                MaHopDong = maHopDong,
                LoaiBienBan = loaiBienBan,
                NgayLap = DateTime.Now,
                MaNhanVienLap = adminId,
                PhuKienKemTheo = phuKienKemTheo ?? "Sạc nguồn, chuột, túi chống sốc",
                TinhTrangNgoaiQuan = tinhTrangNgoaiQuan ?? "Hoạt động bình thường",
                GhiChu = ghiChu,
                HinhAnh1 = await SavePhotoAsync(hinhAnh1, "1"),
                HinhAnh2 = await SavePhotoAsync(hinhAnh2, "2"),
                HinhAnh3 = await SavePhotoAsync(hinhAnh3, "3"),
                HinhAnh4 = await SavePhotoAsync(hinhAnh4, "4")
            };

            _context.BienBanBanGiaos.Add(bb);
            await _context.SaveChangesAsync();

            TempData["Success"] = $"Đã lập biên bản {(loaiBienBan == 0 ? "bàn giao xuất kho" : "thu hồi nhập kho")} thành công!";
            return RedirectToAction(nameof(Details), new { id = maHopDong });
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Duyệt hoặc từ chối biên lai chuyển khoản ngân hàng của khách
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> DuyetBienLai(int maKyHan, bool chapNhan, string ghiChu = null, string returnUrl = null)
        {
            var kyHan = await _context.KyHanThanhToans
                .Include(k => k.HopDong)
                .FirstOrDefaultAsync(k => k.MaKyHan == maKyHan);

            if (kyHan == null) return NotFound();

            if (chapNhan)
            {
                var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
                int? adminId = (claim != null && int.TryParse(claim.Value, out int aId)) ? aId : null;

                kyHan.TrangThaiXacNhan = 2; // Đã duyệt
                kyHan.SoTienDaTra = kyHan.SoTienPhai;
                kyHan.TrangThai = 1; // Đã trả
                kyHan.NgayThanhToan = DateTime.Now;
                kyHan.PhiPhatTreHan = 0;
                kyHan.SoNgayTreHan = 0;

                var phieuThu = new PhieuThu
                {
                    MaHopDong = kyHan.MaHopDong,
                    LoaiPhieu = 0,
                    SoTien = kyHan.SoTienPhai,
                    NgayGiaoDich = DateTime.Now,
                    HinhThucThanhToan = 1, // Chuyển khoản
                    GhiChu = $"Duyệt thanh toán kỳ #{kyHan.SoKyHan} qua chuyển khoản (Mã GD: {kyHan.MaGiaoDichChuyenKhoan ?? "N/A"})",
                    MaKyHan = kyHan.MaKyHan,
                    MaNhanVienThu = adminId,
                    MaGiaoDichNganHang = kyHan.MaGiaoDichChuyenKhoan,
                    NganHangNhan = "MBBank",
                    DaHuy = false
                };
                _context.PhieuThus.Add(phieuThu);

                await SyncTrangThaiThanhToanHopDong(kyHan.HopDong, _context);

                TempData["Success"] = $"Đã duyệt biên lai và xác nhận thanh toán kỳ #{kyHan.SoKyHan} thành công!";
            }
            else
            {
                kyHan.TrangThaiXacNhan = 0; // Từ chối, đưa về 0 để khách gửi lại
                kyHan.GhiChu = (kyHan.GhiChu ?? "") + $" [Biên lai bị từ chối: {ghiChu}]";
                TempData["Success"] = "Đã từ chối biên lai chuyển khoản của khách hàng.";
            }

            await _context.SaveChangesAsync();
            return RedirectToAction(nameof(Details), new { id = kyHan.MaHopDong, returnUrl = returnUrl });
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Lập phiếu chi hoàn tiền cọc
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> HoanCoc(int id, decimal soTienHoan, int hinhThucChi = 1, string maGiaoDich = null, string ghiChu = null)
        {
            var hopDong = await _context.HopDongs.FindAsync(id);
            if (hopDong == null) return NotFound();

            if (soTienHoan <= 0)
            {
                TempData["Error"] = "Số tiền hoàn cọc phải lớn hơn 0!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            int adminId = (claim != null && int.TryParse(claim.Value, out int aId)) ? aId : hopDong.MaNhanVien;

            var phieuChi = new PhieuChi
            {
                MaHopDong = id,
                LoaiChi = 0,
                SoTien = soTienHoan,
                NgayChi = DateTime.Now,
                HinhThucChi = hinhThucChi,
                MaNhanVienChi = adminId,
                MaGiaoDichNganHang = maGiaoDich,
                GhiChu = string.IsNullOrEmpty(ghiChu) ? "Hoàn tiền cọc cho khách hàng" : ghiChu
            };

            _context.PhieuChis.Add(phieuChi);
            hopDong.TrangThaiHoanCoc = 1;
            hopDong.TienCocThucHoan = soTienHoan;
            hopDong.NgayHoanCoc = DateTime.Now;
            hopDong.GhiChuHoanCoc = phieuChi.GhiChu;

            await SyncTrangThaiThanhToanHopDong(hopDong, _context);
            await _context.SaveChangesAsync();
            TempData["Success"] = $"Đã lập phiếu chi hoàn tiền cọc {soTienHoan:N0} đ thành công!";
            return RedirectToAction(nameof(Details), new { id = id });
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        // Quét thủ công giải phóng thiết bị các đơn hàng quá hạn giữ chỗ
        [Authorize(Roles = "Admin,KinhDoanh")]
        public async Task<IActionResult> QuetDonQuaHanGiuCho()
        {
            var now = DateTime.Now;
            var expiredContracts = await _context.HopDongs
                .Where(h => h.TrangThai == 0 && h.HanChotKy != null && h.HanChotKy < now && string.IsNullOrEmpty(h.ChuKyKhachHang) && h.TienDaCoc == 0)
                .ToListAsync();

            int count = 0;
            foreach (var hd in expiredContracts)
            {
                hd.TrangThai = 3;
                hd.GhiChu = (hd.GhiChu ?? "") + " [Tự động hủy do quá hạn giữ chỗ 24h]";

                var chiTiets = await _context.ChiTietHopDongs.Where(c => c.MaHopDong == hd.MaHopDong).ToListAsync();
                foreach (var ct in chiTiets)
                {
                    var tb = await _context.ThietBis.FindAsync(ct.MaThietBi);
                    if (tb != null && tb.TrangThai == 3)
                    {
                        tb.TrangThai = 0;
                    }
                }
                count++;
            }

            await _context.SaveChangesAsync();
            TempData["Success"] = $"Đã quét và giải phóng thành công {count} đơn hàng quá hạn giữ chỗ về kho!";
            return RedirectToAction(nameof(Index));
        }
    }
}
