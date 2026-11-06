-- Call inside the transaction that upgraded the existing schema.
IF @@TRANCOUNT = 0
    THROW 51001, N'Registering schema 001 requires an open transaction.', 1;

IF EXISTS (
    SELECT 1 FROM (VALUES
        (N'VaiTros'), (N'NguoiDungs'), (N'LoaiThietBis'), (N'SanPhams'),
        (N'ThietBis'), (N'LichSuThietBis'), (N'KhuyenMais'), (N'HopDongs'),
        (N'KyHanThanhToans'), (N'ChiTietHopDongs'), (N'PhieuThus'), (N'PhieuChis'),
        (N'PhieuBaoTris'), (N'BienBanBanGiaos'), (N'ThongBaos'), (N'LichSuNhacNos'),
        (N'YeuCauGiaHans'), (N'PhanCongCongViecs')
    ) AS expected(Name)
    WHERE OBJECT_ID(N'dbo.' + expected.Name, N'U') IS NULL
) OR COL_LENGTH(N'dbo.HopDongs', N'AnhCMND') IS NOT NULL
  OR COL_LENGTH(N'dbo.HopDongs', N'AnhCCCD_Truoc') IS NULL
  OR COL_LENGTH(N'dbo.HopDongs', N'AnhCCCD_Sau') IS NULL
    THROW 51002, N'Existing schema is missing required tables or identity columns.', 1;

IF OBJECT_ID(N'dbo.SchemaVersions', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.SchemaVersions (
        Version int NOT NULL CONSTRAINT PK_SchemaVersions PRIMARY KEY,
        AppliedUtc datetime2 NOT NULL CONSTRAINT DF_SchemaVersions_AppliedUtc DEFAULT SYSUTCDATETIME()
    );
    INSERT dbo.SchemaVersions (Version) VALUES (1);
END
ELSE IF (SELECT ISNULL(MAX(Version), 0) FROM dbo.SchemaVersions) <> 1
    THROW 51003, N'This release expects schema version 001.', 1;

IF OBJECT_ID(N'dbo.__EFMigrationsHistory', N'U') IS NOT NULL
    DROP TABLE dbo.__EFMigrationsHistory;
