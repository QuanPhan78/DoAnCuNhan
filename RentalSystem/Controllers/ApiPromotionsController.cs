using Microsoft.AspNetCore.Authorization;
using RentalSystem.Common;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Controllers
{
    [Route("api/promotions")]
    [ApiController]
    [Authorize(AuthenticationSchemes = ApiTokens.Scheme)]
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
                    Code = "WELCOME20",
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

            try
            {
                var promo = await RentalBooking.FindPromotionAsync(_context, code, DateTime.Now, HttpContext.RequestAborted);
                return Ok(new
                {
                    success = true,
                    promoId = promo!.MaKM,
                    code = promo.Code,
                    discountPercent = promo.PhanTramGiam,
                    message = $"Áp dụng mã {promo.Code}, giảm {promo.PhanTramGiam}%."
                });
            }
            catch (RentalBookingException error)
            {
                return StatusCode(error.StatusCode, new { message = error.Message });
            }
        }
    }
}
