using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System.Collections.Generic;
using System.Security.Claims;
using System.Threading.Tasks;

namespace RentalSystem.Controllers
{
    // Controller xử lý Xác thực & Tài khoản: Đăng nhập, Đăng ký, Đăng xuất, Hồ sơ cá nhân.
    // Sử dụng Cookie Authentication dựa trên Claims-based Identity.
    public class AccountController : Controller
    {
        private readonly ApplicationDbContext _context;

        public AccountController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Mở trang Đăng nhập. Nếu người dùng đã đăng nhập rồi thì tự động chuyển về trang chủ.
        [HttpGet]
        public IActionResult Login()
        {
            if (User.Identity != null && User.Identity.IsAuthenticated)
            { 
                return RedirectToAction("Index", "Home"); 
            }
            return View();
        }

        // Xử lý Đăng nhập:
        // 1. Kiểm tra Email và Mật khẩu trong CSDL.
        // 2. Kiểm tra xem tài khoản có bị khóa (TrangThai == false) hay không.
        // 3. Khởi tạo Claims (Id, Họ tên, Email, Vai trò) và tạo Cookie phiên làm việc.
        // 4. Điều hướng: Nếu là Admin/Kinh Doanh thì vào trang quản trị Admin, Khách hàng thì ra trang chủ.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Login(string email, string matKhau)
        {
            var user = await _context.NguoiDungs
                .Include(u => u.VaiTro)
                .FirstOrDefaultAsync(u => u.Email == email && u.MatKhau == matKhau);

            if (user != null)
            {
                if (user.TrangThai == false)
                {
                    ViewBag.Error = "Tài khoản của bạn đã bị tạm khóa bởi quản trị viên.";
                    return View();
                }

                var claims = new List<Claim>
                {
                    new Claim(ClaimTypes.NameIdentifier, user.MaNguoiDung.ToString()),
                    new Claim(ClaimTypes.Name, user.HoTen ?? ""),
                    new Claim(ClaimTypes.Email, user.Email ?? ""),
                    new Claim(ClaimTypes.Role, user.VaiTro?.TenVaiTro ?? "KhachHang")
                };

                var identity = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
                var principal = new ClaimsPrincipal(identity);

                await HttpContext.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, principal);

                if (user.VaiTro?.TenVaiTro == "Admin" || user.VaiTro?.TenVaiTro == "KinhDoanh")
                {
                    return RedirectToAction("Index", "Home", new { area = "Admin" });
                }
                return RedirectToAction("Index", "Home");
            }

            ViewBag.Error = "Email hoặc mật khẩu không chính xác.";
            return View();
        }

        // Mở form Đăng ký tài khoản khách hàng mới.
        [HttpGet]
        public IActionResult Register()
        {
            if (User.Identity != null && User.Identity.IsAuthenticated) return RedirectToAction("Index", "Home");
            return View();
        }

        // Tiếp nhận thông tin Đăng ký tài khoản Khách Hàng:
        // 1. Kiểm tra xác nhận mật khẩu.
        // 2. Kiểm tra email đã tồn tại hay chưa.
        // 3. Gán mặc định vai trò 'KhachHang' và lưu vào hệ thống.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Register(string hoTen, string soDienThoai, string email, string matKhau, string nhapLaiMatKhau)
        {
            if (matKhau != nhapLaiMatKhau)
            {
                ViewBag.Error = "Mật khẩu nhập lại không khớp.";
                return View();
            }

            var existingUser = await _context.NguoiDungs.FirstOrDefaultAsync(u => u.Email == email);
            if (existingUser != null)
            {
                ViewBag.Error = "Email này đã được đăng ký trong hệ thống.";
                return View();
            }

            var vaiTroKhachHang = await _context.VaiTros.FirstOrDefaultAsync(v => v.TenVaiTro == "KhachHang");
            if (vaiTroKhachHang == null)
            {
                ViewBag.Error = "Lỗi cấu hình: Không tìm thấy vai trò Khách Hàng trong CSDL.";
                return View();
            }

            var newUser = new NguoiDung
            {
                HoTen = hoTen,
                SoDienThoai = soDienThoai,
                Email = email,
                MatKhau = matKhau,
                MaVaiTro = vaiTroKhachHang.MaVaiTro,
                TrangThai = true,
                DiaChi = "",
                CCCD = ""
            };

            _context.NguoiDungs.Add(newUser);
            await _context.SaveChangesAsync();

            TempData["Success"] = "Đăng ký tài khoản thành công! Vui lòng đăng nhập.";
            return RedirectToAction(nameof(Login));
        }

        // Xem thông tin Hồ sơ cá nhân của người dùng đang đăng nhập.
        [HttpGet]
        public async Task<IActionResult> Profile()
        {
            var userIdStr = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr)) return RedirectToAction(nameof(Login));

            int userId = int.Parse(userIdStr);
            var user = await _context.NguoiDungs.Include(u => u.VaiTro).FirstOrDefaultAsync(u => u.MaNguoiDung == userId);
            if (user == null) return NotFound();

            return View(user);
        }

        // Cập nhật thông tin cá nhân: Họ tên, Số điện thoại, CCCD, Địa chỉ liên hệ.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Profile(NguoiDung model)
        {
            var userIdStr = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr)) return RedirectToAction(nameof(Login));

            int userId = int.Parse(userIdStr);
            var user = await _context.NguoiDungs.FindAsync(userId);
            if (user == null) return NotFound();

            user.HoTen = model.HoTen;
            user.SoDienThoai = model.SoDienThoai;
            user.DiaChi = model.DiaChi;
            user.CCCD = model.CCCD;

            if (!string.IsNullOrEmpty(model.MatKhau))
            {
                user.MatKhau = model.MatKhau;
            }

            _context.Update(user);
            await _context.SaveChangesAsync();

            TempData["Success"] = "Cập nhật thông tin hồ sơ thành công!";
            return RedirectToAction(nameof(Profile));
        }

        // Đăng xuất khỏi hệ thống: Xóa sạch Cookie xác thực và đưa về Trang chủ.
        public async Task<IActionResult> Logout()
        {
            await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
            return RedirectToAction("Index", "Home");
        }
    }
}
