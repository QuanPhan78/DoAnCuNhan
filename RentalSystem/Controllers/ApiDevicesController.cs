using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Common;
using RentalSystem.Models;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Controllers
{
    [Route("api/devices")]
    [ApiController]
    public class ApiDevicesController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public ApiDevicesController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: api/devices
        [HttpGet]
        public async Task<IActionResult> GetDevices([FromQuery] string? status = null, [FromQuery] string? type = null)
        {
            var query = _context.SanPhams.Include(s => s.LoaiThietBi).AsQueryable();
            if (!string.IsNullOrWhiteSpace(type))
            {
                query = query.Where(s => s.LoaiThietBi != null && s.LoaiThietBi.TenLoai.Contains(type));
            }
            var sanPhams = await query.ToListAsync();
            var thietBis = await _context.ThietBis.ToListAsync();

            var result = sanPhams.Select(s =>
            {
                var relatedTbs = thietBis.Where(t => t.MaSanPham == s.MaSanPham).ToList();
                int readyCount = relatedTbs.Count(t => t.TrangThai == 0);
                int totalCount = relatedTbs.Count;

                string itemStatus = "Sẵn sàng";
                if (totalCount > 0 && readyCount == 0)
                {
                    itemStatus = "Đang cho thuê";
                }

                var firstTb = relatedTbs.FirstOrDefault();
                string serial = firstTb != null ? firstTb.SoSerial : $"SN-{s.MaSanPham:D4}";

                return new
                {
                    id = s.MaSanPham.ToString(),
                    code = $"SP-{s.MaSanPham:D4}",
                    name = s.TenSanPham,
                    type = s.LoaiThietBi != null ? s.LoaiThietBi.TenLoai : "Khác",
                    brand = "Chính hãng",
                    model = s.TenSanPham,
                    serialNumber = serial,
                    specifications = s.CauHinh ?? "",
                    condition = firstTb?.TinhTrangMay ?? "Mới 99%",
                    rentalStatus = itemStatus,
                    rentalPrice = (double)s.GiaThueNgay,
                    depositPrice = (double)s.TienCoc,
                    description = s.MoTa ?? "",
                    imageUrl = s.HinhAnh ?? "",
                    readyQuantity = readyCount,
                    rentableQuantity = relatedTbs.Count(t => RentalBooking.RentableStatuses.Contains(t.TrangThai)),
                    totalQuantity = totalCount
                };
            });

            if (!string.IsNullOrWhiteSpace(status))
            {
                result = result.Where(r => r.rentalStatus.Equals(status.Trim(), StringComparison.OrdinalIgnoreCase));
            }

            return Ok(result.ToList());
        }

        // GET: api/devices/{id}
        [HttpGet("{id}")]
        public async Task<IActionResult> GetDeviceById(int id)
        {
            var s = await _context.SanPhams
                .Include(s => s.LoaiThietBi)
                .FirstOrDefaultAsync(s => s.MaSanPham == id);

            if (s == null)
            {
                return NotFound(new { message = $"Không tìm thấy thiết bị #{id}" });
            }

            var relatedTbs = await _context.ThietBis
                .Where(t => t.MaSanPham == id)
                .ToListAsync();

            int readyCount = relatedTbs.Count(t => t.TrangThai == 0);
            int totalCount = relatedTbs.Count;
            string status = (totalCount > 0 && readyCount == 0) ? "Đang cho thuê" : "Sẵn sàng";
            var firstTb = relatedTbs.FirstOrDefault();

            return Ok(new
            {
                id = s.MaSanPham.ToString(),
                code = $"SP-{s.MaSanPham:D4}",
                name = s.TenSanPham,
                type = s.LoaiThietBi != null ? s.LoaiThietBi.TenLoai : "Khác",
                brand = "Chính hãng",
                model = s.TenSanPham,
                serialNumber = firstTb != null ? firstTb.SoSerial : $"SN-{s.MaSanPham:D4}",
                specifications = s.CauHinh ?? "",
                condition = firstTb?.TinhTrangMay ?? "Mới 99%",
                rentalStatus = status,
                rentalPrice = (double)s.GiaThueNgay,
                depositPrice = (double)s.TienCoc,
                description = s.MoTa ?? "",
                imageUrl = s.HinhAnh ?? "",
                readyQuantity = readyCount,
                rentableQuantity = relatedTbs.Count(t => RentalBooking.RentableStatuses.Contains(t.TrangThai)),
                totalQuantity = totalCount
            });
        }
    }
}
