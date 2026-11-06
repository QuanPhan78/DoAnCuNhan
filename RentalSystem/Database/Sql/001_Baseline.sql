-- Run as one sqlcmd session with -b against an empty database.
SET XACT_ABORT ON;
IF EXISTS (SELECT 1 FROM sys.tables WHERE is_ms_shipped = 0)
    THROW 51000, N'Baseline 001 requires an empty database.', 1;
BEGIN TRANSACTION;
GO

CREATE TABLE [dbo].[KhuyenMais] (
    [MaKhuyenMai] int NOT NULL IDENTITY,
    [MaCode] nvarchar(50) NOT NULL,
    [PhanTramGiam] int NOT NULL,
    [NgayBatDau] datetime2 NOT NULL,
    [NgayKetThuc] datetime2 NOT NULL,
    [SoLuong] int NOT NULL,
    [KichHoat] bit NOT NULL,
    [MoTa] nvarchar(max) NULL,
    CONSTRAINT [PK_KhuyenMais] PRIMARY KEY ([MaKhuyenMai])
);
GO


CREATE TABLE [dbo].[LoaiThietBis] (
    [MaLoai] int NOT NULL IDENTITY,
    [TenLoai] nvarchar(100) NOT NULL,
    CONSTRAINT [PK_LoaiThietBis] PRIMARY KEY ([MaLoai])
);
GO


CREATE TABLE [dbo].[VaiTros] (
    [MaVaiTro] int NOT NULL IDENTITY,
    [TenVaiTro] nvarchar(50) NOT NULL,
    CONSTRAINT [PK_VaiTros] PRIMARY KEY ([MaVaiTro])
);
GO


CREATE TABLE [dbo].[SanPhams] (
    [MaSanPham] int NOT NULL IDENTITY,
    [MaLoai] int NOT NULL,
    [TenSanPham] nvarchar(255) NOT NULL,
    [CauHinh] nvarchar(max) NOT NULL,
    [MoTa] nvarchar(max) NOT NULL,
    [GiaThueNgay] decimal(18,2) NOT NULL,
    [TienCoc] decimal(18,2) NOT NULL,
    [HinhAnh] nvarchar(max) NOT NULL,
    CONSTRAINT [PK_SanPhams] PRIMARY KEY ([MaSanPham]),
    CONSTRAINT [FK_SanPhams_LoaiThietBis_MaLoai] FOREIGN KEY ([MaLoai]) REFERENCES [dbo].[LoaiThietBis] ([MaLoai]) ON DELETE CASCADE
);
GO


CREATE TABLE [dbo].[NguoiDungs] (
    [MaNguoiDung] int NOT NULL IDENTITY,
    [MaVaiTro] int NOT NULL,
    [HoTen] nvarchar(100) NOT NULL,
    [SoDienThoai] nvarchar(20) NOT NULL,
    [Email] nvarchar(max) NOT NULL,
    [MatKhau] nvarchar(max) NOT NULL,
    [CCCD] nvarchar(max) NOT NULL,
    [DiaChi] nvarchar(max) NOT NULL,
    [TrangThai] bit NOT NULL,
    CONSTRAINT [PK_NguoiDungs] PRIMARY KEY ([MaNguoiDung]),
    CONSTRAINT [FK_NguoiDungs_VaiTros_MaVaiTro] FOREIGN KEY ([MaVaiTro]) REFERENCES [dbo].[VaiTros] ([MaVaiTro]) ON DELETE CASCADE
);
GO


CREATE TABLE [dbo].[ThietBis] (
    [MaThietBi] int NOT NULL IDENTITY,
    [MaSanPham] int NOT NULL,
    [SoSerial] nvarchar(50) NOT NULL,
    [TinhTrangMay] nvarchar(max) NOT NULL,
    [TrangThai] int NOT NULL,
    CONSTRAINT [PK_ThietBis] PRIMARY KEY ([MaThietBi]),
    CONSTRAINT [FK_ThietBis_SanPhams_MaSanPham] FOREIGN KEY ([MaSanPham]) REFERENCES [dbo].[SanPhams] ([MaSanPham]) ON DELETE CASCADE
);
GO


