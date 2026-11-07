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

            // Giới hạn giỏ theo số máy có thể cho thuê. Lịch cụ thể được kiểm tra ở bước chọn ngày.
            int available = await _context.ThietBis.CountAsync(t => t.MaSanPham == id && RentalBooking.RentableStatuses.Contains(t.TrangThai));
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
                        // Giới hạn số lượng theo số máy có thể cho thuê.
                        int available = await _context.ThietBis.CountAsync(t => t.MaSanPham == id && RentalBooking.RentableStatuses.Contains(t.TrangThai));
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

            try
            {
                var promo = await RentalBooking.FindPromotionAsync(_context, code, DateTime.Now, HttpContext.RequestAborted);
                return Json(new { success = true, code = promo!.Code, discountPercent = promo.PhanTramGiam,
                    message = $"Áp dụng mã {promo.Code}, giảm {promo.PhanTramGiam}%." });
            }
            catch (RentalBookingException error)
            {
                return Json(new { success = false, message = error.Message });
            }
        }

        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Quote(DateTime? ngayBatDau, DateTime? ngayKetThuc, string? diaChi, string? promoCode)
        {
            if (!int.TryParse(User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value, out int userId))
                return Unauthorized();

            try
            {
                var order = CartOrder(ngayBatDau, ngayKetThuc, diaChi, promoCode);
                return Json(await RentalBooking.QuoteAsync(_context, userId, order, HttpContext.RequestAborted));
            }
            catch (RentalBookingException error)
            {
                return StatusCode(error.StatusCode, new { message = error.Message });
            }
        }

        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Checkout(DateTime? NgayBatDau, DateTime? NgayKetThuc, string? DiaChi,
            string? PromoCode, string? ExpectedTotal = null)
        {
            if (!int.TryParse(User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value, out int userId))
                return RedirectToAction("Login", "Account", new { returnUrl = "/Cart/Checkout" });

            var order = CartOrder(NgayBatDau, NgayKetThuc, DiaChi, PromoCode);
            if (order.Lines.Count == 0) return RedirectToAction("Index");
            if (!string.IsNullOrWhiteSpace(ExpectedTotal))
            {
                if (!decimal.TryParse(ExpectedTotal, System.Globalization.NumberStyles.AllowDecimalPoint,
                    System.Globalization.CultureInfo.InvariantCulture, out decimal quoted))
                {
                    TempData["Error"] = "Tổng tiền tạm tính không hợp lệ. Vui lòng kiểm tra lại.";
                    return RedirectToAction(nameof(Checkout));
                }
                order = order with { ExpectedTotal = quoted };
            }

            await InventoryLock.WaitAsync();
            try
            {
                var (contract, _, _, _) = await RentalBooking.CreateAsync(_context, userId, order, HttpContext.RequestAborted);
                HttpContext.Session.Remove("GioHang");
                TempData["Success"] = "Đã gửi yêu cầu thuê. Vui lòng hoàn tất bước ký hợp đồng.";
                return RedirectToAction(nameof(SignContract), new { id = contract.MaHopDong });
            }
            catch (RentalBookingException error)
            {
                TempData["Error"] = error.Message;
                return RedirectToAction(nameof(Checkout));
            }
            finally
            {
                InventoryLock.Release();
            }
        }

        private RentalOrder CartOrder(DateTime? start, DateTime? end, string? address, string? promoCode)
        {
            var cart = HttpContext.Session.Get<List<CartItem>>("GioHang") ?? new List<CartItem>();
            return new RentalOrder(start, end, address, null, promoCode,
                cart.Select(item => new RentalLine(item.MaSanPham, item.SoLuong)).ToArray());
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

            if (!FirstContractPayment.IsPendingHandover(hopDong))
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

            if (hopDong.TrangThai != 0 || hopDong.YeuCauHuy)
                return RedirectToAction(nameof(ContractDetail), new { id });

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

            try
            {
                bool legacy = cmndTruocFile == null && cmndFile != null;
                var contract = await RentalSystem.Services.ContractDocuments.SignAsync(_context, _env, userId, id,
                    soKyHan, cmndTruocFile ?? cmndFile, cmndSauFile, signatureData, legacy, HttpContext.RequestAborted);
                if (contract == null) return NotFound();
                TempData["Success"] = "Đã ký hợp đồng thành công!";
                return contract.YeuCauThanhToanLanDau
                    ? RedirectToAction(nameof(ContractDetail), new { id })
                    : RedirectToAction(nameof(MyContracts));
            }
            catch (RentalBookingException error)
            {
                TempData["Error"] = error.Message;
                return RedirectToAction(nameof(SignContract), new { id });
            }
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
            if (!string.IsNullOrEmpty(hopDong.ChuKyKhachHang) || hopDong.TrangThai != 0 || hopDong.YeuCauHuy)
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

            await using var transaction = await RentalBooking.BeginInventoryAsync(_context, HttpContext.RequestAborted);
            var hopDong = await _context.HopDongs
                .FirstOrDefaultAsync(h => h.MaHopDong == id && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            if (!string.IsNullOrEmpty(hopDong.ChuKyKhachHang) || hopDong.TrangThai != 0 || hopDong.YeuCauHuy)
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
            int days = RentalBooking.RentalDays(NgayBatDau, NgayKetThuc);

            var chiTiets = await _context.ChiTietHopDongs
                .Include(c => c.ThietBi).ThenInclude(t => t.SanPham)
                .Where(c => c.MaHopDong == id)
                .ToListAsync();

            // Kiểm tra xem thiết bị có bị trùng lịch thuê với hợp đồng khác không
            foreach (var ct in chiTiets)
            {
                bool conflict = await RentalBooking.OverlappingReservations(_context, NgayBatDau, NgayKetThuc)
                    .AnyAsync(other => other.MaThietBi == ct.MaThietBi && other.MaHopDong != id);
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

            hopDong.NgayBatDau = NgayBatDau.Date;
            hopDong.NgayKetThuc = NgayKetThuc.Date;
            hopDong.TongTien = tongTienMoi;
            hopDong.GhiChu = GhiChu ?? "";
            
            int maxInstallments = Math.Max(1, (int)Math.Floor(days / 7.0));
            if (hopDong.SoKyHan > maxInstallments) hopDong.SoKyHan = maxInstallments;

            await _context.SaveChangesAsync();
            await transaction.CommitAsync();
            TempData["Success"] = $"Đã cập nhật đơn hàng #{id} thành công! Tổng tiền mới: {tongTienMoi:N0}đ.";
            return RedirectToAction("MyContracts");
        }

        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public Task<IActionResult> DeleteContract(int id, string? lyDo = null) => YeuCauHuy(id, lyDo);

        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        // Khách hàng gửi yêu cầu hủy đơn hàng khi đang chờ duyệt
        public async Task<IActionResult> YeuCauHuy(int id, string? lyDo)
        {
            if (!int.TryParse(User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value, out int userId))
                return RedirectToAction("Login", "Account");

            try
            {
                var contract = await ContractLifecycle.RequestCancellationAsync(_context, userId, id, lyDo,
                    HttpContext.RequestAborted);
                if (contract == null) return NotFound();
                TempData["Success"] = "Đã gửi yêu cầu hủy. Vui lòng chờ duyệt.";
            }
            catch (RentalBookingException error)
            {
                TempData["Error"] = error.Message;
            }
            return RedirectToAction(nameof(ContractDetail), new { id });
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

            try
            {
                var request = await RentalSystem.Services.ContractRenewal.RequestAsync(_context, userId, id,
                    soNgayGiaHan, lyDo, HttpContext.RequestAborted);
                if (request == null) return NotFound();
                TempData["Success"] = $"Đã gửi yêu cầu gia hạn thêm {soNgayGiaHan} ngày. Vui lòng chờ duyệt!";
            }
            catch (RentalBookingException error)
            {
                TempData["Error"] = error.Message;
            }
            return RedirectToAction(nameof(ContractDetail), new { id });
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

            try
            {
                var row = await RentalSystem.Services.ContractDocuments.ReceiptAsync(_context, _env, userId,
                    maKyHan, maGiaoDich, hinhAnhBienLai, HttpContext.RequestAborted);
                if (row == null) return NotFound();
                TempData["Success"] = "Đã gửi biên lai. Vui lòng chờ nhân viên đối soát.";
                return RedirectToAction(nameof(ContractDetail), new { id = row.MaHopDong });
            }
            catch (RentalBookingException error)
            {
                TempData["Error"] = error.Message;
                return RedirectToAction("MyDebt", "Account");
            }
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
            if (FirstContractPayment.IsPendingHandover(hopDong))
                return RedirectToAction(nameof(ContractDetail), new { id = maHopDong });


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

            var contract = await _context.HopDongs.FirstOrDefaultAsync(h => h.MaHopDong == maHopDong && h.MaKhachHang == userId);
            if (contract == null) return NotFound();
            TempData["Warning"] = "Vui lòng thanh toán qua chuyển khoản hoặc VNPay và chờ xác nhận. Gửi yêu cầu không tự ghi nhận đã thu tiền.";
            return RedirectToAction("MyDebt", "Account");
        }
    }
}
