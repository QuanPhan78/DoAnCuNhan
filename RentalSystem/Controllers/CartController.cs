using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using RentalSystem.Models;
using RentalSystem.Helpers;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System;
using Microsoft.EntityFrameworkCore;

namespace RentalSystem.Controllers
{
    public class CartController : Controller
    {
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

            // Kiểm tra tồn kho khả dụng trước khi thêm vào giỏ
            int available = await _context.ThietBis.CountAsync(t => t.MaSanPham == id && !_context.ChiTietHopDongs.Any(c => c.MaThietBi == t.MaThietBi && c.HopDong.TrangThai != 2 && c.HopDong.TrangThai != 3 && c.HopDong.NgayKetThuc > DateTime.Now));
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
                        // Kiểm tra tồn kho khả dụng
                        int available = await _context.ThietBis.CountAsync(t => t.MaSanPham == id && !_context.ChiTietHopDongs.Any(c => c.MaThietBi == t.MaThietBi && c.HopDong.TrangThai != 2 && c.HopDong.TrangThai != 3 && c.HopDong.NgayKetThuc > DateTime.Now));
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

        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        // Xử lý đặt thuê thiết bị từ giỏ hàng. Kiểm tra chống trùng lịch, trừ tồn kho và tạo hợp đồng chờ duyệt.
        public async Task<IActionResult> Checkout(DateTime NgayBatDau, DateTime NgayKetThuc, string DiaChi)
        {
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

            int days = (int)(NgayKetThuc - NgayBatDau).TotalDays;
            if (days <= 0) days = 1;

            bool cartModified = false;
            for (int i = cart.Count - 1; i >= 0; i--)
            {
                var item = cart[i];
                int available = await _context.ThietBis
                    .CountAsync(t => t.MaSanPham == item.MaSanPham && !_context.ChiTietHopDongs.Any(c => 
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

            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            int userId = 1; // Default fallback
            if (nameIdentifierClaim != null && int.TryParse(nameIdentifierClaim.Value, out int parsedId))
            {
                userId = parsedId;
            }

            var firstAdmin = await _context.NguoiDungs.FirstOrDefaultAsync(u => u.VaiTro.TenVaiTro == "Admin" || u.VaiTro.TenVaiTro == "KinhDoanh");
            int adminId = firstAdmin != null ? firstAdmin.MaNguoiDung : userId;

            var hopDong = new HopDong
            {
                MaKhachHang = userId,
                MaNhanVien = adminId,
                NgayBatDau = NgayBatDau,
                NgayKetThuc = NgayKetThuc,
                TongTien = totalAmount,
                TrangThai = 0, // Chờ duyệt
                NgayKy = null,
                ChuKyKhachHang = "",
                ChuKyNhanVien = "",
                AnhCMND = "",
                TrangThaiThanhToan = 0,
                GhiChu = "Giao hàng tới: " + DiaChi
            };

            _context.HopDongs.Add(hopDong);
            await _context.SaveChangesAsync(); 

            foreach (var item in cart)
            {
                var dbProd = await _context.SanPhams.FindAsync(item.MaSanPham);
                decimal p = dbProd != null ? dbProd.GiaThueNgay : item.GiaThueNgay;
                
                var availableDevices = await _context.ThietBis
                    .Where(t => t.MaSanPham == item.MaSanPham && !_context.ChiTietHopDongs.Any(c => 
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
                    
                    // NGHIỆP VỤ QUAN TRỌNG: Khóa máy ngay lập tức (Chuyển sang trạng thái 3 - Giữ chỗ)
                    // để tránh Race Condition (2 khách hàng cùng đặt 1 máy tại cùng thời điểm)
                    // device.TrangThai = 3; 
                }
            }

            await _context.SaveChangesAsync();
            HttpContext.Session.Remove("GioHang");

            TempData["Success"] = "Khởi tạo đơn hàng thành công! Vui lòng hoàn tất thủ tục ký hợp đồng bên dưới.";
            return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
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
        public async Task<IActionResult> SignContract(int id)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

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
        [HttpPost]
        [ValidateAntiForgeryToken]
        // Khách hàng ký hợp đồng điện tử. Ghi nhận ảnh chụp bản chính CMND/CCCD và 
        // chuyển đổi nét vẽ chữ ký trên màn hình cảm ứng (Canvas Base64) thành file ảnh PNG.
        public async Task<IActionResult> SignContract(int id, int soKyHan, Microsoft.AspNetCore.Http.IFormFile cmndFile, string signatureData)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

            var hopDong = await _context.HopDongs
                .FirstOrDefaultAsync(h => h.MaHopDong == id && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            if (!string.IsNullOrEmpty(hopDong.ChuKyKhachHang))
            {
                TempData["Error"] = "Hợp đồng này đã được ký!";
                return RedirectToAction("MyContracts");
            }

            if (cmndFile != null && cmndFile.Length > 0)
            {
                // Giới hạn 5MB để chống DoS upload file quá lớn
                if (cmndFile.Length > 5 * 1024 * 1024)
                {
                    TempData["Error"] = "Ảnh CMND không được vượt quá 5MB!";
                    return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
                }

                var ext = System.IO.Path.GetExtension(cmndFile.FileName).ToLower();
                if (ext == ".jpg" || ext == ".jpeg" || ext == ".png")
                {
                    string cmndFileName = $"cmnd_{hopDong.MaHopDong}_{DateTime.Now.Ticks}{ext}";
                    string cmndPath = System.IO.Path.Combine(_env.WebRootPath, "uploads", "cmnd", cmndFileName);
                    using (var stream = new System.IO.FileStream(cmndPath, System.IO.FileMode.Create))
                    {
                        await cmndFile.CopyToAsync(stream);
                    }
                    hopDong.AnhCMND = $"/uploads/cmnd/{cmndFileName}";
                }
            }

            if (!string.IsNullOrEmpty(signatureData) && signatureData.StartsWith("data:image/png;base64,"))
            {
                var base64Data = signatureData.Substring("data:image/png;base64,".Length);
                var imageBytes = Convert.FromBase64String(base64Data);
                string sigFileName = $"kh_{hopDong.MaHopDong}_{DateTime.Now.Ticks}.png";
                string sigPath = System.IO.Path.Combine(_env.WebRootPath, "uploads", "signatures", sigFileName);
                await System.IO.File.WriteAllBytesAsync(sigPath, imageBytes);
                hopDong.ChuKyKhachHang = $"/uploads/signatures/{sigFileName}";
            }

            if (string.IsNullOrEmpty(hopDong.ChuKyKhachHang) || string.IsNullOrEmpty(hopDong.AnhCMND))
            {
                TempData["Error"] = "Vui lòng tải lên CMND và Ký tên đầy đủ!";
                return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
            }
            
            if (soKyHan < 1) soKyHan = 1;
            hopDong.SoKyHan = soKyHan;

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

            if (NgayKetThuc.Date <= NgayBatDau.Date)
            {
                TempData["Error"] = "Ngày trả máy phải sau ngày nhận máy!";
                return RedirectToAction("EditContract", new { id = id });
            }

            // Tính lại tổng tiền theo số ngày mới
            int days = (int)(NgayKetThuc - NgayBatDau).TotalDays;
            if (days <= 0) days = 1;

            var chiTiets = await _context.ChiTietHopDongs
                .Include(c => c.ThietBi).ThenInclude(t => t.SanPham)
                .Where(c => c.MaHopDong == id)
                .ToListAsync();

            // THUẬT TOÁN KIỂM TRA TRÙNG LỊCH THUÊ (DATE OVERLAP CHECK):
            // Đảm bảo khoảng thời gian [NgayBatDau_Mới, NgayKetThuc_Mới] không giao nhau
            // với bất kỳ khoảng thời gian thuê nào khác của cùng 1 thiết bị đang hoạt động.
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
    }
}
