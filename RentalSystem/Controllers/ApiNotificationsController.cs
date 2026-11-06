using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Common;
using RentalSystem.Models;

namespace RentalSystem.Controllers;

[ApiController]
[Route("api/notifications")]
[Authorize(AuthenticationSchemes = ApiTokens.Scheme)]
public class ApiNotificationsController(ApplicationDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> List()
    {
        int userId = User.UserId();
        return Ok(await db.ThongBaos.AsNoTracking().Where(n => n.MaNguoiDung == userId)
            .OrderByDescending(n => n.NgayTao).ThenByDescending(n => n.MaThongBao)
            .Select(n => new
            {
                id = n.MaThongBao, title = n.TieuDe, content = n.NoiDung, createdAt = n.NgayTao,
                isRead = n.DaDoc, type = n.LoaiThongBao
            }).ToListAsync());
    }

    [HttpPut("{id:int}/read")]
    public async Task<IActionResult> Read(int id)
    {
        int userId = User.UserId();
        int changed = await db.ThongBaos.Where(n => n.MaNguoiDung == userId && n.MaThongBao == id)
            .ExecuteUpdateAsync(update => update.SetProperty(n => n.DaDoc, true));
        return changed == 0 ? NotFound() : NoContent();
    }

    [HttpPut("read-all")]
    public async Task<IActionResult> ReadAll()
    {
        int userId = User.UserId();
        await db.ThongBaos.Where(n => n.MaNguoiDung == userId && !n.DaDoc)
            .ExecuteUpdateAsync(update => update.SetProperty(n => n.DaDoc, true));
        return NoContent();
    }
}
