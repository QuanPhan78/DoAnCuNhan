"""Exercise debt views and payment updates against a fresh, disposable SQL database."""
import hashlib
import hmac
from html import unescape
from io import BytesIO
import os
from pathlib import Path
import re
import socket
import sys
import tempfile
from urllib.parse import urlencode
import uuid
from zipfile import ZipFile

import cutover

sys.path.insert(0, str(cutover.ROOT / "tools/demo"))
import verify_demo as web

FIXTURE = """
INSERT dbo.VaiTros(TenVaiTro) VALUES(N'Admin'), (N'KhachHang');
INSERT dbo.NguoiDungs(MaVaiTro, HoTen, SoDienThoai, Email, MatKhau, CCCD, DiaChi, TrangThai)
VALUES (1,N'Admin',N'0900000001',N'admin@demo.invalid',N'Demo@123',N'000000000001',N'',1),
       (2,N'Customer',N'0900000002',N'customer@demo.invalid',N'Demo@123',N'000000000002',N'',1),
       (2,N'Threshold',N'0900000003',N'threshold@demo.invalid',N'Demo@123',N'000000000003',N'',1);
DECLARE @today date=GETDATE();
INSERT dbo.HopDongs(MaKhachHang,MaNhanVien,NgayBatDau,NgayKetThuc,TienDaCoc,TongTien,
    TrangThai,SoKyHan,ChuKyKhachHang,ChuKyNhanVien,TrangThaiThanhToan,GhiChu,TrangThaiHoanCoc,
    YeuCauGiaHan,SoNgayGiaHan,YeuCauHuy,TienTraThua,TienGiamTruBaoTri,TienCocBaoDamMay,
    TienThueTraTruoc,YeuCauThanhToanLanDau)
SELECT v.customer,1,DATEADD(day,-10,@today),DATEADD(day,10,@today),v.deposit,v.rent,
    v.lifecycle,v.periods,N'',N'',v.payment,N'',0,v.extension,
    CASE WHEN v.extension=1 THEN 2 END,0,0,0,0,0,v.first_payment
FROM (VALUES
 (2,0,10000000,1,10,2,0,0), (3,0,4000000,1,1,0,0,0), (2,0,1000000,1,1,0,1,0),
 (2,600000,1000000,1,1,1,0,0), (2,100000,1000000,1,1,1,0,0), (2,0,0,1,0,2,0,0),
 (3,0,4000000,0,1,0,0,1), (2,100000,1000000,1,0,1,0,0), (2,0,0,1,0,3,0,0),
 (2,0,1000000,1,0,99,0,0), (2,0,1000000,1,0,0,0,0)
) v(customer,deposit,rent,lifecycle,periods,payment,extension,first_payment);
INSERT dbo.KyHanThanhToans(MaHopDong,SoKyHan,NgayDenHan,SoTienPhai,SoTienDaTra,TrangThai,
    GhiChu,TrangThaiXacNhan,PhiPhatTreHan,TienPhat,SoNgayTreHan,NhomTuoiNo)
SELECT v.contract,v.period,DATEADD(day,v.offset_days,@today),v.amount,v.paid,v.status,N'',0,0,0,0,0
FROM (VALUES
 (1,1,-30,1000000,200000,0),(1,2,-31,100000,0,0),(1,3,-60,100000,0,0),
 (1,4,-61,100000,0,0),(1,5,-90,100000,0,0),(1,6,-91,100000,0,0),
 (1,7,0,100000,0,0),(1,8,12,100000,0,0),(1,9,-25,100000,100000,1),(1,10,-25,100000,0,3),
 (2,1,-15,100000,0,0),(3,1,4,1000000,0,0),(3,2,8,1000000,0,3),
 (4,1,4,1000000,0,0),(5,1,4,1000000,0,0),(7,1,-20,4000000,0,0)
) v(contract,period,offset_days,amount,paid,status);
INSERT dbo.PhieuThus(MaHopDong,LoaiPhieu,SoTien,NgayGiaoDich,HinhThucThanhToan,GhiChu,DaHuy)
VALUES (1,0,200000,GETDATE(),0,N'Fixture partial payment',0),
       (4,1,600000,GETDATE(),0,N'Fixture collected deposit',0),
       (5,1,100000,GETDATE(),0,N'Fixture collected deposit',0);
INSERT dbo.LoaiThietBis(TenLoai) VALUES(N'Fixture');
INSERT dbo.SanPhams(MaLoai,TenSanPham,CauHinh,MoTa,GiaThueNgay,TienCoc,HinhAnh)
VALUES(1,N'Device',N'',N'',100000,0,N'');
INSERT dbo.ThietBis(MaSanPham,SoSerial,TinhTrangMay,TrangThai) VALUES(1,N'DEBT-FIXTURE',N'',0);
INSERT dbo.PhieuBaoTris(MaHopDong,MaThietBi,MoTaLoi,NgayBaoLoi,GhiChuSuaChua,PhiDenBu,
    TrangThai,DaGhiNhanCongNo,DaNghiemThu,TamDungTinhTien,DaTruTien)
VALUES (6,1,N'Damages',GETDATE(),N'',250000,5,1,1,0,0);
"""

