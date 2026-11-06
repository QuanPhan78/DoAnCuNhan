using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Common;
using RentalSystem.Models;

namespace RentalSystem.Controllers
{
    [Route("api/auth")]
    [ApiController]
    [Authorize(AuthenticationSchemes = ApiTokens.Scheme)]
    public class ApiAuthController : ControllerBase
    {
        private readonly ApplicationDbContext _context;
        private readonly ApiTokens _tokens;

        public ApiAuthController(ApplicationDbContext context, ApiTokens tokens)
        {
            _context = context;
            _tokens = tokens;
        }

        // POST: api/auth/login
        [AllowAnonymous]
        [EnableRateLimiting("ApiLoginLimiter")]
        [HttpPost("login")]
        public async Task<IActionResult> Login([FromBody] LoginRequest request)
        {
            var identifier = request?.GetIdentifier()?.Trim();
            if (request == null || string.IsNullOrWhiteSpace(identifier) || string.IsNullOrWhiteSpace(request.Password))
            {
                return BadRequest(new { message = "Vui lòng nhập đầy đủ email/số điện thoại và mật khẩu." });
            }

            var input = identifier.ToLower();

            // Cho phép đăng nhập bằng Email hoặc Số điện thoại
            var user = await _context.NguoiDungs
                .Include(u => u.VaiTro)
                .FirstOrDefaultAsync(u => (u.Email != null && u.Email.ToLower() == input) || u.SoDienThoai == identifier);

            if (user == null || user.MatKhau != request.Password)
            {
                return Unauthorized(new { message = "Email/Số điện thoại hoặc mật khẩu không chính xác." });
            }

            if (!user.TrangThai)
            {
                return BadRequest(new { message = "Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên." });
            }

            string roleDisplay = MapRoleToDisplay(user.VaiTro?.TenVaiTro);
            string roleCode = user.VaiTro?.TenVaiTro ?? "KhachHang";

            var token = _tokens.Issue(user);

            var userInfo = new
            {
                id = user.MaNguoiDung.ToString(),
                name = user.HoTen,
                email = user.Email ?? "",
                phone = user.SoDienThoai,
                role = roleDisplay,
                roleCode = roleCode,
                address = user.DiaChi ?? "",
                cccd = user.CCCD ?? "",
                status = user.TrangThai
            };

            return Ok(new
            {
                success = true,
                message = "Đăng nhập thành công!",
                user = userInfo,
                token = token
            });
        }