CREATE TABLE [dbo].[HopDongs] (
    [MaHopDong] int NOT NULL IDENTITY,
    [MaKhachHang] int NOT NULL,
    [MaNhanVien] int NOT NULL,
    [MaKhuyenMai] int NULL,
    [NgayBatDau] datetime2 NOT NULL,
    [NgayKetThuc] datetime2 NOT NULL,
    [TienDaCoc] decimal(18,2) NOT NULL,
    [TongTien] decimal(18,2) NOT NULL,
    [TrangThai] int NOT NULL,
    [SoKyHan] int NOT NULL,
    [AnhCCCD_Truoc] nvarchar(max) NULL,
    [AnhCCCD_Sau] nvarchar(max) NULL,
    [ChuKyKhachHang] nvarchar(max) NOT NULL,
    [ChuKyNhanVien] nvarchar(max) NOT NULL,
    [NgayKy] datetime2 NULL,
    [TrangThaiThanhToan] int NOT NULL,
    [GhiChu] nvarchar(max) NOT NULL,
    [TrangThaiHoanCoc] int NOT NULL,
    [TienCocThucHoan] decimal(18,2) NULL,
    [NgayHoanCoc] datetime2 NULL,
    [GhiChuHoanCoc] nvarchar(max) NULL,
    [YeuCauGiaHan] bit NOT NULL,
    [SoNgayGiaHan] int NULL,
    [TrangThaiGiaHan] int NULL,
    [LyDoGiaHan] nvarchar(max) NULL,
    [YeuCauHuy] bit NOT NULL,
    [LyDoHuy] nvarchar(max) NULL,
    [NgayYeuCauHuy] datetime2 NULL,
    [HanChotKy] datetime2 NULL,
    [TienTraThua] decimal(18,2) NOT NULL,
    [TienGiamTruBaoTri] decimal(18,2) NOT NULL,
    [TienCocBaoDamMay] decimal(18,2) NOT NULL,
    [TienThueTraTruoc] decimal(18,2) NOT NULL,
    CONSTRAINT [PK_HopDongs] PRIMARY KEY ([MaHopDong]),
    CONSTRAINT [FK_HopDongs_KhuyenMais_MaKhuyenMai] FOREIGN KEY ([MaKhuyenMai]) REFERENCES [dbo].[KhuyenMais] ([MaKhuyenMai]) ON DELETE SET NULL,
    CONSTRAINT [FK_HopDongs_NguoiDungs_MaKhachHang] FOREIGN KEY ([MaKhachHang]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung]) ON DELETE NO ACTION,
    CONSTRAINT [FK_HopDongs_NguoiDungs_MaNhanVien] FOREIGN KEY ([MaNhanVien]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung]) ON DELETE NO ACTION
);
GO


CREATE TABLE [dbo].[ThongBaos] (
    [MaThongBao] int NOT NULL IDENTITY,
    [MaNguoiDung] int NOT NULL,
    [TieuDe] nvarchar(255) NOT NULL,
    [NoiDung] nvarchar(max) NOT NULL,
    [NgayTao] datetime2 NOT NULL,
    [DaDoc] bit NOT NULL,
    [LoaiThongBao] nvarchar(max) NULL,
    [LienKet] nvarchar(max) NULL,
    CONSTRAINT [PK_ThongBaos] PRIMARY KEY ([MaThongBao]),
    CONSTRAINT [FK_ThongBaos_NguoiDungs_MaNguoiDung] FOREIGN KEY ([MaNguoiDung]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung]) ON DELETE CASCADE
);
GO


