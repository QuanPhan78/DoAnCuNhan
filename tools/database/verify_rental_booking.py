"""Verify Web/Mobile checkout parity using the same disposable SQL fixture."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from html import unescape
import json
import re
from threading import Barrier
from urllib.error import HTTPError
from urllib.parse import urlencode

import cutover
import verify_debt_status as fixture

web = fixture.web
check = web.require

def verify(db, _secret):
    sql = lambda query: cutover.sql(query, db)
    sql("""
        INSERT dbo.NguoiDungs(MaVaiTro,HoTen,SoDienThoai,Email,MatKhau,CCCD,DiaChi,TrangThai)
        VALUES (2,N'Booking A',N'0900000004',N'booking@demo.invalid',N'Demo@123',N'000000000004',N'',1);
        INSERT dbo.SanPhams(MaLoai,TenSanPham,CauHinh,MoTa,GiaThueNgay,TienCoc,HinhAnh)
        VALUES (1,N'Parity',N'',N'',170000,0,N''),(1,N'Last device',N'',N'',170000,0,N''),
               (1,N'Unavailable',N'',N'',170000,0,N''),(1,N'Repricing',N'',N'',170000,0,N'');
        INSERT dbo.ThietBis(MaSanPham,SoSerial,TinhTrangMay,TrangThai)
        VALUES (2,N'PARITY-A',N'',0),(2,N'PARITY-B',N'',0),(2,N'PARITY-REPAIR',N'',2),
               (3,N'LAST-REAL',N'',0),(3,N'LAST-BROKEN',N'',4),
               (4,N'ONLY-BROKEN',N'',4),(4,N'ONLY-REPAIR',N'',2),
               (5,N'PRICE-ONE',N'',0),(5,N'PRICE-TWO',N'',0);
        INSERT dbo.KhuyenMais(MaCode,PhanTramGiam,NgayBatDau,NgayKetThuc,SoLuong,KichHoat)
        VALUES (N'PARITY20',20,DATEADD(day,-1,GETDATE()),DATEADD(day,7,GETDATE()),5,1),
               (N'FINAL10',10,DATEADD(day,-1,GETDATE()),DATEADD(day,7,GETDATE()),1,1),
               (N'EXPIRED',10,DATEADD(day,-5,GETDATE()),DATEADD(day,-1,GETDATE()),2,1);
        """)
    desktop, app, admin = (web.Session() for _ in range(3))
    desktop.login("booking@demo.invalid")
    app.api_login("booking@demo.invalid")
    admin.login("admin@demo.invalid")
    today = date.fromisoformat(sql("SELECT CONVERT(varchar(10),GETDATE(),23);"))
    start = today + timedelta(days=20)
    end = start + timedelta(days=7)

    def payload(product, first=start, last=end, promo=None):
        return {"startDate": first.isoformat(), "endDate": last.isoformat(),
                "deliveryAddress": "Fixture address", "promoCode": promo,
                "items": [{"productId": product, "quantity": 1, "rentalPrice": 1, "subtotal": 1}],
                "estimatedAmount": 1, "rentalType": "Theo tháng", "depositAmount": 999999,
                "installmentCount": 30, "customerId": "3"}

    def fields(order):
        return {"NgayBatDau": order["startDate"], "NgayKetThuc": order["endDate"],
                "DiaChi": order["deliveryAddress"], "PromoCode": order["promoCode"] or ""}

    def api_error(path, order, expected, session=app):
        try:
            session.send_json(path, order)
        except HTTPError as error:
            assert error.code == expected, (error.code, error.read().decode())
            return json.loads(error.read())
        raise AssertionError(f"{path} should reject the booking")

    order = payload(2, promo=" parity20 ")
    desktop.request("/Cart/AddToCart/2")
    web_quote = json.loads(desktop.form("/Cart/Quote", fields(order), "/Cart/Checkout")[0])
    api_quote = app.send_json("/api/contracts/quote", order)
    check(web_quote == api_quote and api_quote["rentalDays"] == 7 and api_quote["subtotal"] == 1190000
          and api_quote["discountAmount"] == 238000 and api_quote["totalAmount"] == 952000,
          "Web and Mobile quote the same 7-day rental and validated promo; client prices are ignored")
    check(sql("SELECT SoLuong FROM dbo.KhuyenMais WHERE MaCode=N'PARITY20';") == "5", "Quoting does not use promo quota")
    form = {**fields(order), "ExpectedTotal": api_quote["totalAmount"]}
    _, web_url, _ = desktop.form("/Cart/Checkout", form)
    web_id = int(re.search(r"/SignContract/(\d+)", web_url).group(1))
    created = app.send_json("/api/contracts", {**order, "expectedTotal": api_quote["totalAmount"]})
    app_id = int(created["contractId"])
    check(created["customerId"] == "4" and created["totalAmount"] == 952000 and created["deviceCount"] == 1,
          "API uses the authenticated customer, current price and real inventory")
    check(sql(f"""SELECT COUNT(*) FROM dbo.HopDongs
        WHERE MaHopDong IN ({web_id},{app_id}) AND TongTien=952000 AND TrangThai=0 AND TrangThaiThanhToan=0
        AND NgayKy IS NULL AND HanChotKy IS NOT NULL AND ChuKyKhachHang=N'' AND ChuKyNhanVien=N''
        AND SoKyHan=1 AND TienDaCoc=0 AND YeuCauThanhToanLanDau=0;""") == "2" and
          sql(f"SELECT COUNT(*) FROM dbo.KyHanThanhToans WHERE MaHopDong IN ({web_id},{app_id});") == "0" and
          sql(f"""SELECT COUNT(DISTINCT MaThietBi) FROM dbo.ChiTietHopDongs
                 WHERE MaHopDong IN ({web_id},{app_id}) AND GiaChotThu=1190000;""") == "2" and
          sql("SELECT SoLuong FROM dbo.KhuyenMais WHERE MaCode=N'PARITY20';") == "3",
          "Both orders persist the same pending state, no signature date or installment, and use distinct machines")

    before = sql("SELECT (SELECT COUNT(*) FROM dbo.HopDongs),(SELECT COUNT(*) FROM dbo.ThietBis);")
    api_error("/api/contracts", order, 409)
    api_error("/api/contracts", payload(4), 409)
    api_error("/api/contracts", payload(999), 400)
    api_error("/api/contracts", payload(5, end, start), 400)
    api_error("/api/contracts", payload(5, today - timedelta(days=1), end), 400)
    api_error("/api/contracts", payload(5, promo="EXPIRED"), 400)
    check(sql("SELECT (SELECT COUNT(*) FROM dbo.HopDongs),(SELECT COUNT(*) FROM dbo.ThietBis);") == before and
          sql("SELECT SoLuong FROM dbo.KhuyenMais WHERE MaCode=N'PARITY20';") == "3",
          "Rejected bookings add no contracts, equipment or promo consumption")

    next_booking = app.send_json("/api/contracts", payload(2, end, end + timedelta(days=1)))
    check(next_booking["rentalDays"] == 1, "A new rental can start on the previous return date")

    request = payload(3, start, start)
    race_web = web.Session()
    race_web.login("booking@demo.invalid")
    race_web.request("/Cart/AddToCart/3")
    page = race_web.request("/Cart/Checkout")[0].decode()
    token = web.Inputs(page).values["__RequestVerificationToken"]
    wire = urlencode({**fields(request), "__RequestVerificationToken": token}).encode()
    barrier = Barrier(2)
    def submit_web():
        barrier.wait()
        return race_web.request("/Cart/Checkout", wire, "POST", "application/x-www-form-urlencoded")[1]
    def submit_app():
        barrier.wait()
        try:
            return app.send_json("/api/contracts", request)["success"]
        except HTTPError as error:
            assert error.code == 409, (error.code, error.read().decode())
            return False
    with ThreadPoolExecutor(2) as workers:
        web_result, app_result = workers.submit(submit_web), workers.submit(submit_app)
        winner_on_web = "/SignContract/" in web_result.result()
        check(winner_on_web != app_result.result(), "Concurrent Web and Mobile requests have exactly one winner")
    check(sql("""SELECT COUNT(*) FROM dbo.ChiTietHopDongs c JOIN dbo.ThietBis d ON d.MaThietBi=c.MaThietBi
        WHERE d.SoSerial=N'LAST-REAL';""") == "1", "A same-day rental reserves one real machine for the whole day")
    api_error("/api/contracts", payload(3, start, start + timedelta(days=1)), 409)

    promo_race = payload(5, start, end, "FINAL10")
    def use_last_promo(_):
        try:
            return app.send_json("/api/contracts", promo_race)["success"]
        except HTTPError as error:
            assert error.code == 409, (error.code, error.read().decode())
            return False
    with ThreadPoolExecutor(2) as workers:
        results = list(workers.map(use_last_promo, range(2)))
    check(sum(results) == 1 and sql("SELECT SoLuong FROM dbo.KhuyenMais WHERE MaCode=N'FINAL10';") == "0",
          "Two available machines still consume the last promo quota only once")

    price_request = payload(5, end, end + timedelta(days=2))
    old = app.send_json("/api/contracts/quote", price_request)
    sql("UPDATE dbo.SanPhams SET GiaThueNgay=175000 WHERE MaSanPham=5;")
    problem = api_error("/api/contracts", {**price_request, "expectedTotal": old["totalAmount"]}, 409)
    check("Giá thuê đã thay đổi" in problem["message"], "Changed price requires confirming a fresh quote")

    sign_path = f"/Cart/SignContract/{app_id}"
    signature = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/n2cAAAAASUVORK5CYII="
    admin.form("/Admin/HopDong/AdminSign",
        {"id": app_id, "signatureData": "data:image/png;base64," + signature},
        f"/Admin/HopDong/Details/{app_id}")
    check(sql(f"SELECT COUNT(*) FROM dbo.HopDongs WHERE MaHopDong={app_id} AND NgayKy IS NULL AND ChuKyNhanVien<>N'';") == "1",
          "The staff signature alone does not set the customer's signature date")
    from base64 import b64decode
    image = b64decode(signature)
    web.multipart(desktop, "/Cart/SignContract", sign_path,
        {"id": app_id, "soKyHan": 1, "signatureData": "data:image/png;base64," + signature},
        {"cmndTruocFile": ("front.png", "image/png", image), "cmndSauFile": ("back.png", "image/png", image)})
    check(sql(f"SELECT COUNT(*) FROM dbo.HopDongs WHERE MaHopDong={app_id} AND NgayKy IS NOT NULL AND ChuKyKhachHang<>N'';") == "1",
          "A Mobile-created contract gets its date only after the customer signs on Web")

if __name__ == "__main__":
    fixture.check_flows = verify
    fixture.main()
