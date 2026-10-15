using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using RentalSystem.Models;
using RentalSystem.Helpers;
using RentalSystem.Common;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using System;
using Microsoft.EntityFrameworkCore;

namespace RentalSystem.Controllers
{
    public class CartController : Controller
    {
        public static readonly SemaphoreSlim InventoryLock = new SemaphoreSlim(1, 1);
        private readonly ApplicationDbContext _context;
        private readonly Microsoft.AspNetCore.Hosting.IWebHostEnvironment _env;

        public CartController(ApplicationDbContext context, Microsoft.AspNetCore.Hosting.IWebHostEnvironment env)
        {
            _context = context;
            _env = env;
        }

        public async Task<IActionResult> Index()
        {
            var cart = HttpContext.Session.Get<List<CartItem>>("GioHang") ?? new List<CartItem>();
            
            // Đồng bộ lại Giá thuê và Tên sản phẩm mới nhất từ CSDL vào Session
            if (cart.Any())
            {
                bool modified = false;
                foreach (var item in cart)
                {
                    var dbProd = await _context.SanPhams.FindAsync(item.MaSanPham);
                    if (dbProd != null)
                    {
                        if (item.GiaThueNgay != dbProd.GiaThueNgay || item.TenSanPham != dbProd.TenSanPham)
                        {
                            item.GiaThueNgay = dbProd.GiaThueNgay;
                            item.TenSanPham = dbProd.TenSanPham;
                            modified = true;
                        }
                    }
                }
                if (modified) HttpContext.Session.Set("GioHang", cart);
            }

            return View(cart);
        }

        public async Task<IActionResult> AddToCart(int id)
        {
            var product = await _context.SanPhams.FindAsync(id);
            if (product == null) return NotFound();

            // Kiểm tra tồn kho khả dụng trước khi thêm vào giỏ (loại trừ máy đang bảo trì)
            int available = await _context.ThietBis.CountAsync(t => t.MaSanPham == id && t.TrangThai != 2 && !_context.ChiTietHopDongs.Any(c => c.MaThietBi == t.MaThietBi && c.HopDong.TrangThai != 2 && c.HopDong.TrangThai != 3 && c.HopDong.NgayKetThuc > DateTime.Now));
            if (available <= 0)
            {
                TempData["Error"] = $"Sản phẩm '{product.TenSanPham}' hiện đang tạm hết máy trong kho!";
                return RedirectToAction("Index", "SanPham");
            }

            var cart = HttpContext.Session.Get<List<CartItem>>("GioHang") ?? new List<CartItem>();
            var item = cart.SingleOrDefault(p => p.MaSanPham == id);
            if (item != null)
            {
                if (item.SoLuong >= available)
                {
                    TempData["Error"] = $"Số lượng trong giỏ đã đạt tối đa tồn kho khả dụng ({available} máy)!";
                    return RedirectToAction("Index");
                }
                item.SoLuong++;
            }
            else
            {
                cart.Add(new CartItem
                {
                    MaSanPham = product.MaSanPham,
                    TenSanPham = product.TenSanPham,
                    GiaThueNgay = product.GiaThueNgay,
                    SoLuong = 1,
                    HinhAnh = product.HinhAnh
                });
            }
            HttpContext.Session.Set("GioHang", cart);
            return RedirectToAction("Index");
        }

        public IActionResult Remove(int id)
        {
            var cart = HttpContext.Session.Get<List<CartItem>>("GioHang");
            if (cart != null)
            {
                var item = cart.SingleOrDefault(p => p.MaSanPham == id);
                if (item != null)
                {
                    cart.Remove(item);
                    HttpContext.Session.Set("GioHang", cart);
                }
            }
            return RedirectToAction("Index");
        }

        [HttpPost]
        public async Task<IActionResult> UpdateQuantity(int id, int qty)
        {
            var cart = HttpContext.Session.Get<List<CartItem>>("GioHang");
            if (cart != null)
            {
                var item = cart.SingleOrDefault(p => p.MaSanPham == id);
                if (item != null)
                {
                    if (qty <= 0)
                    {
                        cart.Remove(item);
                    }
                    else
                    {
                        // Kiểm tra tồn kho khả dụng (loại trừ máy đang bảo trì)
                        int available = await _context.ThietBis.CountAsync(t => t.MaSanPham == id && t.TrangThai != 2 && !_context.ChiTietHopDongs.Any(c => c.MaThietBi == t.MaThietBi && c.HopDong.TrangThai != 2 && c.HopDong.TrangThai != 3 && c.HopDong.NgayKetThuc > DateTime.Now));
                        if (qty > available)
                        {
                            TempData["Error"] = $"Sản phẩm '{item.TenSanPham}' chỉ còn tối đa {available} máy trong kho!";
                            item.SoLuong = available;
                        }
                        else
                        {
                            item.SoLuong = qty;
                        }
                    }
                    HttpContext.Session.Set("GioHang", cart);
                }
            }
            return RedirectToAction("Index");
        }

        [Authorize]
        [HttpGet]
        public async Task<IActionResult> Checkout()
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
            {
                return RedirectToAction("Login", "Account", new { returnUrl = "/Cart/Checkout" });
            }

            var user = await _context.NguoiDungs.FindAsync(userId);
            if (user == null || string.IsNullOrWhiteSpace(user.CCCD))
            {
                TempData["Error"] = "Vui lòng cập nhật số CCCD/CMND trong thông tin tài khoản trước khi đặt thuê thiết bị!";
                return RedirectToAction("Profile", "Account");
            }

            if (DebtCalculationHelper.IsCustomerBlacklisted(user.MaNguoiDung, _context, out string blacklistReason))
            {
                TempData["Error"] = $"Tài khoản bị khóa đặt thuê do nợ xấu: {blacklistReason}. Vui lòng thanh toán tại Sổ công nợ.";
                return RedirectToAction("MyDebt", "Account");
            }

