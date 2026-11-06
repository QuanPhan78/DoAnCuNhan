"""Exercise the schema upgrade and HTTP workflow on a disposable SQL backup copy."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from html import unescape
import json
from pathlib import Path
import socket
import sys
import uuid

import cutover

sys.path.insert(0, str(cutover.ROOT / "tools/demo"))
import verify_demo as web


def verify(backup):
    name = "RentalSystemMaintenanceCheck_" + uuid.uuid4().hex[:10]
    web.DB = name
    web.PORT = 5017
    web.BASE = f"http://localhost:{web.PORT}"
    web.OUT = cutover.ROOT / "outputs" / "maintenance-check"
    web.OUT.mkdir(parents=True, exist_ok=True)
    with socket.socket() as port:
        if port.connect_ex(("localhost", web.PORT)) == 0:
            raise RuntimeError("Port 5017 is occupied.")

    sql, lit, require = cutover.sql, cutover.literal, web.require
    files = sql(f"RESTORE FILELISTONLY FROM DISK={lit(backup)};").splitlines()
    data_dir = Path(sql("SELECT CONVERT(nvarchar(4000), SERVERPROPERTY('InstanceDefaultDataPath'));"))
    moves = []
    for row in files:
        logical, _, file_type, *_ = row.split("|")
        suffix = ".mdf" if file_type == "D" else ".ldf"
        moves.append(f"MOVE {lit(logical)} TO {lit(data_dir / (name + suffix))}")
    if len(moves) != 2 or sql(f"SELECT COUNT(*) FROM sys.databases WHERE name={lit(name)};") != "0":
        raise RuntimeError("Expected a fresh test database and a two-file demo backup.")

    process = log = None
    try:
        sql(f"RESTORE DATABASE [{name}] FROM DISK={lit(backup)} WITH {', '.join(moves)};")
        if sql("SELECT COUNT(*) FROM dbo.NguoiDungs WHERE Email IN "
               "(N'admin@demo.invalid', N'tech@demo.invalid', N'customer@demo.invalid');", name) != "3":
            raise RuntimeError("The verification requires a synthetic demo backup.")
        sql(f"ALTER DATABASE [{name}] SET READ_WRITE;")
        upgrade = cutover.SQL / "002_MaintenanceAssignments.sql"
        cutover.sql_file(cutover.SQL / "UpgradeContractIdentityImages.sql", name)
        registration = (cutover.SQL / "RegisterExisting001.sql").read_text(encoding="utf-8-sig")
        sql("SET XACT_ABORT ON; BEGIN TRANSACTION;\n" + registration + "\nCOMMIT TRANSACTION;", name)
        require(sql("SELECT MAX(Version) FROM dbo.SchemaVersions;", name) == "1", "Test starts on schema 001")
        candidates = sql("""
            DECLARE @tech int = (SELECT MaNguoiDung FROM dbo.NguoiDungs WHERE Email=N'tech@demo.invalid');
            DECLARE @open int = (SELECT MIN(MaPhieu) FROM dbo.PhieuBaoTris);
            UPDATE dbo.PhieuBaoTris SET MaKyThuatVien=@tech, TrangThai=2 WHERE MaPhieu=@open;
            INSERT dbo.PhanCongCongViecs (MaNhanVien,TieuDe,NoiDung,MaPhieuBaoTri,TrangThai,NgayGiao)
            VALUES (@tech,N'Older linked work',N'Test work',@open,0,'2026-01-01'),
                   (@tech,N'Latest linked work',N'Test work',@open,0,'2026-01-02'),
                   (@tech,N'Independent work',N'Test work',NULL,0,'2026-01-03');
            SELECT @open;
            """, name)
        cutover.sql_file(upgrade, name)
        count = sql("SELECT COUNT(*) FROM dbo.PhanCongCongViecs;", name)
        cutover.sql_file(upgrade, name)
        require(sql("SELECT MAX(Version) FROM dbo.SchemaVersions;", name) == "2" and
                sql("SELECT COUNT(*) FROM dbo.PhanCongCongViecs;", name) == count,
                "Schema 002 upgrade can be run twice")
        require(sql(f"SELECT TieuDe FROM dbo.PhanCongCongViecs "
                    f"WHERE MaPhieuBaoTri={int(candidates)} AND TuDongTuBaoTri=1;", name) ==
                "Latest linked work", "Upgrade adopts the newest matching open task")
        require(sql("SELECT COUNT(*) FROM dbo.PhanCongCongViecs WHERE TuDongTuBaoTri=0 "
                    "AND TieuDe IN (N'Older linked work',N'Independent work');", name) == "2",
                "Upgrade keeps supplemental and independent tasks")

        second = int(sql("""
            INSERT dbo.NguoiDungs (MaVaiTro, HoTen, SoDienThoai, Email, MatKhau, CCCD, DiaChi, TrangThai)
            SELECT MaVaiTro, N'Technician B', N'0900000099', N'tech2@demo.invalid', MatKhau, CCCD, DiaChi, 1
            FROM dbo.NguoiDungs WHERE Email = N'tech@demo.invalid';
            SELECT CONVERT(int, SCOPE_IDENTITY());
            """, name))
        first = int(sql("SELECT MaNguoiDung FROM dbo.NguoiDungs WHERE Email=N'tech@demo.invalid';", name))
        process, log = web.start_server()
        admin, tech_a, tech_b, customer = [web.Session() for _ in range(4)]
        for session, email in ((admin, "admin"), (tech_a, "tech"), (tech_b, "tech2"), (customer, "customer")):
            session.login(email + "@demo.invalid")
            session.api_login(email + "@demo.invalid")
        endpoint = "/Admin/Database/Backup?format=json"
        require(admin.get_json(endpoint)["DatabaseName"] == name, "Web uses the disposable SQL copy")
        ticket_id = int(customer.send_json("/api/maintenance", {
            "contractId": "1", "deviceId": "1", "description": "Maintenance sync verification",
            "issueType": "Kết nối", "severity": "Trung bình",
        })["id"])
        page = f"/Admin/BaoTri/Details/{ticket_id}"
        status_url = f"/api/maintenance/{ticket_id}/status"

        def assign(session, person, status=1):
            return session.form("/Admin/BaoTri/UpdateStatus",
                                {"id": ticket_id, "status": status, "maKtv": person, "phiDenBu": 0}, page)

        admin_two = web.Session()
        admin_two.login("admin@demo.invalid")
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(assign, session, first) for session in (admin, admin_two)]
            for future in futures:
                future.result()

        def task():
            return [p for p in admin.get_json(endpoint)["PhanCongCongViecs"]
                    if p["MaPhieuBaoTri"] == ticket_id and p["TuDongTuBaoTri"]]

        def shows(session):
            return f'href="{page}"' in session.request("/Admin/PhanCong/MyTasks")[0].decode()

        def listed(session):
            return any(int(p["id"]) == ticket_id for p in
                       session.get_json("/api/maintenance"))

        initial = task()
        require(len(initial) == 1 and initial[0]["MaNhanVien"] == first, "Concurrent saves produce one managed task")
        task_id = initial[0]["MaPhanCong"]
        require(shows(tech_a) and not shows(tech_b) and listed(tech_a) and not listed(tech_b),
                "Only the assignee sees the ticket in Web and Mobile lists")
        assign(admin, second)
        require(task()[0]["MaPhanCong"] == task_id and not shows(tech_a) and shows(tech_b) and
                not listed(tech_a) and listed(tech_b), "Reassignment moves the same task on both platforms")
        require(any(f"Đổi kỹ thuật viên phiếu #{ticket_id}" == h["HanhDong"]
                    for h in admin.get_json(endpoint)["LichSuThietBis"]), "Reassignment records device history")

        tech_b.send_json(status_url, {"statusCode": 2, "notes": "Mobile bắt đầu sửa"}, "PUT")
        require(task()[0]["TrangThai"] == 1, "Mobile starts the Web task")
        tech_b.form("/Admin/BaoTri/UpdateStatus", {"id": ticket_id, "status": 3, "phiDenBu": 0}, page)
        require("Chờ nghiệm thu" in unescape(tech_b.request("/Admin/PhanCong/MyTasks")[0].decode()) and
                customer.get_json(f"/api/maintenance/{ticket_id}")["statusCode"] == 3 and task()[0]["TrangThai"] == 1,
                "Web reports repair done and Mobile sees the pending acceptance")
        customer.send_json(f"/api/maintenance/{ticket_id}/rating", {"rating": 5}, "PUT")
        require(task()[0]["TrangThai"] == 1, "Rating leaves the task open")
        customer_page = f"/BaoTri/ChiTiet/{ticket_id}"
        customer.form("/BaoTri/NghiemThu", {"maPhieu": ticket_id, "dongY": "false", "yKien": "Còn lỗi"}, customer_page)
        require(customer.get_json(f"/api/maintenance/{ticket_id}")["statusCode"] == 2 and
                task()[0]["MaPhanCong"] == task_id, "Rejection reopens repair with the same task ID")
        tech_b.send_json(status_url, {"statusCode": 3, "result": "Đã xử lý lại"}, "PUT")
        customer.form("/BaoTri/NghiemThu", {"maPhieu": ticket_id, "dongY": "true"}, customer_page)
        require(customer.get_json(f"/api/maintenance/{ticket_id}")["statusCode"] == 5 and
                task()[0]["TrangThai"] == 2 and task()[0]["NgayHoanThanh"], "Customer acceptance closes the task")

        modern = admin.get_json(endpoint)
        legacy = deepcopy(modern)
        legacy["PhanCongCongViecs"] = [p for p in legacy["PhanCongCongViecs"] if p["MaPhanCong"] != task_id]
        for p in legacy["PhanCongCongViecs"]:
            p.pop("TuDongTuBaoTri")
        open_ticket = next(t for t in legacy["PhieuBaoTris"] if t["MaPhieu"] == ticket_id)
        open_ticket.update(TrangThai=2, DaNghiemThu=False, NgayNghiemThu=None)
        web.multipart_file(admin, "/Admin/Database/Restore", "schema-001.json", json.dumps(legacy).encode())
        require(len(task()) == 1 and task()[0]["TrangThai"] == 1, "Legacy JSON restore creates the missing active task")
        manual = next(p for p in modern["PhanCongCongViecs"] if p["TieuDe"] == "Independent work")
        admin.form("/Admin/PhanCong/UpdateStatus", {"id": manual["MaPhanCong"], "status": 2}, "/Admin/PhanCong")
        require(any(p["MaPhanCong"] == manual["MaPhanCong"] and p["TrangThai"] == 2
                    for p in admin.get_json(endpoint)["PhanCongCongViecs"]), "Manual work still supports direct updates")

        with backup.open("rb") as archive:
            web.multipart_file(admin, "/Admin/Database/Restore", "schema-001.bak", archive.read())
        require(sql("SELECT MAX(Version) FROM dbo.SchemaVersions;", name) == "2" and
                admin.get_json(endpoint)["DatabaseName"] == name, "Native legacy restore upgrades to schema 002")
    finally:
        web.stop_server(process, log)
        (web.OUT / "verification.json").write_text(
            json.dumps({"checks": web.RESULTS}, ensure_ascii=False, indent=2), encoding="utf-8")
        sql(f"IF DB_ID(N'{name}') IS NOT NULL BEGIN "
            f"ALTER DATABASE [{name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE [{name}]; END;")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("backup", type=Path, help="Path to the synthetic legacy demo .bak file")
    verify(parser.parse_args().backup.resolve(strict=True))
