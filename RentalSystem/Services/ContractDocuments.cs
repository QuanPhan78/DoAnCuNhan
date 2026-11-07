using Microsoft.EntityFrameworkCore;
using RentalSystem.Common;
using RentalSystem.Models;

namespace RentalSystem.Services;

internal static class ContractDocuments
{
    internal static async Task<string> SaveImageAsync(IWebHostEnvironment env, IFormFile? file,
        string folder, string prefix, int id, CancellationToken cancellation = default)
    {
        if (file == null || file.Length == 0) throw new RentalBookingException("Vui lòng chọn ảnh.");
        if (file.Length > 5 * 1024 * 1024) throw new RentalBookingException("Mỗi ảnh không được vượt quá 5 MB.");
        var ext = Path.GetExtension(file.FileName).ToLowerInvariant();
        using var input = file.OpenReadStream();
        using var buffer = new MemoryStream();
        await input.CopyToAsync(buffer, cancellation);
        var bytes = buffer.ToArray();
        bool png = bytes.Length >= 8 && bytes.AsSpan(0, 8).SequenceEqual(new byte[] {137,80,78,71,13,10,26,10});
        bool jpg = bytes.Length >= 3 && bytes[0] == 255 && bytes[1] == 216 && bytes[2] == 255;
        bool webp = bytes.Length >= 12 && System.Text.Encoding.ASCII.GetString(bytes, 0, 4) == "RIFF" &&
            System.Text.Encoding.ASCII.GetString(bytes, 8, 4) == "WEBP";
        if (!(png && ext == ".png" || jpg && (ext == ".jpg" || ext == ".jpeg") || webp && ext == ".webp"))
            throw new RentalBookingException("Ảnh phải có nội dung và đuôi tệp PNG, JPG hoặc WEBP hợp lệ.");
        string directory = Path.Combine(env.WebRootPath, "uploads", folder);
        Directory.CreateDirectory(directory);
        string name = $"{prefix}_{id}_{Guid.NewGuid():N}{ext}";
        await File.WriteAllBytesAsync(Path.Combine(directory, name), bytes, cancellation);
        return $"/uploads/{folder}/{name}";
    }

    internal static byte[] SignatureBytes(string? signature)
    {
        if (string.IsNullOrWhiteSpace(signature) || signature.Length > 256 * 1024)
            throw new RentalBookingException("Vui lòng ký tên bằng ảnh PNG có dữ liệu không quá 256 KB.");
        const string prefix = "data:image/png;base64,";
        if (signature.StartsWith(prefix, StringComparison.OrdinalIgnoreCase)) signature = signature[prefix.Length..];
        byte[] bytes;
        try { bytes = Convert.FromBase64String(signature); }
        catch (FormatException) { throw new RentalBookingException("Dữ liệu chữ ký không hợp lệ."); }
        if (bytes.Length < 8 || !bytes.AsSpan(0, 8).SequenceEqual(new byte[] {137,80,78,71,13,10,26,10}))
            throw new RentalBookingException("Chữ ký phải là ảnh PNG.");
        return bytes;
    }

