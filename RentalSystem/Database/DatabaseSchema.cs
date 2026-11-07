using System.Data;
using System.Data.Common;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata;

namespace RentalSystem.Database;

public static class DatabaseSchema
{
    public const int CurrentVersion = 4;
    public const string TargetDatabase = "RentalSystemDB_V2";
    public const string RehearsalMarker = "RentalSystem.Rehearsal";

    public static void RequireRehearsal(DbConnection connection, DbTransaction? transaction = null)
    {
        if (!string.Equals(connection.Database, TargetDatabase, StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Fixture operations require RentalSystemDB_V2.");

        bool openedHere = connection.State != ConnectionState.Open;
        if (openedHere) connection.Open();
        try
        {
            using var command = connection.CreateCommand();
            command.Transaction = transaction;
            command.CommandText = """
                SELECT COUNT(*) FROM sys.extended_properties
                WHERE class = 0 AND name = N'RentalSystem.Rehearsal'
                  AND TRY_CONVERT(int, value) = 1;
                """;
            if (command.ExecuteScalar() is not 1)
                throw new InvalidOperationException("Fixture operations are disabled on this database.");
        }
        finally
        {
            if (openedHere) connection.Close();
        }
    }

    public static string ReadSql(string filename)
    {
        string resourceName = "RentalSystem.Database.Sql." + filename;
        using var stream = typeof(DatabaseSchema).Assembly.GetManifestResourceStream(resourceName)
            ?? throw new InvalidOperationException($"Missing SQL resource: {resourceName}");
        using var reader = new StreamReader(stream);
        return reader.ReadToEnd();
    }

    public static async Task VerifyModelAsync(IModel model, DbConnection connection, DbTransaction transaction)
    {
        static string Quote(string name) => "[" + name.Replace("]", "]]") + "]";
        var queries = model.GetRelationalModel().Tables.Select(table =>
            $"SELECT TOP (0) {string.Join(", ", table.Columns.Select(c => Quote(c.Name)))} " +
            $"FROM {Quote(table.Schema ?? "dbo")}.{Quote(table.Name)};");
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = string.Join(Environment.NewLine, queries);
        await command.ExecuteNonQueryAsync();
    }

    public static async Task VerifyAsync(DbConnection connection)
    {
        await connection.OpenAsync();
        try
        {
            await using var command = connection.CreateCommand();
            command.CommandText = """
                IF OBJECT_ID(N'dbo.SchemaVersions', N'U') IS NULL
                    THROW 51004, N'Database schema is not registered. Run the versioned SQL deployment first.', 1;
                EXEC sys.sp_executesql N'SELECT ISNULL(MAX(Version), 0) FROM dbo.SchemaVersions';
                """;
            if (await command.ExecuteScalarAsync() is not int version || version != CurrentVersion)
                throw new InvalidOperationException($"Database '{connection.Database}' requires schema version {CurrentVersion:D3}.");
        }
        finally
        {
            await connection.CloseAsync();
        }
    }
}
