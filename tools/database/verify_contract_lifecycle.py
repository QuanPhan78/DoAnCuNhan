"""Verify cancellation, return and settlement over HTTP on a disposable database."""
from datetime import date, timedelta
from html import unescape
from urllib.error import HTTPError

import cutover
import verify_debt_status as fixture

web = fixture.web
check = web.require


def verify(db, _secret):
    def sql(query):
        return cutover.sql(query, db)

    sql("""
        INSERT dbo.NguoiDungs(MaVaiTro,HoTen,SoDienThoai,Email,MatKhau,CCCD,DiaChi,TrangThai)
        VALUES (2,N'Lifecycle fixture',N'0900000004',N'lifecycle@demo.invalid',N'Demo@123',N'000000000004',N'',1);
        INSERT dbo.SanPhams(MaLoai,TenSanPham,CauHinh,MoTa,GiaThueNgay,TienCoc,HinhAnh)
        VALUES (1,N'Return fixture',N'',N'',100000,0,N'');
        INSERT dbo.ThietBis(MaSanPham,SoSerial,TinhTrangMay,TrangThai)
        VALUES (2,N'RETURN-FIXTURE',N'',1);
        INSERT dbo.ChiTietHopDongs(MaHopDong,MaThietBi,GiaChotThu) VALUES (3,2,1000000);
    """)
    admin, desktop, app, other, renter = (web.Session() for _ in range(5))
    admin.login("admin@demo.invalid")
    desktop.login("lifecycle@demo.invalid")
    app.api_login("lifecycle@demo.invalid")
    other.api_login("threshold@demo.invalid")
    renter.api_login("customer@demo.invalid")
    today = date.fromisoformat(sql("SELECT CONVERT(varchar(10),GETDATE(),23);"))

    def book(product, offset):
        return int(app.send_json("/api/contracts", {
            "startDate": (today + timedelta(days=offset)).isoformat(),
            "endDate": (today + timedelta(days=offset + 2)).isoformat(),
            "deliveryAddress": "Fixture address",
            "items": [{"productId": product, "quantity": 1}],
        })["contractId"])

    def reject(session, path, body, code, method="POST"):
        try:
            session.send_json(path, body, method)
        except HTTPError as error:
            return error.code == code
        return False

    def status(contract, expected, label, client, requested=False):
        path = f"/api/contracts/{contract}"
        detail = client.get_json(path)
        listed = next(row for row in client.get_json("/api/contracts") if int(row["id"]) == contract)
        search = client.get_json(f"/api/search?q=HD{contract}&type=contract")
        found = next(row["originalData"] for row in search if int(row["id"]) == contract)
        check(all((entry["statusCode"], entry["status"], entry["cancellationRequested"])
                  == (expected, label, requested) for entry in (detail, listed, found)),
              f"List, detail and search agree for contract {contract}: {label}")
        return detail

    def admin_status(contract, next_status):
        return admin.form("/Admin/HopDong/UpdateStatus", {"id": contract, "status": next_status},
                          f"/Admin/HopDong/Details/{contract}")[0].decode()

    cancel_id = book(1, 1)
    other_booking = book(1, 5)
    request = f"/api/contracts/{cancel_id}/cancellation-request"
    desktop_detail = f"/Cart/ContractDetail/{cancel_id}"
    check(reject(other, request, {"reason": "Other account"}, 404) and
          reject(app, request, {"reason": "  "}, 400) and
          reject(app, f"/api/contracts/{other_booking}/cancel", {}, 400, "PUT"),
          "Cancellation requires ownership and a valid reason, including the legacy route")
    check(app.send_json(request, {"reason": "  Changed plans  "})["cancellationReason"] == "Changed plans",
          "Mobile requests cancellation with a trimmed reason")
    original = status(cancel_id, 0, "Yêu cầu hủy", app, requested=True)
    desktop.form("/Cart/YeuCauHuy", {"id": cancel_id, "lyDo": "Overwrite"}, desktop_detail)
    repeated = app.send_json(request, {"reason": "Overwrite again"})
    check(repeated["cancellationRequestedAt"] == original["cancellationRequestedAt"] and
          repeated["cancellationReason"] == original["cancellationReason"] and
          sql("SELECT TrangThai FROM dbo.ThietBis WHERE MaThietBi=1;") == "3" and
          sql(f"SELECT COUNT(*) FROM dbo.PhieuChis WHERE MaHopDong={cancel_id};") == "0",
          "Repeated Web and Mobile submissions preserve the request, stock and payments")
    check("Yêu cầu hủy" in unescape(desktop.request(desktop_detail)[0].decode()) and
          desktop.request(f"/Cart/SignContract/{cancel_id}")[1].endswith(desktop_detail) and
          "Đơn hàng đang chờ duyệt hủy" in unescape(admin_status(cancel_id, 1)) and
          "tiếp nhận trả máy" in unescape(admin_status(cancel_id, 2)),
          "Pending cancellation blocks signing, handover and completion")

    sql(f"""
        UPDATE dbo.HopDongs SET TienDaCoc=100000 WHERE MaHopDong={cancel_id};
        INSERT dbo.PhieuThus(MaHopDong,LoaiPhieu,SoTien,NgayGiaoDich,HinhThucThanhToan,GhiChu,DaHuy)
        VALUES ({cancel_id},1,100000,GETDATE(),0,N'Fixture deposit',0);
    """)
    admin_status(cancel_id, 3)
    admin_status(cancel_id, 3)
    check(status(cancel_id, 3, "Đã hủy", app)["cancellationReason"] == "Changed plans" and
          sql(f"SELECT COUNT(*),SUM(SoTien) FROM dbo.PhieuChis WHERE MaHopDong={cancel_id};") == "1|100000.00" and
          sql("SELECT TrangThai FROM dbo.ThietBis WHERE MaThietBi=1;") == "3",
          "Admin approval refunds the deposit once and preserves the other reservation")

    check(reject(renter, "/api/contracts/3/cancellation-request", {"reason": "Too late"}, 409),
          "An active contract cannot be canceled by the renter")
    admin_status(3, 4)
    status(3, 4, "Đã trả máy (Chờ quyết toán)", renter)
    check(sql("SELECT TrangThai FROM dbo.ThietBis WHERE MaThietBi=2;") == "0",
          "Web return releases the machine")
    new_booking = book(2, 1)
    admin_status(3, 4)
    admin_status(3,2)
    admin_status(3,3)
    check(sql("SELECT TrangThai FROM dbo.HopDongs WHERE MaHopDong=3;") == "4" and
          sql("SELECT COUNT(*) FROM dbo.ContractSettlements WHERE MaHopDong=3;") == "0",
          "Returned contract cannot be closed with unpaid debt or switched to canceled")

    period = sql("SELECT MaKyHan FROM dbo.KyHanThanhToans WHERE MaHopDong=3 AND SoKyHan=1;")
    admin.form("/Admin/HopDong/ConfirmPayment", {
        "maKyHan": period, "soTienThucThu": 1000000, "hinhThuc": 0, "ghiChu": "Fixture payment",
    }, "/Admin/HopDong/Details/3")
    admin_status(3, 2)
    admin_status(3, 2)
    check(status(3, 2, "Hoàn thành", renter)["paymentStatusCode"] == 3 and
          sql("SELECT COUNT(*) FROM dbo.BienBanBanGiaos WHERE MaHopDong=3 AND LoaiBienBan=1;") == "1" and
          sql(f"""SELECT COUNT(*) FROM dbo.ChiTietHopDongs c JOIN dbo.ThietBis d ON c.MaThietBi=d.MaThietBi
                  WHERE c.MaHopDong={new_booking} AND d.MaThietBi=2 AND d.TrangThai=3;""") == "1",
          "Settlement after payment completes the contract, with one slip and the new booking intact")


if __name__ == "__main__":
    fixture.check_flows = verify
    fixture.main()
