using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System.ComponentModel.DataAnnotations;

namespace RentalSystem.Controllers
{
    [Route("api/auth")]
    [ApiController]
    public class ApiAuthController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public ApiAuthController(ApplicationDbContext context)
        {
            _context = context;
        }

        // POST: api/auth/login
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

            var token = new
            {
                accessToken = $"token_{Guid.NewGuid():N}",
                access_token = $"token_{Guid.NewGuid():N}",
                refreshToken = $"refresh_{Guid.NewGuid():N}",
                refresh_token = $"refresh_{Guid.NewGuid():N}",
                expiresIn = DateTime.UtcNow.AddDays(7).ToString("o"),
                expires_in = DateTime.UtcNow.AddDays(7).ToString("o")
            };

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

            var emailNormalized = email.ToLower();
            var phoneNormalized = phone;

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
            int roleId = vaiTroKhachHang?.MaVaiTro ?? 4;

            var newUser = new NguoiDung
            {
                HoTen = name,
                SoDienThoai = phoneNormalized,
                Email = emailNormalized,
                MatKhau = password,
                MaVaiTro = roleId,
                TrangThai = true,
                DiaChi = address,
                CCCD = cccd
            };

            _context.NguoiDungs.Add(newUser);
            await _context.SaveChangesAsync();

            var token = new
            {
                accessToken = $"token_{Guid.NewGuid():N}",
                access_token = $"token_{Guid.NewGuid():N}",
                refreshToken = $"refresh_{Guid.NewGuid():N}",
                refresh_token = $"refresh_{Guid.NewGuid():N}",
                expiresIn = DateTime.UtcNow.AddDays(7).ToString("o"),
                expires_in = DateTime.UtcNow.AddDays(7).ToString("o")
            };

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
        [HttpGet("profile/{id}")]
        public async Task<IActionResult> GetProfile(int id)
        {
            var user = await _context.NguoiDungs
                .Include(u => u.VaiTro)
                .FirstOrDefaultAsync(u => u.MaNguoiDung == id);

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
            var user = await _context.NguoiDungs.FindAsync(id);
            if (user == null)
            {
                return NotFound(new { message = "Không tìm thấy người dùng." });
            }

            if (!string.IsNullOrWhiteSpace(request.Name)) user.HoTen = request.Name.Trim();
            if (!string.IsNullOrWhiteSpace(request.Phone)) user.SoDienThoai = request.Phone.Trim();
            if (request.Address != null) user.DiaChi = request.Address.Trim();
            if (request.Cccd != null) user.CCCD = request.Cccd.Trim();

            await _context.SaveChangesAsync();

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
                    cccd = user.CCCD ?? ""
                }
            });
        }

        // POST: api/auth/change-password
        [HttpPost("change-password")]
        public async Task<IActionResult> ChangePassword([FromBody] ChangePasswordRequest request)
        {
            var user = await _context.NguoiDungs.FindAsync(request.UserId);
            if (user == null)
            {
                return NotFound(new { message = "Không tìm thấy người dùng." });
            }

            if (user.MatKhau != request.OldPassword)
            {
                return BadRequest(new { message = "Mật khẩu hiện tại không chính xác." });
            }

            if (string.IsNullOrWhiteSpace(request.NewPassword) || request.NewPassword.Length < 6)
            {
                return BadRequest(new { message = "Mật khẩu mới phải có ít nhất 6 ký tự." });
            }

            user.MatKhau = request.NewPassword;
            await _context.SaveChangesAsync();

            return Ok(new { message = "Đổi mật khẩu thành công!" });
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
        public int UserId { get; set; }
        public string OldPassword { get; set; } = string.Empty;
        public string NewPassword { get; set; } = string.Empty;
    }
}
