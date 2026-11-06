using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Controllers
{
    [Route("api/maintenance")]
    [ApiController]
    public class ApiMaintenanceController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public ApiMaintenanceController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: api/maintenance
        // Lấy danh sách phiếu báo sự cố / bảo trì. Hỗ trợ lọc theo userId, role, contractId
        [HttpGet]
        public async Task<IActionResult> GetTickets(
            [FromQuery] string? userId,
            [FromQuery] string? role,
            [FromQuery] int? contractId)
        {
            IQueryable<PhieuBaoTri> query = _context.PhieuBaoTris
                .Include(p => p.HopDong)
                    .ThenInclude(h => h.KhachHang)
                .Include(p => p.ThietBi)
                    .ThenInclude(t => t.SanPham)
                .Include(p => p.KyThuatVien);

            if (contractId.HasValue && contractId.Value > 0)
            {
                query = query.Where(p => p.MaHopDong == contractId.Value);
            }

            if (!string.IsNullOrEmpty(userId) && int.TryParse(userId, out int parsedUserId))
            {
                bool isPrivileged = string.Equals(role, "Admin", StringComparison.OrdinalIgnoreCase) ||
                                   string.Equals(role, "Staff", StringComparison.OrdinalIgnoreCase) ||
                                   string.Equals(role, "KyThuat", StringComparison.OrdinalIgnoreCase) ||
                                   string.Equals(role, "KinhDoanh", StringComparison.OrdinalIgnoreCase) ||
                                   string.Equals(role, "Quản lý", StringComparison.OrdinalIgnoreCase) ||
                                   string.Equals(role, "Nhân viên", StringComparison.OrdinalIgnoreCase);

                if (!isPrivileged)
                {
                    // Khách hàng: chỉ xem phiếu bảo trì thuộc các hợp đồng của chính mình
                    query = query.Where(p => p.HopDong.MaKhachHang == parsedUserId);
                }
            }

            var tickets = await query.OrderByDescending(p => p.NgayBaoLoi).ToListAsync();

            var result = tickets.Select(p =>
            {
                string statusText = p.TrangThai switch
                {
                    1 => "Chờ xử lý",
                    2 => "Đang xử lý",
                    3 => "Đã hoàn thành",
                    4 => "Đã hủy",
                    _ => "Chờ xử lý"
                };

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
                    severity = "Trung bình",
                    occurrenceTime = p.NgayBaoLoi.ToString("dd/MM/yyyy HH:mm"),
                    status = statusText,
                    statusCode = p.TrangThai,
                    assignedStaff = p.KyThuatVien?.HoTen,
                    assignedEmployee = p.KyThuatVien?.HoTen,
                    createdAt = p.NgayBaoLoi.ToString("dd/MM/yyyy HH:mm"),
                    completedAt = p.TrangThai == 3 ? p.NgayBaoLoi.AddHours(2).ToString("dd/MM/yyyy HH:mm") : null,
                    result = p.GhiChuSuaChua,
                    compensationFee = (double)p.PhiDenBu,
                    rating = p.DanhGiaSao,
                    notes = notesList
                };
            }).ToList();

            return Ok(result);
        }

        // GET: api/maintenance/{id}
        [HttpGet("{id}")]
        public async Task<IActionResult> GetTicketById(int id)
        {
            var p = await _context.PhieuBaoTris
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

            string statusText = p.TrangThai switch
            {
                1 => "Chờ xử lý",
                2 => "Đang xử lý",
                3 => "Đã hoàn thành",
                4 => "Đã hủy",
                _ => "Chờ xử lý"
            };

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
                severity = "Trung bình",
                occurrenceTime = p.NgayBaoLoi.ToString("dd/MM/yyyy HH:mm"),
                status = statusText,
                statusCode = p.TrangThai,
                assignedStaff = p.KyThuatVien?.HoTen,
                assignedEmployee = p.KyThuatVien?.HoTen,
                createdAt = p.NgayBaoLoi.ToString("dd/MM/yyyy HH:mm"),
                completedAt = p.TrangThai == 3 ? p.NgayBaoLoi.AddHours(2).ToString("dd/MM/yyyy HH:mm") : null,
                result = p.GhiChuSuaChua,
                compensationFee = (double)p.PhiDenBu,
                rating = p.DanhGiaSao,
                notes = notesList
            });
        }

        // POST: api/maintenance
        // Tạo phiếu sự cố / báo hỏng thiết bị mới vào SQL Server
        [HttpPost]
        public async Task<IActionResult> CreateTicket([FromBody] CreateMaintenanceDto request)
        {
            if (request == null)
            {
                return BadRequest(new { message = "Dữ liệu yêu cầu không hợp lệ." });
            }

            // 1. Phân giải Mã Hợp Đồng
            int contractId = 0;
            if (request.MaHopDong.HasValue && request.MaHopDong.Value > 0)
            {
                contractId = request.MaHopDong.Value;
            }
            else if (!string.IsNullOrEmpty(request.ContractId))
            {
                string cleanId = request.ContractId.ToUpper().Replace("HD-", "").Replace("HD", "").Trim();
                int.TryParse(cleanId, out contractId);
            }

            var hopDong = await _context.HopDongs
                .Include(h => h.KhachHang)
                .FirstOrDefaultAsync(h => h.MaHopDong == contractId);

            if (hopDong == null)
            {
                // Fallback nếu không tìm thấy hợp đồng, tìm hợp đồng gần nhất của user
                if (!string.IsNullOrEmpty(request.CustomerId) && int.TryParse(request.CustomerId, out int cId))
                {
                    hopDong = await _context.HopDongs.OrderByDescending(h => h.MaHopDong).FirstOrDefaultAsync(h => h.MaKhachHang == cId);
                }
                if (hopDong == null)
                {
                    hopDong = await _context.HopDongs.OrderByDescending(h => h.MaHopDong).FirstOrDefaultAsync();
                }
                if (hopDong != null) contractId = hopDong.MaHopDong;
            }

            if (hopDong == null)
            {
                return BadRequest(new { message = "Không tìm thấy hợp đồng để lập phiếu bảo trì." });
            }

            // 2. Phân giải Thiết Bị Vật Lý (ThietBis)
            int thietBiId = 0;
            if (request.MaThietBi.HasValue && request.MaThietBi.Value > 0)
            {
                thietBiId = request.MaThietBi.Value;
            }
            else if (!string.IsNullOrEmpty(request.DeviceId) && int.TryParse(request.DeviceId, out int parsedDevId))
            {
                thietBiId = parsedDevId;
            }

            // Nếu chưa tìm thấy thiết bị, tìm từ ChiTietHopDongs của hợp đồng này
            var chiTiets = await _context.ChiTietHopDongs
                .Include(c => c.ThietBi)
                .ThenInclude(t => t.SanPham)
                .Where(c => c.MaHopDong == contractId)
                .ToListAsync();

            if (thietBiId <= 0 && chiTiets.Any())
            {
                // Tìm theo tên thiết bị nếu DeviceId truyền vào là tên thiết bị
                if (!string.IsNullOrEmpty(request.DeviceId))
                {
                    var match = chiTiets.FirstOrDefault(c => 
                        (c.ThietBi?.SanPham != null && c.ThietBi.SanPham.TenSanPham.Contains(request.DeviceId, StringComparison.OrdinalIgnoreCase)) ||
                        (c.ThietBi != null && c.ThietBi.SoSerial.Contains(request.DeviceId, StringComparison.OrdinalIgnoreCase))
                    );
                    if (match != null) thietBiId = match.MaThietBi;
                }

                if (thietBiId <= 0)
                {
                    thietBiId = chiTiets.First().MaThietBi;
                }
            }

            // Nếu vẫn chưa có thiết bị nào, lấy thiết bị đầu tiên trong bảng ThietBis
            if (thietBiId <= 0)
            {
                var fallbackTb = await _context.ThietBis.FirstOrDefaultAsync();
                thietBiId = fallbackTb?.MaThietBi ?? 1;
            }

            // 3. Chuẩn bị nội dung lỗi
            string moTa = request.Description ?? "Khách hàng báo sự cố thiết bị";
            if (!string.IsNullOrEmpty(request.IssueType))
            {
                moTa = $"[{request.IssueType}] {moTa}";
            }

            var phieu = new PhieuBaoTri
            {
                MaHopDong = contractId,
                MaThietBi = thietBiId,
                MoTaLoi = moTa,
                NgayBaoLoi = DateTime.Now,
                TrangThai = 1, // 1: Mới tiếp nhận / Chờ xử lý
                GhiChuSuaChua = "",
                PhiDenBu = 0,
                DanhGiaSao = null
            };

            _context.PhieuBaoTris.Add(phieu);
            await _context.SaveChangesAsync();

            return Ok(new
            {
                success = true,
                id = phieu.MaPhieu.ToString(),
                code = $"SC-{phieu.MaPhieu:D4}",
                requestCode = $"SC-{phieu.MaPhieu:D4}",
                contractId = phieu.MaHopDong.ToString(),
                deviceId = phieu.MaThietBi.ToString(),
                status = "Chờ xử lý",
                message = "Đã gửi yêu cầu báo sự cố thành công!"
            });
        }

        // PUT: api/maintenance/{id}/status
        // Cập nhật trạng thái xử lý (Nhân viên kỹ thuật tiếp nhận / hoàn thành)
        [HttpPut("{id}/status")]
        public async Task<IActionResult> UpdateStatus(int id, [FromBody] UpdateMaintenanceStatusDto request)
        {
            var phieu = await _context.PhieuBaoTris.FindAsync(id);
            if (phieu == null)
            {
                return NotFound(new { message = $"Không tìm thấy phiếu sự cố #{id}" });
            }

            if (!string.IsNullOrEmpty(request.Status))
            {
                string s = request.Status.ToLower();
                if (s.Contains("hoàn thành") || s.Contains("xong"))
                {
                    phieu.TrangThai = 3;
                }
                else if (s.Contains("đang") || s.Contains("tiếp nhận") || s.Contains("phân công"))
                {
                    phieu.TrangThai = 2;
                }
                else if (s.Contains("hủy"))
                {
                    phieu.TrangThai = 4;
                }
                else
                {
                    phieu.TrangThai = 1;
                }
            }
            else if (request.StatusCode.HasValue)
            {
                phieu.TrangThai = request.StatusCode.Value;
            }

            if (!string.IsNullOrEmpty(request.Result) || !string.IsNullOrEmpty(request.Notes))
            {
                string noteText = !string.IsNullOrEmpty(request.Result) ? request.Result : request.Notes!;
                phieu.GhiChuSuaChua = string.IsNullOrEmpty(phieu.GhiChuSuaChua)
                    ? noteText
                    : $"{phieu.GhiChuSuaChua} | {noteText}";
            }

            if (request.StaffId.HasValue && request.StaffId.Value > 0)
            {
                phieu.MaKyThuatVien = request.StaffId.Value;
            }

            if (request.CompensationFee.HasValue)
            {
                phieu.PhiDenBu = request.CompensationFee.Value;
            }

            await _context.SaveChangesAsync();

            return Ok(new
            {
                success = true,
                message = "Đã cập nhật trạng thái bảo trì thành công!",
                statusCode = phieu.TrangThai
            });
        }

        // PUT: api/maintenance/{id}/rating
        // Khách hàng gửi đánh giá mức độ hài lòng (1 - 5 sao)
        [HttpPut("{id}/rating")]
        public async Task<IActionResult> RateMaintenance(int id, [FromBody] RateMaintenanceDto request)
        {
            var phieu = await _context.PhieuBaoTris.FindAsync(id);
            if (phieu == null)
            {
                return NotFound(new { message = $"Không tìm thấy phiếu sự cố #{id}" });
            }

            if (request.Rating < 1 || request.Rating > 5)
            {
                return BadRequest(new { message = "Điểm đánh giá phải từ 1 đến 5 sao." });
            }

            phieu.DanhGiaSao = request.Rating;
            if (!string.IsNullOrEmpty(request.Feedback))
            {
                phieu.GhiChuSuaChua = string.IsNullOrEmpty(phieu.GhiChuSuaChua)
                    ? $"[Phản hồi KH]: {request.Feedback}"
                    : $"{phieu.GhiChuSuaChua} | [Phản hồi KH]: {request.Feedback}";
            }

            await _context.SaveChangesAsync();

            return Ok(new
            {
                success = true,
                message = "Cảm ơn bạn đã gửi đánh giá chất lượng dịch vụ bảo trì!"
            });
        }
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
