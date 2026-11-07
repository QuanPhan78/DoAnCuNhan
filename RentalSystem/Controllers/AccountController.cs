using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using RentalSystem.Common;

namespace RentalSystem.Controllers
{
    // Xử lý xác thực người dùng: Đăng nhập, đăng ký, đổi mật khẩu và quản lý hồ sơ cá nhân
    public class AccountController : Controller
    {
        private readonly ApplicationDbContext _context;

        // Giới hạn số lần đăng nhập sai (tạm khóa 15 phút nếu nhập sai quá 5 lần)
        public static readonly ConcurrentDictionary<string, (int Failures, DateTime LockoutUntil)> LockoutTracker =
            new(StringComparer.OrdinalIgnoreCase);
        private static ConcurrentDictionary<string, (int Failures, DateTime LockoutUntil)> _loginAttempts => LockoutTracker;

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

        // Xử lý đăng nhập
        [EnableRateLimiting("LoginLimiter")]
        [EnableRateLimiter("LoginLimiter")]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Login(string email, string matKhau)
        {
            string normalizedEmail = (email ?? string.Empty).Trim().ToLowerInvariant();

            // Kiểm tra tài khoản có đang bị tạm khóa không
            if (!string.IsNullOrEmpty(normalizedEmail) && LockoutTracker.TryGetValue(normalizedEmail, out var lockoutInfo))
            {
                if (lockoutInfo.LockoutUntil > DateTime.UtcNow)
                {
                    var remainingMinutes = (int)Math.Ceiling((lockoutInfo.LockoutUntil - DateTime.UtcNow).TotalMinutes);
                    ViewBag.Error = $"Tài khoản tạm thời bị khóa do nhập sai mật khẩu 5 lần liên tiếp. Vui lòng thử lại sau {remainingMinutes} phút.";
                    return View();
                }
            }

            var user = await _context.NguoiDungs
                .Include(u => u.VaiTro)
                .FirstOrDefaultAsync(u => u.Email == email && u.MatKhau == matKhau);

            if (user != null)
            {
                // Đăng nhập thành công, xóa số lần đăng nhập sai
                if (!string.IsNullOrEmpty(normalizedEmail))
                {
                    LockoutTracker.TryRemove(normalizedEmail, out _);
                }
                if (user.TrangThai == false)
                {
                    ViewBag.Error = "Tài khoản của bạn đã bị tạm khóa bởi quản trị viên.";
                    return View();
                }

                var rawRole = user.VaiTro?.TenVaiTro?.Trim();
                string canonicalRole = "KhachHang";
                if (string.Equals(rawRole, "Admin", StringComparison.OrdinalIgnoreCase))
                {
                    canonicalRole = "Admin";
                }
                else if (string.Equals(rawRole, "KinhDoanh", StringComparison.OrdinalIgnoreCase))
                {
                    canonicalRole = "KinhDoanh";
                }
                else if (string.Equals(rawRole, "KyThuat", StringComparison.OrdinalIgnoreCase))
                {
                    canonicalRole = "KyThuat";
                }
                else if (string.Equals(rawRole, "KhachHang", StringComparison.OrdinalIgnoreCase))
                {
                    canonicalRole = "KhachHang";
                }
                else if (!string.IsNullOrWhiteSpace(rawRole))
                {
                    canonicalRole = rawRole;
                }

                string displayName = !string.IsNullOrWhiteSpace(user.HoTen)
                    ? user.HoTen.Trim()
                    : (!string.IsNullOrWhiteSpace(user.Email) ? user.Email.Trim() : "Người dùng");

                var claims = new List<Claim>
                {
                    new Claim(ClaimTypes.NameIdentifier, user.MaNguoiDung.ToString()),
                    new Claim(ClaimTypes.Name, displayName),
                    new Claim(ClaimTypes.Email, user.Email ?? ""),
                    new Claim(ClaimTypes.Role, canonicalRole)
                };

                var identity = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
                var principal = new ClaimsPrincipal(identity);

                await HttpContext.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, principal);

                if (canonicalRole == "Admin" || canonicalRole == "KinhDoanh")
                {
                    return RedirectToAction("Index", "Home", new { area = "Admin" });
                }
                if (canonicalRole == "KyThuat")
                {
                    return RedirectToAction("MyTasks", "PhanCong", new { area = "Admin" });
                }
                return RedirectToAction("Index", "Home");
            }

