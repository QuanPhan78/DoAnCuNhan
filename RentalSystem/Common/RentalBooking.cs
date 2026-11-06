using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Storage;
using RentalSystem.Models;

namespace RentalSystem.Common;

internal record RentalLine(int ProductId, int Quantity);
internal record RentalOrder(DateTime? Start, DateTime? End, string? Address, string? Note,
    string? PromoCode, IReadOnlyList<RentalLine> Lines, decimal? ExpectedTotal = null);
internal record RentalPriceLine(int ProductId, string ProductName, int Quantity, decimal DailyPrice, decimal Subtotal);
internal record RentalQuote(int RentalDays, decimal Subtotal, decimal DiscountAmount, decimal TotalAmount,
    string? PromoCode, int DiscountPercent, IReadOnlyList<RentalPriceLine> Items);

internal sealed class RentalBookingException(string message, int statusCode = StatusCodes.Status400BadRequest)
    : Exception(message)
{
    internal int StatusCode { get; } = statusCode;
}

internal static class RentalBooking
{
    internal static readonly int[] RentableStatuses = [0, 1, 3];

    internal static int RentalDays(DateTime start, DateTime end) => Math.Max(1, (end.Date - start.Date).Days);

    internal static IQueryable<ChiTietHopDong> OverlappingReservations(ApplicationDbContext db, DateTime start, DateTime end)
    {
        start = start.Date;
        end = end.Date;
        if (end == start && end < DateTime.MaxValue.Date) end = end.AddDays(1);
        return db.ChiTietHopDongs.Where(c =>
            (c.HopDong.TrangThai == 0 || c.HopDong.TrangThai == 1) &&
            c.HopDong.NgayBatDau.Date < end &&
            (c.HopDong.NgayKetThuc.Date > start ||
             (c.HopDong.NgayKetThuc.Date == c.HopDong.NgayBatDau.Date && c.HopDong.NgayBatDau.Date >= start)));
    }

    internal static IQueryable<ThietBi> AvailableDevices(ApplicationDbContext db, int productId, DateTime start, DateTime end)
    {
        var reservations = OverlappingReservations(db, start, end);
        return db.ThietBis.Where(t => t.MaSanPham == productId && RentableStatuses.Contains(t.TrangThai) &&
            !reservations.Any(c => c.MaThietBi == t.MaThietBi));
    }

    internal static async Task<IDbContextTransaction> BeginInventoryAsync(ApplicationDbContext db, CancellationToken cancellation = default)
    {
        var transaction = await db.Database.BeginTransactionAsync(System.Data.IsolationLevel.Serializable, cancellation);
        try
        {
            await db.Database.ExecuteSqlRawAsync("""
                DECLARE @result int;
                EXEC @result = sys.sp_getapplock @Resource = 'RentalSystem.Inventory.Booking',
                    @LockMode = 'Exclusive', @LockOwner = 'Transaction', @LockTimeout = 10000;
                IF @result < 0 THROW 51013, N'Inventory lock unavailable.', 1;
                """, cancellation);
            return transaction;
        }
        catch (Microsoft.Data.SqlClient.SqlException error) when (error.Number == 51013)
        {
            await transaction.DisposeAsync();
            throw new RentalBookingException("Kho đang xử lý đơn khác. Vui lòng thử lại.", StatusCodes.Status409Conflict);
        }
        catch
        {
            await transaction.DisposeAsync();
            throw;
        }
    }

    internal static async Task<KhuyenMai?> FindPromotionAsync(ApplicationDbContext db, string? code,
        DateTime now, CancellationToken cancellation = default)
    {
        if (string.IsNullOrWhiteSpace(code)) return null;
        string normalized = code.Trim().ToUpperInvariant();
        var promo = await db.KhuyenMais.FirstOrDefaultAsync(k => k.Code.ToUpper() == normalized, cancellation);
        if (promo == null) throw new RentalBookingException("Mã khuyến mãi không tồn tại.");
        if (!promo.KichHoat || promo.NgayBatDau > now || promo.NgayKetThuc < now || promo.PhanTramGiam is < 1 or > 100)
            throw new RentalBookingException("Mã khuyến mãi chưa có hiệu lực hoặc đã hết hạn.");
        if (promo.SoLuong <= 0)
            throw new RentalBookingException("Mã khuyến mãi đã hết lượt.", StatusCodes.Status409Conflict);
        return promo;
    }

    internal static decimal Discount(decimal subtotal, int percent) =>
        Math.Min(subtotal, Math.Round(subtotal * percent / 100m, 0));

    internal static async Task<RentalQuote> QuoteAsync(ApplicationDbContext db, int customerId, RentalOrder order,
        CancellationToken cancellation)
    {
        var (quote, _, _, _) = await PrepareAsync(db, customerId, order, cancellation);
        return quote;
    }

