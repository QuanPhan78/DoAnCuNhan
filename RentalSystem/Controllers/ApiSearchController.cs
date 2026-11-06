using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Controllers
{
    [Route("api/search")]
    [ApiController]
    public class ApiSearchController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public ApiSearchController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: api/search?q={query}&type={type}&userId={userId}&role={role}
        [HttpGet]
        public async Task<IActionResult> Search([FromQuery] string? q, [FromQuery] string? keyword, [FromQuery] string? type, [FromQuery] string? userId, [FromQuery] string? role)
        {
            var searchStr = !string.IsNullOrWhiteSpace(q) ? q : keyword;
            if (string.IsNullOrWhiteSpace(searchStr))
            {
                return Ok(new List<object>());
            }

            string lower = searchStr.Trim().ToLower();
            string filterType = (type ?? "all").ToLower();
            var results = new List<object>();

            int? parsedId = null;
            var digits = new string(lower.Where(char.IsDigit).ToArray());
            if (int.TryParse(digits, out int pid)) parsedId = pid;

            // 1. Search Devices (SanPhams)
            if (filterType == "all" || filterType == "device")
            {
                var sanPhams = await _context.SanPhams
                    .Include(s => s.LoaiThietBi)
                    .Where(s =>
                        (parsedId.HasValue && s.MaSanPham == parsedId.Value) ||
                        s.TenSanPham.ToLower().Contains(lower) ||
                        (s.LoaiThietBi != null && s.LoaiThietBi.TenLoai.ToLower().Contains(lower)) ||
                        (s.CauHinh != null && s.CauHinh.ToLower().Contains(lower))
                    )
                    .OrderBy(s => s.MaSanPham)
                    .Take(10)
                    .ToListAsync();

                var allTbs = await _context.ThietBis.ToListAsync();
                foreach (var sp in sanPhams)
                {
                    var relatedTbs = allTbs.Where(t => t.MaSanPham == sp.MaSanPham).ToList();
                    var firstTb = relatedTbs.FirstOrDefault();
                    results.Add(new
                    {
                        id = sp.MaSanPham.ToString(),
                        type = "device",
                        title = sp.TenSanPham,
                        subtitle = $"Mã SP-{sp.MaSanPham:D4} - {sp.LoaiThietBi?.TenLoai ?? "Thiết bị"}",
                        status = "Sẵn sàng",
                        originalData = new
                        {
                            id = sp.MaSanPham.ToString(),
                            code = $"SP-{sp.MaSanPham:D4}",
                            name = sp.TenSanPham,
                            type = sp.LoaiThietBi?.TenLoai ?? "Thiết bị",
                            brand = "Chính hãng",
                            model = sp.TenSanPham,
                            serialNumber = firstTb != null ? firstTb.SoSerial : $"SN-{sp.MaSanPham:D4}",
                            condition = firstTb?.TinhTrangMay ?? "Mới 100%",
                            price = (double)sp.GiaThueNgay,
                            pricePerDay = (double)sp.GiaThueNgay,
                            rentalPrice = (double)sp.GiaThueNgay,
                            pricePerMonth = (double)(sp.GiaThueNgay * 20),
                            deposit = (double)sp.TienCoc,
                            image = sp.HinhAnh ?? "",
                            imageUrl = sp.HinhAnh ?? "",
                            description = sp.MoTa ?? "",
                            specs = sp.CauHinh ?? "",
                            specifications = sp.CauHinh ?? "",
                            rentalStatus = "Sẵn sàng",
                            isAvailable = true
                        }
                    });
                }
            }

            // 2. Search Contracts
            if (filterType == "all" || filterType == "contract")
            {
                IQueryable<HopDong> contractQuery = _context.HopDongs
                    .Include(h => h.KhachHang);

                if (!string.IsNullOrEmpty(userId) && int.TryParse(userId, out int parsedUserId))
                {
                    if (!string.Equals(role, "Admin", StringComparison.OrdinalIgnoreCase) &&
                        !string.Equals(role, "KinhDoanh", StringComparison.OrdinalIgnoreCase) &&
                        !string.Equals(role, "Staff", StringComparison.OrdinalIgnoreCase))
                    {
                        contractQuery = contractQuery.Where(h => h.MaKhachHang == parsedUserId);
                    }
                }

                var hopDongs = await contractQuery
                    .Where(h => 
                        (parsedId.HasValue && h.MaHopDong == parsedId.Value) ||
                        (h.KhachHang != null && h.KhachHang.HoTen.ToLower().Contains(lower))
                    )
                    .OrderByDescending(h => h.MaHopDong)
                    .Take(10)
                    .ToListAsync();

                foreach (var h in hopDongs)
                {
                    string statusText = h.TrangThai switch
                    {
                        0 => "Chờ duyệt",
                        1 => "Đang hiệu lực",
                        2 => "Hoàn thành",
                        3 => "Đã hủy",
                        _ => "Chờ duyệt"
                    };

                    results.Add(new
                    {
                        id = h.MaHopDong.ToString(),
                        type = "contract",
                        title = $"HD-{h.MaHopDong:D4}",
                        subtitle = $"KH: {h.KhachHang?.HoTen ?? "Khách hàng"} - {(double)h.TongTien:N0} đ",
                        status = statusText,
                        originalData = new
                        {
                            id = h.MaHopDong.ToString(),
                            contractCode = $"HD-{h.MaHopDong:D4}",
                            customerId = h.MaKhachHang.ToString(),
                            customerName = h.KhachHang?.HoTen ?? "",
                            rentalStart = h.NgayBatDau.ToString("dd/MM/yyyy"),
                            rentalEnd = h.NgayKetThuc.ToString("dd/MM/yyyy"),
                            rentalType = "Theo ngày",
                            status = statusText,
                            totalAmount = (double)h.TongTien,
                            depositAmount = (double)h.TienDaCoc
                        }
                    });
                }
            }

            // 3. Search Incidents / Maintenances
            if (filterType == "all" || filterType == "incident" || filterType == "maintenance")
            {
                IQueryable<PhieuBaoTri> maintQuery = _context.PhieuBaoTris
                    .Include(p => p.HopDong)
                    .ThenInclude(h => h.KhachHang)
                    .Include(p => p.ThietBi)
                    .ThenInclude(t => t.SanPham);

                if (!string.IsNullOrEmpty(userId) && int.TryParse(userId, out int parsedUserId))
                {
                    if (!string.Equals(role, "Admin", StringComparison.OrdinalIgnoreCase) &&
                        !string.Equals(role, "KyThuat", StringComparison.OrdinalIgnoreCase) &&
                        !string.Equals(role, "Staff", StringComparison.OrdinalIgnoreCase))
                    {
                        maintQuery = maintQuery.Where(p => p.HopDong.MaKhachHang == parsedUserId);
                    }
                }

                var maints = await maintQuery
                    .Where(p =>
                        (parsedId.HasValue && (p.MaPhieu == parsedId.Value || p.MaHopDong == parsedId.Value)) ||
                        (p.MoTaLoi != null && p.MoTaLoi.ToLower().Contains(lower)) ||
                        (p.ThietBi != null && p.ThietBi.SanPham != null && p.ThietBi.SanPham.TenSanPham.ToLower().Contains(lower))
                    )
                    .OrderByDescending(p => p.MaPhieu)
                    .Take(10)
                    .ToListAsync();

                foreach (var p in maints)
                {
                    string statusText = p.TrangThai switch
                    {
                        1 => "Chờ xử lý",
                        2 => "Đang xử lý",
                        3 => "Đã hoàn thành",
                        _ => "Chờ xử lý"
                    };

                    string resType = filterType == "maintenance" ? "maintenance" : "incident";
                    results.Add(new
                    {
                        id = p.MaPhieu.ToString(),
                        type = resType,
                        title = $"SC-{p.MaPhieu:D4}",
                        subtitle = $"{p.ThietBi?.SanPham?.TenSanPham ?? "Thiết bị"}: {p.MoTaLoi}",
                        status = statusText,
                        originalData = new
                        {
                            id = p.MaPhieu.ToString(),
                            code = $"SC-{p.MaPhieu:D4}",
                            contractId = p.MaHopDong.ToString(),
                            deviceId = p.ThietBi?.SanPham?.TenSanPham ?? p.MaThietBi.ToString(),
                            issueType = "Sự cố kỹ thuật",
                            description = p.MoTaLoi ?? "",
                            severity = "Trung bình",
                            occurrenceTime = p.NgayBaoLoi.ToString("dd/MM/yyyy HH:mm"),
                            status = statusText,
                            createdAt = p.NgayBaoLoi.ToString("dd/MM/yyyy HH:mm")
                        }
                    });
                }
            }

            return Ok(results);
        }

        // GET: api/search/suggestions?q=keyword
        [HttpGet("suggestions")]
        public async Task<IActionResult> GetSuggestions([FromQuery] string? q)
        {
            if (string.IsNullOrWhiteSpace(q))
            {
                return Ok(new List<string>());
            }

            var queryLower = q.Trim().ToLower();
            var suggestions = await _context.SanPhams
                .Where(s => s.TenSanPham.ToLower().Contains(queryLower))
                .Select(s => s.TenSanPham)
                .Distinct()
                .Take(5)
                .ToListAsync();

            return Ok(suggestions);
        }
    }
}
