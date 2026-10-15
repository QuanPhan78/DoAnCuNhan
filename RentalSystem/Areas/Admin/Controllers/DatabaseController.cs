using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using RentalSystem.Models;

namespace RentalSystem.Areas.Admin.Controllers
{
    [Area("Admin")]
    [Authorize(Roles = "Admin")]
    public class DatabaseController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly IConfiguration _config;
        private readonly IWebHostEnvironment _env;

        public DatabaseController(
            ApplicationDbContext context,
            IConfiguration config,
            IWebHostEnvironment env)
        {
            _context = context;
            _config = config;
            _env = env;
        }

        // Thống kê dữ liệu các bảng trong CSDL
        [HttpGet]
        public async Task<IActionResult> Index()
        {
            var model = new DatabaseDashboardViewModel();

            try
            {
                var conn = _context.Database.GetDbConnection();
                model.ServerName = !string.IsNullOrEmpty(conn.DataSource) ? conn.DataSource : "localhost";
                model.DatabaseName = !string.IsNullOrEmpty(conn.Database) ? conn.Database : "RentalSystemDB";
                model.ProviderName = _context.Database.ProviderName ?? "Microsoft SQL Server";
                model.IsConnected = await _context.Database.CanConnectAsync();

                model.Tables = new List<TableStatItem>
                {
                    new() { TableName = "VaiTros", DisplayName = "Vai trò người dùng", RowCount = await _context.VaiTros.CountAsync(), Icon = "fa-user-tag" },
                    new() { TableName = "NguoiDungs", DisplayName = "Tài khoản người dùng", RowCount = await _context.NguoiDungs.CountAsync(), Icon = "fa-users" },
                    new() { TableName = "LoaiThietBis", DisplayName = "Loại thiết bị", RowCount = await _context.LoaiThietBis.CountAsync(), Icon = "fa-th-large" },
                    new() { TableName = "SanPhams", DisplayName = "Dòng sản phẩm", RowCount = await _context.SanPhams.CountAsync(), Icon = "fa-boxes" },
                    new() { TableName = "ThietBis", DisplayName = "Serial & Máy vật lý", RowCount = await _context.ThietBis.CountAsync(), Icon = "fa-barcode" },
                    new() { TableName = "LichSuThietBis", DisplayName = "Lịch sử vòng đời thiết bị", RowCount = await _context.LichSuThietBis.CountAsync(), Icon = "fa-history" },
                    new() { TableName = "KhuyenMais", DisplayName = "Mã khuyến mãi", RowCount = await _context.KhuyenMais.CountAsync(), Icon = "fa-tags" },
                    new() { TableName = "HopDongs", DisplayName = "Hợp đồng thuê máy", RowCount = await _context.HopDongs.CountAsync(), Icon = "fa-file-contract" },
                    new() { TableName = "KyHanThanhToans", DisplayName = "Kỳ hạn thanh toán", RowCount = await _context.KyHanThanhToans.CountAsync(), Icon = "fa-calendar-alt" },
                    new() { TableName = "ChiTietHopDongs", DisplayName = "Chi tiết thiết bị thuê", RowCount = await _context.ChiTietHopDongs.CountAsync(), Icon = "fa-list-ol" },
                    new() { TableName = "PhieuThus", DisplayName = "Phiếu thu tiền", RowCount = await _context.PhieuThus.CountAsync(), Icon = "fa-receipt" },
                    new() { TableName = "PhieuChis", DisplayName = "Phiếu chi hoàn cọc", RowCount = await _context.PhieuChis.CountAsync(), Icon = "fa-money-bill-wave" },
                    new() { TableName = "PhieuBaoTris", DisplayName = "Phiếu bảo trì & Sự cố", RowCount = await _context.PhieuBaoTris.CountAsync(), Icon = "fa-tools" },
                    new() { TableName = "BienBanBanGiaos", DisplayName = "Biên bản bàn giao thiết bị", RowCount = await _context.BienBanBanGiaos.CountAsync(), Icon = "fa-clipboard-check" },
                    new() { TableName = "ThongBaos", DisplayName = "Thông báo hệ thống", RowCount = await _context.ThongBaos.CountAsync(), Icon = "fa-bell" },
                    new() { TableName = "LichSuNhacNos", DisplayName = "Lịch sử nhắc nợ", RowCount = await _context.LichSuNhacNos.CountAsync(), Icon = "fa-clock" },
                    new() { TableName = "YeuCauGiaHans", DisplayName = "Yêu cầu gia hạn hợp đồng", RowCount = await _context.YeuCauGiaHans.CountAsync(), Icon = "fa-calendar-plus" },
                    new() { TableName = "PhanCongCongViecs", DisplayName = "Phân công công việc", RowCount = await _context.PhanCongCongViecs.CountAsync(), Icon = "fa-tasks" }
                };

                model.TotalRows = model.Tables.Sum(t => t.RowCount);
            }
            catch (Exception ex)
            {
                ViewBag.ErrorMessage = $"Lỗi khi tải thông tin CSDL: {ex.Message}";
                model.IsConnected = false;
            }

            return View(model);
        }