def check_flows(db, secret):
    admin, customer, threshold, api = (web.Session() for _ in range(4))
    admin.login("admin@demo.invalid")
    customer.login("customer@demo.invalid")
    threshold.login("threshold@demo.invalid")
    api.api_login("admin@demo.invalid")
    check = web.require
    admin_page = "/Admin/CongNo"
    customer_page = "/Account/MyDebt"

    def html(session, path):
        return unescape(session.request(path)[0].decode("utf-8"))

    def installment_ids(content):
        return set(map(int, re.findall(r'data-installment-id="(\d+)"', content)))

    def installment(contract, period):
        return int(cutover.sql(f"SELECT MaKyHan FROM dbo.KyHanThanhToans WHERE MaHopDong={contract} AND SoKyHan={period};", db))

    main_ids = {period: installment(1, period) for period in range(1, 11)}
    main = html(admin, admin_page)
    check('nav-link active" href="/Admin/CongNo?activeTab=overdue"' in main and
          {main_ids[i] for i in range(1, 7)} <= installment_ids(main), "Admin opens on overdue installments")
    check(main_ids[9] not in installment_ids(main) and main_ids[10] not in installment_ids(main) and
          "Khóa thuê" not in main and "Phân bổ Tuổi nợ" not in main and
          "<details" in main and re.search(r"250\D?000", main),
          "Debt excludes paid/cancelled periods and retains damages without a schedule")
    check(installment(7, 1) not in installment_ids(main), "Pending first payment is outside ordinary debt")
    for tier, expected in enumerate(({1}, {2, 3}, {4, 5}, {6}), start=1):
        filtered = html(admin, f"{admin_page}?search=Customer&agingTier={tier}")
        check(installment_ids(filtered) == {main_ids[i] for i in expected} and
              "Đang hạn chế thuê tiếp" in filtered, f"Age group {tier} filters individual rows")
    upcoming = html(admin, admin_page + "?activeTab=upcoming")
    seven = html(admin, admin_page + "?activeTab=upcoming&dueSoon=true")
    check({main_ids[7], main_ids[8]} <= installment_ids(upcoming) and
          main_ids[7] in installment_ids(seven) and main_ids[8] not in installment_ids(seven),
          "Today is not overdue and the seven-day filter excludes later periods")

    report = admin.request(admin_page + "/ExportExcel?agingTier=1")[0]
    with ZipFile(BytesIO(report)) as workbook:
        strings = workbook.read("xl/sharedStrings.xml").decode()
        check(all(s in strings for s in ("Tuổi nợ cao nhất", "Trên 90 ngày", "Còn nợ", "HD1")) and
              "HD6" not in strings, "Excel filters by matching period and shows the highest age per contract")

    mine = html(customer, customer_page)
    check({main_ids[i] for i in range(1, 9)} <= installment_ids(mine) and
          not {main_ids[9], main_ids[10]} & installment_ids(mine) and
          "Tuổi nợ" not in mine and "Chưa quá hạn" in mine and "Đang hạn chế thuê tiếp" in mine,
          "Customer debt has two groups and no ageing column")
    check(f"openVietQrModal(1, {main_ids[1]}, 824000, 'HD1 KY1'" in mine,
          "VietQR keeps 800,000 principal plus 24,000 penalty after partial payment")
    reminder = admin.form(admin_page + "/GuiNhacNo", {"maKyHan": main_ids[1]}, admin_page)[0]
    check(b'"success":true' in reminder and cutover.sql(
        f"SELECT COUNT(*) FROM dbo.LichSuNhacNos WHERE MaKyHan={main_ids[1]} AND SoTienNhac=824000;", db) == "1",
        "Reminder retains its history and exact amount")

    for days, amount, blocked in ((15, 100000, False), (16, 100000, True),
                                   (1, 3000000, False), (1, 3000001, True), (0, 4000000, False)):
        cutover.sql(f"""UPDATE dbo.KyHanThanhToans
            SET NgayDenHan=DATEADD(day,-{days},CONVERT(date,GETDATE())), SoTienPhai={amount},
                TrangThai=0, TienPhat=0, PhiPhatTreHan=0, SoNgayTreHan=0, NhomTuoiNo=0
            WHERE MaHopDong=2;""", db)
        checkout = threshold.request("/Cart/Checkout")[1].endswith(customer_page)
        mine = "Đang hạn chế thuê tiếp" in html(threshold, customer_page)
        admin_flag = "Đang hạn chế thuê tiếp" in html(admin, admin_page + "?search=Threshold")
        check(checkout == mine == admin_flag == blocked, f"Checkout and both warnings agree for {days} days, {amount}")

    labels = {0: "Chưa thanh toán", 1: "Đã đặt cọc", 2: "Còn nợ", 3: "Đã tất toán", 99: "Chưa xác định"}
    listing = {int(item["id"]): item for item in api.get_json("/api/contracts")}
    for contract, code in ((11, 0), (8, 1), (1, 2), (9, 3), (10, 99)):
        detail = api.get_json(f"/api/contracts/{contract}")
        check(all((entry["paymentStatusCode"], entry["paymentStatus"]) == (code, labels[code])
                  for entry in (detail, listing[contract])) and
              (code == 99 or labels[code] in html(customer, f"/Cart/ContractDetail/{contract}")),
              f"Payment status {code} is consistent on Web and both API routes")

    def vnpay(contract, period, amount, tx):
        query = urlencode(sorted({
            "vnp_Amount": amount * 100, "vnp_ResponseCode": "00",
            "vnp_TransactionNo": tx, "vnp_TxnRef": f"{contract}_{period}",
        }.items()))
        signature = hmac.new(secret.encode(), query.encode(), hashlib.sha512).hexdigest()
        return api.get_json(f"/Payment/VnPayIPN?{query}&vnp_SecureHash={signature}")["rspCode"]

    period = installment(3, 1)
    check(vnpay(3, installment(3, 2), 10000, "fixture-cancelled") == "01", "VNPay leaves cancelled period untouched")
    check(vnpay(3, period, 400000, "fixture-part") == "00" and
          api.get_json("/api/contracts/3")["paymentStatusCode"] == 2, "VNPay partial payment leaves debt")
    check(vnpay(3, period, 400000, "fixture-part") == "02" and
          vnpay(3, period, 600000, "fixture-full") == "00" and
          api.get_json("/api/contracts/3")["paymentStatusCode"] == 3 and
          cutover.sql("SELECT COUNT(*) FROM dbo.PhieuThus WHERE MaHopDong=3;", db) == "2",
          "VNPay full payment settles contract and duplicate callback adds no receipt")
    admin.form("/Admin/HopDong/DuyetGiaHan", {"id": 3, "chapNhan": "true"}, admin_page)
    check(api.get_json("/api/contracts/3")["paymentStatusCode"] == 2 and
          cutover.sql("SELECT COUNT(*) FROM dbo.KyHanThanhToans WHERE MaHopDong=3 AND TrangThai=0;", db) == "1",
          "Extension creates a new unpaid installment on a settled contract")

    today = cutover.sql("SELECT CONVERT(varchar(10),GETDATE(),23);", db)
    for contract, code in ((4, 3), (5, 2)):
        admin.form("/Admin/HopDong/TraMayTruocHan", {
            "id": contract, "ngayTraThucTe": today, "phiPhatTraSom": 0,
        }, admin_page)
        html(customer, f"/Cart/ContractDetail/{contract}")
        detail = api.get_json(f"/api/contracts/{contract}")
        check(detail["statusCode"] == (2 if contract == 4 else 4) and detail["paymentStatusCode"] == code,
              f"Early settlement retains status {code} after loading Web detail")