        // POST: api/auth/register
        [AllowAnonymous]
        [HttpPost("register")]
        public async Task<IActionResult> Register([FromBody] RegisterRequest request)
        {
            if (request == null)
            {
                return BadRequest(new { message = "Dữ liệu đăng ký không hợp lệ." });
            }

            var name = request.GetName().Trim();
            var phone = request.GetPhone().Trim();
            var email = request.Email?.Trim() ?? "";
            var password = request.GetPassword();
            var address = request.GetAddress()?.Trim() ?? "";
            var cccd = request.Cccd?.Trim() ?? "";

            if (string.IsNullOrWhiteSpace(name))
                return BadRequest(new { message = "Vui lòng nhập họ và tên." });
            if (string.IsNullOrWhiteSpace(phone))
                return BadRequest(new { message = "Vui lòng nhập số điện thoại." });
            if (string.IsNullOrWhiteSpace(email))
                return BadRequest(new { message = "Vui lòng nhập email." });
            if (string.IsNullOrWhiteSpace(password) || password.Length < 6)
                return BadRequest(new { message = "Mật khẩu phải có ít nhất 6 ký tự." });
            if (!AccountCredentials.IsValidIdentity(cccd))
                return BadRequest(new { message = AccountCredentials.InvalidIdentity });

            var emailNormalized = email.ToLower();
            var phoneNormalized = phone;

            await using var transaction = await AccountCredentials.LockIdentityAsync(_context, cccd);
            if (await AccountCredentials.IdentityExistsAsync(_context, cccd))
                return BadRequest(new { message = AccountCredentials.DuplicateIdentity });

            // Kiểm tra email trùng
            var existingEmail = await _context.NguoiDungs.AnyAsync(u => u.Email != null && u.Email.ToLower() == emailNormalized);
            if (existingEmail)
            {
                return BadRequest(new { message = "Email này đã được đăng ký trong hệ thống." });
            }

            // Kiểm tra số điện thoại trùng
            var existingPhone = await _context.NguoiDungs.AnyAsync(u => u.SoDienThoai == phoneNormalized);
            if (existingPhone)
            {
                return BadRequest(new { message = "Số điện thoại này đã được đăng ký trong hệ thống." });
            }

            // Tìm vai trò KhachHang
            var vaiTroKhachHang = await _context.VaiTros.FirstOrDefaultAsync(v => v.TenVaiTro == "KhachHang");
            if (vaiTroKhachHang == null)
                return StatusCode(StatusCodes.Status503ServiceUnavailable, new { message = "Vai trò khách hàng chưa được cấu hình." });

            var newUser = new NguoiDung
            {
                HoTen = name,
                SoDienThoai = phoneNormalized,
                Email = emailNormalized,
                MatKhau = password,
                MaVaiTro = vaiTroKhachHang.MaVaiTro,
                TrangThai = true,
                DiaChi = address,
                CCCD = cccd
            };

            _context.NguoiDungs.Add(newUser);
            await _context.SaveChangesAsync();
            await transaction.CommitAsync();

            var token = _tokens.Issue(newUser);

            var userInfo = new
            {
                id = newUser.MaNguoiDung.ToString(),
                name = newUser.HoTen,
                email = newUser.Email,
                phone = newUser.SoDienThoai,
                role = "Khách hàng",
                roleCode = "KhachHang",
                address = newUser.DiaChi,
                cccd = newUser.CCCD,
                status = newUser.TrangThai
            };

            return Ok(new
            {
                success = true,
                message = "Đăng ký tài khoản thành công!",
                user = userInfo,
                token = token
            });
        }

        // GET: api/auth/profile/{id}
        [HttpGet("me")]
        [HttpGet("profile/{id:int}")]
        public async Task<IActionResult> GetProfile(int? id)
        {
            int accountId = User.UserId();
            if (id.HasValue && id.Value != accountId) return Forbid(ApiTokens.Scheme);

            var user = await _context.NguoiDungs
                .Include(u => u.VaiTro)
                .FirstOrDefaultAsync(u => u.MaNguoiDung == accountId);

            if (user == null)
            {
                return NotFound(new { message = "Không tìm thấy người dùng." });
            }

            return Ok(new
            {
                id = user.MaNguoiDung.ToString(),
                name = user.HoTen,
                email = user.Email ?? "",
                phone = user.SoDienThoai,
                role = MapRoleToDisplay(user.VaiTro?.TenVaiTro),
                roleCode = user.VaiTro?.TenVaiTro ?? "KhachHang",
                address = user.DiaChi ?? "",
                cccd = user.CCCD ?? "",
                status = user.TrangThai
            });
        }

        // PUT: api/auth/profile/{id}
        [HttpPut("profile/{id}")]
        public async Task<IActionResult> UpdateProfile(int id, [FromBody] UpdateProfileRequest request)
        {
            if (id != User.UserId()) return Forbid(ApiTokens.Scheme);
            var user = await _context.NguoiDungs.Include(u => u.VaiTro).FirstOrDefaultAsync(u => u.MaNguoiDung == id);
            if (user == null)
            {
                return NotFound(new { message = "Không tìm thấy người dùng." });
            }

            var candidate = request.Cccd?.Trim() ?? "";
            bool identityChanged = request.Cccd != null && candidate != (user.CCCD?.Trim() ?? "");
            if (identityChanged && !AccountCredentials.IsValidIdentity(candidate))
                return BadRequest(new { message = AccountCredentials.InvalidIdentity });

            await using var transaction = identityChanged ? await AccountCredentials.LockIdentityAsync(_context, candidate) : null;
            if (identityChanged && await AccountCredentials.IdentityExistsAsync(_context, candidate, id))
                return BadRequest(new { message = AccountCredentials.DuplicateIdentity });

            if (!string.IsNullOrWhiteSpace(request.Name)) user.HoTen = request.Name.Trim();
            if (!string.IsNullOrWhiteSpace(request.Phone)) user.SoDienThoai = request.Phone.Trim();
            if (request.Address != null) user.DiaChi = request.Address.Trim();
            if (identityChanged) user.CCCD = candidate;

            await _context.SaveChangesAsync();
            if (transaction != null) await transaction.CommitAsync();

            return Ok(new
            {
                message = "Cập nhật thông tin thành công!",
                user = new
                {
                    id = user.MaNguoiDung.ToString(),
                    name = user.HoTen,
                    email = user.Email ?? "",
                    phone = user.SoDienThoai,
                    address = user.DiaChi ?? "",
                    cccd = user.CCCD ?? "",
                    role = MapRoleToDisplay(user.VaiTro?.TenVaiTro),
                    roleCode = user.VaiTro?.TenVaiTro ?? "KhachHang"
                }
            });
        }