        // Sao lưu dữ liệu
        [HttpGet]
        [HttpPost]
        public async Task<IActionResult> Backup(string? format = "json")
        {
            try
            {
                // Thử xuất native T-SQL .bak nếu được chỉ định tường minh
                if (string.Equals(format, "bak", StringComparison.OrdinalIgnoreCase))
                {
                    try
                    {
                        var conn = _context.Database.GetDbConnection();
                        var dbName = !string.IsNullOrEmpty(conn.Database) ? conn.Database : "RentalSystemDB";
                        var bakFileName = $"{dbName}_Backup_{DateTime.Now:yyyyMMdd_HHmmss}.bak";

                        if (conn.State != System.Data.ConnectionState.Open)
                            await conn.OpenAsync();

                        string? backupDir = null;
                        using (var cmd = conn.CreateCommand())
                        {

                            cmd.CommandText = "SELECT CAST(SERVERPROPERTY('InstanceDefaultBackupPath') AS NVARCHAR(512))";
                            var result = await cmd.ExecuteScalarAsync();
                            if (result != null && result != DBNull.Value)
                            {
                                backupDir = result.ToString();
                            }
                        }

                        if (string.IsNullOrEmpty(backupDir) || !Directory.Exists(backupDir))
                        {
                            backupDir = Path.GetTempPath();
                        }

                        var fullBakPath = Path.Combine(backupDir, bakFileName);
                        var sql = $"BACKUP DATABASE [{dbName}] TO DISK = '{fullBakPath}' WITH FORMAT, INIT;";
                        await _context.Database.ExecuteSqlRawAsync(sql);

                        if (System.IO.File.Exists(fullBakPath))
                        {
                            byte[] fileBytes = await System.IO.File.ReadAllBytesAsync(fullBakPath);
                            try { System.IO.File.Delete(fullBakPath); } catch { }
                            return File(fileBytes, "application/octet-stream", bakFileName);
                        }
                    }
                    catch (Exception bakEx)
                    {
                        // Trường hợp không đủ quyền ghi file .bak thì chuyển sang xuất JSON
                        TempData["Warning"] = $"Không thể xuất file .bak ({bakEx.Message}). Hệ thống đã tự động xuất bản sao lưu cấu trúc JSON.";
                    }
                }

                // Xuất cấu trúc dữ liệu sang tệp JSON
                var payload = new DatabaseBackupPayload
                {
                    Version = "1.0",
                    ExportedAt = DateTime.UtcNow,
                    DatabaseName = _context.Database.GetDbConnection().Database ?? "RentalSystemDB",
                    ServerName = _context.Database.GetDbConnection().DataSource ?? "localhost",

                    VaiTros = await _context.VaiTros.AsNoTracking().ToListAsync(),
                    NguoiDungs = await _context.NguoiDungs.AsNoTracking().ToListAsync(),
                    LoaiThietBis = await _context.LoaiThietBis.AsNoTracking().ToListAsync(),
                    SanPhams = await _context.SanPhams.AsNoTracking().ToListAsync(),
                    ThietBis = await _context.ThietBis.AsNoTracking().ToListAsync(),
                    LichSuThietBis = await _context.LichSuThietBis.AsNoTracking().ToListAsync(),
                    KhuyenMais = await _context.KhuyenMais.AsNoTracking().ToListAsync(),
                    HopDongs = await _context.HopDongs.AsNoTracking().ToListAsync(),
                    KyHanThanhToans = await _context.KyHanThanhToans.AsNoTracking().ToListAsync(),
                    ChiTietHopDongs = await _context.ChiTietHopDongs.AsNoTracking().ToListAsync(),
                    PhieuThus = await _context.PhieuThus.AsNoTracking().ToListAsync(),
                    PhieuChis = await _context.PhieuChis.AsNoTracking().ToListAsync(),
                    PhieuBaoTris = await _context.PhieuBaoTris.AsNoTracking().ToListAsync(),
                    BienBanBanGiaos = await _context.BienBanBanGiaos.AsNoTracking().ToListAsync(),
                    ThongBaos = await _context.ThongBaos.AsNoTracking().ToListAsync(),
                    LichSuNhacNos = await _context.LichSuNhacNos.AsNoTracking().ToListAsync(),
                    YeuCauGiaHans = await _context.YeuCauGiaHans.AsNoTracking().ToListAsync(),
                    PhanCongCongViecs = await _context.PhanCongCongViecs.AsNoTracking().ToListAsync()
                };

                var options = new JsonSerializerOptions
                {
                    WriteIndented = true,
                    ReferenceHandler = ReferenceHandler.IgnoreCycles,
                    Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping
                };

                byte[] jsonBytes = JsonSerializer.SerializeToUtf8Bytes(payload, options);
                string fileName = $"RentalSystemDB_Backup_{DateTime.Now:yyyyMMdd_HHmmss}.json";

                return File(jsonBytes, "application/json", fileName);
            }
            catch (Exception ex)
            {
                TempData["Error"] = $"Lỗi khi tạo bản sao lưu: {ex.Message}";
                return RedirectToAction(nameof(Index));
            }
        }

