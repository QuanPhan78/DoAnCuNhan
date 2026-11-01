using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Controllers
{
    [Route("api/promotions")]
    [ApiController]
    public class ApiPromotionsController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public ApiPromotionsController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: api/promotions
        [HttpGet]
        public async Task<IActionResult> GetPromotions()
        {
            var promos = await _context.KhuyenMais
                .Where(k => k.KichHoat)
                .ToListAsync();

            if (!promos.Any())
            {
                // Seed thêm khuyến mãi nếu rỗng
                var defaultPromo = new KhuyenMai
                {
                    MaCode = "WELCOME20",
                    PhanTramGiam = 20,
                    KichHoat = true
                };
                _context.KhuyenMais.Add(defaultPromo);
                await _context.SaveChangesAsync();
                promos.Add(defaultPromo);
            }

            var result = promos.Select(p => new
            {
                id = p.MaKhuyenMai.ToString(),
                title = $"Ưu đãi {p.PhanTramGiam}% mã {p.MaCode}",
                description = $"Nhập mã {p.MaCode} khi tạo hợp đồng thuê để được giảm ngay {p.PhanTramGiam}% trên tổng tiền thuê.",
                discountValue = $"{p.PhanTramGiam}%",
                validFrom = "01/01/2026",
                validTo = "31/12/2026",
                conditions = $"Áp dụng cho mọi đơn thuê thiết bị khi kích hoạt mã {p.MaCode}",
                status = p.KichHoat ? "Đang áp dụng" : "Hết hạn",
                imageAsset = "assets/images/promotions/promo1.png",
                code = p.MaCode,
                percent = p.PhanTramGiam
            }).ToList();

            return Ok(result);
        }

        // GET: api/promotions/check?code=...
        [HttpGet("check")]
        public async Task<IActionResult> CheckPromo([FromQuery] string code)
        {
            if (string.IsNullOrWhiteSpace(code))
            {
                return BadRequest(new { message = "Vui lòng nhập mã khuyến mãi." });
            }

            var promo = await _context.KhuyenMais
                .FirstOrDefaultAsync(k => k.MaCode.ToLower() == code.Trim().ToLower() && k.KichHoat);

            if (promo == null)
            {
                return NotFound(new { message = "Mã khuyến mãi không tồn tại hoặc đã hết hiệu lực." });
            }

            return Ok(new
            {
                success = true,
                promoId = promo.MaKhuyenMai,
                code = promo.MaCode,
                discountPercent = promo.PhanTramGiam,
                message = $"Áp dụng thành công mã {promo.MaCode}, giảm {promo.PhanTramGiam}%!"
            });
        }
    }
}
