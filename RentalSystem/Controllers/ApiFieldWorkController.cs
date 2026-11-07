using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Common;
using RentalSystem.Models;
using RentalSystem.Services;

namespace RentalSystem.Controllers;

[ApiController]
[Authorize(AuthenticationSchemes = ApiTokens.Scheme, Roles = "KyThuat")]
public sealed class ApiFieldWorkController(ApplicationDbContext db, IWebHostEnvironment env) : ControllerBase
{
    [HttpGet("api/contracts/{id:int}/handovers")]
    public async Task<IActionResult> Handovers(int id)
    {
        var contract = await db.HopDongs.VisibleContracts(User, db).FirstOrDefaultAsync(h => h.MaHopDong == id);
        if (contract == null) return NotFound();
        var records = await db.BienBanBanGiaos.Where(b => b.MaHopDong == id).OrderByDescending(b => b.MaBienBan)
            .Select(b => new { id = b.MaBienBan, kind = b.LoaiBienBan, at = b.NgayLap,
                accessories = b.PhuKienKemTheo, condition = b.TinhTrangNgoaiQuan, notes = b.GhiChu,
                photos = new[] { b.HinhAnh1, b.HinhAnh2, b.HinhAnh3, b.HinhAnh4 }, signature = b.ChuKyXacNhan }).ToListAsync();
        return Ok(new { contractId = id, statusCode = contract.TrangThai,
            canDeliver = contract.TrangThai is 0 or 1, canReturn = contract.TrangThai is 1 or 4, records });
    }

    [HttpPost("api/contracts/{id:int}/handovers")]
    [RequestSizeLimit(22 * 1024 * 1024)]
    public async Task<IActionResult> Handover(int id, [FromForm] HandoverUpload request)
    {
        try
        {
            var row = await EquipmentHandover.CreateAsync(db, env, User, id, request.Kind, request.Accessories,
                request.Condition, request.Notes, request.Photos, request.SignatureData, HttpContext.RequestAborted);
            return row == null ? NotFound() : Ok(new { success = true, id = row.MaBienBan });
        }
        catch (RentalBookingException error) { return StatusCode(error.StatusCode, new { message = error.Message }); }
    }

    [HttpPost("api/maintenance/{id:int}/evidence")]
    [RequestSizeLimit(6 * 1024 * 1024)]
    public async Task<IActionResult> Evidence(int id, [FromForm] MaintenanceEvidenceUpload request)
    {
        await using var transaction = await MaintenanceAssignment.BeginUpdateAsync(db, id);
        var ticket = await db.PhieuBaoTris.FirstOrDefaultAsync(p => p.MaPhieu == id && p.MaKyThuatVien == User.UserId());
        if (ticket == null) return NotFound();
        if (ticket.TrangThai is not (1 or 2 or 3)) return Conflict(new { message = "Phiếu đã đóng." });
        try
        {
            var paths = CustomerMaintenance.ImagePaths(ticket);
            if (paths.Length >= 8) return Conflict(new { message = "Phiếu đã có đủ 8 ảnh minh chứng." });
            string path = await ContractDocuments.SaveImageAsync(env, request.Image, "baotri", "kt", id, HttpContext.RequestAborted);
            bool committed = false;
            try
            {
                ticket.HinhAnhLoi = string.Join(';', paths.Append(path));
                ticket.GhiChuSuaChua = $"{ticket.GhiChuSuaChua}\n[Ảnh hiện trường {DateTime.Now:dd/MM/yyyy HH:mm}] {request.Notes?.Trim()}".Trim();
                await db.SaveChangesAsync();
                await transaction.CommitAsync();
                committed = true;
                return Ok(new { success = true });
            }
            finally { if (!committed) System.IO.File.Delete(Path.Combine(env.WebRootPath, path.TrimStart('/'))); }
        }
        catch (RentalBookingException error) { return StatusCode(error.StatusCode, new { message = error.Message }); }
    }
}

public sealed class HandoverUpload
{
    public int Kind { get; set; }
    public string? Accessories { get; set; }
    public string? Condition { get; set; }
    public string? Notes { get; set; }
    public string? SignatureData { get; set; }
    public List<IFormFile> Photos { get; set; } = [];
}
public sealed class MaintenanceEvidenceUpload
{
    public IFormFile? Image { get; set; }
    public string? Notes { get; set; }
}
