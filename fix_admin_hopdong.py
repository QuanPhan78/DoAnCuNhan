import re

path = r'd:\DoAnCuNhan\RentalSystem\Areas\Admin\Controllers\HopDongController.cs'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace in Create
old_create = '''            // Lưu số kỳ hạn vào GhiChu tạm để dùng khi Giao máy
            if (SoKyHan > 1)
            {
                hd.GhiChu = (string.IsNullOrEmpty(hd.GhiChu) ? "" : hd.GhiChu + " | ") + $"[SoKy:{SoKyHan}]";
            }'''
new_create = '''            hd.SoKyHan = SoKyHan > 0 ? SoKyHan : 1;'''
content = content.replace(old_create, new_create)

# Replace in UpdateStatus
old_updatestatus = '''                    // Đọc số kỳ từ GhiChu (nếu Admin đã chỉ định lúc tạo đơn)
                    int soKy = 1;
                    var ghiChu = hopDong.GhiChu ?? "";
                    var match = System.Text.RegularExpressions.Regex.Match(ghiChu, @"\[SoKy:(\d+)\]");
                    if (match.Success && int.TryParse(match.Groups[1].Value, out int parsedSoKy) && parsedSoKy > 0)
                    {
                        soKy = parsedSoKy;
                    }
                    else
                    {
                        // Nếu không chỉ định -> tự chia theo 30 ngày
                        var totalDays = (hopDong.NgayKetThuc - hopDong.NgayBatDau).TotalDays;
                        soKy = (int)Math.Ceiling(totalDays / 30.0);
                        if (soKy <= 0) soKy = 1;
                    }'''
new_updatestatus = '''                    int soKy = hopDong.SoKyHan > 0 ? hopDong.SoKyHan : 1;'''
content = content.replace(old_updatestatus, new_updatestatus)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed Admin HopDong')
