-- ===============================================================
-- KỊCH BẢN TẠO CƠ SỞ DỮ LIỆU: RentalSystemDB
-- Hệ thống Quản lý Cho thuê Thiết bị (RentalSystem)
-- Tương thích: Microsoft SQL Server 2012 / 2014 / 2016 / 2019 / 2022
-- ===============================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'RentalSystemDB')
BEGIN
    CREATE DATABASE [RentalSystemDB];
    PRINT N'Đã tạo cơ sở dữ liệu RentalSystemDB thành công.';
END
GO

USE [RentalSystemDB];
GO

-- 1. Bảng Vai Trò (__VaiTros)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'VaiTros')
BEGIN
    CREATE TABLE [dbo].[VaiTros] (
        [MaVaiTro] INT IDENTITY(1,1) NOT NULL,
        [TenVaiTro] NVARCHAR(50) NOT NULL,
        CONSTRAINT [PK_VaiTros] PRIMARY KEY CLUSTERED ([MaVaiTro] ASC)
    );
END
GO

-- 2. Bảng Người Dùng (NguoiDungs)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'NguoiDungs')
BEGIN
    CREATE TABLE [dbo].[NguoiDungs] (
        [MaNguoiDung] INT IDENTITY(1,1) NOT NULL,
        [MaVaiTro] INT NOT NULL,
        [HoTen] NVARCHAR(100) NOT NULL,
        [SoDienThoai] NVARCHAR(20) NOT NULL,
        [Email] NVARCHAR(MAX) NULL,
        [MatKhau] NVARCHAR(MAX) NULL,
        [CCCD] NVARCHAR(MAX) NULL,
        [DiaChi] NVARCHAR(MAX) NULL,
        [TrangThai] BIT NOT NULL DEFAULT 1,
        CONSTRAINT [PK_NguoiDungs] PRIMARY KEY CLUSTERED ([MaNguoiDung] ASC),
        CONSTRAINT [FK_NguoiDungs_VaiTros_MaVaiTro] FOREIGN KEY ([MaVaiTro]) REFERENCES [dbo].[VaiTros] ([MaVaiTro]) ON DELETE CASCADE
    );
END
GO

-- 3. Bảng Loại Thiết Bị (LoaiThietBis)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'LoaiThietBis')
BEGIN
    CREATE TABLE [dbo].[LoaiThietBis] (
        [MaLoai] INT IDENTITY(1,1) NOT NULL,
        [TenLoai] NVARCHAR(100) NOT NULL,
        CONSTRAINT [PK_LoaiThietBis] PRIMARY KEY CLUSTERED ([MaLoai] ASC)
    );
END
GO

-- 4. Bảng Sản Phẩm (SanPhams)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SanPhams')
BEGIN
    CREATE TABLE [dbo].[SanPhams] (
        [MaSanPham] INT IDENTITY(1,1) NOT NULL,
        [MaLoai] INT NOT NULL,
        [TenSanPham] NVARCHAR(255) NOT NULL,
        [CauHinh] NVARCHAR(MAX) NULL,
        [MoTa] NVARCHAR(MAX) NULL,
        [GiaThueNgay] DECIMAL(18, 2) NOT NULL,
        [TienCoc] DECIMAL(18, 2) NOT NULL,
        [HinhAnh] NVARCHAR(MAX) NULL,
        CONSTRAINT [PK_SanPhams] PRIMARY KEY CLUSTERED ([MaSanPham] ASC),
        CONSTRAINT [FK_SanPhams_LoaiThietBis_MaLoai] FOREIGN KEY ([MaLoai]) REFERENCES [dbo].[LoaiThietBis] ([MaLoai]) ON DELETE CASCADE
    );
END
GO

-- 5. Bảng Thiết Bị Vật Lý (ThietBis - phân biệt theo Serial)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ThietBis')
BEGIN
    CREATE TABLE [dbo].[ThietBis] (
        [MaThietBi] INT IDENTITY(1,1) NOT NULL,
        [MaSanPham] INT NOT NULL,
        [SoSerial] NVARCHAR(50) NOT NULL,
        [TinhTrangMay] NVARCHAR(MAX) NULL,
        [TrangThai] INT NOT NULL DEFAULT 0, -- 0: Sẵn sàng, 1: Đang thuê, 2: Bảo trì, 3: Giữ chỗ
        CONSTRAINT [PK_ThietBis] PRIMARY KEY CLUSTERED ([MaThietBi] ASC),
        CONSTRAINT [FK_ThietBis_SanPhams_MaSanPham] FOREIGN KEY ([MaSanPham]) REFERENCES [dbo].[SanPhams] ([MaSanPham]) ON DELETE CASCADE
    );
