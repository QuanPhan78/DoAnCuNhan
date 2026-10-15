using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Services
{
    // Dịch vụ chạy ngầm tự động hủy các đơn hàng quá hạn giữ chỗ và giải phóng thiết bị về kho
    public class ReservationCleanupService : BackgroundService
    {
        private readonly IServiceProvider _serviceProvider;
        private readonly ILogger<ReservationCleanupService> _logger;

        public ReservationCleanupService(IServiceProvider serviceProvider, ILogger<ReservationCleanupService> logger)
        {
            _serviceProvider = serviceProvider;
            _logger = logger;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            while (!stoppingToken.IsCancellationRequested)
            {
                try
                {
                    using (var scope = _serviceProvider.CreateScope())
                    {
                        var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
                        var now = DateTime.Now;

                        // Tìm các hợp đồng ở trạng thái 0 (Chờ duyệt), có hạn chót giữ chỗ đã qua, chưa ký và chưa nộp cọc
                        var expiredContracts = await context.HopDongs
                            .Where(h => h.TrangThai == 0 && h.HanChotKy != null && h.HanChotKy < now && string.IsNullOrEmpty(h.ChuKyKhachHang) && h.TienDaCoc == 0)
                            .ToListAsync(stoppingToken);

                        if (expiredContracts.Any())
                        {
                            _logger.LogInformation("ReservationCleanupService: Tìm thấy {count} hợp đồng quá hạn giữ chỗ cần giải phóng.", expiredContracts.Count);

                            foreach (var hd in expiredContracts)
                            {
                                hd.TrangThai = 3; // Hủy do hết hạn giữ chỗ
                                hd.GhiChu = (hd.GhiChu ?? "") + " [Tự động hủy do quá hạn giữ chỗ 24h]";

                                var chiTiets = await context.ChiTietHopDongs.Where(c => c.MaHopDong == hd.MaHopDong).ToListAsync(stoppingToken);
                                foreach (var ct in chiTiets)
                                {
                                    var tb = await context.ThietBis.FindAsync(new object[] { ct.MaThietBi }, stoppingToken);
                                    if (tb != null && tb.TrangThai == 3)
                                    {
                                        tb.TrangThai = 0; // Giải phóng về kho
                                    }
                                }
                            }

                            await context.SaveChangesAsync(stoppingToken);
                        }
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Lỗi xảy ra trong quá trình quét giải phóng thiết bị quá hạn giữ chỗ.");
                }

                // Quét định kỳ mỗi 15 phút
                await Task.Delay(TimeSpan.FromMinutes(15), stoppingToken);
            }
        }
    }
}
