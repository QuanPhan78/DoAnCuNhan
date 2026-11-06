using Microsoft.AspNetCore.Authorization;
using RentalSystem.Common;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using RentalSystem.Services;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Controllers
{
    [Route("api/maintenance")]
    [ApiController]
    [Authorize(AuthenticationSchemes = ApiTokens.Scheme)]
    public class ApiMaintenanceController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        private readonly IWebHostEnvironment _environment;

        public ApiMaintenanceController(ApplicationDbContext context, IWebHostEnvironment environment)
        {
            _context = context;
            _environment = environment;
        }

        // GET: api/maintenance
        [HttpGet]
        public async Task<IActionResult> GetTickets([FromQuery] int? contractId)
        {
            IQueryable<PhieuBaoTri> query = _context.PhieuBaoTris.VisibleTickets(User)
                .Include(p => p.HopDong)
                    .ThenInclude(h => h.KhachHang)
                .Include(p => p.ThietBi)
                    .ThenInclude(t => t.SanPham)
                .Include(p => p.KyThuatVien);

            if (contractId.HasValue && contractId.Value > 0)
            {
                query = query.Where(p => p.MaHopDong == contractId.Value);
            }

            var tickets = await query.OrderByDescending(p => p.NgayBaoLoi).ToListAsync();

            var result = tickets.Select(p =>
            {
                string statusText = MaintenanceAssignment.StatusLabel(p.TrangThai);

                string deviceName = p.ThietBi?.SanPham != null
                    ? $"{p.ThietBi.SanPham.TenSanPham} ({p.ThietBi.SoSerial})"
                    : (p.ThietBi != null ? $"Thiết bị #{p.ThietBi.MaThietBi} ({p.ThietBi.SoSerial})" : $"Thiết bị #{p.MaThietBi}");

                // Trích xuất IssueType từ MoTaLoi nếu có prefix "[Loại] ..."
                string issueType = "Sự cố kỹ thuật";
                string desc = p.MoTaLoi ?? "";
                if (desc.StartsWith("[") && desc.Contains("]"))
                {
                    int closeIdx = desc.IndexOf("]");
                    issueType = desc.Substring(1, closeIdx - 1);
                    desc = desc.Substring(closeIdx + 1).Trim();
                }

                var notesList = new List<object>();
                if (!string.IsNullOrEmpty(p.GhiChuSuaChua))
                {
                    notesList.Add(new
                    {
                        time = p.NgayBaoLoi.ToString("dd/MM/yyyy HH:mm"),
                        content = p.GhiChuSuaChua,
                        author = p.KyThuatVien?.HoTen ?? "Kỹ thuật viên"
                    });
                }

                return new
                {
                    id = p.MaPhieu.ToString(),
                    code = $"SC-{p.MaPhieu:D4}",
                    requestCode = $"SC-{p.MaPhieu:D4}",
                    contractId = p.MaHopDong.ToString(),
                    contractCode = $"HD-{p.MaHopDong:D4}",
                    deviceId = p.MaThietBi.ToString(),
                    deviceName = deviceName,
                    customer = p.HopDong?.KhachHang?.HoTen ?? "Khách hàng",
                    customerPhone = p.HopDong?.KhachHang?.SoDienThoai ?? "",
                    issueType = issueType,
                    description = desc,
                    severity = SeverityLabel(p.MucDoKhanCap),
                    occurrenceTime = p.NgayBaoLoi.ToString("dd/MM/yyyy HH:mm"),
                    status = statusText,
                    statusCode = p.TrangThai,
                    assignedStaffId = p.MaKyThuatVien,
                    assignedStaff = p.KyThuatVien?.HoTen,
                    assignedEmployee = p.KyThuatVien?.HoTen,
                    createdAt = p.NgayBaoLoi.ToString("dd/MM/yyyy HH:mm"),
                    completedAt = p.NgayHoanThanh?.ToString("dd/MM/yyyy HH:mm"),
                    result = p.GhiChuSuaChua,
                    compensationFee = (double)p.PhiDenBu,
                    rating = p.DanhGiaSao,
                    feedback = p.YKienPhanHoi,
                    imagePaths = CustomerMaintenance.ImagePaths(p),
                    notes = notesList
                };
            }).ToList();

            return Ok(result);
        }

        // GET: api/maintenance/{id}
        [HttpGet("{id}")]
        public async Task<IActionResult> GetTicketById(int id)
        {
            var p = await _context.PhieuBaoTris.VisibleTickets(User)
                .Include(p => p.HopDong)
                    .ThenInclude(h => h.KhachHang)
                .Include(p => p.ThietBi)
                    .ThenInclude(t => t.SanPham)
                .Include(p => p.KyThuatVien)
                .FirstOrDefaultAsync(p => p.MaPhieu == id);

            if (p == null)
            {
                return NotFound(new { message = $"Không tìm thấy phiếu sự cố #{id}" });
            }

            string statusText = MaintenanceAssignment.StatusLabel(p.TrangThai);

            string deviceName = p.ThietBi?.SanPham != null
                ? $"{p.ThietBi.SanPham.TenSanPham} ({p.ThietBi.SoSerial})"
                : $"Thiết bị #{p.MaThietBi}";

            string issueType = "Sự cố kỹ thuật";
            string desc = p.MoTaLoi ?? "";
            if (desc.StartsWith("[") && desc.Contains("]"))
            {
                int closeIdx = desc.IndexOf("]");
                issueType = desc.Substring(1, closeIdx - 1);
                desc = desc.Substring(closeIdx + 1).Trim();
            }

            var notesList = new List<object>();
            if (!string.IsNullOrEmpty(p.GhiChuSuaChua))
            {
                notesList.Add(new
                {
                    time = p.NgayBaoLoi.ToString("dd/MM/yyyy HH:mm"),
                    content = p.GhiChuSuaChua,
                    author = p.KyThuatVien?.HoTen ?? "Kỹ thuật viên"
                });
            }

            return Ok(new
            {
                id = p.MaPhieu.ToString(),
                code = $"SC-{p.MaPhieu:D4}",
                requestCode = $"SC-{p.MaPhieu:D4}",
                contractId = p.MaHopDong.ToString(),
                contractCode = $"HD-{p.MaHopDong:D4}",
                deviceId = p.MaThietBi.ToString(),
                deviceName = deviceName,
                customer = p.HopDong?.KhachHang?.HoTen ?? "Khách hàng",
                customerPhone = p.HopDong?.KhachHang?.SoDienThoai ?? "",
                issueType = issueType,
                description = desc,
                severity = SeverityLabel(p.MucDoKhanCap),
                occurrenceTime = p.NgayBaoLoi.ToString("dd/MM/yyyy HH:mm"),
                status = statusText,
                statusCode = p.TrangThai,
                assignedStaffId = p.MaKyThuatVien,
                assignedStaff = p.KyThuatVien?.HoTen,
                assignedEmployee = p.KyThuatVien?.HoTen,
                createdAt = p.NgayBaoLoi.ToString("dd/MM/yyyy HH:mm"),
                completedAt = p.NgayHoanThanh?.ToString("dd/MM/yyyy HH:mm"),
                result = p.GhiChuSuaChua,
                compensationFee = (double)p.PhiDenBu,
                rating = p.DanhGiaSao,
                feedback = p.YKienPhanHoi,
                imagePaths = CustomerMaintenance.ImagePaths(p),
                notes = notesList
            });
        }

        [Authorize(Roles = "KhachHang")]
        [HttpPost]
        [Consumes("application/json")]
        public Task<IActionResult> CreateTicket([FromBody] CreateMaintenanceDto request) =>
            SaveTicketAsync(request, [], request.Description ?? "Khách hàng báo sự cố thiết bị");

        [Authorize(Roles = "KhachHang")]
        [HttpPost]
        [Consumes("multipart/form-data")]
        [RequestSizeLimit(32 * 1024 * 1024)]
        public Task<IActionResult> CreateTicketWithImages([FromForm] CreateMaintenanceDto request, [FromForm] List<IFormFile> images) =>
            SaveTicketAsync(request, images, request.Description);

        private async Task<IActionResult> SaveTicketAsync(CreateMaintenanceDto request, List<IFormFile> images, string? description)
        {
            if (images.Count > 3)
                return BadRequest(new { message = "Chỉ có thể đính kèm tối đa 3 ảnh." });
            if (string.IsNullOrWhiteSpace(description))
                return BadRequest(new { message = "Vui lòng nhập mô tả lỗi." });

            var key = request.ContractId?.Trim() ?? "";
            if (key.StartsWith("HD", StringComparison.OrdinalIgnoreCase)) key = key[2..].TrimStart('-');
            int contractId = request.MaHopDong ?? (int.TryParse(key, out var id) ? id : 0);
            int urgency = request.Severity switch { "Nghiêm trọng" => 2, "Trung bình" => 3, _ => 1 };
            if (!string.IsNullOrWhiteSpace(request.IssueType))
                description = $"[{request.IssueType.Trim()}] {description.Trim()}";

            try
            {
                var ticket = await CustomerMaintenance.ReportAsync(_context, _environment.WebRootPath, User.UserId(),
                    contractId, request.MaThietBi?.ToString() ?? request.DeviceId, description, urgency,
                    images, allowVideo: false, HttpContext.RequestAborted);
                return Ok(new
                {
                    success = true,
                    id = ticket.MaPhieu.ToString(),
                    code = $"SC-{ticket.MaPhieu:D4}",
                    requestCode = $"SC-{ticket.MaPhieu:D4}",
                    contractId = ticket.MaHopDong.ToString(),
                    deviceId = ticket.MaThietBi.ToString(),
                    status = MaintenanceAssignment.StatusLabel(ticket.TrangThai),
                    statusCode = ticket.TrangThai,
                    imagePaths = CustomerMaintenance.ImagePaths(ticket),
                    message = "Đã gửi báo cáo sự cố."
                });
            }
            catch (CustomerMaintenanceException error)
            {
                return StatusCode(error.StatusCode, new { message = error.Message });
            }
        }

        private static string SeverityLabel(int? urgency) => urgency switch
        {
            2 => "Nghiêm trọng",
            3 => "Trung bình",
            _ => "Nhẹ"
        };

        // PUT: api/maintenance/{id}/status
        // Cập nhật trạng thái xử lý (Nhân viên kỹ thuật tiếp nhận / hoàn thành)
        [Authorize(Roles = "Admin,KyThuat")]
        [HttpPut("{id}/status")]
        public async Task<IActionResult> UpdateStatus(int id, [FromBody] UpdateMaintenanceStatusDto request)
        {
            int? status = request.StatusCode;
            if (status == null && !string.IsNullOrWhiteSpace(request.Status))
            {
                var label = request.Status.Trim().ToLowerInvariant();
                status = label switch
                {
                    "đã gửi" or "chờ xử lý" or "tiếp nhận" or "phân công" => 1,
                    "đang xử lý" or "đang sửa chữa" => 2,
                    "hoàn thành" or "đã hoàn thành" or "đã sửa xong" or "chờ nghiệm thu" => 3,
                    "hỏng, chuyển thanh lý" => 4,
                    _ => 0
                };
            }
            if (status is < 1 or > 4)
                return BadRequest(new { message = "Trạng thái xử lý không hợp lệ." });

            await using var transaction = await MaintenanceAssignment.BeginUpdateAsync(_context, id);
            var phieu = await _context.PhieuBaoTris.FindAsync(id);
            if (phieu == null)
                return NotFound(new { message = $"Không tìm thấy phiếu sự cố #{id}" });

            int actorId = User.UserId();
            if (User.IsInRole("KyThuat"))
            {
                if (phieu.MaKyThuatVien != actorId) return NotFound(new { message = "Không tìm thấy phiếu được giao." });
                if (request.StaffId.HasValue || request.CompensationFee.HasValue)
                    return Forbid(ApiTokens.Scheme);
                if (status.HasValue && (status.Value is not (2 or 3) ||
                    (status.Value != phieu.TrangThai && status.Value != phieu.TrangThai + 1)))
                    return Conflict(new { message = "Chỉ có thể bắt đầu sửa hoặc báo sửa xong phiếu được giao." });
            }

            if (phieu.TrangThai is 4 or 5 && status.HasValue && status != phieu.TrangThai)
                return Conflict(new { message = "Phiếu đã đóng." });

            if (status.HasValue)
                await MaintenanceAssignment.ApplyStatusAsync(_context, phieu, status.Value);

            if (!string.IsNullOrWhiteSpace(request.Result) || !string.IsNullOrWhiteSpace(request.Notes))
            {
                string noteText = string.Join(" | ", new[] { request.Notes, request.Result }
                    .Where(value => !string.IsNullOrWhiteSpace(value)).Select(value => value!.Trim()));
                phieu.GhiChuSuaChua = string.IsNullOrEmpty(phieu.GhiChuSuaChua)
                    ? noteText
                    : $"{phieu.GhiChuSuaChua} | {noteText}";
            }

            if (request.StaffId.HasValue && request.StaffId.Value > 0)
            {
                if (request.StaffId != phieu.MaKyThuatVien &&
                    !await MaintenanceAssignment.IsActiveTechnicianAsync(_context, request.StaffId.Value))
                    return BadRequest(new { message = "Hãy chọn kỹ thuật viên đang hoạt động." });
                phieu.MaKyThuatVien = request.StaffId.Value;
            }

            if (request.CompensationFee.HasValue)
            {
                phieu.PhiDenBu = request.CompensationFee.Value;
            }

            await MaintenanceAssignment.SyncAsync(_context, phieu, actorId);
            await _context.SaveChangesAsync();
            await transaction.CommitAsync();

            return Ok(new
            {
                success = true,
                message = "Đã cập nhật trạng thái bảo trì thành công!",
                statusCode = phieu.TrangThai
            });
        }

        [Authorize(Roles = "KhachHang")]
        [HttpPut("{id}/acceptance")]
        public Task<IActionResult> AcceptMaintenance(int id, [FromBody] AcceptMaintenanceDto request) =>
            ReviewAsync(id, request.Accepted, null, request.Feedback);

        [Authorize(Roles = "KhachHang")]
        [HttpPut("{id}/rating")]
        public Task<IActionResult> RateMaintenance(int id, [FromBody] RateMaintenanceDto request) =>
            ReviewAsync(id, null, request.Rating, request.Feedback);

        private async Task<IActionResult> ReviewAsync(int id, bool? accepted, int? rating, string? feedback)
        {
            if (accepted == null && rating == null)
                return BadRequest(new { message = "Chọn đồng ý hoặc từ chối nghiệm thu." });
            try
            {
                var ticket = await CustomerMaintenance.ReviewAsync(_context, User.UserId(), id, accepted, rating, feedback);
                return Ok(new
                {
                    success = true,
                    statusCode = ticket.TrangThai,
                    status = MaintenanceAssignment.StatusLabel(ticket.TrangThai),
                    rating = ticket.DanhGiaSao,
                    feedback = ticket.YKienPhanHoi
                });
            }
            catch (CustomerMaintenanceException error)
            {
                return StatusCode(error.StatusCode, new { message = error.Message });
            }
        }
    }

    public class AcceptMaintenanceDto
    {
        public bool? Accepted { get; set; }
        public string? Feedback { get; set; }
    }

    public class CreateMaintenanceDto
    {
        public string? ContractId { get; set; }
        public int? MaHopDong { get; set; }
        public string? DeviceId { get; set; }
        public int? MaThietBi { get; set; }
        public string? IssueType { get; set; }
        public string? Description { get; set; }
        public string? Severity { get; set; }
        public string? CustomerId { get; set; }
        public int? MaKhachHang { get; set; }
    }

    public class UpdateMaintenanceStatusDto
    {
        public string? Status { get; set; }
        public int? StatusCode { get; set; }
        public string? Result { get; set; }
        public string? Notes { get; set; }
        public int? StaffId { get; set; }
        public decimal? CompensationFee { get; set; }
    }

    public class RateMaintenanceDto
    {
        public int Rating { get; set; }
        public string? Feedback { get; set; }
    }
}
