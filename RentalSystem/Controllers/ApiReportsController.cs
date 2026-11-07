using Microsoft.AspNetCore.Authorization;
using RentalSystem.Common;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using RentalSystem.Services;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Controllers
{
    [Route("api/reports")]
    [ApiController]
    [Authorize(AuthenticationSchemes = ApiTokens.Scheme, Roles = ApiAccess.Managers)]
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
            var today = DateTime.Today;
            var period = RevenuePeriod.Resolve(timeFilter, today);
            var revenue = await RevenueReport.LoadAsync(_context, period, today);

            var devices = await _context.ThietBis.GroupBy(t => t.TrangThai)
                .Select(group => new { Status = group.Key, Count = group.Count() })
                .ToDictionaryAsync(group => group.Status, group => group.Count);
            var contracts = _context.HopDongs.Where(h => h.TrangThai != 3);
            var maintenance = _context.PhieuBaoTris.AsQueryable();
            if (period.Start is DateTime start && period.End is DateTime end)
            {
                contracts = contracts.Where(h => h.NgayBatDau >= start && h.NgayBatDau < end);
                maintenance = maintenance.Where(p => p.NgayBaoLoi >= start && p.NgayBaoLoi < end);
            }

            var result = new
            {
                timeFilter = period.Key,
                fromDate = period.Start?.ToString("yyyy-MM-dd"),
                throughDate = period.End?.AddDays(-1).ToString("yyyy-MM-dd"),
                deviceStats = new
                {
                    total = devices.Values.Sum(),
                    available = devices.GetValueOrDefault(0),
                    rented = devices.GetValueOrDefault(1),
                    maintenance = devices.GetValueOrDefault(2),
                    reserved = devices.GetValueOrDefault(3),
                    broken = devices.GetValueOrDefault(4)
                },
                contractStats = new
                {
                    total = await contracts.CountAsync(),
                    active = await contracts.CountAsync(h => h.TrangThai == 1),
                    completed = await contracts.CountAsync(h => h.TrangThai == 2)
                },
                maintenanceStats = new
                {
                    total = await maintenance.CountAsync(),
                    processing = await maintenance.CountAsync(p => p.TrangThai == 1 || p.TrangThai == 2 || p.TrangThai == 3),
                    completed = await maintenance.CountAsync(p => p.TrangThai == 5)
                },
                revenue = revenue.Total,
                revenueChart = revenue.Chart
            };

            return Ok(result);
        }
    }
}
