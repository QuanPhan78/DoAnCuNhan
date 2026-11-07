"""Check real staff work, notification ownership and revenue parity on disposable SQL."""
from datetime import date, timedelta
from html import unescape
import json
import re
from urllib.error import HTTPError

import cutover
import verify_debt_status as fixture

web = fixture.web
check = web.require


def verify(db, _secret):
    def sql(query):
        return cutover.sql(query, db)

    sql("""
        INSERT dbo.VaiTros(TenVaiTro) VALUES(N'KyThuat');
        INSERT dbo.NguoiDungs(MaVaiTro,HoTen,SoDienThoai,Email,MatKhau,CCCD,DiaChi,TrangThai)
        VALUES (3,N'Tech A',N'0900000004',N'tech-a@demo.invalid',N'Demo@123',N'000000000004',N'',1),
               (3,N'Tech B',N'0900000005',N'tech-b@demo.invalid',N'Demo@123',N'000000000005',N'',1);
    """)
    admin, admin_api, staff, other, staff_web, customer, other_customer = (web.Session() for _ in range(7))
    admin.login("admin@demo.invalid")
    staff_web.login("tech-a@demo.invalid")
    for session, account in ((admin_api, "admin"), (staff, "tech-a"), (other, "tech-b"),
                             (customer, "customer"), (other_customer, "threshold")):
        session.api_login(f"{account}@demo.invalid")

    def denied(code, operation):
        try:
            operation()
        except HTTPError as error:
            return error.code == code
        return False

    assignments = "/Admin/PhanCong"
    create = assignments + "/Create"
    form = {"MaNhanVien": 4, "TieuDe": "Lắp đặt thiết bị kiểm thử", "NoiDung": "Kiểm tra kết nối",
            "MaHopDong": 1}
    _, url, _ = admin.form(create, form)
    check(not url.endswith("/Create"), "Web saves a new manual assignment")
    task = staff.get_json("/api/tasks/mine")[0]
    task_id = task["id"]
    status_url = f"/api/tasks/{task_id}/status"
    notice = staff.get_json("/api/notifications")[0]
    check(task["title"] == form["TieuDe"] and task["statusCode"] == 0 and notice["content"] == form["TieuDe"] and
          not notice["isRead"] and other.get_json("/api/tasks/mine") == [] and other.get_json("/api/notifications") == [],
          "A Web assignment reaches only the assignee's work and notifications")
    check(denied(403, lambda: customer.get_json("/api/tasks/mine")) and
          denied(403, lambda: other.send_json(status_url, {"statusCode": 2}, "PUT")) and
          denied(404, lambda: other.request(f"/api/notifications/{notice['id']}/read", method="PUT")),
          "Customers cannot list staff work and another employee cannot update it or read the notification")
    admin.form(create, {"MaNhanVien": 4, "TieuDe": "Kiểm kê nội bộ", "NoiDung": "Kiểm kho"})
    check(len(staff.get_json("/api/tasks/mine")) == 2, "Internal work without a contract appears in Mobile")

    staff.send_json(status_url, {"statusCode": 1, "notes": "Đang kiểm tra dây"}, "PUT")
    web_task = staff_web.get_json(f"{assignments}/Details/{task_id}")
    install = "/api/tasks/installation/1"
    check(web_task["status"] == 1 and web_task["progressNote"] == "Đang kiểm tra dây" and
          staff.get_json(install)["taskId"] == task_id and staff.get_json(install)["canUpdate"] and
          customer.get_json(install)["statusCode"] == 1 and customer.get_json(install)["notes"] is None and
          denied(404, lambda: other_customer.get_json(install)) and denied(404, lambda: other.get_json(install)),
          "Mobile task updates appear on Web and real installation progress respects ownership")
    staff_web.form(assignments + "/UpdateStatus", {"id": task_id, "status": 2}, assignments + "/MyTasks")
    completed = customer.get_json(install)
    check(completed["statusCode"] == 2 and completed["actualDate"] and
          sql("SELECT TrangThai FROM dbo.HopDongs WHERE MaHopDong=1;") == "1",
          "Completing the installation on Web updates Mobile without changing the contract lifecycle")

    staff.request(f"/api/notifications/{notice['id']}/read", method="PUT")
    check(any(n["id"] == notice["id"] and n["isRead"] for n in staff.get_json("/api/notifications")) and
          sql(f"SELECT DaDoc FROM dbo.ThongBaos WHERE MaThongBao={notice['id']};") == "1",
          "Mobile marks the same notification as read in SQL")
    staff_web.form("/Account/DanhDauDaDoc", {}, "/Account/ThongBao")
    check(all(n["isRead"] for n in staff.get_json("/api/notifications")),
          "Notifications marked read on Web are read on Mobile")
    admin.form(assignments + f"/Edit/{task_id}", {**form, "MaNhanVien": 5, "TrangThai": 2})
    check([t["id"] for t in other.get_json("/api/tasks/mine")] == [task_id] and
          all(t["id"] != task_id for t in staff.get_json("/api/tasks/mine")) and
          len(other.get_json("/api/notifications")) == 1, "Reassignment transfers work and notifies the new assignee")
    other.request("/api/notifications/read-all", method="PUT")
    check(all(n["isRead"] for n in other.get_json("/api/notifications")), "Mobile can mark all its notifications read")

    sql("UPDATE dbo.PhieuBaoTris SET TrangThai=3 WHERE MaPhieu=1;")
    admin_api.send_json("/api/maintenance/1/status", {"staffId": 4, "statusCode": 3}, "PUT")
    automatic = int(sql("SELECT MaPhanCong FROM dbo.PhanCongCongViecs WHERE TuDongTuBaoTri=1;"))
    check(all(t["id"] != automatic for t in staff.get_json("/api/tasks/mine")) and
          staff.get_json("/api/maintenance")[0]["statusCode"] == 3 and
          denied(409, lambda: staff.send_json(f"/api/tasks/{automatic}/status", {"statusCode": 2}, "PUT")),
          "Maintenance work stays on the ticket flow with no duplicate manual row")

    today = date.fromisoformat(sql("SELECT CONVERT(varchar(10),GETDATE(),23);"))
    monday = today - timedelta(days=today.weekday())
    month = today.replace(day=1)
    year = today.replace(month=1, day=1)
    dates = [today, monday - timedelta(days=1), month - timedelta(days=1), year - timedelta(days=1),
             monday + timedelta(days=7), today, today]
    amounts = [11, 22, 44, 88, 176, 352, 704]
    states = [2, 2, 2, 2, 2, 1, 3]
    values = ",".join(f"('{d.isoformat()}T12:00:00',{amount * 1000},{state})"
                      for d, amount, state in zip(dates, amounts, states))
    sql(f"""
        INSERT dbo.HopDongs(MaKhachHang,MaNhanVien,NgayBatDau,NgayKetThuc,TienDaCoc,TongTien,
           TrangThai,SoKyHan,ChuKyKhachHang,ChuKyNhanVien,TrangThaiThanhToan,GhiChu,TrangThaiHoanCoc,
           YeuCauGiaHan,SoNgayGiaHan,YeuCauHuy,TienTraThua,TienGiamTruBaoTri,TienCocBaoDamMay,
           TienThueTraTruoc,YeuCauThanhToanLanDau)
        SELECT 2,1,d,DATEADD(day,2,d),0,amount,status,1,N'',N'',0,N'',0,0,NULL,0,0,0,0,0,0
        FROM (VALUES {values}) rows(d,amount,status);
    """)
    next_month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)
    periods = {"all": (date.min, date.max), "week": (monday, monday + timedelta(days=7)),
               "month": (month, next_month), "year": (year, year.replace(year=year.year + 1))}
    for key, (start, end) in periods.items():
        report = admin_api.get_json(f"/api/reports?timeFilter={key}")
        html = unescape(admin.request(f"/Admin/Home?timeFilter={key}")[0].decode())
        web_amount = int(re.sub(r"\D", "", re.search(r'<div class="stat-value">([^<]*)</div>', html)[1]))
        web_chart = json.loads(re.search(r'var data = (\[[^;]*\]);', html)[1])
        expected = sum(a * 1000 for d, a, state in zip(dates, amounts, states) if start <= d < end and state == 2)
        check(report["revenue"] == web_amount == expected and report["timeFilter"] == key and
              web_chart == [p["value"] for p in report["revenueChart"]] and
              (key == "all" or (sum(web_chart) == expected and report["fromDate"] == start.isoformat())),
              f"Web and Mobile totals and chart agree for {key} using completed contracts and date boundaries")
    check(denied(403, lambda: staff.get_json("/api/reports?timeFilter=week")), "Staff outside management cannot read revenue")


if __name__ == "__main__":
    fixture.check_flows = verify
    fixture.main()
