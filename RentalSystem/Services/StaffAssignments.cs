using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Services;

internal static class StaffAssignments
{
    internal static string StatusLabel(int status) => status switch
    {
        0 => "Mới",
        1 => "Đang thực hiện",
        2 => "Hoàn thành",
        3 => "Đã hủy",
        _ => "Không xác định"
    };

    internal static IQueryable<PhanCongCongViec> Installations(ApplicationDbContext db) =>
        db.PhanCongCongViecs.Where(t => !t.TuDongTuBaoTri && t.MaHopDong != null &&
            t.TieuDe.ToLower().Contains("lắp đặt"));

    internal static async Task<(PhanCongCongViec? Task, int Code, string Message)> UpdateAsync(
        ApplicationDbContext db, int id, int userId, bool allowOtherAssignees, int status, string? note)
    {
        if (status is < 0 or > 3) return (null, 400, "Trạng thái không hợp lệ.");

        var scope = db.PhanCongCongViecs.Where(t => t.MaPhanCong == id &&
            (allowOtherAssignees || t.MaNhanVien == userId));
        var now = DateTime.Now;
        note = string.IsNullOrWhiteSpace(note) ? null : note.Trim();
        int changed = await scope.Where(t => !t.TuDongTuBaoTri)
            .ExecuteUpdateAsync(setters => setters
                .SetProperty(t => t.TrangThai, status)
                .SetProperty(t => t.NgayHoanThanh, t => status == 2 ? t.NgayHoanThanh ?? now : null)
                .SetProperty(t => t.GhiChuTienDo, t => note ?? t.GhiChuTienDo));

        var task = await scope.AsNoTracking().SingleOrDefaultAsync();
        if (task == null)
            return await db.PhanCongCongViecs.AnyAsync(t => t.MaPhanCong == id)
                ? (null, 403, "Bạn không có quyền cập nhật công việc này.")
                : (null, 404, "Không tìm thấy công việc.");
        if (changed == 0)
            return (task, 409, "Hãy cập nhật tiến độ trên phiếu bảo trì.");
        return (task, 200, "Đã cập nhật tiến độ.");
    }

    internal static void NotifyAssignee(ApplicationDbContext db, PhanCongCongViec task) =>
        db.ThongBaos.Add(new ThongBao
        {
            MaNguoiDung = task.MaNhanVien,
            TieuDe = "Bạn được giao công việc",
            NoiDung = task.TieuDe,
            LoaiThongBao = "PhanCong",
            LienKet = "/Admin/PhanCong/MyTasks"
        });
}