CREATE TABLE [dbo].[LichSuThietBis] (
    [MaLichSu] int NOT NULL IDENTITY,
    [MaThietBi] int NOT NULL,
    [HanhDong] nvarchar(max) NOT NULL,
    [ThoiGian] datetime2 NOT NULL,
    [MaNguoiThucHien] int NULL,
    [GhiChu] nvarchar(max) NULL,
    CONSTRAINT [PK_LichSuThietBis] PRIMARY KEY ([MaLichSu]),
    CONSTRAINT [FK_LichSuThietBis_NguoiDungs_MaNguoiThucHien] FOREIGN KEY ([MaNguoiThucHien]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung]) ON DELETE NO ACTION,
    CONSTRAINT [FK_LichSuThietBis_ThietBis_MaThietBi] FOREIGN KEY ([MaThietBi]) REFERENCES [dbo].[ThietBis] ([MaThietBi]) ON DELETE CASCADE
);
GO


CREATE TABLE [dbo].[BienBanBanGiaos] (
    [MaBienBan] int NOT NULL IDENTITY,
    [MaHopDong] int NOT NULL,
    [LoaiBienBan] int NOT NULL,
    [NgayLap] datetime2 NOT NULL,
    [MaNhanVienLap] int NOT NULL,
    [PhuKienKemTheo] nvarchar(max) NULL,
    [TinhTrangNgoaiQuan] nvarchar(max) NULL,
    [HinhAnh1] nvarchar(max) NULL,
    [HinhAnh2] nvarchar(max) NULL,
    [HinhAnh3] nvarchar(max) NULL,
    [HinhAnh4] nvarchar(max) NULL,
    [ChuKyXacNhan] nvarchar(max) NULL,
    [GhiChu] nvarchar(max) NULL,
    CONSTRAINT [PK_BienBanBanGiaos] PRIMARY KEY ([MaBienBan]),
    CONSTRAINT [FK_BienBanBanGiaos_HopDongs_MaHopDong] FOREIGN KEY ([MaHopDong]) REFERENCES [dbo].[HopDongs] ([MaHopDong]) ON DELETE CASCADE,
    CONSTRAINT [FK_BienBanBanGiaos_NguoiDungs_MaNhanVienLap] FOREIGN KEY ([MaNhanVienLap]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung]) ON DELETE NO ACTION
);
GO


CREATE TABLE [dbo].[ChiTietHopDongs] (
    [MaHopDong] int NOT NULL,
    [MaThietBi] int NOT NULL,
    [GiaChotThu] decimal(18,2) NOT NULL,
    CONSTRAINT [PK_ChiTietHopDongs] PRIMARY KEY ([MaHopDong], [MaThietBi]),
    CONSTRAINT [FK_ChiTietHopDongs_HopDongs_MaHopDong] FOREIGN KEY ([MaHopDong]) REFERENCES [dbo].[HopDongs] ([MaHopDong]) ON DELETE CASCADE,
    CONSTRAINT [FK_ChiTietHopDongs_ThietBis_MaThietBi] FOREIGN KEY ([MaThietBi]) REFERENCES [dbo].[ThietBis] ([MaThietBi]) ON DELETE CASCADE
);
GO