    internal static async Task<(HopDong Contract, RentalQuote Quote, int DeviceCount, string CustomerName)> CreateAsync(
        ApplicationDbContext db, int customerId, RentalOrder order, CancellationToken cancellation)
    {
        if (string.IsNullOrWhiteSpace(order.Address))
            throw new RentalBookingException("Vui lòng nhập địa chỉ giao thiết bị.");

        await using var transaction = await BeginInventoryAsync(db, cancellation);
        var (quote, promo, devices, customerName) = await PrepareAsync(db, customerId, order, cancellation);
        if (order.ExpectedTotal.HasValue && order.ExpectedTotal.Value != quote.TotalAmount)
            throw new RentalBookingException("Giá thuê đã thay đổi. Vui lòng kiểm tra lại tổng tiền.", StatusCodes.Status409Conflict);

        int staffId = await db.NguoiDungs.Where(u => u.TrangThai &&
                (u.VaiTro.TenVaiTro == "Admin" || u.VaiTro.TenVaiTro == "KinhDoanh"))
            .OrderBy(u => u.MaNguoiDung)
            .Select(u => u.MaNguoiDung)
            .FirstOrDefaultAsync(cancellation);
        if (staffId == 0) staffId = customerId;

        string note = $"Giao hàng tới: {order.Address!.Trim()}";
        if (!string.IsNullOrWhiteSpace(order.Note)) note += $"\n{order.Note.Trim()}";
        if (promo != null)
        {
            note += $" [Giảm {promo.PhanTramGiam}% theo mã {promo.Code}: -{quote.DiscountAmount:N0}đ]";
            promo.SoLuong--;
        }

        var contract = new HopDong
        {
            MaKhachHang = customerId,
            MaNhanVien = staffId,
            NgayBatDau = order.Start!.Value.Date,
            NgayKetThuc = order.End!.Value.Date,
            TongTien = quote.TotalAmount,
            MaKhuyenMai = promo?.MaKM,
            TrangThai = 0,
            TrangThaiThanhToan = ContractPaymentStatus.Unpaid,
            NgayKy = null,
            ChuKyKhachHang = "",
            ChuKyNhanVien = "",
            GhiChu = note,
            SoKyHan = 1,
            HanChotKy = DateTime.Now.AddHours(24)
        };
        db.HopDongs.Add(contract);
        foreach (var (device, price) in devices)
        {
            db.ChiTietHopDongs.Add(new ChiTietHopDong
            {
                HopDong = contract,
                MaThietBi = device.MaThietBi,
                GiaChotThu = price
            });
            if (device.TrangThai == 0) device.TrangThai = 3;
        }

        await db.SaveChangesAsync(cancellation);
        await transaction.CommitAsync(cancellation);
        return (contract, quote, devices.Count, customerName);
    }

    private static async Task<(RentalQuote Quote, KhuyenMai? Promo, List<(ThietBi Device, decimal Price)> Devices, string CustomerName)>
        PrepareAsync(ApplicationDbContext db, int customerId, RentalOrder order, CancellationToken cancellation)
    {
        var now = DateTime.Now;
        if (order.Start?.Date is not DateTime start || order.End?.Date is not DateTime end ||
            start < now.Date || end < start || start == DateTime.MaxValue.Date)
            throw new RentalBookingException("Ngày nhận phải từ hôm nay, ngày trả từ ngày nhận trở đi.");
        if (order.Lines.Count == 0 || order.Lines.Any(line => line.ProductId <= 0 || line.Quantity <= 0))
            throw new RentalBookingException("Vui lòng chọn sản phẩm và số lượng hợp lệ.");

        var customer = await db.NguoiDungs.AsNoTracking().FirstOrDefaultAsync(u =>
            u.MaNguoiDung == customerId && u.TrangThai && u.VaiTro.TenVaiTro == "KhachHang", cancellation);
        if (customer == null)
            throw new RentalBookingException("Tài khoản không có quyền đặt thuê.", StatusCodes.Status403Forbidden);
        if (string.IsNullOrWhiteSpace(customer.CCCD))
            throw new RentalBookingException("Vui lòng bổ sung số CCCD trong hồ sơ trước khi đặt thuê.");
        var restriction = await DebtCalculationHelper.IsCustomerBlacklistedAsync(customerId, db);
        if (restriction.isBlacklisted)
            throw new RentalBookingException(restriction.reason, StatusCodes.Status403Forbidden);

        int days = RentalDays(start, end);
        var promo = await FindPromotionAsync(db, order.PromoCode, now, cancellation);
        var devices = new List<(ThietBi Device, decimal Price)>();
        var lines = new List<RentalPriceLine>();
        foreach (var group in order.Lines.GroupBy(line => line.ProductId))
        {
            long requested = group.Sum(line => (long)line.Quantity);
            if (requested > int.MaxValue)
                throw new RentalBookingException("Số lượng thiết bị vượt quá giới hạn.");

            int quantity = (int)requested;
            var product = await db.SanPhams.FindAsync([group.Key], cancellation);
            if (product == null) throw new RentalBookingException($"Sản phẩm #{group.Key} không còn trong danh mục.");

            var selected = await AvailableDevices(db, group.Key, start, end)
                .OrderBy(device => device.MaThietBi).Take(quantity).ToListAsync(cancellation);
            if (selected.Count != quantity)
                throw new RentalBookingException(
                    $"Sản phẩm «{product.TenSanPham}» chỉ còn {selected.Count} máy cho thời gian đã chọn.",
                    StatusCodes.Status409Conflict);

            decimal unitTotal = product.GiaThueNgay * days;
            lines.Add(new RentalPriceLine(group.Key, product.TenSanPham, quantity, product.GiaThueNgay, unitTotal * quantity));
            devices.AddRange(selected.Select(device => (device, unitTotal)));
        }

        decimal subtotal = lines.Sum(line => line.Subtotal);
        int percent = promo?.PhanTramGiam ?? 0;
        decimal discount = Discount(subtotal, percent);
        var quote = new RentalQuote(days, subtotal, discount, subtotal - discount, promo?.Code, percent, lines);
        return (quote, promo, devices, customer.HoTen);
    }
}
