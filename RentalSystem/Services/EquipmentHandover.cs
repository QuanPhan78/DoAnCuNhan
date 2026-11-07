using System.Security.Claims;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Common;
using RentalSystem.Models;

namespace RentalSystem.Services;

internal static class EquipmentHandover
{
    internal static async Task<BienBanBanGiao?> CreateAsync(ApplicationDbContext db, IWebHostEnvironment env,
        ClaimsPrincipal user, int contractId, int kind, string? accessories, string? condition, string? note,
        IReadOnlyList<IFormFile> photos, string? signature = null, CancellationToken cancellation = default)
    {
        if (!user.IsManager() && !user.IsInRole("KyThuat")) throw new RentalBookingException("Bạn không có quyền lập biên bản.", 403);
        if (kind is not (0 or 1) || photos.Count > 4) throw new RentalBookingException("Chọn loại biên bản hợp lệ và tối đa 4 ảnh.");
        if (string.IsNullOrWhiteSpace(condition) || condition.Length > 4000 || note?.Length > 4000 || accessories?.Length > 2000)
            throw new RentalBookingException("Nhập tình trạng thiết bị hợp lệ (tối đa 4000 ký tự).");
        await using var transaction = await RentalBooking.BeginInventoryAsync(db, cancellation);
        var contract = await db.HopDongs.VisibleContracts(user, db).FirstOrDefaultAsync(h => h.MaHopDong == contractId, cancellation);
        if (contract == null) return null;
        if (kind == 0 && contract.TrangThai is not (0 or 1) || kind == 1 && contract.TrangThai is not (1 or 4))
            throw new RentalBookingException("Trạng thái hợp đồng không phù hợp để lập biên bản này.", 409);
        var paths = new List<string>();
        bool committed = false;
        try
        {
            foreach (var photo in photos) paths.Add(await ContractDocuments.SaveImageAsync(env, photo, "bienban", "bb", contractId, cancellation));
            string? confirmation = null;
            if (!string.IsNullOrWhiteSpace(signature))
            {
                var bytes = ContractDocuments.SignatureBytes(signature);
                confirmation = $"/uploads/signatures/bb_{contractId}_{Guid.NewGuid():N}.png";
                Directory.CreateDirectory(Path.Combine(env.WebRootPath, "uploads", "signatures"));
                await File.WriteAllBytesAsync(Path.Combine(env.WebRootPath, confirmation.TrimStart('/')), bytes, cancellation);
                paths.Add(confirmation);
            }
            var row = new BienBanBanGiao
            {
                MaHopDong = contractId, LoaiBienBan = kind, MaNhanVienLap = user.UserId(), NgayLap = DateTime.Now,
                PhuKienKemTheo = accessories?.Trim(), TinhTrangNgoaiQuan = condition.Trim(), GhiChu = note?.Trim(),
                HinhAnh1 = paths.ElementAtOrDefault(0), HinhAnh2 = photos.Count > 1 ? paths[1] : null,
                HinhAnh3 = photos.Count > 2 ? paths[2] : null, HinhAnh4 = photos.Count > 3 ? paths[3] : null,
                ChuKyXacNhan = confirmation
            };
            if (photos.Count == 0) row.HinhAnh1 = null;
            db.BienBanBanGiaos.Add(row);
            await db.SaveChangesAsync(cancellation);
            await transaction.CommitAsync(cancellation);
            committed = true;
            return row;
        }
        finally
        {
            if (!committed)
                foreach (var path in paths) File.Delete(Path.Combine(env.WebRootPath, path.TrimStart('/')));
        }
    }
}