            var cart = HttpContext.Session.Get<List<CartItem>>("GioHang");
            if (cart == null || !cart.Any()) return RedirectToAction("Index");

            // Đồng bộ lại Giá thuê mới nhất từ CSDL trước khi render trang thanh toán
            bool modified = false;
            foreach (var item in cart)
            {
                var dbProd = await _context.SanPhams.FindAsync(item.MaSanPham);
                if (dbProd != null && item.GiaThueNgay != dbProd.GiaThueNgay)
                {
                    item.GiaThueNgay = dbProd.GiaThueNgay;
                    modified = true;
                }
            }
            if (modified) HttpContext.Session.Set("GioHang", cart);

            return View(cart);
        }

        // Kiểm tra tính hợp lệ của mã khuyến mãi qua AJAX
        [HttpPost]
        [IgnoreAntiforgeryToken]
        public async Task<IActionResult> CheckPromo(string? code)
        {
            if (string.IsNullOrWhiteSpace(code))
            {
                if (Request.HasJsonContentType())
                {
                    try
                    {
                        using var reader = new System.IO.StreamReader(Request.Body);
                        var body = await reader.ReadToEndAsync();
                        if (!string.IsNullOrWhiteSpace(body))
                        {
                            using var doc = System.Text.Json.JsonDocument.Parse(body);
                            if (doc.RootElement.TryGetProperty("code", out var codeElem) || doc.RootElement.TryGetProperty("Code", out codeElem))
                            {
                                code = codeElem.GetString();
                            }
                        }
                    }
                    catch { }
                }
            }

            if (string.IsNullOrWhiteSpace(code))
            {
                return Json(new { success = false, message = "Vui lòng nhập mã khuyến mãi!" });
            }

            var cleanCode = code.Trim().ToUpperInvariant();
            var now = DateTime.Now;

            var km = await _context.KhuyenMais.FirstOrDefaultAsync(k =>
                (k.Code.ToUpper() == cleanCode || (k.MaCode != null && k.MaCode.ToUpper() == cleanCode)));

            if (km == null)
            {
                return Json(new { success = false, message = "Mã khuyến mãi không tồn tại trong hệ thống!" });
            }

            if (!km.KichHoat)
            {
                return Json(new { success = false, message = "Mã khuyến mãi hiện đang tạm khóa hoặc đã ngừng hoạt động!" });
            }

            if (now < km.NgayBatDau)
            {
                return Json(new { success = false, message = $"Mã khuyến mãi chỉ có hiệu lực từ ngày {km.NgayBatDau:dd/MM/yyyy}!" });
            }

            if (now > km.NgayKetThuc)
            {
                return Json(new { success = false, message = $"Mã khuyến mãi đã hết hạn sử dụng vào ngày {km.NgayKetThuc:dd/MM/yyyy}!" });
            }

            if (km.SoLuong <= 0)
            {
                return Json(new { success = false, message = "Mã khuyến mãi đã hết lượt sử dụng!" });
            }

            return Json(new
            {
                success = true,
                code = km.Code ?? km.MaCode,
                discountPercent = km.PhanTramGiam,
                message = $"Áp dụng thành công mã {km.Code ?? km.MaCode}: Giảm {km.PhanTramGiam}% tổng tiền thuê!"
            });
        }

        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        // Xử lý đặt thuê thiết bị từ giỏ hàng. Kiểm tra chống trùng lịch, trừ tồn kho và tạo hợp đồng chờ duyệt.
        public async Task<IActionResult> Checkout(DateTime NgayBatDau, DateTime NgayKetThuc, string DiaChi)
        {
            string? promoCode = null;
            try
            {
                if (Request != null && Request.HasFormContentType && Request.Form.ContainsKey("PromoCode"))
                {
                    promoCode = Request.Form["PromoCode"].ToString();
                }
            }
            catch { }

            return await Checkout(NgayBatDau, NgayKetThuc, DiaChi, promoCode);
        }

        [NonAction]
        public async Task<IActionResult> Checkout(DateTime NgayBatDau, DateTime NgayKetThuc, string DiaChi, string? PromoCode)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
            {
                return RedirectToAction("Login", "Account", new { returnUrl = "/Cart/Checkout" });
            }

            var user = await _context.NguoiDungs.FindAsync(userId);
            if (user == null || string.IsNullOrWhiteSpace(user.CCCD))
            {
                TempData["Error"] = "Vui lòng cập nhật số CCCD/CMND trong thông tin tài khoản trước khi đặt thuê thiết bị!";
                return RedirectToAction("Profile", "Account");
            }

            if (DebtCalculationHelper.IsCustomerBlacklisted(user.MaNguoiDung, _context, out string blacklistReason))
            {
                TempData["Error"] = $"Không thể hoàn tất đặt thuê/ký hợp đồng do tài khoản đang bị khóa vì nợ xấu: {blacklistReason}. Vui lòng hoàn thành nghĩa vụ tài chính tại Sổ công nợ.";
                return RedirectToAction("MyDebt", "Account");
            }

            if (NgayKetThuc.Date < NgayBatDau.Date)
            {
                TempData["Error"] = "BẢO MẬT: Phát hiện can thiệp dữ liệu! Ngày trả máy không thể nhỏ hơn ngày nhận máy.";
                return RedirectToAction("Checkout");
            }
            if (NgayBatDau.Date < DateTime.Now.Date)
            {
                TempData["Error"] = "Ngày nhận máy không thể nằm trong quá khứ!";
                return RedirectToAction("Checkout");
            }

            var cart = HttpContext.Session.Get<List<CartItem>>("GioHang");
            if (cart == null || !cart.Any()) return RedirectToAction("Index");

            int days = (int)(NgayKetThuc.Date - NgayBatDau.Date).TotalDays;
            if (days <= 0) days = 1;

