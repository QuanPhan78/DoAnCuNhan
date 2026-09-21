import os
import re

path = r'd:\DoAnCuNhan\RentalSystem\Controllers\CartController.cs'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix GET method
old_get = '''        public async Task<IActionResult> SignContract(int id)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

            var hopDong = await _context.HopDongs
                .FirstOrDefaultAsync(h => h.MaHopDong == id && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            if (!string.IsNullOrEmpty(hopDong.ChuKyKhachHang))
            {
                TempData["Error"] = "Hợp đồng này đã được ký!";
                return RedirectToAction("MyContracts");
            }

            return View(hopDong);
        }'''

new_get = '''        public async Task<IActionResult> SignContract(int id)
        {
            var nameIdentifierClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (nameIdentifierClaim == null || !int.TryParse(nameIdentifierClaim.Value, out int userId))
                return RedirectToAction("Login", "Account");

            var hopDong = await _context.HopDongs
                .FirstOrDefaultAsync(h => h.MaHopDong == id && h.MaKhachHang == userId);

            if (hopDong == null) return NotFound();

            if (!string.IsNullOrEmpty(hopDong.ChuKyKhachHang))
            {
                TempData["Error"] = "Hợp đồng này đã được ký!";
                return RedirectToAction("MyContracts");
            }
            
            decimal tienCocYeuCau = await _context.ChiTietHopDongs
                .Where(c => c.MaHopDong == id)
                .Include(c => c.ThietBi)
                .ThenInclude(t => t.SanPham)
                .SumAsync(c => c.ThietBi.SanPham.TienCoc);
                
            ViewBag.TienCocYeuCau = tienCocYeuCau;

            return View(hopDong);
        }'''
content = content.replace(old_get, new_get)


# Fix POST method signature
old_post_sig = 'public async Task<IActionResult> SignContract(int id, Microsoft.AspNetCore.Http.IFormFile cmndFile, string signatureData)'
new_post_sig = 'public async Task<IActionResult> SignContract(int id, int soKyHan, Microsoft.AspNetCore.Http.IFormFile cmndFile, string signatureData)'
content = content.replace(old_post_sig, new_post_sig)

# Add soKyHan assignment
old_post_logic = '''            if (string.IsNullOrEmpty(hopDong.ChuKyKhachHang) || string.IsNullOrEmpty(hopDong.AnhCMND))
            {
                TempData["Error"] = "Vui lòng tải lên CMND và Ký tên đầy đủ!";
                return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
            }

            await _context.SaveChangesAsync();'''

new_post_logic = '''            if (string.IsNullOrEmpty(hopDong.ChuKyKhachHang) || string.IsNullOrEmpty(hopDong.AnhCMND))
            {
                TempData["Error"] = "Vui lòng tải lên CMND và Ký tên đầy đủ!";
                return RedirectToAction("SignContract", new { id = hopDong.MaHopDong });
            }
            
            if (soKyHan < 1) soKyHan = 1;
            hopDong.SoKyHan = soKyHan;

            await _context.SaveChangesAsync();'''

content = content.replace(old_post_logic, new_post_logic)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
