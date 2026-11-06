-- Run after schema 001. Can also reconcile active tickets after a JSON restore.
SET ANSI_NULLS ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET QUOTED_IDENTIFIER ON;
SET NUMERIC_ROUNDABORT OFF;

DECLARE @AssignmentOwnTransaction bit = IIF(@@TRANCOUNT = 0, 1, 0);
IF @AssignmentOwnTransaction = 1 BEGIN TRANSACTION;

BEGIN TRY
    DECLARE @AssignmentVersion int = (SELECT ISNULL(MAX(Version), 0) FROM dbo.SchemaVersions);
    IF @AssignmentVersion NOT IN (1, 2, 3)
        THROW 51010, N'Maintenance assignment upgrade requires schema 001, 002 or 003.', 1;

    IF COL_LENGTH(N'dbo.PhanCongCongViecs', N'TuDongTuBaoTri') IS NULL
        ALTER TABLE dbo.PhanCongCongViecs ADD TuDongTuBaoTri bit NOT NULL
            CONSTRAINT DF_PhanCongCongViecs_TuDongTuBaoTri DEFAULT (0);

    EXEC sys.sp_executesql N'
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
            WHERE object_id = OBJECT_ID(N''dbo.PhanCongCongViecs'')
              AND name = N''UX_PhanCongCongViecs_PhieuBaoTriTuDong''
        )
            CREATE UNIQUE INDEX UX_PhanCongCongViecs_PhieuBaoTriTuDong
            ON dbo.PhanCongCongViecs (MaPhieuBaoTri)
            WHERE TuDongTuBaoTri = 1 AND MaPhieuBaoTri IS NOT NULL;

        ;WITH Candidates AS (
            SELECT p.MaPhanCong, b.MaHopDong, b.HanHoanThanh, b.TrangThai,
                ROW_NUMBER() OVER (PARTITION BY b.MaPhieu ORDER BY p.NgayGiao DESC, p.MaPhanCong DESC) AS Rank
            FROM dbo.PhieuBaoTris b
            JOIN dbo.PhanCongCongViecs p ON p.MaPhieuBaoTri = b.MaPhieu AND p.MaNhanVien = b.MaKyThuatVien
            WHERE b.TrangThai IN (1, 2, 3) AND p.TrangThai IN (0, 1)
              AND NOT EXISTS (SELECT 1 FROM dbo.PhanCongCongViecs x WHERE x.MaPhieuBaoTri = b.MaPhieu AND x.TuDongTuBaoTri = 1)
        )
        UPDATE p SET TuDongTuBaoTri = 1, p.MaHopDong = c.MaHopDong,
            p.HanHoanThanh = c.HanHoanThanh, p.TrangThai = IIF(c.TrangThai = 1, 0, 1), p.NgayHoanThanh = NULL
        FROM dbo.PhanCongCongViecs p JOIN Candidates c ON p.MaPhanCong = c.MaPhanCong
        WHERE c.Rank = 1;

        INSERT dbo.PhanCongCongViecs
            (MaNhanVien, TieuDe, NoiDung, MaHopDong, MaPhieuBaoTri, TrangThai, NgayGiao, HanHoanThanh, TuDongTuBaoTri)
        SELECT b.MaKyThuatVien, CONCAT(N''Xử lý phiếu sự cố #'', b.MaPhieu), b.MoTaLoi,
            b.MaHopDong, b.MaPhieu, IIF(b.TrangThai = 1, 0, 1), b.NgayBaoLoi, b.HanHoanThanh, 1
        FROM dbo.PhieuBaoTris b
        WHERE b.TrangThai IN (1, 2, 3) AND b.MaKyThuatVien IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM dbo.PhanCongCongViecs x WHERE x.MaPhieuBaoTri = b.MaPhieu AND x.TuDongTuBaoTri = 1);';

    IF @AssignmentVersion = 1 INSERT dbo.SchemaVersions (Version) VALUES (2);
    IF @AssignmentOwnTransaction = 1 COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @AssignmentOwnTransaction = 1 AND XACT_STATE() <> 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
