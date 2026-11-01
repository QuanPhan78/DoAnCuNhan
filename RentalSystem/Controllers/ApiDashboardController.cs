using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace RentalSystem.Controllers
{
    [Route("api/dashboard")]
    [ApiController]
    public class ApiDashboardController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public ApiDashboardController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: api/dashboard/stats
        [HttpGet("stats")]
        public async Task<IActionResult> GetDashboardStats(
            [FromQuery] string? userId,
            [FromQuery] string? role)
        {
            int parsedUserId = 0;
            if (!string.IsNullOrEmpty(userId))
            {
                int.TryParse(userId, out parsedUserId);
            }

            var now = DateTime.Now;
            var sevenDaysLater = now.AddDays(7);

            // 1. Dữ liệu Khách hàng
            int activeContracts = 0;
            int expiringContracts = 0;
            int processingMaintenance = 0;

            if (parsedUserId > 0)
            {
                activeContracts = await _context.HopDongs
                    .CountAsync(h => h.MaKhachHang == parsedUserId && h.TrangThai == 1);

                expiringContracts = await _context.HopDongs
                    .CountAsync(h => h.MaKhachHang == parsedUserId && h.TrangThai == 1 && h.NgayKetThuc <= sevenDaysLater);

                processingMaintenance = await _context.PhieuBaoTris
                    .CountAsync(p => p.HopDong.MaKhachHang == parsedUserId && (p.TrangThai == 1 || p.TrangThai == 2));
            }

            var activePromos = await _context.KhuyenMais
                .Where(k => k.KichHoat)
                .Select(k => $"Mã {k.MaCode}: Giảm {k.PhanTramGiam}% khi thuê thiết bị")
                .ToListAsync();

            if (!activePromos.Any())
            {
                activePromos.Add("Giảm 20% thuê Laptop");
                activePromos.Add("Miễn phí bảo trì thiết bị");
            }

            // 2. Dữ liệu Nhân viên (Staff)
            int pendingRequests = await _context.HopDongs.CountAsync(h => h.TrangThai == 0) +
                                  await _context.PhieuBaoTris.CountAsync(p => p.TrangThai == 1);
            int processingRequests = await _context.PhieuBaoTris.CountAsync(p => p.TrangThai == 2);
            int completedRequests = await _context.PhieuBaoTris.CountAsync(p => p.TrangThai == 3);
            int assignedTasks = pendingRequests + processingRequests;

            // 3. Dữ liệu Quản trị viên (Admin)
            int totalDevices = await _context.ThietBis.CountAsync();
            int rentedDevices = await _context.ThietBis.CountAsync(t => t.TrangThai == 1);
            int totalContracts = await _context.HopDongs.CountAsync();
            int maintenanceRequests = await _context.PhieuBaoTris.CountAsync();
            int processingTasks = await _context.HopDongs.CountAsync(h => h.TrangThai == 0) +
                                  await _context.PhieuBaoTris.CountAsync(p => p.TrangThai == 1 || p.TrangThai == 2);

            return Ok(new
            {
                customerStats = new
                {
                    activeContracts = activeContracts,
                    expiringContracts = expiringContracts,
                    processingMaintenance = processingMaintenance,
                    notificationsCount = expiringContracts + processingMaintenance,
                    promotions = activePromos
                },
                staffStats = new
                {
                    assignedTasks = assignedTasks,
                    pendingRequests = pendingRequests,
                    processingRequests = processingRequests,
                    completedRequests = completedRequests
                },
                adminStats = new
                {
                    totalDevices = totalDevices > 0 ? totalDevices : 15,
                    rentedDevices = rentedDevices,
                    totalContracts = totalContracts,
                    maintenanceRequests = maintenanceRequests,
                    processingTasks = processingTasks
                }
            });
        }
    }
}
