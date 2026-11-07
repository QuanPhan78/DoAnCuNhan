using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Common;

public sealed class ContractFileAccess(RequestDelegate next)
{
    public async Task InvokeAsync(HttpContext context, ApplicationDbContext db)
    {
        string path = context.Request.Path.Value ?? "";
        bool identity = path.StartsWith("/uploads/cmnd/", StringComparison.OrdinalIgnoreCase);
        bool signature = path.StartsWith("/uploads/signatures/", StringComparison.OrdinalIgnoreCase);
        bool receipt = path.StartsWith("/uploads/bienlai/", StringComparison.OrdinalIgnoreCase);
        bool handover = path.StartsWith("/uploads/bienban/", StringComparison.OrdinalIgnoreCase);
        if (!identity && !signature && !receipt && !handover) { await next(context); return; }
        var auth = await context.AuthenticateAsync(ApiTokens.Scheme);
        if (!auth.Succeeded) auth = await context.AuthenticateAsync(CookieAuthenticationDefaults.AuthenticationScheme);
        if (!auth.Succeeded || auth.Principal == null) { context.Response.StatusCode = 401; return; }
        var user = auth.Principal;
        context.User = user;
        if (user.IsInRole("KyThuat") && (identity || receipt)) { context.Response.StatusCode = 403; return; }
        var contracts = db.HopDongs.VisibleContracts(user, db);
        bool allowed = handover
            ? await db.BienBanBanGiaos.AnyAsync(b => contracts.Any(h => h.MaHopDong == b.MaHopDong) &&
                (b.HinhAnh1 == path || b.HinhAnh2 == path || b.HinhAnh3 == path || b.HinhAnh4 == path))
            : receipt
            ? await db.KyHanThanhToans.AnyAsync(k => k.HinhAnhBienLai == path && contracts.Any(h => h.MaHopDong == k.MaHopDong))
            : await contracts.AnyAsync(h => identity
                ? h.AnhCCCD_Truoc == path || h.AnhCCCD_Sau == path
                : h.ChuKyKhachHang == path || h.ChuKyNhanVien == path) || signature &&
                await db.BienBanBanGiaos.AnyAsync(b => b.ChuKyXacNhan == path && contracts.Any(h => h.MaHopDong == b.MaHopDong));
        if (!allowed) { context.Response.StatusCode = 404; return; }
        context.Response.Headers.CacheControl = "private, no-store";
        await next(context);
    }
}
