"""Local, name-checked SQL Server rollout for the two RentalSystem databases."""
import argparse
import json
import subprocess
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SQL = ROOT / "RentalSystem" / "Database" / "Sql"
OUT = ROOT / "outputs" / "database-cutover"
OLD, V2 = "RentalSystemDB", "RentalSystemDB_V2"
DEMOS = ("RentalSystemDemoDB", "RentalSystemDemoCheckDB")


def literal(value):
    return "N'" + str(value).replace("'", "''") + "'"


def sql(query, database="master"):
    result = subprocess.run(
        ["sqlcmd", "-S", "lpc:localhost", "-E", "-C", "-b", "-l", "5",
         "-d", database, "-f", "65001", "-h", "-1", "-W", "-s", "|", "-Q",
         "SET NOCOUNT ON;\n" + query],
        capture_output=True, encoding="utf-8", errors="replace", check=False)
    if result.returncode:
        raise RuntimeError(result.stdout.strip() + "\n" + result.stderr.strip())
    return result.stdout.strip()


def sql_file(path, database):
    subprocess.run(["sqlcmd", "-S", "lpc:localhost", "-E", "-C", "-b", "-l", "5",
                    "-d", database, "-f", "65001", "-i", str(path)], check=True)


def marker(database, name):
    return sql("SELECT COUNT(*) FROM sys.extended_properties WHERE class = 0 "
               f"AND name = {literal(name)} AND TRY_CONVERT(int,value) = 1;", database) == "1"


def mark():
    sql("""
        IF NOT EXISTS (SELECT 1 FROM sys.extended_properties WHERE class = 0 AND name = N'RentalSystem.Rehearsal')
            EXEC sys.sp_addextendedproperty @name=N'RentalSystem.Rehearsal', @value=1;
        """, V2)


def require_rehearsal():
    if not marker(V2, "RentalSystem.Rehearsal"):
        raise RuntimeError("Refusing to overwrite V2 outside its explicitly marked rehearsal phase.")


def backup(database, label):
    folder = OUT / "sql-backups"
    if not folder.is_dir():
        raise RuntimeError("Configure the private sql-backups directory for SQL Server first.")
    path = folder / f"{database}-{label}.bak"
    if path.exists():
        path = folder / f"{database}-{label}-{uuid.uuid4().hex}.bak"
    sql(f"BACKUP DATABASE [{database}] TO DISK={literal(path)} WITH COPY_ONLY, CHECKSUM, INIT;")
    sql(f"RESTORE VERIFYONLY FROM DISK={literal(path)} WITH CHECKSUM;")
    with path.open("rb") as archive:
        if not archive.read(1):
            raise RuntimeError("The verified SQL backup is empty.")
    print(f"Verified backup: {path}", flush=True)
    return path


def restore_legacy(path):
    require_rehearsal()
    source = sql(f"SELECT type,name FROM sys.master_files WHERE database_id=DB_ID(N'{OLD}') ORDER BY type;").splitlines()
    target = sql(f"SELECT type,physical_name FROM sys.master_files WHERE database_id=DB_ID(N'{V2}') ORDER BY type;").splitlines()
    if len(source) != 2 or len(target) != 2:
        raise RuntimeError("Expected one data file and one log file in each database.")
    moves = []
    for original, destination in zip(source, target):
        kind, logical = original.split("|", 1)
        target_kind, physical = destination.split("|", 1)
        if kind != target_kind or kind not in ("0", "1"):
            raise RuntimeError("Unexpected SQL Server file types.")
        moves.append(f"MOVE {literal(logical)} TO {literal(physical)}")
    try:
        sql(f"""
            ALTER DATABASE [{V2}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
            RESTORE DATABASE [{V2}] FROM DISK={literal(path)} WITH REPLACE, CHECKSUM, {", ".join(moves)};
            ALTER DATABASE [{V2}] SET READ_WRITE;
            """)
    finally:
        sql(f"ALTER DATABASE [{V2}] SET MULTI_USER WITH ROLLBACK IMMEDIATE;")
    mark()


