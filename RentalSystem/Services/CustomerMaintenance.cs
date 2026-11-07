using Microsoft.EntityFrameworkCore;
using RentalSystem.Common;
using RentalSystem.Models;

namespace RentalSystem.Services;

internal sealed class CustomerMaintenanceException(string message, int statusCode = 400) : Exception(message)
{
    internal int StatusCode { get; } = statusCode;
}

internal static class CustomerMaintenance
{
    internal static async Task<PhieuBaoTri> ReportAsync(ApplicationDbContext db, string webRoot, int customerId,
        int contractId, string? deviceSelection, string? description, int urgency, IEnumerable<IFormFile> files,
        bool allowVideo, CancellationToken cancellation)
    {
        await using var transaction = await RentalBooking.BeginInventoryAsync(db, cancellation);
        var contract = await db.HopDongs.SingleOrDefaultAsync(
            h => h.MaHopDong == contractId && h.MaKhachHang == customerId, cancellation);
        if (contract == null) throw new CustomerMaintenanceException("Không tìm thấy hợp đồng của bạn.", 404);
        if (contract.TrangThai != 1)
            throw new CustomerMaintenanceException("Chỉ có thể báo sự cố cho hợp đồng đang thuê.", 409);

        var devices = await db.ChiTietHopDongs.Where(c => c.MaHopDong == contractId)
            .Select(c => new { Id = c.MaThietBi, Serial = c.ThietBi.SoSerial, Name = c.ThietBi.SanPham.TenSanPham })
            .ToListAsync(cancellation);
        var selection = deviceSelection?.Trim();
        var matches = devices.Where(device => int.TryParse(selection, out var id) ? device.Id == id :
            !string.IsNullOrEmpty(selection) && (string.Equals(selection, device.Serial, StringComparison.OrdinalIgnoreCase) ||
                string.Equals(selection, $"{device.Name} ({device.Serial})", StringComparison.OrdinalIgnoreCase))).ToList();
        if (matches.Count != 1)
            throw new CustomerMaintenanceException("Hãy chọn đúng thiết bị thuộc hợp đồng.");
        int deviceId = matches[0].Id;
        if (await db.PhieuBaoTris.AnyAsync(p => p.MaThietBi == deviceId &&
            (p.TrangThai == 1 || p.TrangThai == 2 || p.TrangThai == 3), cancellation))
            throw new CustomerMaintenanceException("Thiết bị đang có phiếu bảo trì chưa đóng.", 409);
        if (string.IsNullOrWhiteSpace(description))
            throw new CustomerMaintenanceException("Vui lòng nhập mô tả lỗi.");

        var uploads = new List<(IFormFile File, string Extension, bool Image)>();
        foreach (var file in files)
        {
            string extension = Path.GetExtension(file.FileName).ToLowerInvariant();
            bool image = extension is ".jpg" or ".jpeg" or ".png" or ".webp";
            bool video = allowVideo && extension is (".mp4" or ".mov" or ".avi" or ".webm" or ".mkv");
            if (!image && !video || file.Length == 0)
                throw new CustomerMaintenanceException("Tệp đính kèm không đúng định dạng.");
            if (file.Length > (image ? 10L : 50L) * 1024 * 1024)
                throw new CustomerMaintenanceException(image ? "Mỗi ảnh tối đa 10 MB." : "Mỗi video tối đa 50 MB.");
            if (image && !await HasImageSignatureAsync(file, extension, cancellation))
                throw new CustomerMaintenanceException("Tệp đính kèm không phải ảnh hợp lệ.");
            uploads.Add((file, extension, image));
        }

        var saved = new List<(string Path, string Url, bool Image)>();
        try
        {
            if (uploads.Count > 0)
            {
                string folder = Path.Combine(webRoot, "uploads", "baotri");
                Directory.CreateDirectory(folder);
                foreach (var upload in uploads)
                {
                    string name = $"{Guid.NewGuid():N}{upload.Extension}";
                    string path = Path.Combine(folder, name);
                    await using var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None);
                    saved.Add((path, $"/uploads/baotri/{name}", upload.Image));
                    await upload.File.CopyToAsync(stream, cancellation);
                }
            }

            var now = DateTime.Now;
            var ticket = new PhieuBaoTri
            {
                MaHopDong = contractId, MaThietBi = deviceId, MoTaLoi = description.Trim(),
                NgayBaoLoi = now, TrangThai = 1, GhiChuSuaChua = "",
                HinhAnhLoi = JoinPaths(saved.Where(file => file.Image).Select(file => file.Url)),
                VideoLoi = JoinPaths(saved.Where(file => !file.Image).Select(file => file.Url)),
                MucDoKhanCap = urgency, HanHoanThanh = now.AddHours(urgency == 2 ? 12 : urgency == 3 ? 24 : 48)
            };
            db.PhieuBaoTris.Add(ticket);
            await db.SaveChangesAsync(cancellation);
            db.LichSuThietBis.Add(new LichSuThietBi
            {
                MaThietBi = deviceId, MaNguoiThucHien = customerId, ThoiGian = now,
                HanhDong = $"Khách hàng gửi báo hỏng phiếu #{ticket.MaPhieu} theo HĐ #{contractId}",
                GhiChu = $"Yêu cầu xử lý từ khách hàng. SLA hoàn thành: {ticket.HanHoanThanh:dd/MM/yyyy HH:mm}"
            });
            await db.SaveChangesAsync(cancellation);
            await transaction.CommitAsync(cancellation);
            return ticket;
        }
        catch
        {
            foreach (var file in saved)
            {
                try { File.Delete(file.Path); }
                catch (IOException) { }
                catch (UnauthorizedAccessException) { }
            }
            throw;
        }
    }

    internal static string[] ImagePaths(PhieuBaoTri ticket) =>
        ticket.HinhAnhLoi?.Split(';', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries) ?? [];

    private static string? JoinPaths(IEnumerable<string> paths)
    {
        var value = string.Join(';', paths);
        return value.Length == 0 ? null : value;
    }

    private static async Task<bool> HasImageSignatureAsync(IFormFile file, string extension, CancellationToken cancellation)
    {
        var header = new byte[12];
        await using var stream = file.OpenReadStream();
        int read = await stream.ReadAtLeastAsync(header, header.Length, false, cancellation);
        return extension switch
        {
            ".jpg" or ".jpeg" => read >= 3 && header[0] == 0xff && header[1] == 0xd8 && header[2] == 0xff,
            ".png" => read >= 8 && header.AsSpan(0, 8).SequenceEqual(new byte[] { 137, 80, 78, 71, 13, 10, 26, 10 }),
            ".webp" => read == 12 && header.AsSpan(0, 4).SequenceEqual("RIFF"u8) &&
                header.AsSpan(8, 4).SequenceEqual("WEBP"u8),
            _ => false
        };
    }

    internal static async Task<PhieuBaoTri> ReviewAsync(ApplicationDbContext db, int customerId, int id,
        bool? accepted, int? rating, string? feedback)
    {
        await using var transaction = await MaintenanceAssignment.BeginUpdateAsync(db, id);
        var ticket = await db.PhieuBaoTris.FirstOrDefaultAsync(p =>
            p.MaPhieu == id && p.HopDong != null && p.HopDong.MaKhachHang == customerId);
        if (ticket == null) throw new CustomerMaintenanceException("Không tìm thấy phiếu sự cố.", 404);

        feedback = feedback?.Trim();
        if (feedback?.Length > 1000)
            throw new CustomerMaintenanceException("Nhận xét tối đa 1.000 ký tự.");
        string action;
        if (accepted.HasValue)
        {
            if (ticket.TrangThai != 3)
                throw new CustomerMaintenanceException("Chỉ có thể nghiệm thu khi thiết bị đã sửa xong.", 409);
            if (!accepted.Value && string.IsNullOrEmpty(feedback))
                throw new CustomerMaintenanceException("Nhập lý do từ chối nghiệm thu.");

            await MaintenanceAssignment.ApplyStatusAsync(db, ticket, accepted.Value ? 5 : 2);
            if (!accepted.Value)
                ticket.GhiChuSuaChua = $"{ticket.GhiChuSuaChua} [Khách yêu cầu xử lý lại: {feedback}]".Trim();
            await MaintenanceAssignment.SyncAsync(db, ticket, null);
            action = accepted.Value ? "Khách nghiệm thu" : "Khách từ chối nghiệm thu";
        }
        else
        {
            if (ticket.TrangThai is not (3 or 5))
                throw new CustomerMaintenanceException("Chỉ có thể đánh giá sau khi phiếu đã sửa xong.", 409);
            if (rating is null or < 1 or > 5)
                throw new CustomerMaintenanceException("Điểm đánh giá phải từ 1 đến 5 sao.");

            ticket.DanhGiaSao = rating;
            if (!string.IsNullOrEmpty(feedback)) ticket.YKienPhanHoi = feedback;
            action = $"Khách đánh giá {rating} sao";
        }
        db.LichSuThietBis.Add(new LichSuThietBi
        {
            MaThietBi = ticket.MaThietBi, MaNguoiThucHien = customerId, ThoiGian = DateTime.Now,
            HanhDong = $"{action} phiếu bảo trì #{id}", GhiChu = feedback
        });
        await db.SaveChangesAsync();
        await transaction.CommitAsync();
        return ticket;
    }
}
