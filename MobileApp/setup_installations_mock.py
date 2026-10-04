import json
import os

os.makedirs("assets/mock", exist_ok=True)
installations = [
    {
        "contractId": "C001",
        "status": "Đang thực hiện",
        "expectedDate": "02/09/2026",
        "actualDate": "",
        "assignedStaffName": "Trần Nhân Viên",
        "notes": "Cần mang theo thang và khoan"
    },
    {
        "contractId": "C002",
        "status": "Chưa bắt đầu",
        "expectedDate": "16/09/2026",
        "actualDate": "",
        "assignedStaffName": "Trần Nhân Viên",
        "notes": "Liên hệ bảo vệ trước khi vào"
    }
]
with open("assets/mock/installations.json", "w", encoding="utf-8") as f:
    json.dump(installations, f, ensure_ascii=False, indent=2)