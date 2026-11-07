using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Common;
using RentalSystem.Models;
using RentalSystem.Services;
using System.Globalization;

namespace RentalSystem.Controllers;

[ApiController]
[Route("api/tasks")]
[Authorize(AuthenticationSchemes = ApiTokens.Scheme)]
public class ApiTasksController(ApplicationDbContext db) : ControllerBase
{
    [HttpGet("mine")]
    [Authorize(Roles = "Admin,KinhDoanh,KyThuat")]
    public async Task<IActionResult> Mine()
    {
        int userId = User.UserId();
        var assignments = await db.PhanCongCongViecs.AsNoTracking()
            .Where(t => t.MaNhanVien == userId && !t.TuDongTuBaoTri)
            .OrderByDescending(t => t.NgayGiao).ThenByDescending(t => t.MaPhanCong)
            .Select(t => new
            {
                id = t.MaPhanCong, title = t.TieuDe, description = t.NoiDung,
                contractId = t.MaHopDong, ticketId = t.MaPhieuBaoTri,
                customer = t.HopDong == null ? null : t.HopDong.KhachHang.HoTen,
                statusCode = t.TrangThai, assignedAt = t.NgayGiao, dueAt = t.HanHoanThanh,
                completedAt = t.NgayHoanThanh, notes = t.GhiChuTienDo
            }).ToListAsync();
        return Ok(assignments.Select(t => new
        {
            t.id, t.title, t.description, t.contractId, t.ticketId, t.customer, t.statusCode,
            status = StaffAssignments.StatusLabel(t.statusCode), t.assignedAt, t.dueAt, t.completedAt, t.notes
        }));
    }

    [HttpPut("{id:int}/status")]
    [Authorize(Roles = "Admin,KinhDoanh,KyThuat")]
    public async Task<IActionResult> UpdateStatus(int id, [FromBody] ManualTaskStatus request)
    {
        if (request.StatusCode == null) return BadRequest(new { message = "Chọn trạng thái công việc." });
        var result = await StaffAssignments.UpdateAsync(db, id, User.UserId(), false, request.StatusCode.Value, request.Notes);
        if (result.Code != 200) return StatusCode(result.Code, new { message = result.Message });
        return Ok(new { success = true });
    }

    [HttpGet("installation/{contractId:int}")]
    public async Task<IActionResult> Installation(int contractId)
    {
        int userId = User.UserId();
        bool customer = User.IsInRole("KhachHang");
        var assignments = StaffAssignments.Installations(db).AsNoTracking().Where(t => t.MaHopDong == contractId);
        if (customer) assignments = assignments.Where(t => t.HopDong!.MaKhachHang == userId);
        else if (!User.IsManager()) assignments = assignments.Where(t => t.MaNhanVien == userId);
        var task = await assignments.OrderByDescending(t => t.NgayGiao).ThenByDescending(t => t.MaPhanCong)
            .Select(t => new
            {
                t.MaPhanCong, t.MaNhanVien, t.TrangThai, t.HanHoanThanh, t.NgayHoanThanh,
                staff = t.NhanVien.HoTen, notes = t.GhiChuTienDo
            }).FirstOrDefaultAsync();
        if (task == null) return NotFound();
        return Ok(new
        {
            taskId = task.MaPhanCong, contractId = contractId.ToString(CultureInfo.InvariantCulture),
            status = StaffAssignments.StatusLabel(task.TrangThai), statusCode = task.TrangThai,
            expectedDate = task.HanHoanThanh?.ToString("dd/MM/yyyy HH:mm"),
            actualDate = task.NgayHoanThanh?.ToString("dd/MM/yyyy HH:mm"),
            assignedStaffName = task.staff, notes = customer ? null : task.notes,
            canUpdate = !customer && task.MaNhanVien == userId
        });
    }
}

public sealed record ManualTaskStatus(int? StatusCode, string? Notes);