def main():
    db = "RentalSystemDebtCheck_" + uuid.uuid4().hex[:12]
    web.DB = db
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        web.PORT = listener.getsockname()[1]
    web.BASE = f"http://127.0.0.1:{web.PORT}"
    secret = uuid.uuid4().hex
    os.environ["Vnpay__HashSecret"] = secret
    os.environ["Database__EnableBackgroundJobs"] = "false"

    with tempfile.TemporaryDirectory(prefix="rentalsystem-debt-check-") as output:
        web.OUT = Path(output)
        (web.OUT / "wwwroot").mkdir()
        created = False
        process = log = None
        try:
            cutover.sql(f"CREATE DATABASE [{db}];")
            created = True
            for script in ("001_Baseline.sql", "002_MaintenanceAssignments.sql", "003_FirstContractPayment.sql", "004_ContractSettlements.sql"):
                cutover.sql_file(cutover.SQL / script, db)
            cutover.sql(FIXTURE, db)
            process, log = web.start_server()
            check_flows(db, secret)
            print(f"{len(web.RESULTS)} HTTP checks passed on the disposable SQL database.")
        except BaseException:
            log_path = web.OUT / "backend.log"
            if log_path.exists():
                print(log_path.read_text(encoding="utf-8", errors="replace")[-8000:], file=sys.stderr)
            raise
        finally:
            web.stop_server(process, log)
            if created:
                cutover.sql(f"ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE [{db}];")
                print("Disposable SQL database removed.")

if __name__ == "__main__":
    main()
