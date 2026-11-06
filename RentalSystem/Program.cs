using System.Threading.RateLimiting;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authentication;
using RentalSystem.Common;
using RentalSystem.Database;
using RentalSystem.Models;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllersWithViews();
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy => policy.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader());
});
if (builder.Configuration.GetValue("Database:EnableBackgroundJobs", true))
{
    builder.Services.AddHostedService<RentalSystem.Services.ReservationCleanupService>();
}
builder.Services.AddHttpContextAccessor();
builder.Services.AddScoped<RentalSystem.Services.IVnPayService, RentalSystem.Services.VnPayService>();
builder.Services.AddSession(options => { options.IdleTimeout = System.TimeSpan.FromMinutes(60); options.Cookie.HttpOnly = true; options.Cookie.IsEssential = true; });

// Cấu hình giới hạn tần suất đăng nhập (Rate Limiting)
builder.Services.AddRateLimiter(options =>
{
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    options.AddFixedWindowLimiter("LoginLimiter", opt =>
    {
        opt.Window = TimeSpan.FromMinutes(1);
        opt.PermitLimit = 5;
        opt.QueueLimit = 0;
    });
    options.AddPolicy("ApiLoginLimiter", context => RateLimitPartition.GetFixedWindowLimiter(
        context.Connection.RemoteIpAddress?.ToString() ?? "unknown",
        _ => new FixedWindowRateLimiterOptions { Window = TimeSpan.FromMinutes(1), PermitLimit = 20 }));
});

// Thêm cấu hình Xác thực (Cookie Authentication)
builder.Services.AddDataProtection();
builder.Services.AddSingleton<ApiTokens>();
builder.Services.AddAuthentication(Microsoft.AspNetCore.Authentication.Cookies.CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.LoginPath = "/Account/Login";
        options.AccessDeniedPath = "/Account/AccessDenied";
    })
    .AddScheme<AuthenticationSchemeOptions, ApiTokenAuthentication>(ApiTokens.Scheme, _ => { });

builder.Services.AddDbContext<ApplicationDbContext>(options => 
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles(); 
app.UseRouting();

app.UseCors("AllowAll");

// Middleware Rate Limiting (sau UseRouting và trước UseAuthorization)
app.UseRateLimiter();
app.UseSession();
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

app.MapControllerRoute(
    name: "areas",
    pattern: "{area:exists}/{controller=Home}/{action=Index}/{id?}");

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
    await DatabaseSchema.VerifyAsync(context.Database.GetDbConnection());
}

app.Run();




