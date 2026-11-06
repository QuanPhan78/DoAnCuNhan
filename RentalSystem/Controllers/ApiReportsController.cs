using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Controllers
{
    [Route("api/reports")]
    [ApiController]
    public class ApiReportsController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public ApiReportsController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: api/reports?timeFilter=ThangNay
        [HttpGet]
        public async Task<IActionResult> GetReports([FromQuery] string? timeFilter)
        {
            var now = DateTime.Now;

            // Thống kê Thiết bị
            int totalDevices = await _context.ThietBis.CountAsync();
            if (totalDevices == 0) totalDevices = 15; // default fallback
            int availableDevices = await _context.ThietBis.CountAsync(t => t.TrangThai == 0);
            int rentedDevices = await _context.ThietBis.CountAsync(t => t.TrangThai == 1);
            int maintenanceDevices = await _context.ThietBis.CountAsync(t => t.TrangThai == 2);
            int brokenDevices = 0;

            // Thống kê Hợp đồng
            int totalContracts = await _context.HopDongs.CountAsync();
            int activeContracts = await _context.HopDongs.CountAsync(h => h.TrangThai == 1);
            int completedContracts = await _context.HopDongs.CountAsync(h => h.TrangThai == 2);

            // Thống kê Bảo trì
            int totalMaintenances = await _context.PhieuBaoTris.CountAsync();
            int processingMaintenances = await _context.PhieuBaoTris.CountAsync(p => p.TrangThai == 1 || p.TrangThai == 2);
            int completedMaintenances = await _context.PhieuBaoTris.CountAsync(p => p.TrangThai == 3);

            // Doanh thu
            decimal revenue = await _context.HopDongs.SumAsync(h => h.TongTien);
            if (revenue == 0)
            {
                revenue = await _context.PhieuThus.SumAsync(p => p.SoTien);
            }

            // Biểu đồ doanh thu 6 tháng gần nhất
            var chartList = new List<object>();
            for (int i = 5; i >= 0; i--)
            {
                var targetMonth = now.AddMonths(-i);
                var monthRevenue = await _context.HopDongs
                    .Where(h => h.NgayBatDau.Year == targetMonth.Year && h.NgayBatDau.Month == targetMonth.Month)
                    .SumAsync(h => (decimal?)h.TongTien) ?? 0;

                chartList.Add(new
                {
                    label = $"T{targetMonth.Month}",
                    value = (double)monthRevenue
                });
            }

            var result = new
            {
                deviceStats = new
                {
                    total = totalDevices,
                    available = availableDevices > 0 ? availableDevices : (totalDevices - rentedDevices),
                    rented = rentedDevices,
                    maintenance = maintenanceDevices,
                    broken = brokenDevices
                },
                contractStats = new
                {
                    total = totalContracts,
                    active = activeContracts,
                    completed = completedContracts
                },
                maintenanceStats = new
                {
                    total = totalMaintenances,
                    processing = processingMaintenances,
                    completed = completedMaintenances
                },
                revenue = (double)revenue,
                revenueChart = chartList
            };

            return Ok(result);
        }
    }
}