CREATE TABLE [dbo].[KyHanThanhToans] (
    [MaKyHan] int NOT NULL IDENTITY,
    [MaHopDong] int NOT NULL,
    [SoKyHan] int NOT NULL,
    [NgayDenHan] datetime2 NOT NULL,
    [SoTienPhai] decimal(18,2) NOT NULL,
    [SoTienDaTra] decimal(18,2) NOT NULL,
    [TrangThai] int NOT NULL,
    [NgayThanhToan] datetime2 NULL,
    [GhiChu] nvarchar(max) NOT NULL,
    [MaGiaoDichChuyenKhoan] nvarchar(max) NULL,
    [HinhAnhBienLai] nvarchar(max) NULL,
    [TrangThaiXacNhan] int NOT NULL,
    [NgayGuiBienLai] datetime2 NULL,
    [PhiPhatTreHan] decimal(18,2) NOT NULL,
    [TienPhat] decimal(18,2) NOT NULL,
    [SoNgayTreHan] int NOT NULL,
    [NhomTuoiNo] int NOT NULL,
    [NgayHenTraTiepTheo] datetime2 NULL,
    [GhiChuTraThieu] nvarchar(max) NULL,
    CONSTRAINT [PK_KyHanThanhToans] PRIMARY KEY ([MaKyHan]),
    CONSTRAINT [FK_KyHanThanhToans_HopDongs_MaHopDong] FOREIGN KEY ([MaHopDong]) REFERENCES [dbo].[HopDongs] ([MaHopDong]) ON DELETE CASCADE
);
GO


CREATE TABLE [dbo].[PhieuBaoTris] (
    [MaPhieu] int NOT NULL IDENTITY,
    [MaHopDong] int NULL,
    [MaThietBi] int NOT NULL,
    [MaKyThuatVien] int NULL,
    [MoTaLoi] nvarchar(max) NOT NULL,
    [NgayBaoLoi] datetime2 NOT NULL,
    [GhiChuSuaChua] nvarchar(max) NOT NULL,
    [PhiDenBu] decimal(18,2) NOT NULL,
    [DanhGiaSao] int NULL,
    [TrangThai] int NOT NULL,
    [ChiPhiSuaChua] decimal(18,2) NULL,
    [HinhAnhLoi] nvarchar(max) NULL,
    [VideoLoi] nvarchar(max) NULL,
    [LoaiTrachNhiem] int NULL,
    [NguyenNhan] nvarchar(max) NULL,
    [LinhKienThayThe] nvarchar(max) NULL,
    [DaGhiNhanCongNo] bit NOT NULL,
    [MucDoKhanCap] int NULL,
    [HanHoanThanh] datetime2 NULL,
    [NgayHoanThanh] datetime2 NULL,
    [YKienPhanHoi] nvarchar(max) NULL,
    [DaNghiemThu] bit NOT NULL,
    [NgayNghiemThu] datetime2 NULL,
    [TamDungTinhTien] bit NOT NULL,
    [NgayBatDauBaoTri] datetime2 NULL,
    [NgayKetThucBaoTri] datetime2 NULL,
    [SoNgayTamDung] int NULL,
    [TienGiamTru] decimal(18,2) NULL,
    [DaTruTien] bit NOT NULL,
    CONSTRAINT [PK_PhieuBaoTris] PRIMARY KEY ([MaPhieu]),
    CONSTRAINT [FK_PhieuBaoTris_HopDongs_MaHopDong] FOREIGN KEY ([MaHopDong]) REFERENCES [dbo].[HopDongs] ([MaHopDong]) ON DELETE SET NULL,
    CONSTRAINT [FK_PhieuBaoTris_NguoiDungs_MaKyThuatVien] FOREIGN KEY ([MaKyThuatVien]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung]) ON DELETE NO ACTION,
    CONSTRAINT [FK_PhieuBaoTris_ThietBis_MaThietBi] FOREIGN KEY ([MaThietBi]) REFERENCES [dbo].[ThietBis] ([MaThietBi]) ON DELETE CASCADE
);
GO


CREATE TABLE [dbo].[PhieuChis] (
    [MaPhieuChi] int NOT NULL IDENTITY,
    [MaHopDong] int NOT NULL,
    [LoaiChi] int NOT NULL,
    [SoTien] decimal(18,2) NOT NULL,
    [NgayChi] datetime2 NOT NULL,
    [HinhThucChi] int NOT NULL,
    [MaNhanVienChi] int NOT NULL,
    [MaGiaoDichNganHang] nvarchar(max) NULL,
    [GhiChu] nvarchar(max) NULL,
    CONSTRAINT [PK_PhieuChis] PRIMARY KEY ([MaPhieuChi]),
    CONSTRAINT [FK_PhieuChis_HopDongs_MaHopDong] FOREIGN KEY ([MaHopDong]) REFERENCES [dbo].[HopDongs] ([MaHopDong]) ON DELETE CASCADE,
    CONSTRAINT [FK_PhieuChis_NguoiDungs_MaNhanVienChi] FOREIGN KEY ([MaNhanVienChi]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung]) ON DELETE NO ACTION
);
GO