def schema(database):
    return sql("""
        SELECT 'C', t.name, c.name, CONCAT_WS(':', c.system_type_id, c.max_length,
               c.precision, c.scale, c.is_nullable, c.is_identity)
        FROM sys.tables t JOIN sys.columns c ON c.object_id = t.object_id
        WHERE SCHEMA_NAME(t.schema_id) = 'dbo'
          AND t.name NOT IN ('SchemaVersions', '__EFMigrationsHistory', 'sysdiagrams')
        UNION ALL
        SELECT 'I', t.name, c.name, CONCAT_WS(':', i.is_unique, i.is_primary_key,
               i.type, ic.key_ordinal, ic.is_descending_key, ic.is_included_column, i.filter_definition)
        FROM sys.tables t JOIN sys.indexes i ON i.object_id=t.object_id
        JOIN sys.index_columns ic ON ic.object_id=i.object_id AND ic.index_id=i.index_id
        JOIN sys.columns c ON c.object_id=ic.object_id AND c.column_id=ic.column_id
        WHERE i.is_disabled=0 AND SCHEMA_NAME(t.schema_id) = 'dbo'
          AND t.name NOT IN ('SchemaVersions', '__EFMigrationsHistory', 'sysdiagrams')
        UNION ALL
        SELECT 'F', t.name, c.name, CONCAT_WS(':', rt.name, rc.name, f.delete_referential_action,
               f.update_referential_action, fc.constraint_column_id, f.is_disabled)
        FROM sys.foreign_keys f JOIN sys.foreign_key_columns fc ON fc.constraint_object_id=f.object_id
        JOIN sys.tables t ON t.object_id=fc.parent_object_id
        JOIN sys.tables rt ON rt.object_id=fc.referenced_object_id
        JOIN sys.columns c ON c.object_id=t.object_id AND c.column_id=fc.parent_column_id
        JOIN sys.columns rc ON rc.object_id=rt.object_id AND rc.column_id=fc.referenced_column_id
        WHERE SCHEMA_NAME(t.schema_id) = 'dbo'
        ORDER BY 1,2,3,4;
        """, database).splitlines()


def compare_schema(expected):
    missing = sorted(set(expected) - set(schema(V2)))
    if missing:
        raise RuntimeError("V2 is missing baseline columns, keys or indexes: " + "; ".join(missing))
    print("Baseline columns, keys and indexes match V2.", flush=True)


def verify_copy(expected):
    tables = {}
    for item in expected:
        kind, table, column, _ = item.split("|", 3)
        if kind == "C":
            tables.setdefault(table, []).append(column)
    counts = {}
    for table, columns in tables.items():
        projection = ", ".join(f"[{column}]" for column in columns)
        source_columns = ", ".join(
            "CASE WHEN NULLIF(TRIM(NCHAR(9)+NCHAR(10)+NCHAR(13)+N' ' FROM AnhCCCD_Truoc),N'') IS NULL "
            "AND NULLIF(TRIM(NCHAR(9)+NCHAR(10)+NCHAR(13)+N' ' FROM AnhCMND),N'') IS NOT NULL "
            "THEN AnhCMND ELSE AnhCCCD_Truoc END"
            if table == "HopDongs" and column == "AnhCCCD_Truoc" else f"[{column}]"
            for column in columns
        )
        left = f"SELECT {source_columns} FROM [{OLD}].dbo.[{table}]"
        right = f"SELECT {projection} FROM [{V2}].dbo.[{table}]"
        counts[table] = int(sql(f"""
            IF (SELECT COUNT(*) FROM [{OLD}].dbo.[{table}]) <> (SELECT COUNT(*) FROM [{V2}].dbo.[{table}])
               OR EXISTS ({left} EXCEPT {right}) OR EXISTS ({right} EXCEPT {left})
                THROW 51005, N'Copied data differs in {table}.', 1;
            SELECT COUNT(*) FROM [{V2}].dbo.[{table}];
            """))
    violations = sql("DBCC CHECKCONSTRAINTS WITH ALL_CONSTRAINTS, NO_INFOMSGS;", V2)
    if violations:
        raise RuntimeError("V2 contains constraint violations: " + violations)
    return counts


