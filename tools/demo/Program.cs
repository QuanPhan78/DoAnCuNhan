using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Data.SqlClient;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Areas.Admin.Controllers;
using RentalSystem.Database;
using RentalSystem.Models;

var command = args.ElementAtOrDefault(0) ?? "check";
var database = args.ElementAtOrDefault(1) ?? DatabaseSchema.TargetDatabase;
if (command is not ("prepare" or "reset" or "check" or "snapshot") ||
    database != DatabaseSchema.TargetDatabase)
    throw new ArgumentException("Usage: DemoHarness [prepare|reset|check|snapshot] RentalSystemDB_V2");
var root = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "../../../../../"));
if (!File.Exists(Path.Combine(root, "RentalSystem", "RentalSystem.csproj")))
    throw new InvalidOperationException("Cannot resolve workspace root.");
var output = Path.Combine(root, "outputs", "demo-check");
var webroot = Path.Combine(output, "wwwroot");
const string legacyIdentity = "/uploads/demo/identity-demo.svg";
const string frontIdentity = "/uploads/demo/identity-demo-front.png";
const string backIdentity = "/uploads/demo/identity-demo-back.png";
var connection = new SqlConnectionStringBuilder
{
    DataSource = "localhost", InitialCatalog = database,
    IntegratedSecurity = true, TrustServerCertificate = true, ConnectTimeout = 8
};
using var db = new ApplicationDbContext(new DbContextOptionsBuilder<ApplicationDbContext>()
    .UseSqlServer(connection.ConnectionString).Options);
await DatabaseSchema.VerifyAsync(db.Database.GetDbConnection());
DatabaseSchema.RequireRehearsal(db.Database.GetDbConnection());
var json = new JsonSerializerOptions
{
    WriteIndented = true, ReferenceHandler = ReferenceHandler.IgnoreCycles,
    Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
};
Directory.CreateDirectory(output);

if (command == "snapshot")
{
    Console.WriteLine(await Snapshot("manual"));
    return;
}
if (command is "prepare" or "reset")
{
    using (var client = new System.Net.Sockets.TcpClient())
    {
        try
        {
            await client.ConnectAsync("localhost", 5001);
            throw new InvalidOperationException("Stop the demo backend before preparing or resetting its database.");
        }
        catch (System.Net.Sockets.SocketException) { }
    }
    if (command == "prepare" && await db.HopDongs.AnyAsync())
    {
        CopyIdentityAssets();
        var oldDemoContracts = await db.HopDongs.Where(h => h.AnhCCCD_Truoc == legacyIdentity).ToListAsync();
        foreach (var contract in oldDemoContracts.Where(h => string.IsNullOrWhiteSpace(h.AnhCCCD_Sau)))
        {
            contract.AnhCCCD_Truoc = frontIdentity;
            contract.AnhCCCD_Sau = backIdentity;
        }
        await db.SaveChangesAsync();
        await Check();
        Console.WriteLine("Existing demo prepared. Use reset (after stopping its server) for a fresh rehearsal.");
        return;
    }

    if (await db.HopDongs.AnyAsync()) Console.WriteLine("Before reset: " + await Snapshot("pre-reset"));
    PrepareAssets();
    using var tx = await db.Database.BeginTransactionAsync();
    if (command == "reset" && await db.VaiTros.AnyAsync()) DbInitializer.ClearData(db);
    await Seed();
    await db.Database.ExecuteSqlRawAsync(DatabaseSchema.ReadSql("002_MaintenanceAssignments.sql"));
    await tx.CommitAsync();
    db.ChangeTracker.Clear();
    await Check();
    await Export(Path.Combine(output, "baseline.json"));
    var manifest = new
    {
        database, preparedAt = DateTimeOffset.Now, webroot,
        customerId = 4, productId = 1, activeContractId = 1, activeDeviceId = 1,
        fallbackContractId = 2, pendingContractId = 3, fallbackTicketId = 1,
        handoverId = 1, technicianId = 3, receiptId = 1,
        rentalDays = 7, expectedRent = 1190000, requiredDeposit = 8000000,
        reportFrom = DateTime.Today.AddDays(-60).ToString("yyyy-MM-dd"),
        reportTo = DateTime.Today.ToString("yyyy-MM-dd"),
        accounts = new[]
        {
            new { role = "Admin", email = "admin@demo.invalid", password = "Demo@123" },
            new { role = "KinhDoanh", email = "sale@demo.invalid", password = "Demo@123" },
            new { role = "KyThuat", email = "tech@demo.invalid", password = "Demo@123" },
            new { role = "KhachHang", email = "customer@demo.invalid", password = "Demo@123" }
        }
    };
    await File.WriteAllTextAsync(Path.Combine(output, "manifest.json"), JsonSerializer.Serialize(manifest, json));
    Console.WriteLine("Baseline ready: " + output);
}
else await Check();