CREATE TABLE [dbo].[YeuCauGiaHans] (
    [MaYeuCau] int NOT NULL IDENTITY,
    [MaHopDong] int NOT NULL,
    [SoNgayGiaHan] int NOT NULL,
    [LyDo] nvarchar(max) NULL,
    [NgayYeuCau] datetime2 NOT NULL,
    [TrangThai] int NOT NULL,
    [NgayDuyet] datetime2 NULL,
    [MaNguoiDuyet] int NULL,
    [ChiPhiPhatSinh] decimal(18,2) NOT NULL,
    [GhiChuAdmin] nvarchar(max) NULL,
    CONSTRAINT [PK_YeuCauGiaHans] PRIMARY KEY ([MaYeuCau]),
    CONSTRAINT [FK_YeuCauGiaHans_HopDongs_MaHopDong] FOREIGN KEY ([MaHopDong]) REFERENCES [dbo].[HopDongs] ([MaHopDong]) ON DELETE CASCADE,
    CONSTRAINT [FK_YeuCauGiaHans_NguoiDungs_MaNguoiDuyet] FOREIGN KEY ([MaNguoiDuyet]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung]) ON DELETE NO ACTION
);
GO


CREATE TABLE [dbo].[LichSuNhacNos] (
    [MaLichSuNhacNo] int NOT NULL IDENTITY,
    [MaHopDong] int NOT NULL,
    [MaKyHan] int NULL,
    [NgayNhac] datetime2 NOT NULL,
    [HinhThucNhac] nvarchar(max) NOT NULL,
    [NoiDung] nvarchar(max) NULL,
    [NguoiGuiId] int NULL,
    [SoTienNhac] decimal(18,2) NOT NULL,
    [LanNhacThu] int NOT NULL,
    CONSTRAINT [PK_LichSuNhacNos] PRIMARY KEY ([MaLichSuNhacNo]),
    CONSTRAINT [FK_LichSuNhacNos_HopDongs_MaHopDong] FOREIGN KEY ([MaHopDong]) REFERENCES [dbo].[HopDongs] ([MaHopDong]) ON DELETE NO ACTION,
    CONSTRAINT [FK_LichSuNhacNos_KyHanThanhToans_MaKyHan] FOREIGN KEY ([MaKyHan]) REFERENCES [dbo].[KyHanThanhToans] ([MaKyHan]) ON DELETE NO ACTION,
    CONSTRAINT [FK_LichSuNhacNos_NguoiDungs_NguoiGuiId] FOREIGN KEY ([NguoiGuiId]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung]) ON DELETE NO ACTION
);
GO


