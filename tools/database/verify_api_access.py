"""Rehearse API authentication and ownership on a disposable SQL database."""
from urllib.error import HTTPError

import cutover
import verify_debt_status as fixture

web = fixture.web
check = web.require

def denied(session, path, status, method="GET", body=None):
    try:
        if body is None:
            session.request(path, method=method)
        else:
            session.send_json(path, body, method)
    except HTTPError as error:
        check(error.code == status, f"{method} {path.split('?')[0]} rejects request with {status} (got {error.code})")
    else:
        raise AssertionError(f"{method} {path} should return {status}")

def verify(db, _secret):
    cutover.sql("""
        INSERT dbo.VaiTros(TenVaiTro) VALUES(N'KyThuat'), (N'KinhDoanh');
        INSERT dbo.NguoiDungs(MaVaiTro,HoTen,SoDienThoai,Email,MatKhau,CCCD,DiaChi,TrangThai)
        VALUES (3,N'Tech A',N'0900000004',N'tech-a@demo.invalid',N'Demo@123',N'000000000004',N'',1),
               (3,N'Tech B',N'0900000005',N'tech-b@demo.invalid',N'Demo@123',N'000000000005',N'',1),
               (4,N'Sales',N'0900000006',N'sales@demo.invalid',N'Demo@123',N'000000000006',N'',1);
        INSERT dbo.ChiTietHopDongs(MaHopDong,MaThietBi,GiaChotThu) VALUES (1,1,100000);
        """, db)
    guest, customer, other, technician, second, admin, sales = (web.Session() for _ in range(7))
    for session, email in zip((customer, other, technician, second, admin, sales),
                              ("customer", "threshold", "tech-a", "tech-b", "admin", "sales")):
        session.api_login(f"{email}@demo.invalid")

    for path in ("/api/auth/me", "/api/contracts?userId=2&role=Admin",
                 "/api/contracts/1/html?userId=2&role=Admin", "/api/maintenance",
                 "/api/search?q=Customer", "/api/dashboard/stats", "/api/reports", "/api/promotions"):
        denied(guest, path, 401)
    denied(guest, "/api/contracts/1/cancel", 401, "PUT")
    denied(guest, "/api/auth/change-password", 401, "POST", {})
    guest.access_token = "token_mock_legacy"
    denied(guest, "/api/auth/me", 401)
    real_token = customer.access_token
    midpoint = len(real_token) // 2
    guest.access_token = real_token[:midpoint] + ("A" if real_token[midpoint] != "A" else "B") + real_token[midpoint + 1:]
    denied(guest, "/api/auth/me", 401)

    check(customer.get_json("/api/auth/me")["id"] == "2" and
          customer.get_json("/api/auth/profile/2")["id"] == "2", "Current profile is derived from bearer token")
    denied(customer, "/api/auth/profile/3", 403)
    denied(customer, "/api/auth/profile/3", 403, "PUT", {"name": "Invalid change"})
    denied(customer, "/api/auth/change-password", 403, "POST",
           {"userId": 3, "oldPassword": "Demo@123", "newPassword": "WrongTarget", "confirmPassword": "WrongTarget"})

    check(all(c["customerId"] == "2" for c in customer.get_json("/api/contracts?userId=3&role=Admin")),
          "Forged query role and account do not expand customer contract list")
    denied(other, "/api/contracts/1?userId=2&role=Admin", 404)
    denied(other, "/api/contracts/1/html?userId=2&role=Admin", 404)
    check(customer.request("/api/contracts/1/html")[0], "Owner can open the API contract print view")
    denied(other, "/api/contracts/1/cancel", 404, "PUT")
    denied(other, "/api/contracts/1/renew", 404, "POST", {"duration": "7 ngày"})
    denied(customer, "/api/contracts/1/cancel", 409, "PUT")
    denied(technician, "/api/contracts", 403, "POST", {})
    check(len(admin.get_json("/api/contracts")) == len(sales.get_json("/api/contracts")),
          "Manager roles can view contracts according to server claims")
    check(customer.get_json("/api/search?q=Threshold&type=contract&role=Admin") == [],
          "Search cannot expose contracts belonging to another customer")
    dashboard = customer.get_json("/api/dashboard/stats?userId=3&role=Admin")
    check(dashboard["staffStats"] is None and dashboard["adminStats"] is None,
          "Dashboard hides staff and management statistics from customers")
    denied(customer, "/api/reports?role=Admin", 403)
    denied(technician, "/api/reports?role=Admin", 403)
    check("revenue" in admin.get_json("/api/reports"), "Manager can access reports")

    cutover.sql("UPDATE dbo.KyHanThanhToans SET TrangThai=1 WHERE MaHopDong=1;", db)
    dates = cutover.sql("SELECT CONVERT(varchar(10),DATEADD(day,30,GETDATE()),23), "
                       "CONVERT(varchar(10),DATEADD(day,31,GETDATE()),23);", db).split("|")
    new_contract = customer.send_json("/api/contracts", {
        "customerId": "3", "maKhachHang": 3, "deviceId": "1",
        "startDate": dates[0], "endDate": dates[1], "deliveryAddress": "Fixture",
    })
    check(new_contract["customerId"] == "2", "Contract creation binds owner to the token")
    denied(other, "/api/maintenance", 404, "POST", {"contractId": "1", "deviceId": "1"})
    denied(customer, "/api/maintenance", 400, "POST", {"contractId": "1", "deviceId": "999"})
    denied(customer, "/api/maintenance", 409, "POST", {"contractId": new_contract["contractId"], "deviceId": "1"})
    ticket = customer.send_json("/api/maintenance", {"contractId": "1", "deviceId": "Device (DEBT-FIXTURE)"})
    ticket_id = ticket["id"]
    detail = f"/api/maintenance/{ticket_id}"
    update = detail + "/status"
    denied(other, detail, 404)
    denied(technician, update, 404, "PUT", {"statusCode": 2})
    denied(customer, update, 403, "PUT", {"statusCode": 2})
    denied(customer, detail + "/rating", 409, "PUT", {"rating": 5})
    admin.send_json(update, {"statusCode": 1, "staffId": 4}, "PUT")
    check(any(p["id"] == ticket_id for p in technician.get_json("/api/maintenance")) and
          all(p["id"] != ticket_id for p in second.get_json("/api/maintenance?role=Admin&userId=4")) and
          any(h["id"] == "1" for h in technician.get_json("/api/contracts")) and not second.get_json("/api/contracts"),
          "Assignment scopes ticket and related contract to the assigned technician")
    denied(second, update, 404, "PUT", {"statusCode": 2})
    denied(technician, update, 403, "PUT", {"statusCode": 2, "staffId": 5})
    denied(technician, update, 403, "PUT", {"statusCode": 2, "compensationFee": 1000})
    check(technician.send_json(update, {"statusCode": 2}, "PUT")["statusCode"] == 2,
          "Assigned technician can start repair")
    admin.send_json(update, {"statusCode": 2, "staffId": 5}, "PUT")
    denied(technician, update, 404, "PUT", {"statusCode": 3})
    technician.login("tech-a@demo.invalid")
    denied(technician, f"/Admin/BaoTri/Details/{ticket_id}", 404)
    for action, values in (("UpdateStatus", {"status": 3}), ("ApDungTamDungTienThue", {"soNgayTamDung": 1})):
        try:
            technician.form(f"/Admin/BaoTri/{action}", {"id": ticket_id, **values}, "/Account/Profile")
        except HTTPError as error:
            check(error.code == 404, f"Former assignee cannot call Web action {action}")
        else:
            raise AssertionError(f"Former assignee can call Web action {action}")
    check(second.send_json(update, {"statusCode": 3}, "PUT")["statusCode"] == 3,
          "New assignee can finish repair after reassignment")
    denied(other, detail + "/rating", 404, "PUT", {"rating": 5})
    check(customer.send_json(detail + "/rating", {"rating": 5}, "PUT")["success"] and
          customer.get_json(detail)["statusCode"] == 3, "Owner can rate without closing the ticket")

    before = customer.access_token
    rotated = customer.send_json("/api/auth/change-password", {
        "oldPassword": "Demo@123", "newPassword": "Changed@123", "confirmPassword": "Changed@123",
    })
    customer.access_token = rotated["token"]["accessToken"]
    check(customer.get_json("/api/auth/me")["id"] == "2", "Password change returns a replacement token")
    guest.access_token = before
    denied(guest, "/api/auth/me", 401)
    cutover.sql("UPDATE dbo.NguoiDungs SET MaVaiTro=2 WHERE MaNguoiDung=6;", db)
    denied(sales, "/api/reports", 403)
    cutover.sql("UPDATE dbo.NguoiDungs SET TrangThai=0 WHERE MaNguoiDung=5;", db)
    denied(second, detail, 401)
    registration = guest.send_json("/api/auth/register", {
        "name": "Registration", "email": "new@demo.invalid", "phone": "0900000007",
        "password": "New@123", "cccd": "000000000007",
    })
    guest.access_token = registration["token"]["accessToken"]
    check(guest.get_json("/api/auth/me")["roleCode"] == "KhachHang", "Registration issues a usable customer session")
    web_admin = web.Session()
    web_admin.login("admin@demo.invalid")
    check(web_admin.request("/Admin/PhanCong")[0], "Existing Web cookie still authenticates Web routes")
    denied(web_admin, "/api/contracts", 401)

if __name__ == "__main__":
    fixture.check_flows = verify
    fixture.main()
