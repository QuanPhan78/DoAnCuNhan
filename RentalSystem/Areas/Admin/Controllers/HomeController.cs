using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Encodings.Web;
using System.Text.Json;

namespace RentalSystem.Areas.Admin.Controllers
{
    // Controller Bảng điều khiển (Dashboard) trung tâm dành cho Quản trị viên và Bộ phận Kinh doanh.
    // Tổng hợp số liệu thống kê doanh thu, tình trạng thiết bị, khách hàng và biểu đồ kinh doanh.
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
        // 1. Tính toán các chỉ số KPI tổng quan (Doanh thu thực tế, tổng số hợp đồng, máy đang cho thuê).
        // 2. Xuất dữ liệu biểu đồ doanh thu 6 tháng gần nhất sang định dạng JSON cho Chart.js.
        // 3. Lấy 5 đơn thuê gần nhất và danh sách cảnh báo các kỳ hạn nợ đã quá hạn thanh toán.
        public IActionResult Index()
        {
            // 1. Thống kê Card tổng quan
            // Doanh thu thực tế: Chỉ tính các hợp đồng đã hoàn tất chu kỳ thuê (TrangThai = 2)
            ViewBag.TotalRevenue = _context.HopDongs
                .Where(h => h.TrangThai == 2)
                .Sum(h => (decimal?)h.TongTien) ?? 0;

            // Tổng số hợp đồng: Đếm tất cả đơn ngoại trừ những đơn đã bị hủy (TrangThai != 3)
            ViewBag.TotalContracts = _context.HopDongs.Count(h => h.TrangThai != 3); 
            
            // Thiết bị đang hoạt động: Đếm các máy vật lý đang cho khách thuê (TrangThai = 1)
            ViewBag.RentedDevices = _context.ThietBis.Count(t => t.TrangThai == 1);
            
            // Khách hàng thân thiết: Đếm tài khoản Khách Hàng có ít nhất 1 hợp đồng hợp lệ
            ViewBag.TotalCustomers = _context.NguoiDungs.Count(n => n.VaiTro.TenVaiTro == "KhachHang" && 
                _context.HopDongs.Any(h => h.MaKhachHang == n.MaNguoiDung && h.TrangThai != 3));

            // Cảnh báo công nợ: Số kỳ hạn trả góp đã quá hạn mà khách chưa đóng tiền
            ViewBag.OverduePayments = _context.KyHanThanhToans
                .Count(k => k.TrangThai == 0 && k.NgayDenHan.Date < DateTime.Now.Date && (k.HopDong.TrangThai == 0 || k.HopDong.TrangThai == 1));

            // 2. Dữ liệu Biểu đồ Doanh thu (6 tháng gần nhất)
            var allCompletedOrders = _context.HopDongs
                .Where(h => h.TrangThai == 2)
                .ToList();

            var chartLabels = new List<string>();
            var chartData = new List<decimal>();

            for (int i = 5; i >= 0; i--)
            {
                var d = DateTime.Now.AddMonths(-i);
                chartLabels.Add("Tháng " + d.Month + "/" + d.Year);
                
                var sum = allCompletedOrders
                    .Where(x => x.NgayBatDau.Month == d.Month && x.NgayBatDau.Year == d.Year)
                    .Sum(x => x.TongTien);
                    
                chartData.Add(sum);
            }
            
            // Cấu hình không escape ký tự Unicode tiếng Việt khi xuất JSON ra HTML
            var jsonOptions = new JsonSerializerOptions
            {
                Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping
            };

            ViewBag.ChartLabels = JsonSerializer.Serialize(chartLabels, jsonOptions);
            ViewBag.ChartData = JsonSerializer.Serialize(chartData, jsonOptions);

            // 3. Top 5 hợp đồng mới nhất phát sinh trên hệ thống
            ViewBag.RecentOrders = _context.HopDongs
                .Include(h => h.KhachHang)
                .OrderByDescending(h => h.MaHopDong)
                .Take(5)
                .ToList();

            // 4. Danh sách 10 khoản kỳ hạn nợ quá hạn thanh toán khẩn cấp nhất
            ViewBag.OverdueInstallments = _context.KyHanThanhToans
                .Include(k => k.HopDong)
                .ThenInclude(h => h.KhachHang)
                .Where(k => k.TrangThai == 0 && k.NgayDenHan.Date < DateTime.Now.Date && (k.HopDong.TrangThai == 1 || k.HopDong.TrangThai == 0))
                .OrderBy(k => k.NgayDenHan)
                .Take(10)
                .ToList();

            return View();
        }
    }
}