async Task Seed()
{
    var today = DateTime.Today;
    var roles = new[] { "Admin", "KinhDoanh", "KyThuat", "KhachHang" }.Select(r => new VaiTro { TenVaiTro = r }).ToArray();
    db.VaiTros.AddRange(roles);
    await db.SaveChangesAsync();
    var users = new[]
    {
        ("Quản trị Demo", "admin", 0), ("Kinh doanh Demo", "sale", 1),
        ("Kỹ thuật Demo", "tech", 2), ("Khách hàng Demo An", "customer", 3),
        ("Khách hàng Demo Bình", "other", 3)
    }.Select((u, i) => new NguoiDung
    {
        HoTen = u.Item1, Email = u.Item2 + "@demo.invalid", MatKhau = "Demo@123",
        MaVaiTro = roles[u.Item3].MaVaiTro, SoDienThoai = "090000000" + i,
        CCCD = "DEMO-KHONG-HOP-LE", DiaChi = "Phòng demo, 123 Đường Minh Họa, TP.HCM", TrangThai = true
    }).ToArray();
    db.NguoiDungs.AddRange(users);
    var laptop = new LoaiThietBi { TenLoai = "Laptop" };
    var printer = new LoaiThietBi { TenLoai = "Máy in" };
    db.LoaiThietBis.AddRange(laptop, printer);
    await db.SaveChangesAsync();
    var products = new[]
    {
        new SanPham { MaLoai = laptop.MaLoai, TenSanPham = "Laptop Demo Dell Latitude 5430", CauHinh = "Core i7 / RAM 16 GB / SSD 512 GB", MoTa = "Dữ liệu giả lập phục vụ bảo vệ khóa luận", GiaThueNgay = 170000, TienCoc = 8000000, HinhAnh = "/images/sanpham/laptop.png" },
        new SanPham { MaLoai = printer.MaLoai, TenSanPham = "Máy in Demo HP LaserJet", CauHinh = "Laser đen trắng / LAN / A4", MoTa = "Dữ liệu giả lập phục vụ báo cáo", GiaThueNgay = 100000, TienCoc = 3000000, HinhAnh = "/images/sanpham/may-in.png" }
    };
    db.SanPhams.AddRange(products);
    await db.SaveChangesAsync();
    var devices = Enumerable.Range(1, 24).Select(i => new ThietBi
    {
        MaSanPham = products[i <= 5 || i >= 9 ? 0 : 1].MaSanPham,
        SoSerial = $"DEMO-{(i <= 5 || i >= 9 ? "LAP" : "PRN")}-{i:D3}",
        TinhTrangMay = "Thiết bị minh họa, ngoại quan tốt, đủ phụ kiện",
        TrangThai = i is 1 or 2 or 4 or 5 ? 1 : i == 3 ? 3 : 0
    }).ToArray();
    devices[22].TrangThai = 2; // warehouse maintenance
    devices[23].TrangThai = 4; // retired device
    db.ThietBis.AddRange(devices);
    await db.SaveChangesAsync();

    var starts = new[] { -5, -5, 1, -45, -3, -20, -10 };
    var durations = new[] { 30, 30, 7, 60, 30, 14, 7 };
    var statuses = new[] { 1, 1, 0, 1, 1, 2, 3 };
    var periods = new[] { 3, 1, 1, 3, 3, 1, 1 };
    var paidPeriods = new[] { 1, 1, 0, 1, 1, 1, 0 };
    for (var i = 0; i < 7; i++)
    {
        var product = products[i <= 4 ? 0 : 1];
        var activeOrClosed = statuses[i] is 1 or 2;
        var contract = new HopDong
        {
            MaKhachHang = users[i == 4 || i == 5 || i == 6 ? 4 : 3].MaNguoiDung,
            MaNhanVien = users[1].MaNguoiDung,
            NgayBatDau = today.AddDays(starts[i]), NgayKetThuc = today.AddDays(starts[i] + durations[i]),
            TongTien = product.GiaThueNgay * durations[i], TienDaCoc = activeOrClosed ? product.TienCoc : 0,
            TienCocBaoDamMay = product.TienCoc, TrangThai = statuses[i], SoKyHan = periods[i],
            TrangThaiThanhToan = paidPeriods[i] == periods[i] ? 3 : activeOrClosed ? 2 : 0,
            AnhCCCD_Truoc = activeOrClosed ? frontIdentity : null,
            AnhCCCD_Sau = activeOrClosed ? backIdentity : null,
            ChuKyKhachHang = activeOrClosed ? "/uploads/demo/customer-signature.svg" : "",
            ChuKyNhanVien = activeOrClosed ? "/uploads/demo/staff-signature.svg" : "",
            NgayKy = activeOrClosed ? today.AddDays(starts[i]) : null,
            HanChotKy = statuses[i] == 0 ? DateTime.Now.AddHours(24) : null,
            GhiChu = i switch
            {
                0 => "DEMO CHÍNH: hợp đồng đang thuê để báo lỗi Wi-Fi; hồ sơ và chữ ký giả lập.",
                1 => "DEMO DỰ PHÒNG: phiếu sửa xong chưa đánh giá.",
                2 => "DEMO DỰ PHÒNG: yêu cầu chờ duyệt, chưa thu cọc.",
                3 => "DEMO CÔNG NỢ: một kỳ quá hạn và một kỳ chưa đến hạn.",
                _ => "DỮ LIỆU GIẢ LẬP phục vụ báo cáo và diễn tập."
            },
            TrangThaiHoanCoc = statuses[i] == 2 ? 1 : 0,
            TienCocThucHoan = statuses[i] == 2 ? product.TienCoc : null,
            NgayHoanCoc = statuses[i] == 2 ? today.AddDays(-6) : null
        };
        db.HopDongs.Add(contract);
        await db.SaveChangesAsync();
        db.ChiTietHopDongs.Add(new ChiTietHopDong
        {
            MaHopDong = contract.MaHopDong, MaThietBi = devices[i].MaThietBi, GiaChotThu = contract.TongTien
        });
        for (var p = 0; p < periods[i]; p++)
        {
            var due = contract.NgayBatDau.AddDays(p * durations[i] / periods[i]);
            var paid = p < paidPeriods[i];
            var period = new KyHanThanhToan
            {
                MaHopDong = contract.MaHopDong, SoKyHan = p + 1, NgayDenHan = due,
                SoTienPhai = contract.TongTien / periods[i],
                SoTienDaTra = paid ? contract.TongTien / periods[i] : 0,
                TrangThai = statuses[i] == 3 ? 3 : paid ? 1 : due < today ? 2 : 0,
                NgayThanhToan = paid ? due : null, GhiChu = "Kỳ thanh toán giả lập cho demo",
                NhomTuoiNo = !paid && due < today ? 1 : 0,
                SoNgayTreHan = !paid && due < today ? (today - due).Days : 0
            };
            db.KyHanThanhToans.Add(period);
            await db.SaveChangesAsync();
            if (paid) db.PhieuThus.Add(new PhieuThu
            {
                MaHopDong = contract.MaHopDong, MaKyHan = period.MaKyHan, LoaiPhieu = 0,
                SoTien = period.SoTienDaTra, NgayGiaoDich = due, HinhThucThanhToan = 0,
                MaNhanVienThu = users[1].MaNguoiDung, GhiChu = "DEMO: thu tiền thuê giả lập"
            });
        }
        if (activeOrClosed)
        {
            db.PhieuThus.Add(new PhieuThu
            {
                MaHopDong = contract.MaHopDong, LoaiPhieu = 1, SoTien = product.TienCoc,
                NgayGiaoDich = contract.NgayBatDau, HinhThucThanhToan = 0,
                MaNhanVienThu = users[1].MaNguoiDung, GhiChu = "DEMO: thu cọc giả lập"
            });
            db.BienBanBanGiaos.Add(new BienBanBanGiao
            {
                MaHopDong = contract.MaHopDong, LoaiBienBan = 0, NgayLap = contract.NgayBatDau,
                MaNhanVienLap = users[2].MaNguoiDung, PhuKienKemTheo = "Sạc, túi đựng, chuột",
                TinhTrangNgoaiQuan = "Hoạt động bình thường trước bàn giao",
                ChuKyXacNhan = "/uploads/demo/customer-signature.svg", GhiChu = "BIÊN BẢN GIẢ LẬP CHO DEMO"
            });
        }
        if (statuses[i] == 2) db.PhieuChis.Add(new PhieuChi
        {
            MaHopDong = contract.MaHopDong, LoaiChi = 0, SoTien = product.TienCoc,
            NgayChi = today.AddDays(-6), HinhThucChi = 0, MaNhanVienChi = users[0].MaNguoiDung,
            GhiChu = "DEMO: hoàn cọc khi kết thúc hợp đồng giả lập"
        });
        await db.SaveChangesAsync();
    }
    db.PhieuBaoTris.Add(new PhieuBaoTri
    {
        MaHopDong = 2, MaThietBi = 2, MaKyThuatVien = 3, TrangThai = 3,
        MoTaLoi = "[Mất kết nối] DEMO DỰ PHÒNG: máy không kết nối Wi-Fi",
        NgayBaoLoi = today.AddDays(-1).AddHours(9), NgayBatDauBaoTri = today.AddDays(-1).AddHours(10),
        NgayHoanThanh = today.AddDays(-1).AddHours(11), NgayKetThucBaoTri = today.AddDays(-1).AddHours(11),
        GhiChuSuaChua = "Đã cấu hình lại kết nối, kiểm tra hoạt động ổn định",
        LoaiTrachNhiem = 2, NguyenNhan = "Cấu hình mạng", LinhKienThayThe = "Không thay linh kiện",
        DanhGiaSao = null, HanHoanThanh = today.AddDays(1), ChiPhiSuaChua = 0
    });
    await db.SaveChangesAsync();
}