END
GO

-- 6. Bảng Khuyến Mãi (KhuyenMais)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'KhuyenMais')
BEGIN
    CREATE TABLE [dbo].[KhuyenMais] (
        [MaKhuyenMai] INT IDENTITY(1,1) NOT NULL,
        [MaCode] NVARCHAR(MAX) NOT NULL,
        [PhanTramGiam] INT NOT NULL,
        [KichHoat] BIT NOT NULL DEFAULT 1,
        CONSTRAINT [PK_KhuyenMais] PRIMARY KEY CLUSTERED ([MaKhuyenMai] ASC)
    );
END
GO

-- 7. Bảng Hợp Đồng (HopDongs)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'HopDongs')
BEGIN
    CREATE TABLE [dbo].[HopDongs] (
        [MaHopDong] INT IDENTITY(1,1) NOT NULL,
        [MaKhachHang] INT NOT NULL,
        [MaNhanVien] INT NOT NULL,
        [MaKhuyenMai] INT NULL,
        [NgayBatDau] DATETIME2 NOT NULL,
        [NgayKetThuc] DATETIME2 NOT NULL,
        [TienDaCoc] DECIMAL(18, 2) NOT NULL,
        [TongTien] DECIMAL(18, 2) NOT NULL,
        [TrangThai] INT NOT NULL, -- 0: Chờ duyệt, 1: Đang hiệu lực, 2: Đã kết thúc, 3: Đã hủy
        [SoKyHan] INT NOT NULL DEFAULT 1,
        [AnhCMND] NVARCHAR(MAX) NULL,
        [ChuKyKhachHang] NVARCHAR(MAX) NULL,
        [ChuKyNhanVien] NVARCHAR(MAX) NULL,
        [NgayKy] DATETIME2 NULL,
        [TrangThaiThanhToan] INT NOT NULL DEFAULT 0, -- 0: Chưa thanh toán, 1: Còn nợ, 2: Đã thanh toán đủ
        [GhiChu] NVARCHAR(MAX) NULL,
        CONSTRAINT [PK_HopDongs] PRIMARY KEY CLUSTERED ([MaHopDong] ASC),
        CONSTRAINT [FK_HopDongs_NguoiDungs_MaKhachHang] FOREIGN KEY ([MaKhachHang]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung]),
        CONSTRAINT [FK_HopDongs_NguoiDungs_MaNhanVien] FOREIGN KEY ([MaNhanVien]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung])
    );
END
GO

-- 8. Bảng Chi Tiết Hợp Đồng (ChiTietHopDongs)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ChiTietHopDongs')
BEGIN
    CREATE TABLE [dbo].[ChiTietHopDongs] (
        [MaHopDong] INT NOT NULL,
        [MaThietBi] INT NOT NULL,
        [GiaChotThu] DECIMAL(18, 2) NOT NULL,
        CONSTRAINT [PK_ChiTietHopDongs] PRIMARY KEY CLUSTERED ([MaHopDong] ASC, [MaThietBi] ASC),
        CONSTRAINT [FK_ChiTietHopDongs_HopDongs_MaHopDong] FOREIGN KEY ([MaHopDong]) REFERENCES [dbo].[HopDongs] ([MaHopDong]) ON DELETE CASCADE,
        CONSTRAINT [FK_ChiTietHopDongs_ThietBis_MaThietBi] FOREIGN KEY ([MaThietBi]) REFERENCES [dbo].[ThietBis] ([MaThietBi]) ON DELETE CASCADE
    );
END
GO

