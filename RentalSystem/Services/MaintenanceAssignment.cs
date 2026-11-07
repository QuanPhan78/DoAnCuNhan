using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Storage;
using RentalSystem.Models;

namespace RentalSystem.Services;

public static class MaintenanceAssignment
{
    public static async Task<IDbContextTransaction> BeginUpdateAsync(ApplicationDbContext db, int ticketId)
    {
        var transaction = await db.Database.BeginTransactionAsync();
        try
        {
            var resource = $"RentalSystem.Maintenance.{ticketId}";
            await db.Database.ExecuteSqlInterpolatedAsync($"""
                DECLARE @result int;
                EXEC @result = sys.sp_getapplock @Resource = {resource},
                    @LockMode = 'Exclusive', @LockOwner = 'Transaction', @LockTimeout = 10000;
                IF @result < 0 THROW 51011, N'Không thể khóa phiếu bảo trì để cập nhật.', 1;
                """);
            return transaction;
        }
        catch
        {
            await transaction.DisposeAsync();
            throw;
        }
    }

    public static Task<bool> IsActiveTechnicianAsync(ApplicationDbContext db, int id) =>
        db.NguoiDungs.AnyAsync(u => u.MaNguoiDung == id && u.TrangThai && u.VaiTro.TenVaiTro == "KyThuat");

    public static string StatusLabel(int status) => status switch
    {
        1 => "Chờ xử lý",
        2 => "Đang xử lý",
        3 => "Chờ nghiệm thu",
        4 => "Hỏng, chuyển thanh lý",
        5 => "Đã nghiệm thu",
        _ => "Chưa xác định"
    };

    public static string TaskLabel(PhanCongCongViec task) => task.PhieuBaoTri?.TrangThai switch
    {
        1 => "Mới giao",
        2 => "Đang xử lý",
        3 => "Chờ nghiệm thu",
        4 => "Hỏng, chuyển thanh lý",
        5 => "Hoàn thành",
        _ => "Phiếu không còn liên kết"
    };

    public static async Task ApplyStatusAsync(ApplicationDbContext db, PhieuBaoTri ticket, int status)
    {
        if (ticket.TrangThai == status) return;

        var now = DateTime.Now;
        int previousStatus = ticket.TrangThai;
        ticket.TrangThai = status;
        if (status == 2)
        {
            ticket.NgayBatDauBaoTri ??= now;
            if (previousStatus is 3 or 5)
            {
                ticket.NgayHoanThanh = null;
                ticket.NgayKetThucBaoTri = null;
                ticket.NgayNghiemThu = null;
                ticket.DaNghiemThu = false;
            }
        }
        else if (status == 3)
        {
            ticket.NgayHoanThanh = now;
            ticket.NgayKetThucBaoTri = now;
            ticket.DaNghiemThu = false;
            ticket.NgayNghiemThu = null;
        }
        else if (status == 5)
        {
            ticket.DaNghiemThu = true;
            ticket.NgayNghiemThu = now;
        }

        if (status is 2 or 4 or 5)
        {
            var device = await db.ThietBis.FindAsync(ticket.MaThietBi);
            if (device != null)
            {
                if (status == 4)
                {
                    device.TrangThai = 4;
                    device.TinhTrangMay = $"Hỏng không thể khắc phục (Thanh lý) - Phiếu #{ticket.MaPhieu}";
                }
                else if (status == 2 && device.TrangThai != 4)
                {
                    device.TrangThai = 2;
                }
                else if (status == 5 && device.TrangThai == 2 && !await db.PhieuBaoTris.AnyAsync(p =>
                    p.MaThietBi == ticket.MaThietBi && p.MaPhieu != ticket.MaPhieu &&
                    (p.TrangThai == 2 || p.TrangThai == 3)))
                {
                    var bookings = db.ChiTietHopDongs.Where(c => c.MaThietBi == ticket.MaThietBi);
                    device.TrangThai = await bookings.AnyAsync(c => c.HopDong.TrangThai == 1) ? 1 :
                        await bookings.AnyAsync(c => c.HopDong.TrangThai == 0) ? 3 : 0;
                }
            }
        }
    }

    // The caller saves the ticket and task together before committing the transaction.
    public static async Task SyncAsync(ApplicationDbContext db, PhieuBaoTri ticket, int? actorId)
    {
        if (ticket.MaKyThuatVien is not int technicianId) return;

        var task = await db.PhanCongCongViecs.SingleOrDefaultAsync(
            p => p.MaPhieuBaoTri == ticket.MaPhieu && p.TuDongTuBaoTri);
        var now = DateTime.Now;

        if (task == null)
        {
            task = new PhanCongCongViec
            {
                TuDongTuBaoTri = true,
                MaPhieuBaoTri = ticket.MaPhieu,
                MaNhanVien = technicianId,
                MaNguoiGiao = actorId,
                NgayGiao = now,
                TieuDe = $"Xử lý phiếu sự cố #{ticket.MaPhieu}",
                NoiDung = ticket.MoTaLoi
            };
            db.PhanCongCongViecs.Add(task);
        }
        else if (task.MaNhanVien != technicianId)
        {
            db.LichSuThietBis.Add(new LichSuThietBi
            {
                MaThietBi = ticket.MaThietBi,
                MaNguoiThucHien = actorId,
                ThoiGian = now,
                HanhDong = $"Đổi kỹ thuật viên phiếu #{ticket.MaPhieu}",
                GhiChu = $"Nhân viên #{task.MaNhanVien} → #{technicianId}"
            });
            task.MaNhanVien = technicianId;
            task.MaNguoiGiao = actorId;
            task.NgayGiao = now;
        }

        task.MaHopDong = ticket.MaHopDong;
        task.HanHoanThanh = ticket.HanHoanThanh;
        task.TrangThai = ticket.TrangThai switch { 1 => 0, 4 or 5 => 2, _ => 1 };
        task.NgayHoanThanh = task.TrangThai == 2 ? task.NgayHoanThanh ?? ticket.NgayNghiemThu ?? now : null;
    }
}