        // Alias tiện ích hỗ trợ GET request tải sao lưu trực tiếp
        [HttpGet]
        public async Task<IActionResult> DownloadBackup(string? format = "json")
        {
            return await Backup(format);
        }

        // Khôi phục cơ sở dữ liệu
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Restore(IFormFile? backupFile)
        {
            if (backupFile == null || backupFile.Length == 0)
            {
                TempData["Error"] = "Vui lòng chọn tệp sao lưu (.json hoặc .bak) để khôi phục!";
                return RedirectToAction(nameof(Index));
            }

            try
            {
                var ext = Path.GetExtension(backupFile.FileName).ToLowerInvariant();

                if (ext == ".json")
                {
                    using var stream = backupFile.OpenReadStream();
                    var options = new JsonSerializerOptions
                    {
                        PropertyNameCaseInsensitive = true,
                        ReferenceHandler = ReferenceHandler.IgnoreCycles
                    };

                    var payload = await JsonSerializer.DeserializeAsync<DatabaseBackupPayload>(stream, options);

                    if (payload == null)
                    {
                        TempData["Error"] = "Tệp sao lưu JSON không có dữ liệu hợp lệ!";
                        return RedirectToAction(nameof(Index));
                    }

                    await RestoreJsonPayloadAsync(payload);
                    TempData["Success"] = "Khôi phục cơ sở dữ liệu thành công từ tệp sao lưu JSON!";
                }
                else if (ext == ".bak")
                {
                    var dbName = _context.Database.GetDbConnection().Database ?? "RentalSystemDB";
                    var tempPath = Path.Combine(Path.GetTempPath(), $"{Guid.NewGuid():N}.bak");

                    using (var fs = new FileStream(tempPath, FileMode.Create))
                    {
                        await backupFile.CopyToAsync(fs);
                    }

                    try
                    {
                        var sql = $"ALTER DATABASE [{dbName}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; " +
                                  $"RESTORE DATABASE [{dbName}] FROM DISK = '{tempPath}' WITH REPLACE; " +
                                  $"ALTER DATABASE [{dbName}] SET MULTI_USER;";
                        await _context.Database.ExecuteSqlRawAsync(sql);
                        TempData["Success"] = "Khôi phục cơ sở dữ liệu thành công từ tệp .bak!";
                    }
                    finally
                    {
                        if (System.IO.File.Exists(tempPath))
                        {
                            try { System.IO.File.Delete(tempPath); } catch { }
                        }
                    }
                }
                else
                {
                    TempData["Error"] = "Định dạng tệp không được hỗ trợ. Vui lòng chọn tệp .json hoặc .bak!";
                }
            }
            catch (Exception ex)
            {
                TempData["Error"] = $"Lỗi khi khôi phục cơ sở dữ liệu: {ex.Message}";
            }

            return RedirectToAction(nameof(Index));
        }

