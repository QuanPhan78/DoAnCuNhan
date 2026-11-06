using System.Globalization;
using System.Security.Claims;
using RentalSystem.Models;

namespace RentalSystem.Common;

internal static class ApiAccess
{
    internal const string Managers = "Admin,KinhDoanh";

    internal static int UserId(this ClaimsPrincipal user) =>
        int.Parse(user.FindFirstValue(ClaimTypes.NameIdentifier)!, CultureInfo.InvariantCulture);

    internal static bool IsManager(this ClaimsPrincipal user) =>
        user.IsInRole("Admin") || user.IsInRole("KinhDoanh");

    internal static IQueryable<HopDong> VisibleContracts(this IQueryable<HopDong> contracts,
        ClaimsPrincipal user, ApplicationDbContext db)
    {
        if (user.IsManager()) return contracts;
        int id = user.UserId();
        if (user.IsInRole("KyThuat"))
            return contracts.Where(h => db.PhieuBaoTris.Any(p => p.MaHopDong == h.MaHopDong && p.MaKyThuatVien == id));
        return contracts.Where(h => h.MaKhachHang == id);
    }

    internal static IQueryable<PhieuBaoTri> VisibleTickets(this IQueryable<PhieuBaoTri> tickets, ClaimsPrincipal user)
    {
        if (user.IsManager()) return tickets;
        int id = user.UserId();
        return user.IsInRole("KyThuat")
            ? tickets.Where(p => p.MaKyThuatVien == id)
            : tickets.Where(p => p.HopDong != null && p.HopDong.MaKhachHang == id);
    }
}
