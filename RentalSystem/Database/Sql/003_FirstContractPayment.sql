SET XACT_ABORT ON;
BEGIN TRANSACTION;

DECLARE @Version int = (SELECT ISNULL(MAX(Version), 0) FROM dbo.SchemaVersions);
IF @Version NOT IN (2, 3)
    THROW 51012, N'First contract payment requires schema 002 or 003.', 1;

IF COL_LENGTH(N'dbo.HopDongs', N'YeuCauThanhToanLanDau') IS NULL
    ALTER TABLE dbo.HopDongs ADD YeuCauThanhToanLanDau bit NOT NULL
        CONSTRAINT DF_HopDongs_YeuCauThanhToanLanDau DEFAULT (0);

IF @Version = 2 INSERT dbo.SchemaVersions (Version) VALUES (3);
COMMIT TRANSACTION;
