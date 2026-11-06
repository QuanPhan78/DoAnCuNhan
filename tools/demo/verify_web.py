"""Check MVC Web pages/forms only, on the existing owned demo server.

No /api calls, no Android commands, no reset of existing demonstration data.
Uses HTTP forms and antiforgery cookies; this does not claim to automate JS/UI.
"""
import html
import io
import json
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path

import verify_demo as helper

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

helper.BASE = "http://localhost:5000"
OUT = helper.ROOT / "outputs/demo/web-only"
OUT.mkdir(parents=True, exist_ok=True)
checks = []
created = {}


def check(ok, label):
    checks.append({"name": label, "passed": bool(ok)})
    print(("PASS " if ok else "FAIL ") + label, flush=True)
    if not ok:
        raise AssertionError(label)


def page(session, path):
    body, url, headers = session.request(path)
    return html.unescape(body.decode("utf-8")), url


def submit(session, path, fields, token_page=None):
    body, url, _ = session.form(path, fields, token_page)
    return html.unescape(body.decode("utf-8")), url


def saved(session, path, name):
    body, _, _ = session.request(path)
    (OUT / name).write_bytes(body)
    return html.unescape(body.decode("utf-8"))


def login(email):
    session = helper.Session()
    for attempt in range(4):
        try:
            _, url = submit(session, "/Account/Login", {"email": email, "matKhau": "Demo@123"})
            break
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 3:
                raise
            print("Đợi giới hạn đăng nhập Web (20 giây)...", flush=True)
            time.sleep(20)
    check("/Account/Login" not in url, "Đăng nhập Web: " + email)
    return session


