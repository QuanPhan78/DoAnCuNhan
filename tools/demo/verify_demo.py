"""Rehearse real HTTP endpoints against an owned, disposable demo database.

Never accepts a caller-provided host/connection string. No phone UI is simulated.
Run after building DemoHarness.csproj. Uses only Python's standard library.
"""
from __future__ import annotations

import io
import html
import json
import os
import re
import socket
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "demo-check"
HARNESS = ROOT / "tools/demo/bin/Debug/net9.0/DemoHarness.dll"
APP = ROOT / "RentalSystem/bin/Debug/net9.0/RentalSystem.dll"
DB = os.environ.get("RENTALSYSTEM_VERIFY_DATABASE", "RentalSystemDB_V2")
if DB != "RentalSystemDB_V2":
    raise ValueError("Verification is limited to the explicitly marked V2 rehearsal database.")
PORT = 5001
BASE = f"http://localhost:{PORT}"
RESULTS: list[dict] = []


class Inputs(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.values = {}
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "input" and attrs.get("name"):
            self.values[attrs["name"]] = attrs.get("value", "")


class Session:
    def __init__(self):
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))

    def request(self, path, data=None, method=None, content_type=None):
        req = urllib.request.Request(BASE + path, data=data, method=method)
        if content_type:
            req.add_header("Content-Type", content_type)
        with self.opener.open(req, timeout=30) as response:
            return response.read(), response.url, response.headers

    def get_json(self, path):
        return json.loads(self.request(path)[0])

    def send_json(self, path, value, method="POST"):
        return json.loads(self.request(path, json.dumps(value).encode(), method, "application/json")[0])

    def form(self, path, fields, token_page=None):
        page = self.request(token_page or path)[0].decode("utf-8")
        token = Inputs(page).values["__RequestVerificationToken"]
        data = urllib.parse.urlencode({**fields, "__RequestVerificationToken": token}).encode()
        return self.request(path, data, "POST", "application/x-www-form-urlencoded")

    def login(self, email):
        _, url, _ = self.form("/Account/Login", {"email": email, "matKhau": "Demo@123"})
        require("/Account/Login" not in url, f"Web login: {email}")


def require(condition, name):
    RESULTS.append({"name": name, "passed": bool(condition)})
    if not condition:
        raise AssertionError(name)
    print("PASS " + name, flush=True)


def is_denied(session, path):
    try:
        return "/Account/AccessDenied" in session.request(path)[1]
    except urllib.error.HTTPError as error:
        return error.code == 403


