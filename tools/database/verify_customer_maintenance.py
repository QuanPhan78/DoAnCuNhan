"""Exercise actual incident uploads, acceptance and ratings across Web and API."""
from base64 import b64decode
import json
from urllib.error import HTTPError
from uuid import uuid4

import cutover
import verify_debt_status as fixture

web = fixture.web
check = web.require
PNG = b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=")


def upload(session, path, fields, field_name, content):
    boundary = uuid4().hex
    data = b"".join(
        f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode()
        for key, value in fields.items()
    )
    if content is not None:
        data += (f'--{boundary}\r\nContent-Disposition: form-data; name="{field_name}"; filename="fixture.png"\r\n'
                 'Content-Type: image/png\r\n\r\n').encode() + content + b'\r\n'
    data += f'--{boundary}--\r\n'.encode()
    return session.request(path, data, "POST", f"multipart/form-data; boundary={boundary}")


def verify(db, _secret):
    def sql(query):
        return cutover.sql(query, db)

    sql("""
        INSERT dbo.VaiTros(TenVaiTro) VALUES (N'KyThuat');
        INSERT dbo.NguoiDungs(MaVaiTro,HoTen,SoDienThoai,Email,MatKhau,CCCD,DiaChi,TrangThai)
        VALUES (3,N'Technician',N'0900000004',N'tech@demo.invalid',N'Demo@123',N'000000000004',N'',1);
        INSERT dbo.ThietBis(MaSanPham,SoSerial,TinhTrangMay,TrangThai)
        VALUES (1,N'WEB-REPORT',N'',1),(1,N'OTHER-MACHINE',N'',0);
        INSERT dbo.ChiTietHopDongs(MaHopDong,MaThietBi,GiaChotThu) VALUES (1,1,100000),(1,2,100000);
    """)
    customer, other, technician, admin, customer_web, admin_web = (web.Session() for _ in range(6))
    for session, account in ((customer, "customer"), (other, "threshold"),
                             (technician, "tech"), (admin, "admin")):
        session.api_login(f"{account}@demo.invalid")
    customer_web.login("customer@demo.invalid")
    admin_web.login("admin@demo.invalid")

    def rejects(expected, operation):
        try:
            operation()
        except HTTPError as error:
            return error.code == expected
        return False

    fields = {"contractId": 1, "deviceId": 1, "description": "Máy mất kết nối", "severity": "Nghiêm trọng"}

    def report(session, overrides=None, content=PNG):
        return upload(session, "/api/maintenance", {**fields, **(overrides or {})}, "images", content)

    check(rejects(404, lambda: report(other)) and
          rejects(400, lambda: report(customer, {"deviceId": 3})) and
          rejects(409, lambda: report(other, {"contractId": 7})) and
          rejects(400, lambda: report(customer, content=b"not an image")),
          "Multipart refuses another renter, wrong machine, pending contract and fake image")
    check(not (web.OUT / "wwwroot/uploads/baotri").exists(), "Rejected requests leave no evidence files")
    contract = next(row for row in customer.get_json("/api/contracts") if row["id"] == "1")
    check({(device["deviceId"], device["serialNumber"]) for device in contract["devices"]}
          == {("1", "DEBT-FIXTURE"), ("2", "WEB-REPORT")}, "Mobile can select exact serials with real device IDs")

    created = json.loads(report(customer)[0])
    ticket = int(created["id"])
    path = f"/api/maintenance/{ticket}"
    image = created["imagePaths"][0]
    check(customer.request(image)[0] == PNG and
          customer.get_json(path)["imagePaths"] == [image] and
          image in admin_web.request(f"/Admin/BaoTri/Details/{ticket}")[0].decode() and
          image in customer_web.request(f"/BaoTri/ChiTiet/{ticket}")[0].decode(),
          "Uploaded bytes, API detail and Web images match")

    form_page = "/BaoTri/TaoPhieu?hopDongId=1"
    token = web.Inputs(customer_web.request(form_page)[0].decode()).values["__RequestVerificationToken"]
    upload(customer_web, "/BaoTri/TaoPhieu", {"__RequestVerificationToken": token,
        "maHopDong": 1, "maThietBi": 2, "moTaLoi": "Báo từ Web", "mucDoKhanCap": 1}, "hinhAnhSuCo", PNG)
    second = next(row for row in customer.get_json("/api/maintenance") if row["deviceId"] == "2")
    check(customer.request(second["imagePaths"][0])[0] == PNG, "Web uploaded evidence appears in the Mobile API")

    admin.send_json(path + "/status", {"staffId": 4, "statusCode": 1}, "PUT")
    technician.send_json(path + "/status", {"statusCode": 2}, "PUT")
    technician.send_json(path + "/status", {"statusCode": 3, "result": "Đã thay cáp"}, "PUT")
    check(rejects(409, lambda: report(customer)), "A ticket awaiting acceptance prevents duplicate reporting")
    search = customer.get_json(f"/api/search?q=SC-{ticket}&type=maintenance")
    check(any(row["id"] == str(ticket) and row["type"] == "incident" and
              row["status"] == "Chờ nghiệm thu" and row["originalData"]["statusCode"] == 3 for row in search),
          "Customer search reports the acceptance state and opens the incident detail")
    accept = path + "/acceptance"
    check(rejects(404, lambda: other.send_json(accept, {"accepted": True}, "PUT")) and
          rejects(403, lambda: technician.send_json(accept, {"accepted": True}, "PUT")) and
          rejects(400, lambda: customer.send_json(accept, {"accepted": False}, "PUT")),
          "Only the owner can accept and rejection requires a reason")
    rated = customer.send_json(path + "/rating", {"rating": 4, "feedback": "Phản hồi riêng"}, "PUT")
    task = sql(f"""SELECT MaPhanCong,TrangThai FROM dbo.PhanCongCongViecs
        WHERE MaPhieuBaoTri={ticket} AND TuDongTuBaoTri=1;""")
    check(rated["statusCode"] == 3 and rated["rating"] == 4 and task.endswith("|1") and
          "Phản hồi riêng" not in customer.get_json(path)["result"],
          "Rating stores separate feedback and leaves ticket and work open")
    rejected = customer.send_json(accept, {"accepted": False, "feedback": "Lỗi tái diễn"}, "PUT")
    check(rejected["statusCode"] == 2 and rejected["rating"] == 4 and
          "Lỗi tái diễn" in customer.get_json(path)["result"] and
          sql(f"SELECT MaPhanCong,TrangThai FROM dbo.PhanCongCongViecs WHERE MaPhieuBaoTri={ticket};") == task,
          "Mobile rejection reopens the same assigned work and retains the rating")
    technician.send_json(path + "/status", {"statusCode": 3}, "PUT")
    customer_web.form("/BaoTri/NghiemThu", {"maPhieu": ticket, "dongY": "true", "yKien": "Đã kiểm tra lại"},
                      f"/BaoTri/ChiTiet/{ticket}")
    result = customer.get_json(path)
    check(result["statusCode"] == 5 and result["rating"] == 4 and result["feedback"] == "Phản hồi riêng" and
          sql(f"SELECT MaPhanCong,TrangThai FROM dbo.PhanCongCongViecs WHERE MaPhieuBaoTri={ticket};") == task[:-1] + "2" and
          sql("SELECT TrangThai FROM dbo.ThietBis WHERE MaThietBi=1;") == "1",
          "Web acceptance closes the existing work, preserves feedback and restores the rented device")

    second_path = f"/api/maintenance/{second['id']}"
    admin.send_json(second_path + "/status", {"staffId": 4, "statusCode": 1}, "PUT")
    technician.send_json(second_path + "/status", {"statusCode": 2}, "PUT")
    technician.send_json(second_path + "/status", {"statusCode": 3}, "PUT")
    check(customer.send_json(second_path + "/acceptance", {"accepted": True}, "PUT")["statusCode"] == 5 and
          rejects(409, lambda: customer.send_json(second_path + "/acceptance", {"accepted": True}, "PUT")),
          "Mobile accepts without requiring a rating and repeat acceptance is refused")
    new_ticket = json.loads(report(customer, content=None)[0])
    check(new_ticket["id"] != str(ticket) and new_ticket["imagePaths"] == [],
          "A new incident after closure can be reported without attaching an image")


if __name__ == "__main__":
    fixture.check_flows = verify
    fixture.main()
