-- Run against the selected RentalSystem database, after taking a backup.
-- EF supplies a transaction when this script is used by the migration.
DECLARE @IdentityImagesOwnTransaction bit = IIF(@@TRANCOUNT = 0, 1, 0);
IF @IdentityImagesOwnTransaction = 1 BEGIN TRANSACTION;

BEGIN TRY
    IF OBJECT_ID(N'dbo.HopDongs', N'U') IS NULL
        THROW 50001, N'Không tìm thấy bảng dbo.HopDongs trong cơ sở dữ liệu đã chọn.', 1;

    IF COL_LENGTH(N'dbo.HopDongs', N'AnhCCCD_Truoc') IS NULL
        ALTER TABLE dbo.HopDongs ADD AnhCCCD_Truoc nvarchar(max) NULL;

    IF COL_LENGTH(N'dbo.HopDongs', N'AnhCCCD_Sau') IS NULL
        ALTER TABLE dbo.HopDongs ADD AnhCCCD_Sau nvarchar(max) NULL;

    IF COL_LENGTH(N'dbo.HopDongs', N'AnhCMND') IS NOT NULL
    BEGIN
        -- Defer column binding until after any missing columns have been added.
        EXEC sys.sp_executesql N'
            DECLARE @SpaceCharacters nvarchar(32) =
                NCHAR(9) + NCHAR(10) + NCHAR(11) + NCHAR(12) + NCHAR(13) + N'' '' +
                NCHAR(133) + NCHAR(160) + NCHAR(5760) + NCHAR(8192) + NCHAR(8193) +
                NCHAR(8194) + NCHAR(8195) + NCHAR(8196) + NCHAR(8197) + NCHAR(8198) +
                NCHAR(8199) + NCHAR(8200) + NCHAR(8201) + NCHAR(8202) + NCHAR(8232) +
                NCHAR(8233) + NCHAR(8239) + NCHAR(8287) + NCHAR(12288);
            UPDATE dbo.HopDongs
            SET AnhCCCD_Truoc = AnhCMND
            WHERE NULLIF(TRIM(@SpaceCharacters FROM AnhCCCD_Truoc), N'''') IS NULL
              AND NULLIF(TRIM(@SpaceCharacters FROM AnhCMND), N'''') IS NOT NULL;';

        DECLARE @IdentityImagesDefault sysname;
        SELECT @IdentityImagesDefault = dc.name
        FROM sys.default_constraints AS dc
        INNER JOIN sys.columns AS c
            ON c.object_id = dc.parent_object_id AND c.column_id = dc.parent_column_id
        WHERE dc.parent_object_id = OBJECT_ID(N'dbo.HopDongs') AND c.name = N'AnhCMND';

        IF @IdentityImagesDefault IS NOT NULL
        BEGIN
            DECLARE @IdentityImagesDropDefault nvarchar(400) =
                N'ALTER TABLE dbo.HopDongs DROP CONSTRAINT ' + QUOTENAME(@IdentityImagesDefault);
            EXEC sys.sp_executesql @IdentityImagesDropDefault;
        END;

        ALTER TABLE dbo.HopDongs DROP COLUMN AnhCMND;
    END;

    IF @IdentityImagesOwnTransaction = 1 COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @IdentityImagesOwnTransaction = 1 AND XACT_STATE() <> 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