def upgrade():
    require_rehearsal()
    expected = json.loads((OUT / "baseline-schema.json").read_text(encoding="utf-8"))
    script = (SQL / "UpgradeContractIdentityImages.sql").read_text(encoding="utf-8-sig")
    registration = (SQL / "RegisterExisting001.sql").read_text(encoding="utf-8-sig")
    # Validate the upgraded catalog before publishing its version.
    sql(script, V2)
    compare_schema(expected)
    sql("SET XACT_ABORT ON; BEGIN TRANSACTION;\n" + registration + "\nCOMMIT TRANSACTION;", V2)
    sql("IF COL_LENGTH(N'dbo.HopDongs', N'AnhCMND') IS NOT NULL THROW 51006, N'Legacy column remains.', 1;", V2)
    sql(script, V2)
    print("Identity upgrade verified after a second run.", flush=True)
    return expected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["baseline", "restore-legacy", "upgrade", "refresh", "promote", "archive-demos", "remove-demo-databases"])
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.action == "baseline":
        if sql(f"SELECT COUNT(*) FROM sys.databases WHERE name=N'{V2}';") != "0":
            raise RuntimeError("V2 already exists. Baseline requires a new database.")
        sql(f"CREATE DATABASE [{V2}];")
        sql_file(SQL / "001_Baseline.sql", V2)
        mark()
        expected = schema(V2)
        if len({row.split("|")[1] for row in expected if row.startswith("C|")}) != 18:
            raise RuntimeError("Expected all 18 business tables.")
        (OUT / "baseline-schema.json").write_text(json.dumps(expected, indent=2), encoding="utf-8")
        print("Created and checked empty V2 baseline.", flush=True)
    elif args.action == "restore-legacy":
        require_rehearsal()
        restore_legacy(backup(OLD, "rehearsal-source"))
    elif args.action == "upgrade":
        upgrade()
    elif args.action == "refresh":
        require_rehearsal()
        if sql(f"SELECT COUNT(*) FROM sys.dm_exec_sessions WHERE database_id=DB_ID(N'{OLD}') AND is_user_process=1 AND (status<>N'sleeping' OR open_transaction_count>0);") != "0":
            raise RuntimeError("Legacy database has active requests or transactions.")
        sql(f"ALTER DATABASE [{OLD}] SET READ_ONLY WITH ROLLBACK IMMEDIATE;")
        try:
            restore_legacy(backup(OLD, "cutover-source"))
            counts = verify_copy(upgrade())
            (OUT / "cutover-data-verification.json").write_text(json.dumps(counts, indent=2), encoding="utf-8")
            print(f"Verified every row in {len(counts)} business tables.", flush=True)
        except BaseException:
            sql(f"ALTER DATABASE [{OLD}] SET READ_WRITE WITH ROLLBACK IMMEDIATE;")
            raise
    elif args.action == "promote":
        require_rehearsal()
        if not all((OUT / name).is_file() for name in ("cutover-data-verification.json", "cutover-smoke.json")):
            raise RuntimeError("Final-copy or startup verification evidence is missing.")
        sql("EXEC sys.sp_dropextendedproperty @name=N'RentalSystem.Rehearsal';", V2)
        print("V2 fixture operations disabled.", flush=True)
    elif args.action == "archive-demos":
        for database in DEMOS:
            if not marker(database, "RentalSystem.DemoFixture"):
                raise RuntimeError(f"Refusing to archive database without the expected demo marker: {database}")
            backup(database, "retired")
    else:
        if marker(V2, "RentalSystem.Rehearsal") or not (OUT / "live-smoke.json").is_file():
            raise RuntimeError("Promote and smoke-test V2 before removing demo databases.")
        for database in DEMOS:
            archive = OUT / "sql-backups" / f"{database}-retired.bak"
            if not marker(database, "RentalSystem.DemoFixture") or not archive.is_file():
                raise RuntimeError(f"Demo ownership or verified backup missing: {database}")
            sql(f"RESTORE VERIFYONLY FROM DISK={literal(archive)} WITH CHECKSUM;")
        for database in DEMOS:
            sql(f"ALTER DATABASE [{database}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE [{database}];")
            print(f"Removed archived demo database: {database}", flush=True)


if __name__ == "__main__":
    main()
