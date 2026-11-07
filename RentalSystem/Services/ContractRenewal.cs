using Microsoft.EntityFrameworkCore;
using RentalSystem.Common;
using RentalSystem.Models;
using System.Globalization;
using System.Text.RegularExpressions;

namespace RentalSystem.Services;

internal static class ContractRenewal
{
    internal static int ParseDays(int? days, string? duration)
    {
        if (days.HasValue) return days.Value;
        var match = Regex.Match(duration?.Trim() ?? "", @"^(\d+)\s*(?:ngày|ngay|days?)?$", RegexOptions.IgnoreCase);
        if (!match.Success || !int.TryParse(match.Groups[1].Value, NumberStyles.None,
                CultureInfo.InvariantCulture, out int parsed))
            throw new RentalBookingException("Nhập số ngày gia hạn từ 1 đến 365.");
        return parsed;
    }

    internal static async Task<YeuCauGiaHan?> RequestAsync(ApplicationDbContext db, int customerId,
        int contractId, int days, string? reason, CancellationToken cancellation = default)
    {
        if (days is < 1 or > 365) throw new RentalBookingException("Số ngày gia hạn phải từ 1 đến 365.");
        if (reason?.Length > 2000) throw new RentalBookingException("Lý do không được vượt quá 2000 ký tự.");
        await using var transaction = await RentalBooking.BeginInventoryAsync(db, cancellation);
        var contract = await db.HopDongs.FirstOrDefaultAsync(h => h.MaHopDong == contractId &&
            h.MaKhachHang == customerId, cancellation);
        if (contract == null) return null;
        if (contract.TrangThai != 1)
            throw new RentalBookingException("Chỉ có thể gia hạn hợp đồng đang thuê.", 409);
        if ((contract.YeuCauGiaHan && contract.TrangThaiGiaHan == 0) ||
            await db.YeuCauGiaHans.AnyAsync(y => y.MaHopDong == contractId && y.TrangThai == 0, cancellation))
            throw new RentalBookingException("Hợp đồng đang có yêu cầu gia hạn chờ duyệt.", 409);
        DateTime start = contract.NgayKetThuc.Date;
        if (start > DateTime.MaxValue.Date.AddDays(-days))
            throw new RentalBookingException("Ngày kết thúc gia hạn không hợp lệ.");
        DateTime end = start.AddDays(days);
        var deviceIds = db.ChiTietHopDongs.Where(c => c.MaHopDong == contractId).Select(c => c.MaThietBi);
        if (await RentalBooking.OverlappingReservations(db, start, end)
            .AnyAsync(c => c.MaHopDong != contractId && deviceIds.Contains(c.MaThietBi), cancellation))
            throw new RentalBookingException("Thiết bị đã có lịch thuê khác trong thời gian gia hạn.", 409);
        var request = new YeuCauGiaHan
        {
            MaHopDong = contractId, SoNgayGiaHan = days, LyDo = reason?.Trim(),
            NgayYeuCau = DateTime.Now, TrangThai = 0
        };
        db.YeuCauGiaHans.Add(request);
        contract.YeuCauGiaHan = true;
        contract.SoNgayGiaHan = days;
        contract.TrangThaiGiaHan = 0;
        contract.LyDoGiaHan = request.LyDo;
        await db.SaveChangesAsync(cancellation);
        await transaction.CommitAsync(cancellation);
        return request;
    }
}