            // Đăng nhập thất bại, tăng số lần đếm và tạm khóa nếu sai 5 lần liên tiếp
            if (!string.IsNullOrEmpty(normalizedEmail))
            {
                var updated = LockoutTracker.AddOrUpdate(
                    normalizedEmail,
                    _ => (1, DateTime.MinValue),
                    (_, current) =>
                    {
                        int newFailures = (current.LockoutUntil != DateTime.MinValue && current.LockoutUntil <= DateTime.UtcNow)
                            ? 1
                            : current.Failures + 1;
                        return (newFailures, DateTime.MinValue);
                    });

                if (updated.Failures >= 5)
                {
                    var lockUntil = DateTime.UtcNow.AddMinutes(15);
                    LockoutTracker[normalizedEmail] = (updated.Failures, lockUntil);
                    ViewBag.Error = "Tài khoản đã bị tạm khóa 15 phút do nhập sai mật khẩu 5 lần liên tiếp.";
                    return View();
                }
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

        // Xử lý đăng ký tài khoản khách hàng mới
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Register(string hoTen, string soDienThoai, string email, string matKhau, string nhapLaiMatKhau, string? cccd)
        {
            cccd = cccd?.Trim() ?? "";
            if (!AccountCredentials.IsValidIdentity(cccd))
            {
                ViewBag.Error = AccountCredentials.InvalidIdentity;
                return View();
            }

            if (string.IsNullOrWhiteSpace(hoTen) || string.IsNullOrWhiteSpace(soDienThoai) || string.IsNullOrWhiteSpace(email))
            {
                ViewBag.Error = "Nhập họ tên, số điện thoại và email.";
                return View();
            }

            if (string.IsNullOrWhiteSpace(matKhau) || matKhau.Length < 6)
            {
                ViewBag.Error = "Mật khẩu cần ít nhất 6 ký tự.";
                return View();
            }

            if (matKhau != nhapLaiMatKhau)
            {
                ViewBag.Error = "Mật khẩu nhập lại không khớp.";
                return View();
            }

            email = email.Trim();
            await using var transaction = await AccountCredentials.LockIdentityAsync(_context, cccd);
            if (await AccountCredentials.IdentityExistsAsync(_context, cccd))
            {
                ViewBag.Error = AccountCredentials.DuplicateIdentity;
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
                HoTen = hoTen.Trim(),
                SoDienThoai = soDienThoai.Trim(),
                Email = email,
                MatKhau = matKhau,
                MaVaiTro = vaiTroKhachHang.MaVaiTro,
                TrangThai = true,
                DiaChi = "",
                CCCD = cccd
            };

            _context.NguoiDungs.Add(newUser);
            await _context.SaveChangesAsync();
            await transaction.CommitAsync();

            TempData["Success"] = "Đăng ký tài khoản thành công! Vui lòng đăng nhập.";
            return RedirectToAction(nameof(Login));
        }

        // Xem thông tin Hồ sơ cá nhân của người dùng đang đăng nhập.
        [Authorize]
        [HttpGet]
        public async Task<IActionResult> Profile()
        {
            var userIdStr = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId)) return RedirectToAction(nameof(Login));


            var user = await _context.NguoiDungs.Include(u => u.VaiTro).FirstOrDefaultAsync(u => u.MaNguoiDung == userId);
            if (user == null) return NotFound();

            return View(user);
        }