-- 9. Bảng Kỳ Hạn Thanh Toán (KyHanThanhToans)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'KyHanThanhToans')
BEGIN
    CREATE TABLE [dbo].[KyHanThanhToans] (
        [MaKyHan] INT IDENTITY(1,1) NOT NULL,
        [MaHopDong] INT NOT NULL,
        [SoKyHan] INT NOT NULL,
        [NgayDenHan] DATETIME2 NOT NULL,
        [SoTienPhai] DECIMAL(18, 2) NOT NULL,
        [SoTienDaTra] DECIMAL(18, 2) NOT NULL,
        [TrangThai] INT NOT NULL, -- 0: Chưa trả, 1: Đã trả, 2: Trễ hạn
        [NgayThanhToan] DATETIME2 NULL,
        [GhiChu] NVARCHAR(MAX) NULL,
        CONSTRAINT [PK_KyHanThanhToans] PRIMARY KEY CLUSTERED ([MaKyHan] ASC),
        CONSTRAINT [FK_KyHanThanhToans_HopDongs_MaHopDong] FOREIGN KEY ([MaHopDong]) REFERENCES [dbo].[HopDongs] ([MaHopDong]) ON DELETE CASCADE
    );
END
GO

-- 10. Bảng Phiếu Thu (PhieuThus)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PhieuThus')
BEGIN
    CREATE TABLE [dbo].[PhieuThus] (
        [MaPhieuThu] INT IDENTITY(1,1) NOT NULL,
        [MaHopDong] INT NOT NULL,
        [LoaiPhieu] INT NOT NULL, -- 0: Thu thuê, 1: Thu cọc, 2: Thu phí BT
        [SoTien] DECIMAL(18, 2) NOT NULL,
        [NgayGiaoDich] DATETIME2 NOT NULL,
        [HinhThucThanhToan] INT NOT NULL DEFAULT 0, -- 0: Tiền mặt, 1: Chuyển khoản, 2: Khác
        [GhiChu] NVARCHAR(MAX) NULL,
        [MaKyHan] INT NULL,
        CONSTRAINT [PK_PhieuThus] PRIMARY KEY CLUSTERED ([MaPhieuThu] ASC),
        CONSTRAINT [FK_PhieuThus_HopDongs_MaHopDong] FOREIGN KEY ([MaHopDong]) REFERENCES [dbo].[HopDongs] ([MaHopDong]) ON DELETE CASCADE
    );
END
GO

-- 11. Bảng Phiếu Bảo Trì (PhieuBaoTris)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PhieuBaoTris')
BEGIN
    CREATE TABLE [dbo].[PhieuBaoTris] (
        [MaPhieu] INT IDENTITY(1,1) NOT NULL,
        [MaHopDong] INT NOT NULL,
        [MaThietBi] INT NOT NULL,
        [MaKyThuatVien] INT NULL,
        [MoTaLoi] NVARCHAR(MAX) NOT NULL,
        [NgayBaoLoi] DATETIME2 NOT NULL,
        [GhiChuSuaChua] NVARCHAR(MAX) NULL,
        [PhiDenBu] DECIMAL(18, 2) NOT NULL DEFAULT 0,
        [DanhGiaSao] INT NULL,
        [TrangThai] INT NOT NULL DEFAULT 0,
        CONSTRAINT [PK_PhieuBaoTris] PRIMARY KEY CLUSTERED ([MaPhieu] ASC),
        CONSTRAINT [FK_PhieuBaoTris_HopDongs_MaHopDong] FOREIGN KEY ([MaHopDong]) REFERENCES [dbo].[HopDongs] ([MaHopDong]) ON DELETE CASCADE,
        CONSTRAINT [FK_PhieuBaoTris_ThietBis_MaThietBi] FOREIGN KEY ([MaThietBi]) REFERENCES [dbo].[ThietBis] ([MaThietBi]) ON DELETE CASCADE,
        CONSTRAINT [FK_PhieuBaoTris_NguoiDungs_MaKyThuatVien] FOREIGN KEY ([MaKyThuatVien]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung])
    );
END
GO

-- 12. Bảng Lịch Sử Thiết Bị (LichSuThietBis)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'LichSuThietBis')
BEGIN
    CREATE TABLE [dbo].[LichSuThietBis] (
        [MaLichSu] INT IDENTITY(1,1) NOT NULL,
        [MaThietBi] INT NOT NULL,
        [HanhDong] NVARCHAR(MAX) NOT NULL,
        [ThoiGian] DATETIME2 NOT NULL,
        [MaNguoiThucHien] INT NOT NULL,
        CONSTRAINT [PK_LichSuThietBis] PRIMARY KEY CLUSTERED ([MaLichSu] ASC),
        CONSTRAINT [FK_LichSuThietBis_ThietBis_MaThietBi] FOREIGN KEY ([MaThietBi]) REFERENCES [dbo].[ThietBis] ([MaThietBi]) ON DELETE CASCADE,
        CONSTRAINT [FK_LichSuThietBis_NguoiDungs_MaNguoiThucHien] FOREIGN KEY ([MaNguoiThucHien]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung])
    );