def harness(action):
    subprocess.run(["dotnet", str(HARNESS), action, DB], cwd=ROOT, check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")


def start_server():
    env = dict(os.environ)
    env.update({
        "ConnectionStrings__DefaultConnection": f"Server=localhost;Database={DB};Trusted_Connection=True;TrustServerCertificate=True;",
        "ASPNETCORE_ENVIRONMENT": "Development",
        "Logging__LogLevel__Default": "Warning",
    })
    log = open(OUT / "backend.log", "ab")
    process = subprocess.Popen([
        "dotnet", str(APP), "--contentRoot", str(ROOT / "RentalSystem"),
        "--webroot", str(OUT / "wwwroot"), "--urls", BASE,
    ], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
       creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    try:
        for _ in range(90):
            if process.poll() is not None:
                raise RuntimeError("Backend stopped. See outputs/demo-check/backend.log")
            try:
                Session().get_json("/api/devices")
                return process, log
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.5)
        raise TimeoutError("Backend did not become ready")
    except BaseException:
        stop_server(process, log)
        raise


def stop_server(process, log):
    if process and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    if log:
        log.close()


def multipart_file(session, path, filename, body):
    return multipart(session, path, "/Admin/Database", {},
                     {"backupFile": (filename, "application/octet-stream", body)})


def multipart(session, path, token_page, fields, files):
    token = Inputs(session.request(token_page)[0].decode()).values["__RequestVerificationToken"]
    boundary = "RentalSystemDemoBoundary"
    parts = []
    for name, value in {**fields, "__RequestVerificationToken": token}.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    for name, (filename, content_type, body) in files.items():
        parts.append(
            (f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
             f'Content-Type: {content_type}\r\n\r\n').encode() + body + b"\r\n")
    payload = b"".join(parts) + f"--{boundary}--\r\n".encode()
    return session.request(path, payload, "POST", f"multipart/form-data; boundary={boundary}")


def save_html(session, path, filename):
    body, url, _ = session.request(path)
    require("/Account/" not in url and len(body) > 1000, f"Printable document: {filename}")
    text = body.decode("utf-8")
    # Local copies use sibling copied web assets, rather than a running server.
    text = text.replace('src="/', 'src="../wwwroot/').replace('href="/', 'href="../wwwroot/')
    (OUT / "evidence" / filename).write_text(text, encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    evidence = OUT / "evidence"
    evidence.mkdir(exist_ok=True)
    with socket.socket() as probe:
        if probe.connect_ex(("localhost", PORT)) == 0:
            raise RuntimeError("Port 5001 is occupied. Verification refuses to contact an unknown backend.")
    process = log = None
    try:
        harness("reset")
        baseline = json.loads((OUT / "baseline.json").read_text(encoding="utf-8"))
        process, log = start_server()
        api = Session()
        admin, sale, tech, customer = Session(), Session(), Session(), Session()
        # Authenticate every synthetic role through both API and Web entry points.
        for role, email in [("Admin", "admin@demo.invalid"), ("KinhDoanh", "sale@demo.invalid"),
                            ("KyThuat", "tech@demo.invalid"), ("KhachHang", "customer@demo.invalid")]:
            response = api.send_json("/api/auth/login", {"email": email, "password": "Demo@123"})
            require(response["user"]["roleCode"] == role, f"API login role: {role}")
        admin.login("admin@demo.invalid")
        sale.login("sale@demo.invalid")
        tech.login("tech@demo.invalid")
        customer.login("customer@demo.invalid")
        backup = json.loads(admin.request("/Admin/Database/Backup?format=json")[0])
        require(backup["DatabaseName"] == DB, "Backend is using the isolated verification database")
        require(len(backup["HopDongs"]) == 7 and len(backup["ThietBis"]) == 24
                and len(backup["KyHanThanhToans"]) == 13, "Startup preserves fixture counts")
        require(len(api.get_json("/api/contracts?userId=4&role=KhachHang")) == 4, "Customer sees the expected contracts")
        require(all(c["customerId"] == "4" for c in api.get_json("/api/contracts?userId=4&role=KhachHang")), "Customer list excludes other customer")
        devices = api.get_json("/api/devices")
        laptop = next(d for d in devices if d["id"] == "1")
        require(laptop["readyQuantity"] > 0 and laptop["rentalPrice"] == 170000, "Available laptop and daily price")
        require("DEMO ONLY" in api.request("/uploads/demo/customer-signature.svg")[0].decode(), "Synthetic signature served from the demo webroot")
        image_files = {}
        for side, field in (("front", "cmndTruocFile"), ("back", "cmndSauFile")):
            filename = f"identity-demo-{side}.png"
            image_bytes, _, headers = api.request(f"/uploads/demo/{filename}")
            require(headers.get_content_type() == "image/png" and
                    image_bytes == (ROOT / "tools/demo/assets" / filename).read_bytes(),
                    f"Approved redacted {side} PNG served unchanged")
            image_files[field] = (filename, "image/png", image_bytes)
        front_path = "/uploads/demo/identity-demo-front.png"
        back_path = "/uploads/demo/identity-demo-back.png"
        for session, page in ((customer, "/Cart/ContractDetail/1"), (sale, "/Admin/HopDong/Details/1")):
            detail_html = session.request(page)[0].decode()
            require(front_path in detail_html and back_path in detail_html, f"Both identity sides are shown on {page}")
        require(is_denied(sale, "/Admin/Database"), "Sales role cannot access database administration")
        require(is_denied(tech, "/Admin/ThongKe"), "Technician cannot access management reports")

        today = date.today()
        rental_request = {
            "customerId": "4", "deviceId": "1", "quantity": 1, "rentalType": "Theo ngày",
            "startDate": today.isoformat(), "endDate": (today + timedelta(days=6)).isoformat(),
            "deliveryAddress": "Phòng demo, 123 Đường Minh Họa, TP.HCM",
            "note": "DEMO LIVE", "estimatedAmount": 1190000, "installmentCount": 1,
            "items": [{"deviceId": "1", "quantity": 1, "rentalPrice": 170000, "subtotal": 1190000}],
        }
        created = api.send_json("/api/contracts", rental_request)
        new_id = int(created["contractId"])
        require(created["success"] and created["totalAmount"] == 1190000 and created["depositAmount"] == 0,
                "Mobile-shaped rental request creates pending contract with matching amount, no deposit collected")
        body = html.unescape(sale.request(f"/Admin/HopDong/Details/{new_id}")[0].decode())
        require("Khách hàng Demo An" in body and "Laptop Demo Dell" in body
                and re.search(r"1[.,]190[.,]000", body), "Sales Web shows the new customer's rental and matching money")
        contracts = api.get_json("/api/contracts?userId=4&role=KhachHang")
        require(any(int(c["id"]) == new_id and c["statusCode"] == 0 for c in contracts), "New contract persists in customer API list")

        ticket = api.send_json("/api/maintenance", {
            "contractId": "1", "deviceId": "Laptop Demo Dell Latitude 5430 (DEMO-LAP-001)",
            "issueType": "Mất kết nối", "description": "Máy không kết nối Wi-Fi", "severity": "Trung bình",
        })
        ticket_id = int(ticket["id"])
        page = f"/Admin/BaoTri/Details/{ticket_id}"
        detail = api.get_json(f"/api/maintenance/{ticket_id}")
        require(detail["contractId"] == "1" and detail["deviceId"] == "1", "Reported incident links the exact contract and physical device")
        admin.form("/Admin/BaoTri/UpdateStatus", {"id": ticket_id, "status": 1, "maKtv": 3,
                    "ghiChu": "Đã phân công kỹ thuật Demo", "phiDenBu": 0, "chiPhiSuaChua": 0}, page)
        require(api.get_json(f"/api/maintenance/{ticket_id}")["assignedStaff"] == "Kỹ thuật Demo", "Admin assigns the technician through Web")
        for status, note in [(2, "Đang kiểm tra kết nối Wi-Fi"), (3, "Đã cấu hình lại kết nối, kiểm tra hoạt động ổn định")]:
            tech.form("/Admin/BaoTri/UpdateStatus", {"id": ticket_id, "status": status, "maKtv": 3,
                      "ghiChu": note, "phiDenBu": 0, "chiPhiSuaChua": 0, "loaiTrachNhiem": 2,
                      "nguyenNhan": "Cấu hình mạng", "linhKienThayThe": "Không thay linh kiện"}, page)
            require(api.get_json(f"/api/maintenance/{ticket_id}")["statusCode"] == status, f"Technician Web updates status {status}; API reads it back")
        rated = api.send_json(f"/api/maintenance/{ticket_id}/rating", {"rating": 5, "feedback": "Hỗ trợ nhanh, máy hoạt động ổn định"}, "PUT")
        detail = api.get_json(f"/api/maintenance/{ticket_id}")
        require(rated["success"] and detail["rating"] == 5, "Customer feedback persists as five stars")
        require(api.get_json("/api/maintenance/1")["rating"] is None, "Fallback ticket remains available for rating")
        web_detail = html.unescape(admin.request(page)[0].decode())
        require("Hỗ trợ nhanh" in web_detail, "Customer feedback is visible on Web")

        manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
        query = urllib.parse.urlencode({"range": "custom", "tuNgay": manifest["reportFrom"], "denNgay": manifest["reportTo"]})
        require("Báo" in html.unescape(admin.request("/Admin/ThongKe?" + query)[0].decode()), "Management dashboard renders")
        excel = admin.request("/Admin/ThongKe/ExportExcel?" + query)[0]
        with zipfile.ZipFile(io.BytesIO(excel)) as archive:
            require(archive.testzip() is None and "xl/workbook.xml" in archive.namelist(), "Exported Excel is a valid workbook")
            sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
            ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            values = [n.text for n in sheet.findall(".//x:v", ns)]
            require(any(v and v.isdigit() and int(v) >= 1190000 for v in values), "Excel contains financial data")
        (evidence / "BaoCaoDemo.xlsx").write_bytes(excel)
        save_html(admin, "/Document/InHopDong/1", "HopDongDemo.html")
        save_html(admin, "/Document/InBienBanBanGiao/1", "BienBanBanGiaoDemo.html")
        save_html(admin, "/Document/InPhieuThu/1", "PhieuThuDemo.html")
        exported = admin.request("/Admin/Database/Backup?format=json")[0]
        payload = json.loads(exported)
        require(payload["DatabaseName"] == DB and len(payload["HopDongs"]) == 8, "Downloaded JSON backup contains the new rental")
        (evidence / "BackupSauDienTap.json").write_bytes(exported)

        signer = Session()
        signer.login("other@demo.invalid")
        # The presentation customer deliberately has an overdue installment.
        sign_id = int(api.send_json("/api/contracts", {**rental_request, "customerId": "5"})["contractId"])
        sign_page = f"/Cart/SignContract/{sign_id}"
        signature_png = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/n2cAAAAASUVORK5CYII="
        )
        sign_fields = {"id": sign_id, "soKyHan": 1,
                       "signatureData": "data:image/png;base64," + signature_png}
        _, sign_result_url, _ = multipart(signer, "/Cart/SignContract", sign_page, sign_fields, image_files)
        signed = next(h for h in admin.get_json("/Admin/Database/Backup?format=json")["HopDongs"]
                      if h["MaHopDong"] == sign_id)
        require(signed["ChuKyKhachHang"] and
                api.request(signed["AnhCCCD_Truoc"])[0] == image_files["cmndTruocFile"][2] and
                api.request(signed["AnhCCCD_Sau"])[0] == image_files["cmndSauFile"][2],
                f"Customer signing saves distinct front and back uploads ({sign_result_url})")

        legacy = json.loads(json.dumps(baseline))
        legacy_pending = next(h for h in legacy["HopDongs"] if h["MaHopDong"] == 3)
        legacy_pending.update({
            "AnhCMND": "/uploads/demo/identity-demo.svg", "AnhCCCD_Truoc": "  ", "AnhCCCD_Sau": None,
            "ChuKyKhachHang": "/uploads/demo/customer-signature.svg",
            "ChuKyNhanVien": "/uploads/demo/staff-signature.svg",
        })
        legacy_main = next(h for h in legacy["HopDongs"] if h["MaHopDong"] == 1)
        legacy_main["AnhCMND"] = "/uploads/demo/identity-demo.svg"
        multipart_file(admin, "/Admin/Database/Restore", "legacy.json", json.dumps(legacy).encode())
        normalized = admin.get_json("/Admin/Database/Backup?format=json")["HopDongs"]
        normalized_pending = next(h for h in normalized if h["MaHopDong"] == 3)
        normalized_main = next(h for h in normalized if h["MaHopDong"] == 1)
        require(normalized_pending["AnhCCCD_Truoc"] == legacy_pending["AnhCMND"] and
                normalized_pending["AnhCCCD_Sau"] is None and
                normalized_main["AnhCCCD_Truoc"] == front_path and
                normalized_main["AnhCCCD_Sau"] == back_path and
                all("AnhCMND" not in h for h in normalized),
                "Legacy JSON restore fills missing front, preserves existing sides and exports only current columns")
        sale.form("/Admin/HopDong/UpdateStatus", {"id": 3, "status": 1}, "/Admin/HopDong/Details/3")
        require(api.get_json("/api/contracts/3")["statusCode"] == 1,
                "Migrated one-photo contract can be handed over")

        details = "/Admin/HopDong/Details/3"
        payment_before = admin.get_json("/Admin/Database/Backup?format=json")
        period = next(k for k in payment_before["KyHanThanhToans"] if k["MaHopDong"] == 3)
        sale.form("/Admin/HopDong/ConfirmPayment", {
            "maKyHan": period["MaKyHan"], "soTienThucThu": int(period["SoTienPhai"]),
            "hinhThuc": 0, "ghiChu": "cutover verification",
        }, details)
        paid = admin.get_json("/Admin/Database/Backup?format=json")
        require(any(k["MaKyHan"] == period["MaKyHan"] and k["TrangThai"] == 1
                    for k in paid["KyHanThanhToans"]) and
                any(r["MaKyHan"] == period["MaKyHan"] and r["SoTien"] == period["SoTienPhai"]
                    for r in paid["PhieuThus"]), "Staff payment records the receipt and closes the installment")

        customer.form("/Cart/YeuCauGiaHan", {"id": 3, "soNgayGiaHan": 2, "lyDo": "cutover verification"},
                      "/Cart/ContractDetail/3")
        for _ in range(2):
            sale.form("/Admin/HopDong/DuyetGiaHan", {"id": 3, "chapNhan": "true"}, details)
        extended = admin.get_json("/Admin/Database/Backup?format=json")
        require(sum(k["MaHopDong"] == 3 for k in extended["KyHanThanhToans"]) ==
                sum(k["MaHopDong"] == 3 for k in paid["KyHanThanhToans"]) + 1 and
                sum(y["MaHopDong"] == 3 and y["TrangThai"] == 1 for y in extended["YeuCauGiaHans"]) == 1,
                "Extension approval adds one installment even when submitted again")

        # Exercise actual restore only on the disposable DB, then compare all 18 tables.
        baseline_body = json.dumps(baseline, ensure_ascii=False).encode()
        multipart_file(admin, "/Admin/Database/Restore", "baseline.json", baseline_body)
        restored = json.loads(admin.request("/Admin/Database/Backup?format=json")[0])
        table_names = [name for name, value in baseline.items() if isinstance(value, list)]
        require(all(restored[name] == baseline[name] for name in table_names), "Restore round-trip matches all baseline tables")
        stop_server(process, log)
        process = log = None
        process, log = start_server()
        admin = Session()
        admin.login("admin@demo.invalid")
        restarted = json.loads(admin.request("/Admin/Database/Backup?format=json")[0])
        require(all(restarted[name] == baseline[name] for name in table_names), "Restart preserves all restored baseline tables")
        harness("check")
    except Exception as error:
        if not RESULTS or RESULTS[-1]["passed"]:
            RESULTS.append({"name": f"Unhandled check error: {error}", "passed": False})
        raise
    finally:
        stop_server(process, log)
        report = {
            "checkedAt": datetime.now().astimezone().isoformat(), "database": DB, "baseUrl": BASE,
            "passed": sum(r["passed"] for r in RESULTS), "failed": sum(not r["passed"] for r in RESULTS),
            "checks": RESULTS, "phoneUiVerified": False, "timedRehearsalsCompleted": 0,
            "note": "HTTP integration rehearsal. Real Android interaction, projection and recordings require a connected phone.",
        }
        (OUT / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
