using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Common;

internal static class ContractLifecycle
{
    internal static string Label(HopDong contract) => contract.TrangThai switch
    {
        0 when contract.YeuCauHuy => "Yêu cầu hủy",
        0 => "Chờ duyệt",
        1 => "Đang hiệu lực",
        2 => "Hoàn thành",
        3 => "Đã hủy",
        4 => "Đã trả máy (Chờ quyết toán)",
        _ => "Chưa xác định"
    };

    internal static bool CanTransition(int current, int next) => (current, next) switch
    {
        (0, 1 or 3) => true,
        (1, 2 or 4) => true,
        (4, 2) => true,
        _ => false
    };

    internal static async Task<int> ReleasedDeviceStatusAsync(ApplicationDbContext db, ThietBi device, int contractId)
    {
        if (device.TrangThai == 2) return 2;
        var otherBookings = db.ChiTietHopDongs.Where(c =>
            c.MaThietBi == device.MaThietBi && c.MaHopDong != contractId);
        if (await otherBookings.AnyAsync(c => c.HopDong.TrangThai == 1)) return 1;
        return await otherBookings.AnyAsync(c => c.HopDong.TrangThai == 0) ? 3 : 0;
    }

    internal static async Task<HopDong?> RequestCancellationAsync(ApplicationDbContext db, int customerId,
        int contractId, string? reason, CancellationToken cancellation)
    {
        await using var transaction = await RentalBooking.BeginInventoryAsync(db, cancellation);
        var contract = await db.HopDongs.FirstOrDefaultAsync(
            h => h.MaHopDong == contractId && h.MaKhachHang == customerId, cancellation);
        if (contract == null) return null;
        if (contract.TrangThai != 0)
            throw new RentalBookingException("Chỉ có thể yêu cầu hủy đơn chờ duyệt.", StatusCodes.Status409Conflict);
        if (contract.YeuCauHuy) return contract;

        reason = reason?.Trim();
        if (string.IsNullOrEmpty(reason) || reason.Length > 500)
            throw new RentalBookingException("Nhập lý do hủy từ 1 đến 500 ký tự.");

        contract.YeuCauHuy = true;
        contract.LyDoHuy = reason;
        contract.NgayYeuCauHuy = DateTime.Now;
        await db.SaveChangesAsync(cancellation);
        await transaction.CommitAsync(cancellation);
        return contract;
    }
}
