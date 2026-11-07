using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using RentalSystem.Services;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Encodings.Web;
using System.Text.Json;

namespace RentalSystem.Areas.Admin.Controllers
{
    // Bảng điều khiển tổng quan cho quản trị viên
    [Area("Admin")]
    [Authorize(Roles = "Admin,KinhDoanh")]
    public class HomeController : Controller
    {
        private readonly ApplicationDbContext _context;

        public HomeController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Màn hình Dashboard chính:
        // thống kê chỉ số tổng quan, biểu đồ doanh thu và các kỳ hạn nợ cần theo dõi
        public async Task<IActionResult> Index(string? timeFilter)
        {
            var today = DateTime.Today;
            var period = RevenuePeriod.Resolve(timeFilter, today);
            var revenue = await RevenueReport.LoadAsync(_context, period, today);
            ViewBag.TotalRevenue = revenue.Total;
            ViewBag.TimeFilter = period.Key;

            var contracts = _context.HopDongs.Where(h => h.TrangThai != 3);
            if (period.Start is DateTime start && period.End is DateTime end)
                contracts = contracts.Where(h => h.NgayBatDau >= start && h.NgayBatDau < end);
            ViewBag.TotalContracts = await contracts.CountAsync();

            // Thiết bị đang hoạt động: Đếm các máy vật lý đang cho khách thuê (TrangThai = 1)
            ViewBag.RentedDevices = _context.ThietBis.Count(t => t.TrangThai == 1);
            
            // Khách hàng thân thiết: Đếm tài khoản Khách Hàng có ít nhất 1 hợp đồng hợp lệ
            ViewBag.TotalCustomers = _context.NguoiDungs.Count(n => n.VaiTro.TenVaiTro == "KhachHang" && 
                _context.HopDongs.Any(h => h.MaKhachHang == n.MaNguoiDung && h.TrangThai != 3));

            // Cảnh báo công nợ: Số kỳ hạn trả góp đã quá hạn mà khách chưa đóng tiền
            ViewBag.OverduePayments = _context.KyHanThanhToans
                .Count(k => (k.TrangThai == 0 || k.TrangThai == 2) && k.NgayDenHan.Date < DateTime.Now.Date && (k.HopDong.TrangThai == 0 || k.HopDong.TrangThai == 1));

            // Cấu hình không escape ký tự Unicode tiếng Việt khi xuất JSON ra HTML
            var jsonOptions = new JsonSerializerOptions
            {
                Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping
            };

            ViewBag.ChartLabels = JsonSerializer.Serialize(revenue.Chart.Select(point => point.Label), jsonOptions);
            ViewBag.ChartData = JsonSerializer.Serialize(revenue.Chart.Select(point => point.Value), jsonOptions);

            // Top 5 hợp đồng mới nhất
            ViewBag.RecentOrders = _context.HopDongs
                .Include(h => h.KhachHang)
                .OrderByDescending(h => h.MaHopDong)
                .Take(5)
                .ToList();

            // Danh sách 10 kỳ hạn quá hạn gần nhất
            ViewBag.OverdueInstallments = _context.KyHanThanhToans
                .Include(k => k.HopDong)
                .ThenInclude(h => h.KhachHang)
                .Where(k => (k.TrangThai == 0 || k.TrangThai == 2) && k.NgayDenHan.Date < DateTime.Now.Date && (k.HopDong.TrangThai == 1 || k.HopDong.TrangThai == 0))
                .OrderBy(k => k.NgayDenHan)
                .Take(10)
                .ToList();

            return View();
        }
    }
}
