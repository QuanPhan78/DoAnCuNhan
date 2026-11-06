using Microsoft.AspNetCore.Authorization;
using RentalSystem.Common;
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
    [Authorize(AuthenticationSchemes = ApiTokens.Scheme)]
    public class ApiDashboardController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public ApiDashboardController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: api/dashboard/stats
        [HttpGet("stats")]
        public async Task<IActionResult> GetDashboardStats()
        {
            int accountId = User.UserId();

            var now = DateTime.Now;
            var sevenDaysLater = now.AddDays(7);

            int activeContracts = await _context.HopDongs.CountAsync(h => h.MaKhachHang == accountId && h.TrangThai == 1);
            int expiringContracts = await _context.HopDongs.CountAsync(h =>
                h.MaKhachHang == accountId && h.TrangThai == 1 && h.NgayKetThuc <= sevenDaysLater);
            int processingMaintenance = await _context.PhieuBaoTris.CountAsync(p =>
                p.HopDong != null && p.HopDong.MaKhachHang == accountId && (p.TrangThai == 1 || p.TrangThai == 2));

            var activePromos = (await _context.KhuyenMais
                .Where(k => k.KichHoat)
                .Select(k => new { k.Code, k.PhanTramGiam })
                .ToListAsync())
                .Select(k => $"Mã {k.Code}: Giảm {k.PhanTramGiam}% khi thuê thiết bị")
                .ToList();

            if (!activePromos.Any())
            {
                activePromos.Add("Giảm 20% thuê Laptop");
                activePromos.Add("Miễn phí bảo trì thiết bị");
            }

            bool manager = User.IsManager();
            var tickets = _context.PhieuBaoTris.VisibleTickets(User);
            object? staffStats = null;
            if (manager || User.IsInRole("KyThuat"))
            {
                var myTickets = _context.PhieuBaoTris.Where(p => p.MaKyThuatVien == accountId);
                var manualTasks = _context.PhanCongCongViecs.Where(t => t.MaNhanVien == accountId && !t.TuDongTuBaoTri);
                int pending = await myTickets.CountAsync(p => p.TrangThai == 1) +
                    await manualTasks.CountAsync(t => t.TrangThai == 0);
                int processing = await myTickets.CountAsync(p => p.TrangThai == 2 || p.TrangThai == 3) +
                    await manualTasks.CountAsync(t => t.TrangThai == 1);
                staffStats = new
                {
                    assignedTasks = pending + processing,
                    pendingRequests = pending,
                    processingRequests = processing,
                    completedRequests = await myTickets.CountAsync(p => p.TrangThai == 4 || p.TrangThai == 5) +
                        await manualTasks.CountAsync(t => t.TrangThai == 2)
                };
            }

            object? adminStats = manager ? new
            {
                totalDevices = await _context.ThietBis.CountAsync(),
                rentedDevices = await _context.ThietBis.CountAsync(t => t.TrangThai == 1),
                totalContracts = await _context.HopDongs.CountAsync(),
                maintenanceRequests = await tickets.CountAsync(),
                processingTasks = await _context.HopDongs.CountAsync(h => h.TrangThai == 0) +
                    await tickets.CountAsync(p => p.TrangThai == 1 || p.TrangThai == 2)
            } : null;

            return Ok(new
            {
                customerStats = new
                {
                    activeContracts,
                    expiringContracts,
                    processingMaintenance,
                    notificationsCount = await _context.ThongBaos.CountAsync(n => n.MaNguoiDung == accountId && !n.DaDoc),
                    promotions = activePromos
                },
                staffStats,
                adminStats
            });
        }
    }
}
