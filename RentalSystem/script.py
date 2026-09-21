import os
import re

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

overlap_query = '''!_context.ChiTietHopDongs.Any(c => 
                        c.MaThietBi == t.MaThietBi && 
                        c.HopDong.TrangThai != 2 && c.HopDong.TrangThai != 3 &&
                        c.HopDong.NgayBatDau < NgayKetThuc && 
                        c.HopDong.NgayKetThuc > NgayBatDau)'''

# 1. CartController
cart_path = r'd:\DoAnCuNhan\RentalSystem\Controllers\CartController.cs'
cart = read_file(cart_path)

cart = cart.replace(
    't.TrangThai == 0',
    overlap_query
)

cart = cart.replace(
    'device.TrangThai = 3;',
    '// Bỏ khóa cứng TrangThai = 3.'
)

cart = cart.replace(
    '_context.PhieuThus.RemoveRange(phieuThus);',
    '_context.PhieuThus.RemoveRange(phieuThus);\n\n            var phieuBaoTris = _context.PhieuBaoTris.Where(p => p.MaHopDong == id);\n            _context.PhieuBaoTris.RemoveRange(phieuBaoTris);\n\n            var kyHans = _context.KyHanThanhToans.Where(k => k.MaHopDong == id);\n            _context.KyHanThanhToans.RemoveRange(kyHans);'
)

write_file(cart_path, cart)

# 2. HopDongController (Admin)
hd_path = r'd:\DoAnCuNhan\RentalSystem\Areas\Admin\Controllers\HopDongController.cs'
hd = read_file(hd_path)

hd = hd.replace(
    't.TrangThai == 0',
    overlap_query
)
hd = hd.replace(
    'dev.TrangThai = 3;',
    '// Bỏ khóa cứng TrangThai = 3.'
)

# Replace GhiChu append with SoKyHan assignment
hd = re.sub(
    r'if \(SoKyHan > 1\)\s*\{\s*hd\.GhiChu = \(string\.IsNullOrEmpty\(hd\.GhiChu\) \? \"\" \: hd\.GhiChu \+ \" \| \"\) \+ \$\"\[SoKy:\{SoKyHan\}\]\";\s*\}',
    'hd.SoKyHan = SoKyHan;',
    hd
)

# UpdateStatus Bug 13 parse SoKyHan
hd = re.sub(
    r'int soKy = 1;\s*var ghiChu = hopDong\.GhiChu \?\? \"\";\s*var match = System\.Text\.RegularExpressions\.Regex\.Match\(ghiChu, \@\"\\\[SoKy:\\(\\\\d\+\)\\\]\"\);\s*if \(match\.Success && int\.TryParse\(match\.Groups\[1\]\.Value, out int parsedSoKy\) && parsedSoKy > 0\)\s*\{\s*soKy = parsedSoKy;\s*\}',
    'int soKy = hopDong.SoKyHan;\n                    if (soKy <= 0) soKy = 1;',
    hd
)

# UpdateStatus Bug 9, 10
# We need to replace the else if (status == 2 || status == 3) block completely
old_block = '''else if (status == 2 || status == 3) // Hoàn tất hoặc Hủy -> Trả máy về kho 0 (Sẵn sàng)
            {
                foreach (var ct in chiTiets)
                {
                    var tb = await _context.ThietBis.FindAsync(ct.MaThietBi);
                    if (tb != null)
                    {
                        tb.TrangThai = 0; // Sẵn sàng
                    }
                }
            }'''

new_block = '''else if (status == 2)
            {
                if (hopDong.TrangThaiThanhToan != 2)
                {
                    TempData["Error"] = "Không thể hoàn tất hợp đồng khi khách hàng chưa thanh toán đủ công nợ!";
                    return RedirectToAction(nameof(Details), new { id = id });
                }
                foreach (var ct in chiTiets)
                {
                    var tb = await _context.ThietBis.FindAsync(ct.MaThietBi);
                    if (tb != null) tb.TrangThai = 0;
                }
            }
            else if (status == 3)
            {
                var phieuBaoTris = _context.PhieuBaoTris.Where(p => p.MaHopDong == id);
                _context.PhieuBaoTris.RemoveRange(phieuBaoTris);
                var kyHans = _context.KyHanThanhToans.Where(k => k.MaHopDong == id);
                _context.KyHanThanhToans.RemoveRange(kyHans);

                foreach (var ct in chiTiets)
                {
                    var tb = await _context.ThietBis.FindAsync(ct.MaThietBi);
                    if (tb != null) tb.TrangThai = 0;
                }
            }'''

hd = hd.replace(old_block, new_block)

# Bug 7 ThemTienCoc
hd = hd.replace(
    'k.SoTienPhai = moiKy;',
    'k.SoTienPhai = k.SoTienDaTra + moiKy;'
)

# Bug 11 ConfirmPayment
hd = hd.replace(
    'if (kyHan.TrangThai != 1)',
    'if (soTienThucThu <= 0)\n            {\n                TempData["Error"] = "Số tiền thu phải lớn hơn 0!";\n                return RedirectToAction(nameof(Details), new { id = kyHan.MaHopDong, returnUrl = returnUrl });\n            }\n\n            if (kyHan.TrangThai != 1)'
)

write_file(hd_path, hd)

# 3. BaoTriController (Client) Bug 12
bt_path = r'd:\DoAnCuNhan\RentalSystem\Controllers\BaoTriController.cs'
bt = read_file(bt_path)
bt = bt.replace(
    'phieu.DanhGiaSao = rating;',
    'if (phieu.TrangThai != 3)\n            {\n                TempData["Error"] = "Chỉ đánh giá được phiếu đã hoàn thành (sửa xong)!";\n                return RedirectToAction("MyTickets");\n            }\n\n            phieu.DanhGiaSao = rating;'
)
write_file(bt_path, bt)

# 4. HomeController (Admin) Bug 14
hc_path = r'd:\DoAnCuNhan\RentalSystem\Areas\Admin\Controllers\HomeController.cs'
hc = read_file(hc_path)
hc = hc.replace(
    '''var allCompletedOrders = _context.HopDongs
                .Where(h => h.TrangThai == 2)
                .ToList();''',
    '''var monthly = _context.HopDongs
                .Where(h => h.TrangThai == 2 && h.NgayBatDau >= DateTime.Now.AddMonths(-5))
                .GroupBy(h => new { h.NgayBatDau.Year, h.NgayBatDau.Month })
                .Select(g => new { g.Key.Year, g.Key.Month, Total = g.Sum(x => x.TongTien) })
                .ToList();'''
)

hc = hc.replace(
    '''var sum = allCompletedOrders
                    .Where(x => x.NgayBatDau.Month == d.Month && x.NgayBatDau.Year == d.Year)
                    .Sum(x => x.TongTien);
                    
                chartData.Add(sum);''',
    '''var monthData = monthly.FirstOrDefault(m => m.Year == d.Year && m.Month == d.Month);
                chartData.Add(monthData != null ? monthData.Total : 0);'''
)
write_file(hc_path, hc)
print('Done!')
