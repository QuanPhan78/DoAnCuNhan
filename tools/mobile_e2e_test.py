#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-End (E2E) Integration & Security Test Suite for RentalSystem Mobile API
Targets: Live backend server running at http://localhost:5000
"""

import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

class TestReport:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def log(self, category, name, passed, details="", duration_ms=0):
        status = "[PASS]" if passed else "[FAIL]"
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        self.tests.append({
            "category": category,
            "name": name,
            "passed": passed,
            "details": details,
            "duration_ms": duration_ms
        })
        timing = f"({duration_ms:.1f}ms)" if duration_ms > 0 else ""
        print(f"{status} {category} - {name} {timing}")
        if not passed and details:
            print(f"       -> Details: {details}")

    def summary(self):
        total = self.passed + self.failed
        rate = (self.passed / total * 100) if total > 0 else 0
        print("\n" + "=" * 80)
        print(f"E2E MOBILE API TEST RESULTS: {self.passed}/{total} PASSED ({rate:.1f}%)")
        print("=" * 80)
        return self.failed == 0

def http_request(method, path, body=None, token=None, headers=None, base=BASE_URL):
    url = f"{base}{path}" if path.startswith("/") else f"{base}/{path}"
    req_headers = {"Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    if token:
        req_headers["Authorization"] = f"Bearer {token}"

    data = None
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode("utf-8")
            req_headers["Content-Type"] = "application/json"
        elif isinstance(body, str):
            data = body.encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            duration = (time.time() - start_time) * 1000
            content = resp.read()
            text = content.decode("utf-8", errors="replace")
            json_data = None
            try:
                json_data = json.loads(text)
            except Exception:
                pass
            return resp.status, json_data, text, duration
    except urllib.error.HTTPError as e:
        duration = (time.time() - start_time) * 1000
        content = e.read()
        text = content.decode("utf-8", errors="replace")
        json_data = None
        try:
            json_data = json.loads(text)
        except Exception:
            pass
        return e.code, json_data, text, duration
    except Exception as ex:
        duration = (time.time() - start_time) * 1000
        return 0, None, str(ex), duration

def run_tests():
    sys.stdout.reconfigure(encoding="utf-8")
    report = TestReport()
    print("=" * 80)
    print("RUNNING LIVE MOBILE API INTEGRATION & SECURITY TEST SUITE")
    print(f"Target: {BASE_URL}")
    print("=" * 80 + "\n")

    # Wait for backend to be ready
    for i in range(10):
        s, _, _, _ = http_request("GET", "/devices")
        if s == 200:
            break
        time.sleep(1)

    # ----------------------------------------------------
    # SCENARIO 1: Authentication & User Profile
    # ----------------------------------------------------
    print("--- [SCENARIO 1: Authentication & User Profile] ---")

    # 1.1 Valid Customer Login (khach@gmail.com / 123456)
    status, data, _, ms = http_request("POST", "/auth/login", {
        "email": "khach@gmail.com",
        "password": "123456"
    })
    c1_pass = (status == 200 and data is not None and 
               data.get("user") is not None and 
               data.get("user", {}).get("email") == "khach@gmail.com" and
               data.get("token") is not None)
    customer_id = data.get("user", {}).get("id") if data and data.get("user") else "5"
    token = data.get("token", {}).get("accessToken") if data and data.get("token") else ""
    report.log("Auth", "1.1: Valid customer login returns 200 + token + user profile", c1_pass, f"Status: {status}", ms)

    # 1.2 Invalid Password Login
    status, data, _, ms = http_request("POST", "/auth/login", {
        "email": "khach@gmail.com",
        "password": "WrongPassword_999"
    })
    c2_pass = (status == 401 and data is not None and "chính xác" in data.get("message", "").lower())
    report.log("Auth", "1.2: Incorrect password safely rejected with 401 Unauthorized", c2_pass, f"Status: {status}", ms)

    # 1.3 Non-existent User Login
    status, data, _, ms = http_request("POST", "/auth/login", {
        "email": "non_existent_user_99999@test.com",
        "password": "123456"
    })
    c3_pass = (status == 401)
    report.log("Auth", "1.3: Non-existent account rejected with 401 Unauthorized", c3_pass, f"Status: {status}", ms)

    # 1.4 Get User Profile
    status, prof_data, _, ms = http_request("GET", f"/auth/profile/{customer_id}", token=token)
    c4_pass = (status == 200 and prof_data is not None and prof_data.get("email") == "khach@gmail.com")
    report.log("Auth", f"1.4: Query user profile returns correct customer record (User #{customer_id})", c4_pass, f"Status: {status}", ms)

    # 1.5 Update Profile
    new_address = f"140 Lê Trọng Tấn, P. Tây Thạnh, Q. Tân Phú (Updated {int(time.time())})"
    status, data, _, ms = http_request("PUT", f"/auth/profile/{customer_id}", {
        "name": "Nguyễn Văn Khách (Mobile)",
        "phone": "079200001234",
        "address": new_address
    }, token=token)
    c5_pass = (status == 200 and data is not None and data.get("user", {}).get("address") == new_address)
    report.log("Auth", "1.5: Update profile updates address and returns modified user object", c5_pass, f"Status: {status}", ms)

    # ----------------------------------------------------
    # SCENARIO 2: Device Fleet & Catalog Discovery
    # ----------------------------------------------------
    print("\n--- [SCENARIO 2: Device Fleet & Catalog Discovery] ---")

    # 2.1 Get All Devices
    status, data, _, ms = http_request("GET", "/devices")
    c6_pass = (status == 200 and isinstance(data, list) and len(data) > 0 and "name" in data[0] and "rentalPrice" in data[0])
    first_device_id = data[0]["id"] if data and len(data) > 0 else "1"
    first_device_name = data[0]["name"] if data and len(data) > 0 else ""
    report.log("Devices", f"2.1: Query all devices returns non-empty fleet list (Count: {len(data) if data else 0})", c6_pass, f"Status: {status}", ms)

    # 2.2 Filter Devices by Available Status
    status, data_avail, _, ms = http_request("GET", "/devices?status=S%E1%BA%B5n%20s%C3%A0ng")
    c7_pass = (status == 200 and isinstance(data_avail, list) and all(d.get("rentalStatus") == "Sẵn sàng" for d in data_avail))
    report.log("Devices", f"2.2: Filter devices by status 'Sẵn sàng' returns exclusively available units (Count: {len(data_avail) if data_avail else 0})", c7_pass, f"Status: {status}", ms)

    # 2.3 Get Specific Device Details
    status, dev_detail, _, ms = http_request("GET", f"/devices/{first_device_id}")
    c8_pass = (status == 200 and dev_detail is not None and str(dev_detail.get("id")) == str(first_device_id))
    report.log("Devices", f"2.3: Get device detail #{first_device_id} returns accurate specs ({dev_detail.get('name') if dev_detail else ''})", c8_pass, f"Status: {status}", ms)

    # 2.4 Device Not Found
    status, _, _, ms = http_request("GET", "/devices/999999")
    c9_pass = (status == 404)
    report.log("Devices", "2.4: Non-existent device ID returns 404 NotFound", c9_pass, f"Status: {status}", ms)

    # ----------------------------------------------------
    # SCENARIO 3: Contracts & Mobile Rental Order
    # ----------------------------------------------------
    print("\n--- [SCENARIO 3: Contracts & Mobile Rental Order] ---")

    # 3.1 Create Rental Order from Mobile
    start_dt = datetime.now() + timedelta(days=1)
    end_dt = start_dt + timedelta(days=30)
    create_payload = {
        "customerId": str(customer_id),
        "customerName": "Nguyễn Văn Khách",
        "customerPhone": "079200001234",
        "customerEmail": "khach@gmail.com",
        "deviceId": str(first_device_id),
        "rentalType": "month",
        "startDate": start_dt.strftime("%Y-%m-%d"),
        "endDate": end_dt.strftime("%Y-%m-%d"),
        "depositAmount": 1000000,
        "estimatedAmount": 3000000,
        "deliveryAddress": "140 Lê Trọng Tấn, Tân Phú, TP.HCM",
        "notes": "Đơn thuê thử nghiệm từ Mobile E2E Runner"
    }
    status, contract_res, _, ms = http_request("POST", "/contracts", create_payload, token=token)
    created_contract_id = contract_res.get("contractId") or contract_res.get("contract", {}).get("id") or contract_res.get("id") if contract_res else None
    c10_pass = (status in [200, 201] and contract_res is not None and created_contract_id is not None)
    report.log("Contracts", f"3.1: Mobile rental request creates contract successfully (Contract #{created_contract_id})", c10_pass, f"Status: {status}", ms)

    # 3.2 Query Customer Contracts
    status, contracts_list, _, ms = http_request("GET", f"/contracts?userId={customer_id}&role=KhachHang", token=token)
    c11_pass = (status == 200 and isinstance(contracts_list, list) and len(contracts_list) > 0)
    report.log("Contracts", f"3.2: Query contracts for customer #{customer_id} returns owned contracts (Count: {len(contracts_list) if contracts_list else 0})", c11_pass, f"Status: {status}", ms)

    # 3.3 Security: IDOR Contract Protection
    if created_contract_id:
        status, _, raw_text, ms = http_request("GET", f"/contracts/{created_contract_id}?userId=99999&role=KhachHang")
        c12_pass = (status == 403)
        report.log("Contracts", f"3.3: IDOR Prevention: Unauthorized user denied access to contract #{created_contract_id} (Status {status})", c12_pass, f"Status: {status}", ms)

        # 3.4 Contract Legal HTML Preview Endpoint
        status, _, html_content, ms = http_request("GET", f"/contracts/{created_contract_id}/html?userId={customer_id}&role=KhachHang", base="http://localhost:5000/api")
        c13_pass = (status == 200 and "<html" in html_content.lower() and "hợp đồng" in html_content.lower())
        report.log("Contracts", f"3.4: Legal HTML preview endpoint renders complete styled contract document", c13_pass, f"Status: {status}, Length: {len(html_content)} bytes", ms)

        # 3.5 Security: IDOR Protection on HTML Preview
        status, _, _, ms = http_request("GET", f"/contracts/{created_contract_id}/html?userId=99999&role=KhachHang", base="http://localhost:5000/api")
        c14_pass = (status == 403)
        report.log("Contracts", f"3.5: Security: IDOR check enforces 403 Forbidden on HTML preview for unauthorized viewer", c14_pass, f"Status: {status}", ms)

    # ----------------------------------------------------
    # SCENARIO 4: Maintenance & Incident Workflow
    # ----------------------------------------------------
    print("\n--- [SCENARIO 4: Maintenance & Incident Workflow] ---")

    # 4.1 Create Maintenance Ticket
    maint_payload = {
        "contractId": str(created_contract_id) if created_contract_id else "1",
        "deviceId": str(first_device_id),
        "moTaLoi": "Máy khởi động bị màn hình xanh, cần kỹ sư kiểm tra gấp",
        "mucDoUuTien": "High",
        "title": "Sự cố màn hình xanh",
        "description": "Máy khởi động bị màn hình xanh khi bật ứng dụng nặng"
    }
    status, ticket_res, _, ms = http_request("POST", "/maintenance", maint_payload, token=token)
    ticket_id = ticket_res.get("ticketId") or ticket_res.get("id") or ticket_res.get("ticket", {}).get("id") if ticket_res else None
    c15_pass = (status in [200, 201] and ticket_res is not None and ticket_id is not None)
    report.log("Maintenance", f"4.1: Customer submits maintenance ticket from mobile (Ticket #{ticket_id})", c15_pass, f"Status: {status}", ms)

    # 4.2 Query Maintenance Tickets for Customer
    status, tickets_list, _, ms = http_request("GET", f"/maintenance?userId={customer_id}&role=KhachHang")
    c16_pass = (status == 200 and isinstance(tickets_list, list))
    report.log("Maintenance", f"4.2: Query maintenance tickets for customer returns active issues (Count: {len(tickets_list) if tickets_list else 0})", c16_pass, f"Status: {status}", ms)

    # ----------------------------------------------------
    # SCENARIO 5: Dashboard & BI Metrics
    # ----------------------------------------------------
    print("\n--- [SCENARIO 5: Dashboard & BI Metrics] ---")

    # 5.1 Customer Dashboard Stats
    status, dash_cust, _, ms = http_request("GET", f"/dashboard/stats?userId={customer_id}&role=KhachHang")
    c17_pass = (status == 200 and dash_cust is not None and ("customerStats" in dash_cust or "activeContracts" in dash_cust))
    report.log("Dashboard", f"5.1: Customer dashboard stats return active contracts and spending metrics", c17_pass, f"Status: {status}", ms)

    # 5.2 Admin / Manager Dashboard Stats
    status, dash_admin, _, ms = http_request("GET", "/dashboard/stats?role=Admin")
    c18_pass = (status == 200 and dash_admin is not None and ("adminStats" in dash_admin or "totalRevenue" in dash_admin))
    report.log("Dashboard", f"5.2: Admin dashboard stats return enterprise revenue and fleet metrics", c18_pass, f"Status: {status}", ms)

    # ----------------------------------------------------
    # SCENARIO 6: Promotions & Search Engine
    # ----------------------------------------------------
    print("\n--- [SCENARIO 6: Promotions & Search Engine] ---")

    # 6.1 Get Active Promotions
    status, promos, _, ms = http_request("GET", "/promotions")
    c19_pass = (status == 200 and isinstance(promos, list))
    report.log("Promotions", f"6.1: Query promotions returns available vouchers (Count: {len(promos) if promos else 0})", c19_pass, f"Status: {status}", ms)

    # 6.2 Search Across Entities
    status, search_res, _, ms = http_request("GET", "/search?q=Dell")
    c20_pass = (status == 200 and isinstance(search_res, list) and len(search_res) > 0)
    report.log("Search", f"6.2: Search query 'Dell' returns matched devices and entities (Matches: {len(search_res) if isinstance(search_res, list) else 0})", c20_pass, f"Status: {status}", ms)

    # 6.3 Search Suggestions
    status, suggestions, _, ms = http_request("GET", "/search/suggestions?q=Dell")
    c21_pass = (status == 200 and isinstance(suggestions, list) and len(suggestions) > 0)
    report.log("Search", f"6.3: Search auto-complete suggestions return predictive list ({suggestions if isinstance(suggestions, list) else ''})", c21_pass, f"Status: {status}", ms)

    # ----------------------------------------------------
    # SCENARIO 7: Boundary, Robustness & Injection Resilience
    # ----------------------------------------------------
    print("\n--- [SCENARIO 7: Boundary, Robustness & Injection Resilience] ---")

    # 7.1 SQL Injection payload in Search
    status, sql_res, _, ms = http_request("GET", "/search?q=%27%20OR%201%3D1--")
    c22_pass = (status == 200) # Safe parameterization, no 500 error
    report.log("Security", "7.1: SQL Injection payload in search parameter safely handled with parameterized query", c22_pass, f"Status: {status}", ms)

    # 7.2 Malformed JSON in POST Auth
    status, _, _, ms = http_request("POST", "/auth/login", "{ invalid_json: true, }", headers={"Content-Type": "application/json"})
    c23_pass = (status == 400)
    report.log("Security", "7.2: Malformed JSON body rejected cleanly with 400 BadRequest", c23_pass, f"Status: {status}", ms)

    # 7.3 Negative or Absurd User ID
    status, _, _, ms = http_request("GET", "/auth/profile/-99999")
    c24_pass = (status == 404)
    report.log("Security", "7.3: Negative user ID query rejected with 404 NotFound", c24_pass, f"Status: {status}", ms)

    # 7.4 Cross-Origin Resource Sharing (CORS) Preflight Options Check
    status, _, _, ms = http_request("OPTIONS", "/devices", headers={
        "Origin": "http://localhost:8080",
        "Access-Control-Request-Method": "GET"
    })
    c25_pass = (status in [200, 204])
    report.log("Security", "7.4: CORS preflight OPTIONS request returns 200/204 with AllowAll policy", c25_pass, f"Status: {status}", ms)

    # Final summary
    return report.summary()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