END
GO

-- 13. Bảng Lịch Sử EF Migrations (__EFMigrationsHistory)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '__EFMigrationsHistory')
BEGIN
    CREATE TABLE [dbo].[__EFMigrationsHistory] (
        [MigrationId] NVARCHAR(150) NOT NULL,
        [ProductVersion] NVARCHAR(32) NOT NULL,
        CONSTRAINT [PK___EFMigrationsHistory] PRIMARY KEY CLUSTERED ([MigrationId] ASC)
    );

    INSERT INTO [dbo].[__EFMigrationsHistory] ([MigrationId], [ProductVersion]) VALUES
    (N'20260904160944_InitialCreate', N'9.0.0'),
    (N'20260906185643_AddMoTaSanPham', N'9.0.0'),
    (N'20260907140326_AddHopDongOnlineAndTraGop', N'9.0.0'),
    (N'20260918151713_AddPaymentMethodToPhieuThu', N'9.0.0'),
    (N'20260921101803_AddSoKyHanToHopDong', N'9.0.0');
END
GO

-- ===============================================================
-- DỮ LIỆU MẪU BAN ĐẦU (SEED DATA - DbInitializer)
-- ===============================================================

-- 1. Nạp 4 Vai Trò
IF NOT EXISTS (SELECT 1 FROM [dbo].[VaiTros])
BEGIN
    SET IDENTITY_INSERT [dbo].[VaiTros] ON;
    INSERT INTO [dbo].[VaiTros] ([MaVaiTro], [TenVaiTro]) VALUES
    (1, N'Admin'),
    (2, N'KinhDoanh'),
    (3, N'KyThuat'),
    (4, N'KhachHang');
    SET IDENTITY_INSERT [dbo].[VaiTros] OFF;
END
GO

-- 2. Nạp Tài Khoản Mẫu (Admin & Khách hàng)
IF NOT EXISTS (SELECT 1 FROM [dbo].[NguoiDungs])
BEGIN
    SET IDENTITY_INSERT [dbo].[NguoiDungs] ON;
    INSERT INTO [dbo].[NguoiDungs] ([MaNguoiDung], [MaVaiTro], [HoTen], [SoDienThoai], [Email], [MatKhau], [CCCD], [DiaChi], [TrangThai]) VALUES
    (1, 1, N'Quản Trị Viên', N'0123456789', N'admin@rentalsystem.com', N'Admin@123', N'000000000000', N'Trung tâm Hệ thống', 1),
    (2, 4, N'Nguyễn Văn An', N'0987654321', N'khach@gmail.com', N'123456', N'079200001234', N'123 Nguyễn Trãi, Q.1, TP.HCM', 1);
    SET IDENTITY_INSERT [dbo].[NguoiDungs] OFF;
END
GO

-- 3. Nạp Danh Mục Thiết Bị
IF NOT EXISTS (SELECT 1 FROM [dbo].[LoaiThietBis])
BEGIN
    SET IDENTITY_INSERT [dbo].[LoaiThietBis] ON;
    INSERT INTO [dbo].[LoaiThietBis] ([MaLoai], [TenLoai]) VALUES
    (1, N'Máy tính bàn'),
    (2, N'Máy lạnh'),
    (3, N'Máy in');
    SET IDENTITY_INSERT [dbo].[LoaiThietBis] OFF;
END
GO