        // POST: api/auth/change-password
        [HttpPost("change-password")]
        public async Task<IActionResult> ChangePassword([FromBody] ChangePasswordRequest request)
        {
            int accountId = User.UserId();
            if (request.UserId.HasValue && request.UserId.Value != accountId) return Forbid(ApiTokens.Scheme);
            var user = await _context.NguoiDungs.FindAsync(accountId);
            if (user == null)
            {
                return NotFound(new { message = "Không tìm thấy người dùng." });
            }

            var error = AccountCredentials.PasswordError(user.MatKhau, request.OldPassword, request.NewPassword, request.ConfirmPassword);
            if (error != null) return BadRequest(new { message = error });

            user.MatKhau = request.NewPassword;
            await _context.SaveChangesAsync();

            return Ok(new { success = true, message = "Đổi mật khẩu thành công!", token = _tokens.Issue(user) });
        }

        private static string MapRoleToDisplay(string? roleCode)
        {
            if (string.IsNullOrWhiteSpace(roleCode)) return "Khách hàng";
            var normalized = roleCode.Trim().ToLower();

            if (normalized == "admin" || normalized == "quanly" || normalized == "quản trị viên")
                return "Quản lý";
            if (normalized == "kinhdoanh" || normalized == "kythuat" || normalized == "nhanvien" || normalized == "nhân viên")
                return "Nhân viên";
            return "Khách hàng";
        }
    }

    public class LoginRequest
    {
        public string? Email { get; set; }
        public string? EmailOrPhone { get; set; }
        public string? Username { get; set; }
        public string Password { get; set; } = string.Empty;

        public string GetIdentifier()
        {
            if (!string.IsNullOrWhiteSpace(EmailOrPhone)) return EmailOrPhone;
            if (!string.IsNullOrWhiteSpace(Email)) return Email;
            return Username ?? string.Empty;
        }
    }

    public class RegisterRequest
    {
        public string? Name { get; set; }
        public string? HoTen { get; set; }
        public string? Phone { get; set; }
        public string? SoDienThoai { get; set; }
        public string? Email { get; set; }
        public string? Password { get; set; }
        public string? MatKhau { get; set; }
        public string? Address { get; set; }
        public string? DiaChi { get; set; }
        public string? Cccd { get; set; }

        public string GetName() => !string.IsNullOrWhiteSpace(Name) ? Name : (HoTen ?? string.Empty);
        public string GetPhone() => !string.IsNullOrWhiteSpace(Phone) ? Phone : (SoDienThoai ?? string.Empty);
        public string GetPassword() => !string.IsNullOrWhiteSpace(Password) ? Password : (MatKhau ?? string.Empty);
        public string? GetAddress() => !string.IsNullOrWhiteSpace(Address) ? Address : DiaChi;
    }

    public class UpdateProfileRequest
    {
        public string? Name { get; set; }
        public string? Phone { get; set; }
        public string? Address { get; set; }
        public string? Cccd { get; set; }
    }

    public class ChangePasswordRequest
    {
        public int? UserId { get; set; }
        public string OldPassword { get; set; } = string.Empty;
        public string NewPassword { get; set; } = string.Empty;
        public string? ConfirmPassword { get; set; }
    }
}
