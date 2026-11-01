USE [RentalSystemDB];
GO

-- Sửa bảng VaiTros
UPDATE [dbo].[VaiTros] SET [TenVaiTro] = N'Admin' WHERE [MaVaiTro] = 1;
UPDATE [dbo].[VaiTros] SET [TenVaiTro] = N'KinhDoanh' WHERE [MaVaiTro] = 2;
UPDATE [dbo].[VaiTros] SET [TenVaiTro] = N'KyThuat' WHERE [MaVaiTro] = 3;
UPDATE [dbo].[VaiTros] SET [TenVaiTro] = N'KhachHang' WHERE [MaVaiTro] = 4;

-- Sửa bảng NguoiDungs
UPDATE [dbo].[NguoiDungs] 
SET [HoTen] = N'Quản Trị Viên', [DiaChi] = N'Trung tâm Hệ thống' 
WHERE [MaNguoiDung] = 1;

UPDATE [dbo].[NguoiDungs] 
SET [HoTen] = N'Nguyễn Văn An', [DiaChi] = N'123 Nguyễn Trãi, Q.1, TP.HCM' 
WHERE [MaNguoiDung] = 2;

-- Sửa bảng LoaiThietBis
UPDATE [dbo].[LoaiThietBis] SET [TenLoai] = N'Máy tính bàn' WHERE [MaLoai] = 1;
UPDATE [dbo].[LoaiThietBis] SET [TenLoai] = N'Máy lạnh' WHERE [MaLoai] = 2;
UPDATE [dbo].[LoaiThietBis] SET [TenLoai] = N'Máy in' WHERE [MaLoai] = 3;

-- Sửa bảng SanPhams
UPDATE [dbo].[SanPhams]
SET [TenSanPham] = N'Bộ PC Dell OptiPlex 7010',
    [CauHinh] = N'Intel Core i5-13500, 16GB RAM DDR5, SSD 512GB, Màn hình 24 inch FHD',
    [MoTa] = N'Máy tính bàn Dell OptiPlex 7010 dòng doanh nghiệp, thiết kế nhỏ gọn, bền bỉ, phù hợp cho văn phòng, phòng học, sự kiện hội nghị.'
WHERE [MaSanPham] = 1;

UPDATE [dbo].[SanPhams]
SET [TenSanPham] = N'Bộ PC HP ProDesk 400 G9',
    [CauHinh] = N'Intel Core i7-12700, 16GB RAM, SSD 256GB, Màn hình 22 inch',
    [MoTa] = N'PC HP ProDesk hiệu năng cao, dáng đứng tiết kiệm diện tích, lý tưởng cho thuê theo tháng cho doanh nghiệp vừa và nhỏ.'
WHERE [MaSanPham] = 2;

UPDATE [dbo].[SanPhams]
SET [TenSanPham] = N'Máy lạnh Daikin FTKZ35VVMV (1.5HP)',
    [CauHinh] = N'Inverter, 1.5 HP, Gas R-32, Làm lạnh nhanh, Chế độ Eco tiết kiệm điện',
    [MoTa] = N'Máy lạnh Daikin Inverter cao cấp, vận hành êm ái, phù hợp cho thuê phòng họp, văn phòng tạm, sự kiện ngoài trời có mái che.'
WHERE [MaSanPham] = 3;

UPDATE [dbo].[SanPhams]
SET [TenSanPham] = N'Máy lạnh tủ đứng LG APNQ48GT3E4 (5HP)',
    [CauHinh] = N'Inverter, 5 HP, 48.000 BTU, Làm lạnh diện tích lớn 60-80m²',
    [MoTa] = N'Máy lạnh tủ đứng công suất lớn LG, chuyên dùng cho thuê sự kiện, hội trường, showroom, nhà xưởng. Lắp đặt nhanh trong 30 phút.'
WHERE [MaSanPham] = 4;

UPDATE [dbo].[SanPhams]
SET [TenSanPham] = N'Máy in HP LaserJet Pro M404dn',
    [CauHinh] = N'In Laser trắng đen, tốc độ 40 trang/phút, In 2 mặt tự động, Kết nối LAN',
    [MoTa] = N'Máy in HP LaserJet tốc độ cao, bền bỉ, chi phí mực thấp. Lý tưởng cho thuê tại văn phòng dự án, phòng thi, hội thảo.'
WHERE [MaSanPham] = 5;

UPDATE [dbo].[SanPhams]
SET [TenSanPham] = N'Máy in màu Canon PIXMA G3020',
    [CauHinh] = N'In phun màu, In - Scan - Copy, Kết nối Wifi, Hệ thống mực liên tục',
    [MoTa] = N'Máy in phun màu Canon đa năng với hệ thống mực liên tục tiết kiệm. Phù hợp cho thuê in ấn tài liệu màu, poster nhỏ tại sự kiện.'
WHERE [MaSanPham] = 6;

-- Sửa bảng ThietBis
UPDATE [dbo].[ThietBis] SET [TinhTrangMay] = N'Mới 100%' WHERE [MaThietBi] IN (1, 4, 8, 11);
UPDATE [dbo].[ThietBis] SET [TinhTrangMay] = N'Mới 99%' WHERE [MaThietBi] = 2;
UPDATE [dbo].[ThietBis] SET [TinhTrangMay] = N'Mới 98%' WHERE [MaThietBi] = 3;
UPDATE [dbo].[ThietBis] SET [TinhTrangMay] = N'Mới 97%' WHERE [MaThietBi] = 5;
UPDATE [dbo].[ThietBis] SET [TinhTrangMay] = N'Hoạt động tốt' WHERE [MaThietBi] IN (6, 7);
UPDATE [dbo].[ThietBis] SET [TinhTrangMay] = N'Mới, mực đầy' WHERE [MaThietBi] IN (9, 10);
GO
