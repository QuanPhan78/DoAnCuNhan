SET XACT_ABORT ON;
BEGIN TRANSACTION;
DECLARE @Version int = (SELECT ISNULL(MAX(Version),0) FROM dbo.SchemaVersions);
IF @Version NOT IN (3,4) THROW 51014, N'Contract settlements require schema 003 or 004.',1;
IF OBJECT_ID(N'dbo.ContractSettlements',N'U') IS NULL
BEGIN
 CREATE TABLE dbo.ContractSettlements (
  MaHopDong int NOT NULL CONSTRAINT PK_ContractSettlements PRIMARY KEY,
  LoaiQuyetToan int NOT NULL, MaNhanVien int NOT NULL, NgayQuyetToan datetime2 NOT NULL,
  CocThucThu decimal(18,2) NOT NULL, CocDaHoan decimal(18,2) NOT NULL,
  CocCanTruThue decimal(18,2) NOT NULL, CocCanTruBoiThuong decimal(18,2) NOT NULL,
  HoanCoc decimal(18,2) NOT NULL, HoanThue decimal(18,2) NOT NULL,
  HoanThua decimal(18,2) NOT NULL, HoanKhac decimal(18,2) NOT NULL,
  ChiTietJson nvarchar(max) NOT NULL, MaBanXemTruoc nvarchar(64) NOT NULL,
  CONSTRAINT FK_ContractSettlements_HopDongs FOREIGN KEY(MaHopDong) REFERENCES dbo.HopDongs(MaHopDong),
  CONSTRAINT FK_ContractSettlements_NguoiDungs FOREIGN KEY(MaNhanVien) REFERENCES dbo.NguoiDungs(MaNguoiDung),
  CONSTRAINT CK_ContractSettlements_Amounts CHECK (
   CocThucThu>=0 AND CocDaHoan>=0 AND CocCanTruThue>=0 AND CocCanTruBoiThuong>=0 AND
   HoanCoc>=0 AND HoanThue>=0 AND HoanThua>=0 AND HoanKhac>=0 AND
   CocDaHoan+CocCanTruThue+CocCanTruBoiThuong+HoanCoc<=CocThucThu)
 );
END;
IF @Version=3 INSERT dbo.SchemaVersions(Version) VALUES(4);
COMMIT TRANSACTION;
