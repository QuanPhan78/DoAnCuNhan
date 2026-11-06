using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using RentalSystem.Common;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Controllers
{
    // Danh mục và chi tiết sản phẩm cho khách hàng
    public class SanPhamController : Controller
    {
        private readonly ApplicationDbContext _context;

        public SanPhamController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Danh sách sản phẩm cho thuê kèm số lượng máy khả dụng trong kho
        public async Task<IActionResult> Index()
        {
            var sanPhams = await _context.SanPhams.Include(s => s.LoaiThietBi).ToListAsync();
            ViewBag.Categories = await _context.LoaiThietBis.ToListAsync();
            
            // Đếm máy có thể nhận đặt thuê theo lịch.
            var stockCounts = await _context.ThietBis
                .Where(t => RentalBooking.RentableStatuses.Contains(t.TrangThai))
                .GroupBy(t => t.MaSanPham)
                .Select(g => new { MaSanPham = g.Key, Count = g.Count() })
                .ToDictionaryAsync(x => x.MaSanPham, x => x.Count);

            ViewBag.StockMap = stockCounts;

            return View(sanPhams);
        }

        // Chi tiết sản phẩm
        public async Task<IActionResult> Details(int id)
        {
            var sp = await _context.SanPhams
                .Include(s => s.LoaiThietBi)
                .FirstOrDefaultAsync(m => m.MaSanPham == id);

            if (sp == null) return NotFound();

            // Đếm máy có thể nhận đặt thuê theo lịch.
            ViewBag.InStock = await _context.ThietBis
                .CountAsync(t => t.MaSanPham == id && RentalBooking.RentableStatuses.Contains(t.TrangThai));

            // Gợi ý danh sách sản phẩm cùng nhóm phân loại
            ViewBag.RelatedProducts = await _context.SanPhams
                .Where(x => x.MaLoai == sp.MaLoai && x.MaSanPham != id)
                .Take(4)
                .ToListAsync();

            return View(sp);
        }
    }
}
