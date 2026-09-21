using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Controllers
{
    // Controller Sản phẩm phía giao diện Khách hàng:
    // Cho phép duyệt danh mục sản phẩm, xem chi tiết cấu hình, giá thuê và số lượng máy sẵn sàng.
    public class SanPhamController : Controller
    {
        private readonly ApplicationDbContext _context;

        public SanPhamController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Trang danh mục tất cả sản phẩm cho thuê:
        // Đồng bộ số lượng máy thực tế đang 'Sẵn sàng' (TrangThai = 0) trong kho
        // để khách biết còn máy hay đã hết hàng trước khi thêm vào giỏ.
        public async Task<IActionResult> Index()
        {
            var sanPhams = await _context.SanPhams.Include(s => s.LoaiThietBi).ToListAsync();
            ViewBag.Categories = await _context.LoaiThietBis.ToListAsync();
            
            // Đồng bộ số lượng tồn kho khả dụng thực tế của từng sản phẩm từ Database
            var stockCounts = await _context.ThietBis
                .Where(t => t.TrangThai == 0)
                .GroupBy(t => t.MaSanPham)
                .Select(g => new { MaSanPham = g.Key, Count = g.Count() })
                .ToDictionaryAsync(x => x.MaSanPham, x => x.Count);

            ViewBag.StockMap = stockCounts;

            return View(sanPhams);
        }

        // Xem trang chi tiết một sản phẩm:
        // Hiển thị thông số kỹ thuật, cấu hình, đơn giá và các sản phẩm cùng phân khúc liên quan.
        public async Task<IActionResult> Details(int id)
        {
            var sp = await _context.SanPhams
                .Include(s => s.LoaiThietBi)
                .FirstOrDefaultAsync(m => m.MaSanPham == id);

            if (sp == null) return NotFound();

            // Đếm số lượng máy vật lý đang sẵn sàng cho thuê trong kho
            ViewBag.InStock = await _context.ThietBis
                .CountAsync(t => t.MaSanPham == id && t.TrangThai == 0);

            // Gợi ý danh sách sản phẩm cùng nhóm phân loại
            ViewBag.RelatedProducts = await _context.SanPhams
                .Where(x => x.MaLoai == sp.MaLoai && x.MaSanPham != id)
                .Take(4)
                .ToListAsync();

            return View(sp);
        }
    }
}