        // Cập nhật thông tin cá nhân: Họ tên, Số điện thoại, CCCD, Địa chỉ liên hệ.
        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Profile(string hoTen, string soDienThoai, string? diaChi, string? cccd)
        {
            var userIdStr = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId)) return RedirectToAction(nameof(Login));


            var user = await _context.NguoiDungs.FindAsync(userId);
            if (user == null) return NotFound();

            // MVC binds an empty input to null. The visible CCCD field is included
            // whenever the user submits this form, even when they clear it.
            bool submittedIdentity = cccd != null || (Request.HasFormContentType && Request.Form.ContainsKey("CCCD"));
            string candidate = cccd?.Trim() ?? "";
            bool identityChanged = submittedIdentity && candidate != (user.CCCD?.Trim() ?? "");
            if (identityChanged && !AccountCredentials.IsValidIdentity(candidate))
            {
                TempData["Error"] = AccountCredentials.InvalidIdentity;
                return RedirectToAction(nameof(Profile));
            }

            await using var transaction = identityChanged ? await AccountCredentials.LockIdentityAsync(_context, candidate) : null;
            if (identityChanged && await AccountCredentials.IdentityExistsAsync(_context, candidate, userId))
            {
                TempData["Error"] = AccountCredentials.DuplicateIdentity;
                return RedirectToAction(nameof(Profile));
            }

            if (!string.IsNullOrWhiteSpace(hoTen)) user.HoTen = hoTen.Trim();
            if (!string.IsNullOrWhiteSpace(soDienThoai)) user.SoDienThoai = soDienThoai.Trim();
            user.DiaChi = diaChi?.Trim() ?? "";
            if (identityChanged) user.CCCD = candidate;
            await _context.SaveChangesAsync();
            if (transaction != null) await transaction.CommitAsync();

            TempData["Success"] = "Cập nhật thông tin hồ sơ thành công!";
            return RedirectToAction(nameof(Profile));
        }

        // Đổi mật khẩu tài khoản
        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DoiMatKhau(string? currentPassword, string? newPassword, string? confirmPassword)
        {
            var userIdStr = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId)) 
                return RedirectToAction(nameof(Login));

            var user = await _context.NguoiDungs.FindAsync(userId);
            if (user == null) return NotFound();

            var error = AccountCredentials.PasswordError(user.MatKhau, currentPassword, newPassword, confirmPassword);
            if (error != null)
            {
                TempData["Error"] = error;
                return RedirectToAction(nameof(Profile));
            }

            user.MatKhau = newPassword!;
            await _context.SaveChangesAsync();

            TempData["Success"] = "Đổi mật khẩu thành công!";
            return RedirectToAction(nameof(Profile));
        }

        // Sổ công nợ khách hàng: hiển thị tổng dư nợ, kỳ hạn sắp đến hạn, quá hạn và tiền phạt
        [Authorize]
        [HttpGet]
        public async Task<IActionResult> MyDebt()
        {
            var userIdStr = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
                return RedirectToAction(nameof(Login));

            var user = await _context.NguoiDungs.FindAsync(userId);
            if (user == null)
                return NotFound();

            // Lấy tất cả hợp đồng của khách hàng (loại trừ đã hủy) kèm các thông tin liên quan
            var hopDongs = await _context.HopDongs
                .Include(h => h.KhachHang)
                .Include(h => h.KyHanThanhToans)
                .Include(h => h.PhieuBaoTris)
                    .ThenInclude(b => b.ThietBi)
                    .ThenInclude(t => t.SanPham)
                .Include(h => h.PhieuThus)
                .Where(h => h.MaKhachHang == userId && h.TrangThai != 3)
                .OrderByDescending(h => h.NgayBatDau)
                .ToListAsync();

            // Cập nhật tự động trạng thái quá hạn và phí phạt trễ hạn cho tất cả kỳ hạn
            var allKyHans = hopDongs
                .SelectMany(h => h.KyHanThanhToans ?? Enumerable.Empty<KyHanThanhToan>())
                .ToList();
            RentalSystem.Areas.Admin.Controllers.HopDongController.CapNhatTreHanVaPhiPhat(allKyHans);
            await _context.SaveChangesAsync();

            // Tổng dư nợ các hợp đồng
            decimal totalDebt = 0m;
            decimal totalReceivableAll = 0m;
            decimal totalCollectedAll = 0m;
            foreach (var hd in hopDongs)
            {
                var (receivable, collected, remaining) = DebtCalculationHelper.CalculateContractDebt(hd);
                totalReceivableAll += receivable;
                totalCollectedAll += collected;
                totalDebt += Math.Max(0m, remaining);
            }

            var today = DateTime.Today;
            // Các kỳ thu thông thường. Hợp đồng chờ bàn giao dùng luồng thanh toán lần đầu.
            var unpaidKyHans = allKyHans
                .Where(k => DebtCalculationHelper.IsPayableInstallment(k) &&
                    Math.Max(0m, k.SoTienPhai - k.SoTienDaTra) + k.TienPhat > 0m)
                .OrderBy(k => k.NgayDenHan)
                .ToList();

            // Kỳ hạn sắp đến hạn trong 7 ngày tới
            var upcomingLimit = today.AddDays(7);
            var upcomingInstallments = unpaidKyHans
                .Where(k => k.NgayDenHan.Date >= today && k.NgayDenHan.Date <= upcomingLimit)
                .OrderBy(k => k.NgayDenHan)
                .ToList();
            decimal upcomingRentAmount = upcomingInstallments.Sum(k => Math.Max(0m, k.SoTienPhai - k.SoTienDaTra));

            // Kỳ hạn đã quá hạn thanh toán
            var overdueInstallments = unpaidKyHans
                .Where(k => DebtCalculationHelper.DaysPastDue(k, today) > 0)
                .OrderBy(k => k.NgayDenHan)
                .ToList();
            decimal totalOverdueDebt = overdueInstallments.Sum(k => Math.Max(0m, k.SoTienPhai - k.SoTienDaTra + k.TienPhat));

            // Tiền phạt trễ hạn
            decimal totalLateFee = allKyHans.Sum(k => k.TienPhat);

            // Phiếu bảo trì có phí đền bù
            var damageTickets = hopDongs
                .SelectMany(h => h.PhieuBaoTris ?? Enumerable.Empty<PhieuBaoTri>())
                .Where(b => b.PhiDenBu > 0)
                .OrderByDescending(b => b.NgayBaoLoi)
                .ToList();

            decimal totalDamageFees = damageTickets.Sum(b => b.PhiDenBu);
            decimal paidDamageFees = hopDongs
                .SelectMany(h => h.PhieuThus ?? Enumerable.Empty<PhieuThu>())
                .Where(p => !p.DaHuy && p.LoaiPhieu == 2)
                .Sum(p => p.SoTien);
            decimal unpaidDamageFees = Math.Max(0m, totalDamageFees - paidDamageFees);

            // Kiểm tra khách hàng có bị hạn chế đặt thuê do nợ xấu hay không
            bool isBlacklisted = DebtCalculationHelper.IsCustomerBlacklisted(userId, _context, out string blacklistReason);

            ViewBag.User = user;
            ViewBag.HopDongs = hopDongs;
            ViewBag.AllKyHans = allKyHans;
            ViewBag.UnpaidKyHans = unpaidKyHans;
            ViewBag.Today = today;
            ViewBag.UpcomingInstallments = upcomingInstallments;
            ViewBag.UpcomingRentAmount = upcomingRentAmount;
            ViewBag.OverdueInstallments = overdueInstallments;
            ViewBag.TotalOverdueDebt = totalOverdueDebt;
            ViewBag.DamageTickets = damageTickets;
            ViewBag.TotalDamageFees = totalDamageFees;
            ViewBag.PaidDamageFees = paidDamageFees;
            ViewBag.UnpaidDamageFees = unpaidDamageFees;
            ViewBag.TotalLateFee = totalLateFee;
            ViewBag.TotalDebt = totalDebt;
            ViewBag.TotalReceivableAll = totalReceivableAll;
            ViewBag.TotalCollectedAll = totalCollectedAll;
            ViewBag.IsBlacklisted = isBlacklisted;
            ViewBag.BlacklistReason = blacklistReason;

            return View(hopDongs);
        }

        // Mở trang từ chối quyền truy cập (Access Denied)
        [HttpGet]
        public IActionResult AccessDenied()
        {
            if (Response != null)
            {
                Response.StatusCode = StatusCodes.Status403Forbidden;
            }
            return View();
        }

        // Trung tâm thông báo của người dùng
        [Authorize]
        [HttpGet]
        public async Task<IActionResult> ThongBao()
        {
            var userIdStr = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
            {
                return Challenge();
            }

            var thongBaos = await _context.ThongBaos
                .Where(t => t.MaNguoiDung == userId)
                .OrderByDescending(t => t.NgayTao)
                .ToListAsync();

            ViewBag.UnreadCount = thongBaos.Count(t => !t.DaDoc);
            return View(thongBaos);
        }

        // Đánh dấu thông báo đã đọc
        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DanhDauDaDoc(int? id, string? returnUrl = null)
        {
            var userIdStr = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
            {
                return Challenge();
            }

            if (id.HasValue)
            {
                var tb = await _context.ThongBaos.FirstOrDefaultAsync(t => t.MaThongBao == id.Value && t.MaNguoiDung == userId);
                if (tb != null)
                {
                    tb.DaDoc = true;
                    await _context.SaveChangesAsync();
                }
            }
            else
            {
                var unreadList = await _context.ThongBaos.Where(t => t.MaNguoiDung == userId && !t.DaDoc).ToListAsync();
                foreach (var tb in unreadList)
                {
                    tb.DaDoc = true;
                }
                await _context.SaveChangesAsync();
                TempData["Success"] = "Đã đánh dấu tất cả thông báo là đã đọc!";
            }

            if (!string.IsNullOrEmpty(returnUrl) && Url.IsLocalUrl(returnUrl))
            {
                return Redirect(returnUrl);
            }
            return RedirectToAction(nameof(ThongBao));
        }

        // Đăng xuất khỏi hệ thống: Xóa sạch Cookie xác thực và đưa về Trang chủ.
        public async Task<IActionResult> Logout()
        {
            HttpContext.Session?.Clear();
            await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
            return RedirectToAction("Index", "Home");
        }
    }
}

namespace Microsoft.AspNetCore.RateLimiting
{
    // Cấu hình Rate Limiter
    [AttributeUsage(AttributeTargets.Class | AttributeTargets.Method, AllowMultiple = false, Inherited = true)]
    public sealed class EnableRateLimiterAttribute : Attribute
    {
        public string PolicyName { get; }
        public EnableRateLimiterAttribute(string policyName)
        {
            PolicyName = policyName;
        }
    }
}