async Task Check()
{
    var contracts = await db.HopDongs.CountAsync();
    var devices = await db.ThietBis.CountAsync();
    var periods = await db.KyHanThanhToans.CountAsync();
    if (contracts < 7 || devices < 20 || periods < 10)
        throw new InvalidOperationException("Unsafe startup: initializer would replace this fixture.");
    var main = await db.HopDongs.SingleAsync(h => h.MaHopDong == 1);
    if (main.MaKhachHang != 4 || main.TrangThai != 1 || string.IsNullOrEmpty(main.ChuKyKhachHang) || string.IsNullOrEmpty(main.ChuKyNhanVien))
        throw new InvalidOperationException("Main demonstration contract is not ready.");
    var assets = new List<string> { main.AnhCCCD_Truoc, main.ChuKyKhachHang, main.ChuKyNhanVien };
    if (main.AnhCCCD_Truoc == frontIdentity || !string.IsNullOrWhiteSpace(main.AnhCCCD_Sau))
        assets.Add(main.AnhCCCD_Sau);
    foreach (var path in assets)
        if (string.IsNullOrWhiteSpace(path) || !File.Exists(Path.Combine(webroot, path.TrimStart('/'))))
            throw new FileNotFoundException($"Missing demo contract asset: {path}");
    if (!await db.ThietBis.AnyAsync(t => t.MaSanPham == 1 && t.TrangThai == 0))
        throw new InvalidOperationException("No laptop available for live rental.");
    var fallback = await db.PhieuBaoTris.SingleAsync(p => p.MaPhieu == 1);
    var report = new
    {
        database, checkedAt = DateTimeOffset.Now, contracts, devices, periods,
        mainContractReady = true, fallbackRatingAvailable = fallback.TrangThai == 3 && fallback.DanhGiaSao == null,
        paidPeriods = await db.KyHanThanhToans.CountAsync(k => k.TrangThai == 1),
        overduePeriods = await db.KyHanThanhToans.CountAsync(k => k.TrangThai == 2),
        futurePeriods = await db.KyHanThanhToans.CountAsync(k => k.TrangThai == 0 && k.NgayDenHan > DateTime.Today),
        receiptCount = await db.PhieuThus.CountAsync(),
        note = "Database checks only. Phone, timed rehearsals and video must be checked separately."
    };
    await File.WriteAllTextAsync(Path.Combine(output, "data-check.json"), JsonSerializer.Serialize(report, json));
    Console.WriteLine(JsonSerializer.Serialize(report, json));
}