-- 4. Nạp 6 Sản Phẩm Mẫu
IF NOT EXISTS (SELECT 1 FROM [dbo].[SanPhams])
BEGIN
    SET IDENTITY_INSERT [dbo].[SanPhams] ON;
    INSERT INTO [dbo].[SanPhams] ([MaSanPham], [MaLoai], [TenSanPham], [CauHinh], [MoTa], [GiaThueNgay], [TienCoc], [HinhAnh]) VALUES
    (1, 1, N'Bộ PC Dell OptiPlex 7010', N'Intel Core i5-13500, 16GB RAM DDR5, SSD 512GB, Màn hình 24 inch FHD', N'Máy tính bàn Dell OptiPlex 7010 dòng doanh nghiệp, thiết kế nhỏ gọn, bền bỉ, phù hợp cho văn phòng, phòng học, sự kiện hội nghị.', 150000, 8000000, N'/images/sanpham/may-tinh.png'),
    (2, 1, N'Bộ PC HP ProDesk 400 G9', N'Intel Core i7-12700, 16GB RAM, SSD 256GB, Màn hình 22 inch', N'PC HP ProDesk hiệu năng cao, dáng đứng tiết kiệm diện tích, lý tưởng cho thuê theo tháng cho doanh nghiệp vừa và nhỏ.', 180000, 10000000, N'/images/sanpham/may-tinh.png'),
    (3, 2, N'Máy lạnh Daikin FTKZ35VVMV (1.5HP)', N'Inverter, 1.5 HP, Gas R-32, Làm lạnh nhanh, Chế độ Eco tiết kiệm điện', N'Máy lạnh Daikin Inverter cao cấp, vận hành êm ái, phù hợp cho thuê phòng họp, văn phòng tạm, sự kiện ngoài trời có mái che.', 200000, 5000000, N'/images/sanpham/may-lanh.png'),
    (4, 2, N'Máy lạnh tủ đứng LG APNQ48GT3E4 (5HP)', N'Inverter, 5 HP, 48.000 BTU, Làm lạnh diện tích lớn 60-80m²', N'Máy lạnh tủ đứng công suất lớn LG, chuyên dùng cho thuê sự kiện, hội trường, showroom, nhà xưởng. Lắp đặt nhanh trong 30 phút.', 500000, 15000000, N'/images/sanpham/may-lanh.png'),
    (5, 3, N'Máy in HP LaserJet Pro M404dn', N'In Laser trắng đen, tốc độ 40 trang/phút, In 2 mặt tự động, Kết nối LAN', N'Máy in HP LaserJet tốc độ cao, bền bỉ, chi phí mực thấp. Lý tưởng cho thuê tại văn phòng dự án, phòng thi, hội thảo.', 100000, 3000000, N'/images/sanpham/may-in.png'),
    (6, 3, N'Máy in màu Canon PIXMA G3020', N'In phun màu, In - Scan - Copy, Kết nối Wifi, Hệ thống mực liên tục', N'Máy in phun màu Canon đa năng với hệ thống mực liên tục tiết kiệm. Phù hợp cho thuê in ấn tài liệu màu, poster nhỏ tại sự kiện.', 80000, 2000000, N'/images/sanpham/may-in.png');
    SET IDENTITY_INSERT [dbo].[SanPhams] OFF;
END
GO

-- 5. Nạp Máy Vật Lý (Số Serial)
IF NOT EXISTS (SELECT 1 FROM [dbo].[ThietBis])
BEGIN
    SET IDENTITY_INSERT [dbo].[ThietBis] ON;
    INSERT INTO [dbo].[ThietBis] ([MaThietBi], [MaSanPham], [SoSerial], [TinhTrangMay], [TrangThai]) VALUES
    (1, 1, N'DELL-OPT-001', N'Mới 100%', 0),
    (2, 1, N'DELL-OPT-002', N'Mới 99%', 0),
    (3, 1, N'DELL-OPT-003', N'Mới 98%', 0),
    (4, 2, N'HP-PRO-001', N'Mới 100%', 0),
    (5, 2, N'HP-PRO-002', N'Mới 97%', 0),
    (6, 3, N'DK-15HP-001', N'Hoạt động tốt', 0),
    (7, 3, N'DK-15HP-002', N'Hoạt động tốt', 0),
    (8, 4, N'LG-5HP-001', N'Mới 100%', 0),
    (9, 5, N'HP-M404-001', N'Mới, mực đầy', 0),
    (10, 5, N'HP-M404-002', N'Mới, mực đầy', 0),
    (11, 6, N'CANON-G3020-001', N'Mới 100%', 0);
    SET IDENTITY_INSERT [dbo].[ThietBis] OFF;
END
GO

PRINT N'Hoàn tất thiết lập cơ sở dữ liệu RentalSystemDB và nạp dữ liệu mẫu thành công!';
GO
