using System.Globalization;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using System.Text.Encodings.Web;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.Data.SqlClient;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;
using RentalSystem.Models;

namespace RentalSystem.Common;

public sealed class ApiTokens
{
    internal const string Scheme = "RentalApi";
    private const string Prefix = "rs1.";
    private readonly ITimeLimitedDataProtector _protector;

    public ApiTokens(IDataProtectionProvider provider, IConfiguration configuration)
    {
        var connection = new SqlConnectionStringBuilder(configuration.GetConnectionString("DefaultConnection"));
        _protector = provider.CreateProtector("RentalSystem.ApiAccess.v1", connection.DataSource, connection.InitialCatalog)
            .ToTimeLimitedDataProtector();
    }

    internal object Issue(NguoiDung user)
    {
        var expiry = DateTimeOffset.UtcNow.AddHours(8);
        string payload = FormattableString.Invariant($"{user.MaNguoiDung}:{PasswordStamp(user.MatKhau)}");
        string accessToken = Prefix + _protector.Protect(payload, expiry);
        return new { accessToken, access_token = accessToken, expiresIn = expiry, expires_in = expiry };
    }

    internal (int Id, string Stamp)? Read(string token)
    {
        if (!token.StartsWith(Prefix, StringComparison.Ordinal) || token.Length > 4096)
            return null;

        try
        {
            var fields = _protector.Unprotect(token[Prefix.Length..]).Split(':', 2);
            return fields.Length == 2 &&
                int.TryParse(fields[0], NumberStyles.None, CultureInfo.InvariantCulture, out int id) && id > 0
                ? (id, fields[1])
                : null;
        }
        catch (CryptographicException)
        {
            return null;
        }
        catch (FormatException)
        {
            return null;
        }
    }

    internal static string PasswordStamp(string password) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(password)));
}

internal sealed class ApiTokenAuthentication(
    IOptionsMonitor<AuthenticationSchemeOptions> options,
    ILoggerFactory logger,
    UrlEncoder encoder,
    ApiTokens tokens,
    ApplicationDbContext db) : AuthenticationHandler<AuthenticationSchemeOptions>(options, logger, encoder)
{
    protected override async Task<AuthenticateResult> HandleAuthenticateAsync()
    {
        string authorization = Request.Headers.Authorization.ToString();
        if (!authorization.StartsWith("Bearer ", StringComparison.OrdinalIgnoreCase))
            return AuthenticateResult.NoResult();

        var payload = tokens.Read(authorization["Bearer ".Length..].Trim());
        if (payload == null) return AuthenticateResult.Fail("Invalid or expired API token.");

        var (id, stamp) = payload.Value;
        var user = await db.NguoiDungs.AsNoTracking().Include(u => u.VaiTro)
            .SingleOrDefaultAsync(u => u.MaNguoiDung == id && u.TrangThai, Context.RequestAborted);
        if (user?.VaiTro == null || !CryptographicOperations.FixedTimeEquals(
            Encoding.ASCII.GetBytes(stamp), Encoding.ASCII.GetBytes(ApiTokens.PasswordStamp(user.MatKhau))))
            return AuthenticateResult.Fail("Invalid API session.");

        var identity = new ClaimsIdentity(
            [
                new Claim(ClaimTypes.NameIdentifier, id.ToString(CultureInfo.InvariantCulture)),
                new Claim(ClaimTypes.Role, user.VaiTro.TenVaiTro)
            ], Scheme.Name);
        return AuthenticateResult.Success(new AuthenticationTicket(new ClaimsPrincipal(identity), Scheme.Name));
    }

    protected override Task HandleChallengeAsync(AuthenticationProperties properties)
    {
        Response.StatusCode = StatusCodes.Status401Unauthorized;
        Response.Headers.WWWAuthenticate = "Bearer";
        return Response.WriteAsJsonAsync(new { message = "Phiên đăng nhập đã hết hoặc không hợp lệ." });
    }

    protected override Task HandleForbiddenAsync(AuthenticationProperties properties)
    {
        Response.StatusCode = StatusCodes.Status403Forbidden;
        return Response.WriteAsJsonAsync(new { message = "Bạn không có quyền thực hiện thao tác này." });
    }
}