    internal static async Task<HopDong?> SignAsync(ApplicationDbContext db, IWebHostEnvironment env,
        int customerId, int id, int periods, IFormFile? front, IFormFile? back, string? signature,
        bool legacyFrontOnly = false, CancellationToken cancellation = default)
    {
        var bytes = SignatureBytes(signature);
        await using var transaction = await RentalBooking.BeginInventoryAsync(db, cancellation);
        var contract = await db.HopDongs.FirstOrDefaultAsync(h => h.MaHopDong == id && h.MaKhachHang == customerId, cancellation);
        if (contract == null) return null;
        var customer = await db.NguoiDungs.FindAsync([customerId], cancellation);
        if (string.IsNullOrWhiteSpace(customer?.CCCD)) throw new RentalBookingException("Vui lòng cập nhật CCCD trong hồ sơ.");
        var restriction = await DebtCalculationHelper.IsCustomerBlacklistedAsync(customerId, db);
        if (restriction.isBlacklisted) throw new RentalBookingException(restriction.reason, 409);
        if (contract.TrangThai != 0 || contract.YeuCauHuy || !string.IsNullOrWhiteSpace(contract.ChuKyKhachHang))
            throw new RentalBookingException("Hợp đồng không còn chờ ký hoặc đã gửi yêu cầu hủy.", 409);
        if (contract.HanChotKy.HasValue && contract.HanChotKy.Value < DateTime.Now)
            throw new RentalBookingException("Hợp đồng đã hết thời hạn giữ chỗ.", 409);
        int maxPeriods = Math.Max(1, RentalBooking.RentalDays(contract.NgayBatDau, contract.NgayKetThuc) / 7);
        if (periods < 1 || periods > maxPeriods) throw new RentalBookingException($"Số kỳ thanh toán phải từ 1 đến {maxPeriods}.");
        if ((front == null && string.IsNullOrWhiteSpace(contract.AnhCCCD_Truoc)) ||
            (!legacyFrontOnly && back == null && string.IsNullOrWhiteSpace(contract.AnhCCCD_Sau)))
            throw new RentalBookingException("Vui lòng tải đủ ảnh CCCD mặt trước và mặt sau.");
        var saved = new List<string>();
        bool committed = false;
        try
        {
            if (front != null)
            {
                contract.AnhCCCD_Truoc = await SaveImageAsync(env, front, "cmnd", "cccd_front", id, cancellation);
                saved.Add(contract.AnhCCCD_Truoc);
            }
            if (back != null)
            {
                contract.AnhCCCD_Sau = await SaveImageAsync(env, back, "cmnd", "cccd_back", id, cancellation);
                saved.Add(contract.AnhCCCD_Sau);
            }
            string folder = Path.Combine(env.WebRootPath, "uploads", "signatures");
            Directory.CreateDirectory(folder);
            string name = $"kh_{id}_{Guid.NewGuid():N}.png";
            contract.ChuKyKhachHang = $"/uploads/signatures/{name}";
            await File.WriteAllBytesAsync(Path.Combine(folder, name), bytes, cancellation);
            saved.Add(contract.ChuKyKhachHang);
            contract.SoKyHan = periods;
            contract.NgayKy = DateTime.Now;
            if (contract.YeuCauThanhToanLanDau && !await db.KyHanThanhToans.AnyAsync(k => k.MaHopDong == id, cancellation))
                db.KyHanThanhToans.AddRange(FirstContractPayment.CreateSchedule(contract));
            await db.SaveChangesAsync(cancellation);
            await transaction.CommitAsync(cancellation);
            committed = true;
            return contract;
        }
        finally
        {
            if (!committed)
                foreach (string path in saved)
                    File.Delete(Path.Combine(env.WebRootPath, path.TrimStart('/').Replace('/', Path.DirectorySeparatorChar)));
        }
    }

    internal static async Task<KyHanThanhToan?> ReceiptAsync(ApplicationDbContext db, IWebHostEnvironment env,
        int customerId, int installmentId, string? reference, IFormFile? image, CancellationToken cancellation = default)
    {
        reference = reference?.Trim();
        if (reference?.Length is not (> 0 and <= 100)) throw new RentalBookingException("Nhập mã giao dịch từ 1 đến 100 ký tự.");
        await using var transaction = await db.Database.BeginTransactionAsync(System.Data.IsolationLevel.Serializable, cancellation);
        var installment = await db.KyHanThanhToans.Include(k => k.HopDong)
            .FirstOrDefaultAsync(k => k.MaKyHan == installmentId && k.HopDong.MaKhachHang == customerId, cancellation);
        if (installment == null) return null;
        if (installment.TrangThai is 1 or 3 || installment.HopDong.TrangThai == 3 ||
            installment.HopDong.YeuCauHuy || await db.ContractSettlements.AnyAsync(s => s.MaHopDong == installment.MaHopDong, cancellation))
            throw new RentalBookingException("Kỳ hạn không còn nhận yêu cầu thanh toán.", 409);
        if (installment.TrangThaiXacNhan == 1) throw new RentalBookingException("Biên lai đang chờ đối soát.", 409);
        if (FirstContractPayment.IsPendingHandover(installment.HopDong) &&
            (installment.SoKyHan != 1 || string.IsNullOrWhiteSpace(installment.HopDong.ChuKyKhachHang)))
            throw new RentalBookingException("Vui lòng ký hợp đồng trước khi gửi biên lai khoản đầu.", 409);
        string path = await SaveImageAsync(env, image, "bienlai", "bill", installmentId, cancellation);
        bool committed = false;
        try
        {
            installment.MaGiaoDichChuyenKhoan = reference;
            installment.HinhAnhBienLai = path;
            installment.TrangThaiXacNhan = 1;
            installment.NgayGuiBienLai = DateTime.Now;
            await db.SaveChangesAsync(cancellation);
            await transaction.CommitAsync(cancellation);
            committed = true;
            return installment;
        }
        finally
        {
            if (!committed) File.Delete(Path.Combine(env.WebRootPath, path.TrimStart('/').Replace('/', Path.DirectorySeparatorChar)));
        }
    }
}