CREATE TABLE [dbo].[PhieuThus] (
    [MaPhieuThu] int NOT NULL IDENTITY,
    [MaHopDong] int NOT NULL,
    [LoaiPhieu] int NOT NULL,
    [SoTien] decimal(18,2) NOT NULL,
    [NgayGiaoDich] datetime2 NOT NULL,
    [HinhThucThanhToan] int NOT NULL,
    [GhiChu] nvarchar(max) NOT NULL,
    [MaKyHan] int NULL,
    [MaNhanVienThu] int NULL,
    [MaGiaoDichNganHang] nvarchar(max) NULL,
    [NganHangNhan] nvarchar(max) NULL,
    [DaHuy] bit NOT NULL,
    [LyDoHuy] nvarchar(max) NULL,
    [NgayHuy] datetime2 NULL,
    CONSTRAINT [PK_PhieuThus] PRIMARY KEY ([MaPhieuThu]),
    CONSTRAINT [FK_PhieuThus_HopDongs_MaHopDong] FOREIGN KEY ([MaHopDong]) REFERENCES [dbo].[HopDongs] ([MaHopDong]) ON DELETE CASCADE,
    CONSTRAINT [FK_PhieuThus_KyHanThanhToans_MaKyHan] FOREIGN KEY ([MaKyHan]) REFERENCES [dbo].[KyHanThanhToans] ([MaKyHan]) ON DELETE NO ACTION,
    CONSTRAINT [FK_PhieuThus_NguoiDungs_MaNhanVienThu] FOREIGN KEY ([MaNhanVienThu]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung]) ON DELETE NO ACTION
);
GO


CREATE TABLE [dbo].[PhanCongCongViecs] (
    [MaPhanCong] int NOT NULL IDENTITY,
    [MaNhanVien] int NOT NULL,
    [TieuDe] nvarchar(255) NOT NULL,
    [NoiDung] nvarchar(max) NOT NULL,
    [MaHopDong] int NULL,
    [MaPhieuBaoTri] int NULL,
    [TrangThai] int NOT NULL,
    [NgayGiao] datetime2 NOT NULL,
    [HanHoanThanh] datetime2 NULL,
    [NgayHoanThanh] datetime2 NULL,
    [MaNguoiGiao] int NULL,
    [GhiChuTienDo] nvarchar(max) NULL,
    CONSTRAINT [PK_PhanCongCongViecs] PRIMARY KEY ([MaPhanCong]),
    CONSTRAINT [FK_PhanCongCongViecs_HopDongs_MaHopDong] FOREIGN KEY ([MaHopDong]) REFERENCES [dbo].[HopDongs] ([MaHopDong]) ON DELETE SET NULL,
    CONSTRAINT [FK_PhanCongCongViecs_NguoiDungs_MaNguoiGiao] FOREIGN KEY ([MaNguoiGiao]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung]) ON DELETE NO ACTION,
    CONSTRAINT [FK_PhanCongCongViecs_NguoiDungs_MaNhanVien] FOREIGN KEY ([MaNhanVien]) REFERENCES [dbo].[NguoiDungs] ([MaNguoiDung]) ON DELETE NO ACTION,
    CONSTRAINT [FK_PhanCongCongViecs_PhieuBaoTris_MaPhieuBaoTri] FOREIGN KEY ([MaPhieuBaoTri]) REFERENCES [dbo].[PhieuBaoTris] ([MaPhieu]) ON DELETE SET NULL
);
GO


CREATE INDEX [IX_BienBanBanGiaos_MaHopDong] ON [dbo].[BienBanBanGiaos] ([MaHopDong]);
GO


CREATE INDEX [IX_BienBanBanGiaos_MaNhanVienLap] ON [dbo].[BienBanBanGiaos] ([MaNhanVienLap]);
GO


CREATE INDEX [IX_ChiTietHopDongs_MaThietBi] ON [dbo].[ChiTietHopDongs] ([MaThietBi]);
GO


CREATE INDEX [IX_HopDongs_MaKhachHang] ON [dbo].[HopDongs] ([MaKhachHang]);
GO


CREATE INDEX [IX_HopDongs_MaKhuyenMai] ON [dbo].[HopDongs] ([MaKhuyenMai]);
GO


CREATE INDEX [IX_HopDongs_MaNhanVien] ON [dbo].[HopDongs] ([MaNhanVien]);
GO


CREATE INDEX [IX_KyHanThanhToans_MaHopDong] ON [dbo].[KyHanThanhToans] ([MaHopDong]);
GO


CREATE INDEX [IX_LichSuNhacNos_MaHopDong] ON [dbo].[LichSuNhacNos] ([MaHopDong]);
GO