            await InventoryLock.WaitAsync();
            try
            {
                bool cartModified = false;
                for (int i = cart.Count - 1; i >= 0; i--)
                {
                    var item = cart[i];
                    int available = await _context.ThietBis
                        .CountAsync(t => t.MaSanPham == item.MaSanPham && t.TrangThai != 2 && !_context.ChiTietHopDongs.Any(c => 
                            c.MaThietBi == t.MaThietBi && 
                            c.HopDong.TrangThai != 2 && c.HopDong.TrangThai != 3 &&
                            c.HopDong.NgayBatDau < NgayKetThuc && 
                            c.HopDong.NgayKetThuc > NgayBatDau));
                    if (available < item.SoLuong)
                    {
                        cartModified = true;
                        if (available == 0) 
                        {
                            cart.RemoveAt(i);
                            TempData["Error"] = "Sản phẩm '" + item.TenSanPham + "' đã hết hàng và bị xóa khỏi giỏ!";
                        } 
                        else 
                        {
                            item.SoLuong = available;
                            TempData["Error"] = "Sản phẩm '" + item.TenSanPham + "' không đủ số lượng, hệ thống đã điều chỉnh lại!";
                        }
                    }
                }
                if (cartModified)
                {
                    HttpContext.Session.Set("GioHang", cart);
                    return RedirectToAction("Index");
                }

                decimal totalAmount = 0;
                foreach (var item in cart)
                {
                    var dbProd = await _context.SanPhams.FindAsync(item.MaSanPham);
                    decimal p = dbProd != null ? dbProd.GiaThueNgay : item.GiaThueNgay;
                    totalAmount += (p * item.SoLuong) * days;
                }

                // Xử lý áp dụng mã khuyến mãi (nếu có)
                KhuyenMai? appliedKM = null;
                decimal discountAmount = 0;
                if (!string.IsNullOrWhiteSpace(PromoCode))
                {
                    var codeClean = PromoCode.Trim().ToUpperInvariant();
                    var now = DateTime.Now;
                    appliedKM = await _context.KhuyenMais.FirstOrDefaultAsync(k =>
                        (k.Code.ToUpper() == codeClean || (k.MaCode != null && k.MaCode.ToUpper() == codeClean)) &&
                        k.KichHoat &&
                        k.NgayBatDau <= now &&
                        k.NgayKetThuc >= now &&
                        k.SoLuong > 0);

                    if (appliedKM != null)
                    {
                        discountAmount = Math.Round((totalAmount * appliedKM.PhanTramGiam) / 100m);
                        totalAmount = Math.Max(0m, totalAmount - discountAmount);
                        appliedKM.SoLuong = Math.Max(0, appliedKM.SoLuong - 1);
                    }
                }

                var firstAdmin = await _context.NguoiDungs.FirstOrDefaultAsync(u => u.VaiTro.TenVaiTro == "Admin" || u.VaiTro.TenVaiTro == "KinhDoanh");
                int adminId = firstAdmin != null ? firstAdmin.MaNguoiDung : userId;

                string ghiChu = "Giao hàng tới: " + DiaChi;
                if (appliedKM != null)
                {
                    ghiChu += $" [Giảm {appliedKM.PhanTramGiam}% theo mã {appliedKM.Code}: -{discountAmount:N0}đ]";
                }

                var hopDong = new HopDong
                {
                    MaKhachHang = userId,
                    MaNhanVien = adminId,
                    NgayBatDau = NgayBatDau,
                    NgayKetThuc = NgayKetThuc,
                    TongTien = totalAmount,
                    MaKhuyenMai = appliedKM?.MaKM,
                    TrangThai = 0, // Chờ duyệt
                    NgayKy = null,
                    ChuKyKhachHang = "",
                    ChuKyNhanVien = "",
                    AnhCMND = "",
                    TrangThaiThanhToan = 0,
                    GhiChu = ghiChu,
                    SoKyHan = 1,
                    HanChotKy = DateTime.Now.AddHours(24)
                };

                _context.HopDongs.Add(hopDong);
                await _context.SaveChangesAsync(); 

                foreach (var item in cart)
                {
                    var dbProd = await _context.SanPhams.FindAsync(item.MaSanPham);
                    decimal p = dbProd != null ? dbProd.GiaThueNgay : item.GiaThueNgay;
                    
                    var availableDevices = await _context.ThietBis
                        .Where(t => t.MaSanPham == item.MaSanPham && t.TrangThai != 2 && !_context.ChiTietHopDongs.Any(c => 
                            c.MaThietBi == t.MaThietBi && 
                            c.HopDong.TrangThai != 2 && c.HopDong.TrangThai != 3 &&
                            c.HopDong.NgayBatDau < NgayKetThuc && 
                            c.HopDong.NgayKetThuc > NgayBatDau))
                        .Take(item.SoLuong)
                        .ToListAsync();

                    foreach (var device in availableDevices)
                    {
                        var ct = new ChiTietHopDong
                        {
                            MaHopDong = hopDong.MaHopDong,
                            MaThietBi = device.MaThietBi,
                            GiaChotThu = p * days
                        };
                        _context.ChiTietHopDongs.Add(ct);
                        
                        // Giữ chỗ thiết bị (TrangThai = 3)
                        device.TrangThai = 3; 
                    }
                }

                await _context.SaveChangesAsync();
                HttpContext.Session.Remove("GioHang");

                TempData["Success"] = "Khởi tạo đơn hàng thành công! Vui lòng hoàn tất thủ tục ký hợp đồng bên dưới.";
                return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
            }
            finally
            {
                InventoryLock.Release();
            }
        }

        public IActionResult Success()
        {
            return View();
        }

        [Authorize]
        public async Task<IActionResult> MyContracts()
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

            var contracts = await _context.HopDongs
                .Where(h => h.MaKhachHang == userId)
                .OrderByDescending(h => h.NgayBatDau)
                .ToListAsync();

            return View(contracts);
        }

        [Authorize]
        [HttpGet]
        public async Task<IActionResult> ContractDetail(int id)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

            var hopDong = await _context.HopDongs
                .Include(h => h.KhachHang)
                .Include(h => h.NhanVien)
                .Include(h => h.KyHanThanhToans)
                .Include(h => h.BienBanBanGiaos)
                .Include(h => h.PhieuChis)
                .Include(h => h.PhieuBaoTris)
                .Include(h => h.PhieuThus)
                .Include(h => h.DanhSachYeuCauGiaHan)
                .FirstOrDefaultAsync(h => h.MaHopDong == id && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            var chiTiets = await _context.ChiTietHopDongs
                .Include(c => c.ThietBi)
                .ThenInclude(t => t.SanPham)
                .Where(c => c.MaHopDong == id)
                .ToListAsync();

            var kyHans = await _context.KyHanThanhToans
                .Where(k => k.MaHopDong == id)
                .OrderBy(k => k.SoKyHan)
                .ToListAsync();

            RentalSystem.Areas.Admin.Controllers.HopDongController.CapNhatTreHanVaPhiPhat(kyHans);
            await RentalSystem.Areas.Admin.Controllers.HopDongController.SyncTrangThaiThanhToanHopDong(hopDong, _context);
            await _context.SaveChangesAsync();

            var phieuThus = await _context.PhieuThus
                .Include(p => p.NhanVienThu)
                .Where(p => p.MaHopDong == id)
                .OrderByDescending(p => p.NgayGiaoDich)
                .ToListAsync();

            var phieuBaoTris = await _context.PhieuBaoTris
                .Include(b => b.ThietBi)
                .ThenInclude(t => t.SanPham)
                .Where(b => b.MaHopDong == id)
                .OrderByDescending(b => b.NgayBaoLoi)
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

            var yeuCauGiaHans = await _context.YeuCauGiaHans
                .Include(y => y.NguoiDuyet)
                .Where(y => y.MaHopDong == id)
                .OrderByDescending(y => y.NgayYeuCau)
                .ToListAsync();

            ViewBag.ChiTiets = chiTiets;
            ViewBag.KyHans = kyHans;
            ViewBag.PhieuThus = phieuThus;
            ViewBag.PhieuBaoTris = phieuBaoTris;
            ViewBag.BienBanBanGiaos = bienBanBanGiaos;
            ViewBag.PhieuChis = phieuChis;
            ViewBag.YeuCauGiaHans = yeuCauGiaHans;
            return View(hopDong);
        }

        [Authorize]
        [HttpGet]
        public async Task<IActionResult> SignContract(int id)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

            var user = await _context.NguoiDungs.FindAsync(userId);
            if (user == null || string.IsNullOrWhiteSpace(user.CCCD))
            {
                TempData["Error"] = "Vui lòng cập nhật số CCCD/CMND trong thông tin tài khoản trước khi ký hợp đồng!";
                return RedirectToAction("Profile", "Account");
            }

            if (DebtCalculationHelper.IsCustomerBlacklisted(user.MaNguoiDung, _context, out string blacklistReason))
            {
                TempData["Error"] = $"Tài khoản bị khóa đặt thuê do nợ xấu: {blacklistReason}. Vui lòng thanh toán tại Sổ công nợ.";
                return RedirectToAction("MyDebt", "Account");
            }

            var hopDong = await _context.HopDongs
                .FirstOrDefaultAsync(h => h.MaHopDong == id && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            if (!string.IsNullOrEmpty(hopDong.ChuKyKhachHang))
            {
                TempData["Error"] = "Hợp đồng này đã được ký!";
                return RedirectToAction("MyContracts");
            }
            
            decimal tienCocYeuCau = await _context.ChiTietHopDongs
                .Where(c => c.MaHopDong == id)
                .Include(c => c.ThietBi)
                .ThenInclude(t => t.SanPham)
                .SumAsync(c => c.ThietBi.SanPham.TienCoc);
                
            ViewBag.TienCocYeuCau = tienCocYeuCau;

            return View(hopDong);
        }

        [Authorize]
        private async Task<(bool Success, string? Error, string? Path)> ValidateAndSaveImageAsync(Microsoft.AspNetCore.Http.IFormFile file, string subFolder, string prefix, int entityId)
        {
            if (file == null || file.Length == 0) return (false, "Tệp tin rỗng!", null);
            if (file.Length > 5 * 1024 * 1024) return (false, "Kích thước tệp không được vượt quá 5MB!", null);

            var ext = System.IO.Path.GetExtension(file.FileName).ToLower();
            if (ext != ".jpg" && ext != ".jpeg" && ext != ".png" && ext != ".webp")
                return (false, "Đuôi tệp phải là .jpg, .jpeg, .png hoặc .webp!", null);

            var contentType = file.ContentType?.ToLower();
            if (contentType != null && !contentType.StartsWith("image/"))
                return (false, "Định dạng tệp không phải hình ảnh hợp lệ!", null);

            byte[] header = new byte[8];
            using (var stream = file.OpenReadStream())
            {
                int bytesRead = await stream.ReadAsync(header, 0, 8);
                if (bytesRead < 4) return (false, "Tệp ảnh bị hỏng hoặc không đọc được!", null);
            }

            bool isPng = header[0] == 0x89 && header[1] == 0x50 && header[2] == 0x4E && header[3] == 0x47;
            bool isJpg = header[0] == 0xFF && header[1] == 0xD8 && header[2] == 0xFF;
            bool isRiff = header[0] == 0x52 && header[1] == 0x49 && header[2] == 0x46 && header[3] == 0x46;
            if (!isPng && !isJpg && !isRiff)
                return (false, "Nội dung tệp không phải ảnh JPG, PNG hoặc WEBP hợp lệ!", null);

            string folder = System.IO.Path.Combine(_env.WebRootPath, "uploads", subFolder);
            if (!System.IO.Directory.Exists(folder)) System.IO.Directory.CreateDirectory(folder);

            string fileName = $"{prefix}_{entityId}_{DateTime.Now.Ticks}{ext}";
            string path = System.IO.Path.Combine(folder, fileName);
            using (var stream = new System.IO.FileStream(path, System.IO.FileMode.Create))
            {
                await file.CopyToAsync(stream);
            }
            return (true, null, $"/uploads/{subFolder}/{fileName}");
        }

        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        // Khách hàng ký hợp đồng điện tử và tải lên ảnh CCCD (mặt trước và mặt sau)
        public async Task<IActionResult> SignContract(int id, int soKyHan, Microsoft.AspNetCore.Http.IFormFile cmndTruocFile, Microsoft.AspNetCore.Http.IFormFile cmndSauFile, Microsoft.AspNetCore.Http.IFormFile cmndFile, string signatureData)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

            var user = await _context.NguoiDungs.FindAsync(userId);
            if (user == null || string.IsNullOrWhiteSpace(user.CCCD))
            {
                TempData["Error"] = "Vui lòng cập nhật số CCCD/CMND trong thông tin tài khoản trước khi ký hợp đồng!";
                return RedirectToAction("Profile", "Account");
            }

            if (DebtCalculationHelper.IsCustomerBlacklisted(user.MaNguoiDung, _context, out string blacklistReason))
            {
                TempData["Error"] = $"Không thể hoàn tất đặt thuê/ký hợp đồng do tài khoản đang bị khóa vì nợ xấu: {blacklistReason}. Vui lòng hoàn thành nghĩa vụ tài chính tại Sổ công nợ.";
                return RedirectToAction("MyDebt", "Account");
            }

            var hopDong = await _context.HopDongs
                .FirstOrDefaultAsync(h => h.MaHopDong == id && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            if (!string.IsNullOrEmpty(hopDong.ChuKyKhachHang))
            {
                TempData["Error"] = "Hợp đồng này đã được ký!";
                return RedirectToAction("MyContracts");
            }

            // Lưu ảnh CCCD mặt trước
            if (cmndTruocFile != null && cmndTruocFile.Length > 0)
            {
                var (success, error, path) = await ValidateAndSaveImageAsync(cmndTruocFile, "cmnd", "cccd_front", hopDong.MaHopDong);
                if (!success)
                {
                    TempData["Error"] = "Ảnh mặt trước CCCD lỗi: " + error;
                    return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
                }
                hopDong.AnhCCCD_Truoc = path;
                hopDong.AnhCMND = path;
            }
            else if (cmndFile != null && cmndFile.Length > 0)
            {
                var (success, error, path) = await ValidateAndSaveImageAsync(cmndFile, "cmnd", "cccd_front", hopDong.MaHopDong);
                if (!success)
                {
                    TempData["Error"] = "Ảnh CCCD lỗi: " + error;
                    return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
                }
                hopDong.AnhCCCD_Truoc = path;
                hopDong.AnhCMND = path;
            }

            // Lưu ảnh CCCD mặt sau
            if (cmndSauFile != null && cmndSauFile.Length > 0)
            {
                var (success, error, path) = await ValidateAndSaveImageAsync(cmndSauFile, "cmnd", "cccd_back", hopDong.MaHopDong);
                if (!success)
                {
                    TempData["Error"] = "Ảnh mặt sau CCCD lỗi: " + error;
                    return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
                }
                hopDong.AnhCCCD_Sau = path;
            }

            if (string.IsNullOrEmpty(hopDong.AnhCMND) && string.IsNullOrEmpty(hopDong.AnhCCCD_Truoc))
            {
                TempData["Error"] = "Vui lòng tải lên ảnh CCCD mặt trước!";
                return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
            }

            if (string.IsNullOrEmpty(hopDong.AnhCCCD_Sau) && cmndSauFile == null && cmndFile == null)
            {
                TempData["Error"] = "Vui lòng tải lên ảnh CCCD mặt sau!";
                return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
            }

            // Kiểm tra tính hợp lệ của dữ liệu chữ ký điện tử (Base64)
            if (!string.IsNullOrEmpty(signatureData))
            {
                // Giới hạn dung lượng chữ ký tối đa 256KB
                if (signatureData.Length > 256 * 1024)
                {
                    TempData["Error"] = "Kích thước dữ liệu chữ ký vượt quá giới hạn cho phép (tối đa 256KB)!";
                    return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
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
                    return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
                }

                byte[] imageBytes;
                try
                {
                    imageBytes = Convert.FromBase64String(base64Data);
                }
                catch (FormatException)
                {
                    TempData["Error"] = "Dữ liệu chữ ký Base64 bị lỗi định dạng!";
                    return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
                }

                // Kiểm tra định dạng ảnh PNG hợp lệ
                if (imageBytes.Length < 8 || imageBytes[0] != 0x89 || imageBytes[1] != 0x50 || imageBytes[2] != 0x4E || imageBytes[3] != 0x47)
                {
                    TempData["Error"] = "Dữ liệu chữ ký không phải là ảnh PNG hợp lệ!";
                    return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
                }

                string sigFolder = System.IO.Path.Combine(_env.WebRootPath, "uploads", "signatures");
                if (!System.IO.Directory.Exists(sigFolder))
                {
                    System.IO.Directory.CreateDirectory(sigFolder);
                }

                string sigFileName = $"kh_{hopDong.MaHopDong}_{DateTime.Now.Ticks}.png";
                string sigPath = System.IO.Path.Combine(sigFolder, sigFileName);
                await System.IO.File.WriteAllBytesAsync(sigPath, imageBytes);
                hopDong.ChuKyKhachHang = $"/uploads/signatures/{sigFileName}";
            }
            else if (string.IsNullOrEmpty(hopDong.ChuKyKhachHang))
            {
                TempData["Error"] = "Vui lòng ký tên vào khung chữ ký!";
                return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
            }

            if (string.IsNullOrEmpty(hopDong.ChuKyKhachHang) || (string.IsNullOrEmpty(hopDong.AnhCMND) && string.IsNullOrEmpty(hopDong.AnhCCCD_Truoc)))
            {
                TempData["Error"] = "Vui lòng tải lên CCCD và Ký tên đầy đủ!";
                return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
            }
            
            // Giới hạn số kỳ hạn trả góp dựa trên tổng thời gian thuê
            var rentalDays = (hopDong.NgayKetThuc.Date - hopDong.NgayBatDau.Date).TotalDays;
            if (rentalDays <= 0) rentalDays = 1;
            int maxInstallments = Math.Max(1, (int)Math.Floor(rentalDays / 7.0));

            if (soKyHan < 1) soKyHan = 1;
            if (soKyHan > maxInstallments) soKyHan = maxInstallments;
            hopDong.SoKyHan = soKyHan;
            hopDong.NgayKy = DateTime.Now;

            await _context.SaveChangesAsync();
            TempData["Success"] = "Đã ký hợp đồng thành công!";
            return RedirectToAction("MyContracts");
        }
        [Authorize]
        [HttpGet]
        public async Task<IActionResult> EditContract(int id)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

            var hopDong = await _context.HopDongs
                .FirstOrDefaultAsync(h => h.MaHopDong == id && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            // Chỉ cho phép sửa nếu chưa ký và đang chờ duyệt
            if (!string.IsNullOrEmpty(hopDong.ChuKyKhachHang) || hopDong.TrangThai != 0)
            {
                TempData["Error"] = "Không thể chỉnh sửa hợp đồng đã ký hoặc đang xử lý!";
                return RedirectToAction("MyContracts");
            }

            return View(hopDong);
        }

        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> EditContract(int id, DateTime NgayBatDau, DateTime NgayKetThuc, string GhiChu)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

            var hopDong = await _context.HopDongs
                .FirstOrDefaultAsync(h => h.MaHopDong == id && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            if (!string.IsNullOrEmpty(hopDong.ChuKyKhachHang) || hopDong.TrangThai != 0)
            {
                TempData["Error"] = "Không thể chỉnh sửa hợp đồng đã ký hoặc đang xử lý!";
                return RedirectToAction("MyContracts");
            }

            if (NgayKetThuc.Date < NgayBatDau.Date)
            {
                TempData["Error"] = "Ngày trả máy không thể nhỏ hơn ngày nhận máy!";
                return RedirectToAction("EditContract", new { id = id });
            }
            if (NgayBatDau.Date < DateTime.Now.Date)
            {
                TempData["Error"] = "Ngày nhận máy không thể nằm trong quá khứ!";
                return RedirectToAction("EditContract", new { id = id });
            }

            // Tính lại tổng tiền theo số ngày mới (thuê trong ngày tính tối thiểu 1 ngày)
            int days = Math.Max(1, (int)(NgayKetThuc.Date - NgayBatDau.Date).TotalDays);

            var chiTiets = await _context.ChiTietHopDongs
                .Include(c => c.ThietBi).ThenInclude(t => t.SanPham)
                .Where(c => c.MaHopDong == id)
                .ToListAsync();

            // Kiểm tra xem thiết bị có bị trùng lịch thuê với hợp đồng khác không
            foreach (var ct in chiTiets)
            {
                bool conflict = await _context.ChiTietHopDongs
                    .AnyAsync(other =>
                        other.MaThietBi == ct.MaThietBi &&
                        other.MaHopDong != id &&
                        other.HopDong.TrangThai != 2 && other.HopDong.TrangThai != 3 &&
                        other.HopDong.NgayBatDau < NgayKetThuc &&
                        other.HopDong.NgayKetThuc > NgayBatDau);
                if (conflict)
                {
                    TempData["Error"] = $"Thiết bị '{ct.ThietBi?.SoSerial}' đã được đặt bởi đơn hàng khác trong khoảng thời gian bạn chọn. Vui lòng chọn ngày khác!";
                    return RedirectToAction("EditContract", new { id = id });
                }
            }

            decimal tongTienMoi = 0;
            foreach (var ct in chiTiets)
            {
                decimal giaThueNgay = ct.ThietBi?.SanPham?.GiaThueNgay ?? 0;
                ct.GiaChotThu = giaThueNgay * days;
                tongTienMoi += ct.GiaChotThu;
            }

            hopDong.NgayBatDau = NgayBatDau;
            hopDong.NgayKetThuc = NgayKetThuc;
            hopDong.TongTien = tongTienMoi;
            hopDong.GhiChu = GhiChu ?? "";
            
            int maxInstallments = Math.Max(1, (int)Math.Floor(days / 7.0));
            if (hopDong.SoKyHan > maxInstallments) hopDong.SoKyHan = maxInstallments;

            await _context.SaveChangesAsync();
            TempData["Success"] = $"Đã cập nhật đơn hàng #{id} thành công! Tổng tiền mới: {tongTienMoi:N0}đ.";
            return RedirectToAction("MyContracts");
        }

        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DeleteContract(int id)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

            var hopDong = await _context.HopDongs
                .FirstOrDefaultAsync(h => h.MaHopDong == id && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            // Chỉ cho phép xóa nếu chưa ký và đang chờ duyệt
            if (!string.IsNullOrEmpty(hopDong.ChuKyKhachHang) || hopDong.TrangThai != 0)
            {
                TempData["Error"] = "Không thể xóa hợp đồng đã ký hoặc đang xử lý!";
                return RedirectToAction("MyContracts");
            }

            if (hopDong.TienDaCoc > 0 || await _context.PhieuThus.AnyAsync(p => p.MaHopDong == id))
            {
                TempData["Error"] = "Không thể tự xóa đơn hàng đã có lịch sử nộp tiền/cọc. Vui lòng liên hệ Admin để hủy!";
                return RedirectToAction("MyContracts");
            }

            // Trả thiết bị về kho (trạng thái 0 = Sẵn sàng)
            var chiTiets = await _context.ChiTietHopDongs
                .Include(c => c.ThietBi)
                .Where(c => c.MaHopDong == id)
                .ToListAsync();

            foreach (var ct in chiTiets)
            {
                if (ct.ThietBi != null)
                    ct.ThietBi.TrangThai = 0; // Trả về kho
            }

            // Xóa phiếu thu liên quan (tiền cọc nếu có)
            var phieuThus = await _context.PhieuThus.Where(p => p.MaHopDong == id).ToListAsync();
            _context.PhieuThus.RemoveRange(phieuThus);

            var phieuBaoTris = await _context.PhieuBaoTris.Where(p => p.MaHopDong == id).ToListAsync();
            _context.PhieuBaoTris.RemoveRange(phieuBaoTris);

            var kyHans = await _context.KyHanThanhToans.Where(k => k.MaHopDong == id).ToListAsync();
            _context.KyHanThanhToans.RemoveRange(kyHans);

            // Xóa chi tiết hợp đồng
            _context.ChiTietHopDongs.RemoveRange(chiTiets);

            // Xóa hợp đồng
            _context.HopDongs.Remove(hopDong);

            await _context.SaveChangesAsync();
            TempData["Success"] = $"Đã xóa đơn hàng #{id} thành công. Thiết bị đã được trả về kho.";
            return RedirectToAction("MyContracts");
        }

        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        // Khách hàng gửi yêu cầu hủy đơn hàng khi đang chờ duyệt
        public async Task<IActionResult> YeuCauHuy(int id, string lyDo)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

            var hd = await _context.HopDongs.FirstOrDefaultAsync(h => h.MaHopDong == id && h.MaKhachHang == userId);
            if (hd == null) return NotFound();

            if (hd.TrangThai != 0)
            {
                TempData["Error"] = "Chỉ có thể gửi yêu cầu hủy cho đơn hàng đang chờ duyệt!";
                return RedirectToAction("ContractDetail", new { id = id });
            }

            if (string.IsNullOrWhiteSpace(lyDo))
            {
                TempData["Error"] = "Vui lòng nhập lý do yêu cầu hủy đơn!";
                return RedirectToAction("ContractDetail", new { id = id });
            }

            hd.YeuCauHuy = true;
            hd.LyDoHuy = lyDo.Trim();
            hd.NgayYeuCauHuy = DateTime.Now;
            await _context.SaveChangesAsync();

            TempData["Success"] = "Đã gửi yêu cầu hủy hợp đồng tới quản trị viên xét duyệt!";
            return RedirectToAction("ContractDetail", new { id = id });
        }

        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        // Khách hàng gửi yêu cầu gia hạn hợp đồng đang cho thuê
        public async Task<IActionResult> YeuCauGiaHan(int id, int soNgayGiaHan, string lyDo)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

            var hd = await _context.HopDongs.FirstOrDefaultAsync(h => h.MaHopDong == id && h.MaKhachHang == userId);
            if (hd == null) return NotFound();

            if (hd.TrangThai != 1)
            {
                TempData["Error"] = "Chỉ có thể yêu cầu gia hạn khi hợp đồng đang trong thời gian thuê!";
                return RedirectToAction("ContractDetail", new { id = id });
            }

            if (soNgayGiaHan <= 0 || soNgayGiaHan > 365)
            {
                TempData["Error"] = "Số ngày gia hạn không hợp lệ (từ 1 đến 365 ngày)!";
                return RedirectToAction("ContractDetail", new { id = id });
            }

            DateTime extStart = hd.NgayKetThuc.Date;
            DateTime extEnd = hd.NgayKetThuc.Date.AddDays(soNgayGiaHan);

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
                    TempData["Error"] = $"Không thể gia hạn: Thiết bị #{ct.MaThietBi} đã có đơn hàng khác đặt trước trong khoảng thời gian này!";
                    return RedirectToAction("ContractDetail", new { id = id });
                }
            }

            // Lưu thông tin yêu cầu gia hạn chờ duyệt
            var yc = new YeuCauGiaHan
            {
                MaHopDong = id,
                SoNgayGiaHan = soNgayGiaHan,
                LyDo = lyDo?.Trim(),
                NgayYeuCau = DateTime.Now,
                TrangThai = 0 // 0: Chờ duyệt
            };
            _context.YeuCauGiaHans.Add(yc);

            // Đồng bộ các cờ trên HopDong
            hd.YeuCauGiaHan = true;
            hd.SoNgayGiaHan = soNgayGiaHan;
            hd.TrangThaiGiaHan = 0; // 0: Chờ duyệt
            hd.LyDoGiaHan = lyDo?.Trim();
            await _context.SaveChangesAsync();

            TempData["Success"] = $"Đã gửi yêu cầu gia hạn thêm {soNgayGiaHan} ngày. Vui lòng chờ quản trị viên phê duyệt!";
            return RedirectToAction("ContractDetail", new { id = id });
        }

        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        // Khách hàng gửi mã giao dịch và tải ảnh biên lai chuyển khoản ngân hàng
        public async Task<IActionResult> GuiBienLai(int maKyHan, string maGiaoDich, Microsoft.AspNetCore.Http.IFormFile hinhAnhBienLai)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

            var kyHan = await _context.KyHanThanhToans
                .Include(k => k.HopDong)
                .FirstOrDefaultAsync(k => k.MaKyHan == maKyHan && k.HopDong.MaKhachHang == userId);

            if (kyHan == null) return NotFound();

            if (kyHan.TrangThai == 1)
            {
                TempData["Error"] = "Kỳ hạn này đã được thanh toán đầy đủ!";
                return RedirectToAction("ContractDetail", new { id = kyHan.MaHopDong });
            }

            if (string.IsNullOrWhiteSpace(maGiaoDich))
            {
                TempData["Error"] = "Vui lòng nhập mã giao dịch ngân hàng!";
                return RedirectToAction("ContractDetail", new { id = kyHan.MaHopDong });
            }

            if (hinhAnhBienLai == null || hinhAnhBienLai.Length == 0)
            {
                TempData["Error"] = "Vui lòng tải lên ảnh chụp biên lai chuyển khoản!";
                return RedirectToAction("ContractDetail", new { id = kyHan.MaHopDong });
            }

            var (success, error, path) = await ValidateAndSaveImageAsync(hinhAnhBienLai, "bienlai", "bill", kyHan.MaKyHan);
            if (!success)
            {
                TempData["Error"] = "Ảnh biên lai lỗi: " + error;
                return RedirectToAction("ContractDetail", new { id = kyHan.MaHopDong });
            }

            kyHan.MaGiaoDichChuyenKhoan = maGiaoDich.Trim();
            kyHan.HinhAnhBienLai = path;
            kyHan.TrangThaiXacNhan = 1; // 1: Chờ duyệt đối soát
            kyHan.NgayGuiBienLai = DateTime.Now;

            await _context.SaveChangesAsync();
            TempData["Success"] = "Đã gửi thông tin chuyển khoản và ảnh biên lai thành công! Kế toán sẽ đối soát và xác nhận sớm.";
            return RedirectToAction("ContractDetail", new { id = kyHan.MaHopDong });
        }

        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        // Khách hàng tải minh chứng thanh toán (Ủy nhiệm chi / Biên lai chuyển khoản)
        public async Task<IActionResult> UploadMinhChungThanhToan(int maHopDong, int? maKyHan, Microsoft.AspNetCore.Http.IFormFile fileMinhChung)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

            var hopDong = await _context.HopDongs
                .Include(h => h.KyHanThanhToans)
                .FirstOrDefaultAsync(h => h.MaHopDong == maHopDong && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            if (fileMinhChung == null || fileMinhChung.Length == 0)
            {
                TempData["Error"] = "Vui lòng chọn tệp hình ảnh minh chứng thanh toán!";
                return RedirectToAction("ContractDetail", new { id = maHopDong });
            }

            var (success, error, path) = await ValidateAndSaveImageAsync(fileMinhChung, "minhchung", "proof", maHopDong);
            if (!success)
            {
                TempData["Error"] = "Tệp minh chứng lỗi: " + error;
                return RedirectToAction("ContractDetail", new { id = maHopDong });
            }

            if (maKyHan.HasValue && maKyHan.Value > 0)
            {
                var kyHan = hopDong.KyHanThanhToans?.FirstOrDefault(k => k.MaKyHan == maKyHan.Value);
                if (kyHan != null)
                {
                    kyHan.HinhAnhBienLai = path;
                    kyHan.TrangThaiXacNhan = 1; // 1: Chờ duyệt đối soát
                    kyHan.NgayGuiBienLai = DateTime.Now;
                    kyHan.GhiChu = ((kyHan.GhiChu ?? "") + $" [Minh chứng tải lên lúc {DateTime.Now:dd/MM/yyyy HH:mm}]").Trim();
                }
            }
            else
            {
                var firstUnpaid = hopDong.KyHanThanhToans?.FirstOrDefault(k => k.TrangThai == 0 || k.TrangThai == 2);
                if (firstUnpaid != null)
                {
                    firstUnpaid.HinhAnhBienLai = path;
                    firstUnpaid.TrangThaiXacNhan = 1;
                    firstUnpaid.NgayGuiBienLai = DateTime.Now;
                    firstUnpaid.GhiChu = ((firstUnpaid.GhiChu ?? "") + $" [Minh chứng tải lên lúc {DateTime.Now:dd/MM/yyyy HH:mm}]").Trim();
                }
                hopDong.GhiChu = ((hopDong.GhiChu ?? "") + $" [Khách đã tải minh chứng thanh toán: {path}]").Trim();
            }

            await _context.SaveChangesAsync();
            TempData["Success"] = "Đã tải lên minh chứng thanh toán thành công! Quản trị viên sẽ đối soát và xác nhận sớm.";
            return RedirectToAction("ContractDetail", new { id = maHopDong });
        }

        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        // Tất toán sớm toàn bộ các kỳ hạn còn lại
        public async Task<IActionResult> TatToanSom(int maHopDong, int hinhThuc = 1, string? ghiChu = null, string? maGiaoDichNganHang = null)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

            var hopDong = await _context.HopDongs
                .Include(h => h.KyHanThanhToans)
                .FirstOrDefaultAsync(h => h.MaHopDong == maHopDong && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            var openKyHans = hopDong.KyHanThanhToans
                .Where(k => k.TrangThai != 1 && k.TrangThai != 3)
                .OrderBy(k => k.SoKyHan)
                .ToList();

            if (!openKyHans.Any())
            {
                TempData["Error"] = "Hợp đồng không còn kỳ hạn nào cần thanh toán!";
                return RedirectToAction("ContractDetail", new { id = maHopDong });
            }

            decimal tongConNo = openKyHans.Sum(k => (k.SoTienPhai - k.SoTienDaTra) + k.PhiPhatTreHan);
            if (tongConNo <= 0)
            {
                TempData["Error"] = "Số tiền còn nợ bằng 0, không cần tất toán!";
                return RedirectToAction("ContractDetail", new { id = maHopDong });
            }

            var phieuThu = new PhieuThu
            {
                MaHopDong = maHopDong,
                LoaiPhieu = 0,
                SoTien = tongConNo,
                NgayGiaoDich = DateTime.Now,
                HinhThucThanhToan = hinhThuc,
                GhiChu = string.IsNullOrEmpty(ghiChu) ? "Khách hàng tất toán sớm toàn bộ hợp đồng" : ghiChu,
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

            await RentalSystem.Areas.Admin.Controllers.HopDongController.SyncTrangThaiThanhToanHopDong(hopDong, _context);
            await _context.SaveChangesAsync();

            TempData["Success"] = $"Đã tất toán toàn bộ các kỳ hạn thành công với số tiền {tongConNo:N0}đ!";
            return RedirectToAction("ContractDetail", new { id = maHopDong });
        }
    }
}