async Task<string> Snapshot(string label)
{
    var folder = Path.Combine(output, "snapshots", $"{DateTime.Now:yyyyMMdd-HHmmss-fff}-{label}");
    Directory.CreateDirectory(folder);
    await Export(Path.Combine(folder, "database.json"));
    if (Directory.Exists(Path.Combine(webroot, "uploads")))
        CopyTree(Path.Combine(webroot, "uploads"), Path.Combine(folder, "uploads"));
    if (File.Exists(Path.Combine(output, "manifest.json")))
        File.Copy(Path.Combine(output, "manifest.json"), Path.Combine(folder, "manifest.json"));
    return folder;
}

async Task Export(string path)
{
    // Same payload as /Admin/Database/Backup, no loaded navigation graphs.
    var payload = new DatabaseBackupPayload
    {
        DatabaseName = database, ServerName = "localhost",
        VaiTros = await db.VaiTros.AsNoTracking().ToListAsync(),
        NguoiDungs = await db.NguoiDungs.AsNoTracking().ToListAsync(),
        LoaiThietBis = await db.LoaiThietBis.AsNoTracking().ToListAsync(),
        SanPhams = await db.SanPhams.AsNoTracking().ToListAsync(),
        ThietBis = await db.ThietBis.AsNoTracking().ToListAsync(),
        LichSuThietBis = await db.LichSuThietBis.AsNoTracking().ToListAsync(),
        KhuyenMais = await db.KhuyenMais.AsNoTracking().ToListAsync(),
        HopDongs = await db.HopDongs.AsNoTracking().ToListAsync(),
        KyHanThanhToans = await db.KyHanThanhToans.AsNoTracking().ToListAsync(),
        ChiTietHopDongs = await db.ChiTietHopDongs.AsNoTracking().ToListAsync(),
        PhieuThus = await db.PhieuThus.AsNoTracking().ToListAsync(),
        PhieuChis = await db.PhieuChis.AsNoTracking().ToListAsync(),
        PhieuBaoTris = await db.PhieuBaoTris.AsNoTracking().ToListAsync(),
        BienBanBanGiaos = await db.BienBanBanGiaos.AsNoTracking().ToListAsync(),
        ThongBaos = await db.ThongBaos.AsNoTracking().ToListAsync(),
        LichSuNhacNos = await db.LichSuNhacNos.AsNoTracking().ToListAsync(),
        YeuCauGiaHans = await db.YeuCauGiaHans.AsNoTracking().ToListAsync(),
        PhanCongCongViecs = await db.PhanCongCongViecs.AsNoTracking().ToListAsync()
    };
    await File.WriteAllTextAsync(path, JsonSerializer.Serialize(payload, json));
}