        // Khôi phục dữ liệu theo quan hệ các bảng
        private async Task RestoreJsonPayloadAsync(DatabaseBackupPayload payload)
        {
            using var transaction = await _context.Database.BeginTransactionAsync();
            try
            {
                // Tắt khóa ngoại và xóa dữ liệu bảng con trước bảng cha
                await _context.Database.ExecuteSqlRawAsync(@"
                    ALTER TABLE [PhanCongCongViecs] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [YeuCauGiaHans] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [LichSuNhacNos] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [ThongBaos] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [BienBanBanGiaos] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [PhieuBaoTris] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [PhieuChis] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [PhieuThus] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [ChiTietHopDongs] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [KyHanThanhToans] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [HopDongs] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [KhuyenMais] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [LichSuThietBis] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [ThietBis] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [SanPhams] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [LoaiThietBis] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [NguoiDungs] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [VaiTros] NOCHECK CONSTRAINT ALL;

                    DELETE FROM [PhanCongCongViecs];
                    DELETE FROM [YeuCauGiaHans];
                    DELETE FROM [LichSuNhacNos];
                    DELETE FROM [ThongBaos];
                    DELETE FROM [BienBanBanGiaos];
                    DELETE FROM [PhieuBaoTris];
                    DELETE FROM [PhieuChis];
                    DELETE FROM [PhieuThus];
                    DELETE FROM [ChiTietHopDongs];
                    DELETE FROM [KyHanThanhToans];
                    DELETE FROM [HopDongs];
                    DELETE FROM [KhuyenMais];
                    DELETE FROM [LichSuThietBis];
                    DELETE FROM [ThietBis];
                    DELETE FROM [SanPhams];
                    DELETE FROM [LoaiThietBis];
                    DELETE FROM [NguoiDungs];
                    DELETE FROM [VaiTros];
                ");

                // Nạp lại từng bảng theo thứ tự cha trước con, bật IDENTITY_INSERT
                if (payload.VaiTros != null && payload.VaiTros.Any())
                {
                    await InsertWithIdentityAsync(_context.VaiTros, "VaiTros", payload.VaiTros);
                }

                if (payload.NguoiDungs != null && payload.NguoiDungs.Any())
                {
                    foreach (var u in payload.NguoiDungs) { u.VaiTro = null!; }
                    await InsertWithIdentityAsync(_context.NguoiDungs, "NguoiDungs", payload.NguoiDungs);
                }

                if (payload.LoaiThietBis != null && payload.LoaiThietBis.Any())
                {
                    await InsertWithIdentityAsync(_context.LoaiThietBis, "LoaiThietBis", payload.LoaiThietBis);
                }

                if (payload.SanPhams != null && payload.SanPhams.Any())
                {
                    foreach (var s in payload.SanPhams) { s.LoaiThietBi = null!; }
                    await InsertWithIdentityAsync(_context.SanPhams, "SanPhams", payload.SanPhams);
                }

                if (payload.ThietBis != null && payload.ThietBis.Any())
                {
                    foreach (var t in payload.ThietBis)
                    {
                        t.SanPham = null!;
                        t.LichSuThietBis = null;
                        t.PhieuBaoTris = null;
                    }
                    await InsertWithIdentityAsync(_context.ThietBis, "ThietBis", payload.ThietBis);
                }

                if (payload.LichSuThietBis != null && payload.LichSuThietBis.Any())
                {
                    foreach (var l in payload.LichSuThietBis)
                    {
                        l.ThietBi = null!;
                        l.NguoiThucHien = null;
                    }
                    await InsertWithIdentityAsync(_context.LichSuThietBis, "LichSuThietBis", payload.LichSuThietBis);
                }

                if (payload.KhuyenMais != null && payload.KhuyenMais.Any())
                {
                    foreach (var k in payload.KhuyenMais)
                    {
                        k.HopDongs = null;
                    }
                    await InsertWithIdentityAsync(_context.KhuyenMais, "KhuyenMais", payload.KhuyenMais);
                }

                if (payload.HopDongs != null && payload.HopDongs.Any())
                {
                    foreach (var h in payload.HopDongs)
                    {
                        h.KhachHang = null!;
                        h.NhanVien = null!;
                        h.KhuyenMai = null;
                        h.KyHanThanhToans = null!;
                        h.BienBanBanGiaos = null;
                        h.PhieuChis = null;
                        h.PhieuThus = null;
                        h.PhieuBaoTris = null;
                        h.LichSuNhacNos = null;
                        h.DanhSachYeuCauGiaHan = null;
                    }
                    await InsertWithIdentityAsync(_context.HopDongs, "HopDongs", payload.HopDongs);
                }

                if (payload.KyHanThanhToans != null && payload.KyHanThanhToans.Any())
                {
                    foreach (var k in payload.KyHanThanhToans)
                    {
                        k.HopDong = null!;
                        k.LichSuNhacNos = null;
                    }
                    await InsertWithIdentityAsync(_context.KyHanThanhToans, "KyHanThanhToans", payload.KyHanThanhToans);
                }

                if (payload.ChiTietHopDongs != null && payload.ChiTietHopDongs.Any())
                {
                    foreach (var c in payload.ChiTietHopDongs)
                    {
                        c.HopDong = null!;
                        c.ThietBi = null!;
                    }
                    await _context.ChiTietHopDongs.AddRangeAsync(payload.ChiTietHopDongs);
                    await _context.SaveChangesAsync();
                    _context.ChangeTracker.Clear();
                }

                if (payload.PhieuThus != null && payload.PhieuThus.Any())
                {
                    foreach (var pt in payload.PhieuThus)
                    {
                        pt.HopDong = null!;
                        pt.KyHanThanhToan = null;
                        pt.NhanVienThu = null;
                    }
                    await InsertWithIdentityAsync(_context.PhieuThus, "PhieuThus", payload.PhieuThus);
                }

                if (payload.PhieuChis != null && payload.PhieuChis.Any())
                {
                    foreach (var pc in payload.PhieuChis)
                    {
                        pc.HopDong = null!;
                        pc.NhanVienChi = null!;
                    }
                    await InsertWithIdentityAsync(_context.PhieuChis, "PhieuChis", payload.PhieuChis);
                }

                if (payload.PhieuBaoTris != null && payload.PhieuBaoTris.Any())
                {
                    foreach (var pb in payload.PhieuBaoTris)
                    {
                        pb.HopDong = null;
                        pb.ThietBi = null!;
                        pb.KyThuatVien = null;
                    }
                    await InsertWithIdentityAsync(_context.PhieuBaoTris, "PhieuBaoTris", payload.PhieuBaoTris);
                }

                if (payload.BienBanBanGiaos != null && payload.BienBanBanGiaos.Any())
                {
                    foreach (var bb in payload.BienBanBanGiaos)
                    {
                        bb.HopDong = null!;
                        bb.NhanVienLap = null!;
                    }
                    await InsertWithIdentityAsync(_context.BienBanBanGiaos, "BienBanBanGiaos", payload.BienBanBanGiaos);
                }

                if (payload.ThongBaos != null && payload.ThongBaos.Any())
                {
                    foreach (var tb in payload.ThongBaos)
                    {
                        tb.NguoiDung = null!;
                    }
                    await InsertWithIdentityAsync(_context.ThongBaos, "ThongBaos", payload.ThongBaos);
                }

                if (payload.LichSuNhacNos != null && payload.LichSuNhacNos.Any())
                {
                    foreach (var ln in payload.LichSuNhacNos)
                    {
                        ln.HopDong = null;
                        ln.KyHanThanhToan = null;
                        ln.NguoiGui = null;
                    }
                    await InsertWithIdentityAsync(_context.LichSuNhacNos, "LichSuNhacNos", payload.LichSuNhacNos);
                }

                if (payload.YeuCauGiaHans != null && payload.YeuCauGiaHans.Any())
                {
                    foreach (var yg in payload.YeuCauGiaHans)
                    {
                        yg.HopDong = null!;
                        yg.NguoiDuyet = null;
                    }
                    await InsertWithIdentityAsync(_context.YeuCauGiaHans, "YeuCauGiaHans", payload.YeuCauGiaHans);
                }

                if (payload.PhanCongCongViecs != null && payload.PhanCongCongViecs.Any())
                {
                    foreach (var pc in payload.PhanCongCongViecs)
                    {
                        pc.NhanVien = null!;
                        pc.NguoiGiao = null;
                        pc.HopDong = null;
                        pc.PhieuBaoTri = null;
                    }
                    await InsertWithIdentityAsync(_context.PhanCongCongViecs, "PhanCongCongViecs", payload.PhanCongCongViecs);
                }

                // Bật lại các ràng buộc khóa ngoại
                await _context.Database.ExecuteSqlRawAsync(@"
                    ALTER TABLE [VaiTros] CHECK CONSTRAINT ALL;
                    ALTER TABLE [NguoiDungs] CHECK CONSTRAINT ALL;
                    ALTER TABLE [LoaiThietBis] CHECK CONSTRAINT ALL;
                    ALTER TABLE [SanPhams] CHECK CONSTRAINT ALL;
                    ALTER TABLE [ThietBis] CHECK CONSTRAINT ALL;
                    ALTER TABLE [LichSuThietBis] CHECK CONSTRAINT ALL;
                    ALTER TABLE [KhuyenMais] CHECK CONSTRAINT ALL;
                    ALTER TABLE [HopDongs] CHECK CONSTRAINT ALL;
                    ALTER TABLE [KyHanThanhToans] CHECK CONSTRAINT ALL;
                    ALTER TABLE [ChiTietHopDongs] CHECK CONSTRAINT ALL;
                    ALTER TABLE [PhieuThus] CHECK CONSTRAINT ALL;
                    ALTER TABLE [PhieuChis] CHECK CONSTRAINT ALL;
                    ALTER TABLE [PhieuBaoTris] CHECK CONSTRAINT ALL;
                    ALTER TABLE [BienBanBanGiaos] CHECK CONSTRAINT ALL;
                    ALTER TABLE [ThongBaos] CHECK CONSTRAINT ALL;
                    ALTER TABLE [LichSuNhacNos] CHECK CONSTRAINT ALL;
                    ALTER TABLE [YeuCauGiaHans] CHECK CONSTRAINT ALL;
                    ALTER TABLE [PhanCongCongViecs] CHECK CONSTRAINT ALL;
                ");

                await transaction.CommitAsync();
            }
            catch
            {
                await transaction.RollbackAsync();
                throw;
            }
        }

        private async Task InsertWithIdentityAsync<T>(DbSet<T> dbSet, string tableName, IEnumerable<T> items) where T : class
        {
            if (items == null || !items.Any()) return;

            string sqlOn = string.Format("SET IDENTITY_INSERT [{0}] ON;", tableName);
            await _context.Database.ExecuteSqlRawAsync(sqlOn);
            await dbSet.AddRangeAsync(items);
            await _context.SaveChangesAsync();
            string sqlOff = string.Format("SET IDENTITY_INSERT [{0}] OFF;", tableName);
            await _context.Database.ExecuteSqlRawAsync(sqlOff);
            _context.ChangeTracker.Clear();
        }
    }

    // ViewModels cho chức năng sao lưu và khôi phục
    public class TableStatItem
    {
        public string TableName { get; set; } = string.Empty;
        public string DisplayName { get; set; } = string.Empty;
        public int RowCount { get; set; }
        public string Icon { get; set; } = "fa-table";
    }

    public class DatabaseDashboardViewModel
    {
        public string ServerName { get; set; } = string.Empty;
        public string DatabaseName { get; set; } = string.Empty;
        public string ProviderName { get; set; } = "Microsoft SQL Server";
        public bool IsConnected { get; set; }
        public int TotalRows { get; set; }
        public DateTime CheckedAt { get; set; } = DateTime.Now;
        public List<TableStatItem> Tables { get; set; } = new();
    }

    public class DatabaseBackupPayload
    {
        public string Version { get; set; } = "1.0";
        public DateTime ExportedAt { get; set; } = DateTime.UtcNow;
        public string DatabaseName { get; set; } = "RentalSystemDB";
        public string ServerName { get; set; } = "localhost";

        public List<VaiTro> VaiTros { get; set; } = new();
        public List<NguoiDung> NguoiDungs { get; set; } = new();
        public List<LoaiThietBi> LoaiThietBis { get; set; } = new();
        public List<SanPham> SanPhams { get; set; } = new();
        public List<ThietBi> ThietBis { get; set; } = new();
        public List<LichSuThietBisBackupDto>? LegacyLichSuThietBis { get; set; }
        public List<LichSuThietBi> LichSuThietBis { get; set; } = new();
        public List<KhuyenMai> KhuyenMais { get; set; } = new();
        public List<HopDong> HopDongs { get; set; } = new();
        public List<KyHanThanhToan> KyHanThanhToans { get; set; } = new();
        public List<ChiTietHopDong> ChiTietHopDongs { get; set; } = new();
        public List<PhieuThu> PhieuThus { get; set; } = new();
        public List<PhieuChi> PhieuChis { get; set; } = new();
        public List<PhieuBaoTri> PhieuBaoTris { get; set; } = new();
        public List<BienBanBanGiao> BienBanBanGiaos { get; set; } = new();
        public List<ThongBao> ThongBaos { get; set; } = new();
        public List<LichSuNhacNo> LichSuNhacNos { get; set; } = new();
        public List<YeuCauGiaHan> YeuCauGiaHans { get; set; } = new();
        public List<PhanCongCongViec> PhanCongCongViecs { get; set; } = new();
    }

    public class LichSuThietBisBackupDto
    {
        public int MaLichSu { get; set; }
        public int MaThietBi { get; set; }
        public string HanhDong { get; set; } = string.Empty;
        public DateTime ThoiGian { get; set; }
        public int? MaNguoiThucHien { get; set; }
        public string? GhiChu { get; set; }
    }
}