def main():
    # Establish database identity through the Admin Web export before writes.
    admin = login("admin@demo.invalid")
    raw = admin.request("/Admin/Database/Backup?format=json")[0]
    before = json.loads(raw)
    check(before["DatabaseName"] == "RentalSystemDemoDB", "Đúng CSDL demo riêng")
    (OUT / "backup-before.json").write_bytes(raw)
    upload_source = helper.ROOT / "outputs/demo/wwwroot/uploads"
    if upload_source.exists():
        shutil.copytree(upload_source, OUT / "uploads-before", dirs_exist_ok=True)
    sale = login("sale@demo.invalid")
    tech = login("tech@demo.invalid")
    customer = login("customer@demo.invalid")

    anon = helper.Session()
    check("/Account/Login" in page(anon, "/Admin/HopDong")[1], "Trang quản trị yêu cầu đăng nhập")
    check(helper.is_denied(sale, "/Admin/Database"), "Kinh doanh không được quản trị CSDL")
    check(helper.is_denied(tech, "/Admin/ThongKe"), "Kỹ thuật không được xem báo cáo quản trị")
    check(helper.is_denied(customer, "/Admin/HopDong"), "Khách hàng không được vào quản trị hợp đồng")
    try:
        customer.request("/Cart/ContractDetail/5")
        check(False, "Chặn xem hợp đồng khách hàng khác")
    except urllib.error.HTTPError as error:
        check(error.code in (401, 403, 404), "Chặn xem hợp đồng khách hàng khác")

    check("Laptop Demo Dell" in page(customer, "/SanPham")[0], "Danh mục sản phẩm hiển thị")
    check("170.000" in page(customer, "/SanPham/Details/1")[0], "Chi tiết sản phẩm hiển thị giá thuê")
    customer.request("/Cart/AddToCart/1")
    cart, _ = page(customer, "/Cart")
    check("Laptop Demo Dell" in cart, "Thêm laptop vào giỏ hàng Web")
    blocked, blocked_url = page(customer, "/Cart/Checkout")
    check("/Account/MyDebt" in blocked_url and "nợ xấu" in blocked,
          "Chặn đặt thuê mới khi khách Demo An có nợ quá hạn")
    renter = login("other@demo.invalid")
    renter.request("/Cart/AddToCart/1")
    today = date.today()
    fields = {"NgayBatDau": today.isoformat(), "NgayKetThuc": (today + timedelta(days=7)).isoformat(),
              "DiaChi": "DEMO WEB ONLY - Phòng demo, 123 Đường Minh Họa, TP.HCM"}
    bad, bad_url = submit(renter, "/Cart/Checkout", {**fields, "NgayKetThuc": (today - timedelta(days=1)).isoformat()})
    check("/Cart/Checkout" in bad_url and "không thể nhỏ hơn" in bad, "Chặn ngày trả trước ngày nhận")
    body, url = submit(renter, "/Cart/Checkout", fields)
    match = re.search(r"/Cart/SignContract/(\d+)", url)
    check(match is not None, "Gửi yêu cầu thuê Web và chuyển đến bước ký hợp đồng")
    contract_id = int(match[1])
    created["webContractId"] = contract_id
    contract = saved(sale, f"/Admin/HopDong/Details/{contract_id}", "hop-dong-web.html")
    check("Khách hàng Demo Bình" in contract and "1.190.000" in contract and "7 ngày" in contract,
          "Kinh doanh xem đúng đơn mới, 7 ngày, 1.190.000đ")
    check("Chờ duyệt" in contract, "Đơn mới ở trạng thái chờ duyệt")
    blocked, _ = submit(sale, "/Admin/HopDong/UpdateStatus", {"id": contract_id, "status": 1}, f"/Admin/HopDong/Details/{contract_id}")
    check("Không thể giao máy" in blocked and "chữ ký" in blocked, "Chặn bàn giao đơn chưa đủ hồ sơ/chữ ký")

    before_ticket_ids = {row["MaPhieu"] for row in before["PhieuBaoTris"]}
    result, _ = submit(customer, "/BaoTri/TaoPhieu", {
        "maHopDong": 1, "maThietBi": 1, "moTaLoi": "DEMO WEB ONLY: Máy không kết nối Wi-Fi", "mucDoKhanCap": 1,
    }, "/BaoTri/TaoPhieu?hopDongId=1")
    check("Đã gửi yêu cầu bảo trì thành công" in result, "Khách báo sự cố qua biểu mẫu Web")
    current = json.loads(admin.request("/Admin/Database/Backup?format=json")[0])
    new_tickets = [row for row in current["PhieuBaoTris"] if row["MaPhieu"] not in before_ticket_ids]
    check(len(new_tickets) == 1 and new_tickets[0]["MaHopDong"] == 1 and new_tickets[0]["MaThietBi"] == 1,
          "Phiếu mới gắn đúng hợp đồng và serial thiết bị")
    ticket = new_tickets[0]["MaPhieu"]
    created["webTicketId"] = ticket
    ticket_page = f"/Admin/BaoTri/Details/{ticket}"
    result, _ = submit(customer, "/BaoTri/DanhGia", {"maPhieu": ticket, "rating": 5}, "/BaoTri/MyTickets")
    check("Chỉ đánh giá được phiếu đã hoàn thành" in result, "Chặn đánh giá khi chưa sửa xong")
    result, _ = submit(admin, "/Admin/BaoTri/UpdateStatus", {
        "id": ticket, "status": 1, "maKtv": 3, "ghiChu": "Đã phân công Kỹ thuật Demo", "phiDenBu": 0,
    }, ticket_page)
    check("Cập nhật tiến độ bảo trì thành công" in result, "Quản trị phân công kỹ thuật qua Web")
    for status, note in [(2, "Đang kiểm tra kết nối Wi-Fi"), (3, "Đã cấu hình lại kết nối, kiểm tra hoạt động ổn định - WEB ONLY")]:
        result, _ = submit(tech, "/Admin/BaoTri/UpdateStatus", {
            "id": ticket, "status": status, "maKtv": 3, "ghiChu": note, "phiDenBu": 0,
            "chiPhiSuaChua": 0, "loaiTrachNhiem": 2, "nguyenNhan": "Cấu hình mạng", "linhKienThayThe": "Không thay linh kiện",
        }, ticket_page)
        check("Cập nhật tiến độ bảo trì thành công" in result, f"Kỹ thuật cập nhật trạng thái {status} qua Web")
    customer_ticket = saved(customer, f"/BaoTri/ChiTiet/{ticket}", "bao-tri-khach-hang.html")
    check("Đã cấu hình lại kết nối" in customer_ticket and "Gửi Đánh Giá Dịch Vụ" in customer_ticket,
          "Khách thấy kết quả sửa chữa và biểu mẫu đánh giá Web")
    result, _ = submit(customer, "/BaoTri/DanhGia", {
        "maPhieu": ticket, "rating": 6,
    }, "/BaoTri/MyTickets")
    check("phải từ 1 đến 5 sao" in result, "Chặn điểm đánh giá ngoài 1–5")
    result, _ = submit(customer, "/BaoTri/DanhGia", {
        "maPhieu": ticket, "rating": 5, "yKienPhanHoi": "CHẠY THỬ WEB: Hỗ trợ nhanh, máy hoạt động ổn định",
    }, "/BaoTri/MyTickets")
    check("Cảm ơn bạn đã gửi đánh giá" in result, "Gửi 5 sao thành công qua Web")
    result = saved(admin, ticket_page, "bao-tri-quan-tri.html")
    customer_ticket = saved(customer, f"/BaoTri/ChiTiet/{ticket}", "bao-tri-khach-hang.html")
    check("5 / 5 sao" in customer_ticket and "CHẠY THỬ WEB" in customer_ticket,
          "Khách tải lại vẫn thấy 5 sao và phản hồi đã lưu")
    result, _ = submit(customer, "/BaoTri/NghiemThu", {"maPhieu": ticket, "dongY": "true", "yKien": "WEB ONLY: Đã kiểm tra máy hoạt động ổn định"}, f"/BaoTri/ChiTiet/{ticket}")
    check("Cảm ơn bạn đã xác nhận nghiệm thu" in result and "Đã nghiệm thu" in result,
          "Khách nghiệm thu và đóng phiếu qua Web")

    query = urllib.parse.urlencode({"range": "custom", "tuNgay": (today - timedelta(days=60)).isoformat(), "denNgay": today.isoformat()})
    report = saved(admin, "/Admin/ThongKe?" + query, "bao-cao-web.html")
    check("DOANH THU" in report.upper() and "13.300.000" in report, "Báo cáo theo kỳ hiển thị dữ liệu thu tiền")
    workbook = admin.request("/Admin/ThongKe/ExportExcel?" + query)[0]
    with zipfile.ZipFile(io.BytesIO(workbook)) as archive:
        check(archive.testzip() is None and "xl/workbook.xml" in archive.namelist(), "Xuất Excel qua Web, tệp mở được")
    (OUT / "BaoCaoKiemTraWeb.xlsx").write_bytes(workbook)
    for path, name in [("/Document/InHopDong/1", "hop-dong-da-ky.html"),
                       ("/Document/InBienBanBanGiao/1", "bien-ban-ban-giao.html")]:
        check("Khách hàng Demo An" in saved(admin, path, name), "Kết xuất biểu mẫu: " + name)
    raw = admin.request("/Admin/Database/Backup?format=json")[0]
    after = json.loads(raw)
    (OUT / "backup-after.json").write_bytes(raw)
    new_ticket = next(row for row in after["PhieuBaoTris"] if row["MaPhieu"] == ticket)
    new_contract = next(row for row in after["HopDongs"] if row["MaHopDong"] == contract_id)
    check(new_ticket["DanhGiaSao"] == 5 and new_ticket["DaNghiemThu"] and new_ticket["TrangThai"] == 5,
          "Sao lưu Web xác nhận lưu 5 sao và phiếu đã nghiệm thu")
    check(new_contract["TongTien"] == 1190000 and new_contract["TrangThai"] == 0,
          "Sao lưu Web xác nhận đơn mới 1.190.000đ, chờ duyệt")
    check(next(row for row in after["HopDongs"] if row["MaHopDong"] == 8) == next(row for row in before["HopDongs"] if row["MaHopDong"] == 8),
          "Giữ nguyên dữ liệu HD-0008 đã có")


if __name__ == "__main__":
    error = None
    try:
        main()
    except Exception as exc:
        error = str(exc)
        if not checks or checks[-1]["passed"]:
            checks.append({"name": "Lỗi khi kiểm tra: " + error, "passed": False})
        raise
    finally:
        payload = {
            "testedAt": datetime.now().astimezone().isoformat(), "baseUrl": helper.BASE,
            "scope": "MVC Web pages/forms only; HTTP with cookies and antiforgery. No Mobile/API tests.",
            "browserClickAutomation": False,
            "passed": sum(c["passed"] for c in checks), "failed": sum(not c["passed"] for c in checks),
            "created": created, "checks": checks, "error": error,
        }
        (OUT / "result.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