void PrepareAssets()
{
    CopyIdentityAssets();
    var original = Path.Combine(root, "RentalSystem", "wwwroot");
    Directory.CreateDirectory(webroot);
    foreach (var dir in Directory.GetDirectories(original).Where(d => Path.GetFileName(d) != "uploads"))
        CopyTree(dir, Path.Combine(webroot, Path.GetFileName(dir)));
    foreach (var file in Directory.GetFiles(original)) File.Copy(file, Path.Combine(webroot, Path.GetFileName(file)), true);
    var mock = Path.Combine(webroot, "uploads", "demo");
    Directory.CreateDirectory(mock);
    foreach (var (filename, label) in new[] { ("customer-signature.svg", "KHACH HANG DEMO"), ("staff-signature.svg", "NHAN VIEN DEMO"), ("identity-demo.svg", "HO SO GIA LAP - KHONG CO GIA TRI") })
        File.WriteAllText(Path.Combine(mock, filename), $"<svg xmlns='http://www.w3.org/2000/svg' width='680' height='180' viewBox='0 0 680 180'><rect width='680' height='180' fill='#f1f5f9'/><text x='24' y='54' font-family='Arial' font-size='23' fill='#123'>{label}</text><path d='M30 115 Q80 65 110 110 T200 105 T300 100' stroke='#123' stroke-width='3' fill='none'/><text x='24' y='158' font-family='Arial' font-size='16' fill='#555'>DEMO ONLY - synthetic sample</text></svg>");
}

void CopyIdentityAssets()
{
    var target = Path.Combine(webroot, "uploads", "demo");
    Directory.CreateDirectory(target);
    foreach (var asset in new[] { frontIdentity, backIdentity })
    {
        var filename = Path.GetFileName(asset);
        File.Copy(Path.Combine(root, "tools", "demo", "assets", filename), Path.Combine(target, filename), true);
    }
}

static void CopyTree(string source, string target)
{
    Directory.CreateDirectory(target);
    foreach (var file in Directory.GetFiles(source)) File.Copy(file, Path.Combine(target, Path.GetFileName(file)), true);
    foreach (var dir in Directory.GetDirectories(source)) CopyTree(dir, Path.Combine(target, Path.GetFileName(dir)));
}
