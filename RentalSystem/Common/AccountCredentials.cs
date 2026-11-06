using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Storage;
using RentalSystem.Models;
using System.Security.Cryptography;
using System.Text;

namespace RentalSystem.Common;

internal static class AccountCredentials
{
    internal const string InvalidIdentity = "Số CCCD phải có đúng 12 chữ số.";
    internal const string DuplicateIdentity = "Số CCCD đã được sử dụng.";

    internal static bool IsValidIdentity(string value) =>
        value.Length == 12 && value.All(ch => ch is >= '0' and <= '9');

    internal static Task<bool> IdentityExistsAsync(ApplicationDbContext db, string cccd, int? exceptId = null) =>
        db.NguoiDungs.AnyAsync(user =>
            (!exceptId.HasValue || user.MaNguoiDung != exceptId.Value) &&
            user.CCCD.Trim() == cccd);

    internal static async Task<IDbContextTransaction> LockIdentityAsync(ApplicationDbContext db, string cccd)
    {
        var transaction = await db.Database.BeginTransactionAsync();
        try
        {
            string resource = "RentalSystem.Account.CCCD." + Convert.ToHexString(SHA256.HashData(Encoding.ASCII.GetBytes(cccd)));
            await db.Database.ExecuteSqlInterpolatedAsync($"""
                DECLARE @result int;
                EXEC @result = sys.sp_getapplock @Resource = {resource}, @LockMode = 'Exclusive',
                    @LockOwner = 'Transaction', @LockTimeout = 10000;
                IF @result < 0 THROW 51012, N'Không thể kiểm tra CCCD. Vui lòng thử lại.', 1;
                """);
            return transaction;
        }
        catch
        {
            await transaction.DisposeAsync();
            throw;
        }
    }

    internal static string? PasswordError(string stored, string? current, string? next, string? confirmation)
    {
        if (string.IsNullOrEmpty(current)) return "Nhập mật khẩu hiện tại.";
        if (!string.Equals(stored, current, StringComparison.Ordinal)) return "Mật khẩu hiện tại không đúng.";
        if (string.IsNullOrWhiteSpace(next) || next.Length < 6) return "Mật khẩu mới cần ít nhất 6 ký tự.";
        if (!string.Equals(next, confirmation, StringComparison.Ordinal)) return "Mật khẩu nhập lại không khớp.";
        return null;
    }
}