CREATE INDEX [IX_LichSuNhacNos_MaKyHan] ON [dbo].[LichSuNhacNos] ([MaKyHan]);
GO


CREATE INDEX [IX_LichSuNhacNos_NguoiGuiId] ON [dbo].[LichSuNhacNos] ([NguoiGuiId]);
GO


CREATE INDEX [IX_LichSuThietBis_MaNguoiThucHien] ON [dbo].[LichSuThietBis] ([MaNguoiThucHien]);
GO


CREATE INDEX [IX_LichSuThietBis_MaThietBi] ON [dbo].[LichSuThietBis] ([MaThietBi]);
GO


CREATE INDEX [IX_NguoiDungs_MaVaiTro] ON [dbo].[NguoiDungs] ([MaVaiTro]);
GO


CREATE INDEX [IX_PhanCongCongViecs_MaHopDong] ON [dbo].[PhanCongCongViecs] ([MaHopDong]);
GO


CREATE INDEX [IX_PhanCongCongViecs_MaNguoiGiao] ON [dbo].[PhanCongCongViecs] ([MaNguoiGiao]);
GO


CREATE INDEX [IX_PhanCongCongViecs_MaNhanVien] ON [dbo].[PhanCongCongViecs] ([MaNhanVien]);
GO


CREATE INDEX [IX_PhanCongCongViecs_MaPhieuBaoTri] ON [dbo].[PhanCongCongViecs] ([MaPhieuBaoTri]);
GO


CREATE INDEX [IX_PhieuBaoTris_MaHopDong] ON [dbo].[PhieuBaoTris] ([MaHopDong]);
GO


CREATE INDEX [IX_PhieuBaoTris_MaKyThuatVien] ON [dbo].[PhieuBaoTris] ([MaKyThuatVien]);
GO


CREATE INDEX [IX_PhieuBaoTris_MaThietBi] ON [dbo].[PhieuBaoTris] ([MaThietBi]);
GO


CREATE INDEX [IX_PhieuChis_MaHopDong] ON [dbo].[PhieuChis] ([MaHopDong]);
GO


CREATE INDEX [IX_PhieuChis_MaNhanVienChi] ON [dbo].[PhieuChis] ([MaNhanVienChi]);
GO


CREATE INDEX [IX_PhieuThus_MaHopDong] ON [dbo].[PhieuThus] ([MaHopDong]);
GO


CREATE INDEX [IX_PhieuThus_MaKyHan] ON [dbo].[PhieuThus] ([MaKyHan]);
GO


CREATE INDEX [IX_PhieuThus_MaNhanVienThu] ON [dbo].[PhieuThus] ([MaNhanVienThu]);
GO


CREATE INDEX [IX_SanPhams_MaLoai] ON [dbo].[SanPhams] ([MaLoai]);
GO


CREATE INDEX [IX_ThietBis_MaSanPham] ON [dbo].[ThietBis] ([MaSanPham]);
GO


CREATE INDEX [IX_ThongBaos_MaNguoiDung] ON [dbo].[ThongBaos] ([MaNguoiDung]);
GO


CREATE INDEX [IX_YeuCauGiaHans_MaHopDong] ON [dbo].[YeuCauGiaHans] ([MaHopDong]);
GO


CREATE INDEX [IX_YeuCauGiaHans_MaNguoiDuyet] ON [dbo].[YeuCauGiaHans] ([MaNguoiDuyet]);
GO



CREATE TABLE dbo.SchemaVersions (
    Version int NOT NULL CONSTRAINT PK_SchemaVersions PRIMARY KEY,
    AppliedUtc datetime2 NOT NULL CONSTRAINT DF_SchemaVersions_AppliedUtc DEFAULT SYSUTCDATETIME()
);
INSERT dbo.SchemaVersions (Version) VALUES (1);
COMMIT TRANSACTION;
GO

