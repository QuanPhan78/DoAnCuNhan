import os
import urllib.request

PLANTUML_DIAGRAMS = {
    "hinh_2_2_1_use_case_tong_quat": """@startuml
skinparam dpi 300
skinparam monochrome true
skinparam shadowing false
skinparam defaultFontName "Times New Roman"
skinparam defaultFontSize 11
skinparam packageStyle rectangle
skinparam usecase {
    BackgroundColor #FFFFFF
    BorderColor #0F172A
    BorderThickness 1.2
}
skinparam actor {
    BackgroundColor #FFFFFF
    BorderColor #0F172A
}

left to right direction

actor "Khách hàng\\n(KhachHang)" as ActKH
actor "Nhân viên Kinh doanh\\n(KinhDoanh)" as ActKD
actor "Kỹ thuật viên\\n(KyThuat)" as ActKT
actor "Quản trị viên\\n(Admin)" as ActAD
actor "Cổng thanh toán\\nVietQR / NAPAS" as ActBank <<Automated>>

rectangle "Hệ thống Quản lý Thuê Thiết bị (RentalSystem)" {
    package "Phân hệ Khách hàng" {
        usecase "UC-01: Đăng ký & Đăng nhập" as UC01
        usecase "UC-02: Đặt thuê & Giữ chỗ máy" as UC02
        usecase "UC-03: Ký hợp đồng Canvas" as UC03
    }

    package "Phân hệ Kinh doanh & Vận hành" {
        usecase "UC-04: Thẩm định duyệt hợp đồng" as UC04
        usecase "UC-05: Quản lý kho máy Serial" as UC05
        usecase "UC-06: Giám sát công nợ 4 cấp" as UC06
    }

    package "Phân hệ Kỹ thuật & Bảo trì" {
        usecase "UC-07: Xuất kho bàn giao máy" as UC07
        usecase "UC-08: Tiếp nhận bảo trì SLA" as UC08
        usecase "UC-09: Thu hồi & Đổi máy" as UC09
    }

    package "Phân hệ Tài chính & Thanh toán" {
        usecase "UC-10: Thanh toán VietQR động" as UC10
        usecase "UC-11: Đối soát tự động Webhook" as UC11
        usecase "UC-12: Hoàn tất thanh toán & Đóng HĐ" as UC12
    }
}

ActKH --> UC01
ActKH --> UC02
ActKH --> UC03
ActKH --> UC08
ActKH --> UC10

ActKD --> UC04
ActKD --> UC05
ActKD --> UC06

ActKT --> UC05
ActKT --> UC07
ActKT --> UC08
ActKT --> UC09

ActAD --> UC04
ActAD --> UC05
ActAD --> UC06

ActBank --> UC10
ActBank --> UC11
@enduml
""",
    "hinh_2_2_2_use_case_khach_hang": """@startuml
skinparam dpi 300
skinparam monochrome true
skinparam shadowing false
skinparam defaultFontName "Times New Roman"
skinparam defaultFontSize 11
skinparam packageStyle rectangle
skinparam usecase {
    BackgroundColor #FFFFFF
    BorderColor #0F172A
    BorderThickness 1.2
}
skinparam actor {
    BackgroundColor #FFFFFF
    BorderColor #0F172A
}

left to right direction

actor "Khách hàng\\n(KhachHang)" as ActKH
actor "Cổng thanh toán\\nNAPAS 247" as ActBank <<Automated>>

rectangle "Phân hệ Khách hàng (Customer Portal)" {
    usecase "UC-KH01: Đăng ký & Đăng nhập tài khoản" as UCKH01
    usecase "UC-KH02: Tìm kiếm & Lọc danh mục thiết bị" as UCKH02
    usecase "UC-KH03: Đặt thuê máy & Chọn thời hạn" as UCKH03
    usecase "UC-KH04: Ký hợp đồng số Canvas & Upload CCCD" as UCKH04
    usecase "UC-KH05: Thanh toán cọc qua VietQR NAPAS" as UCKH05
    usecase "UC-KH06: Theo dõi tiến độ trả góp & Sổ nợ" as UCKH06
    usecase "UC-KH07: Gửi yêu cầu báo sự cố kỹ thuật" as UCKH07
    usecase "UC-KH08: Yêu cầu gia hạn hợp đồng thuê" as UCKH08
}

ActKH --> UCKH01
ActKH --> UCKH02
ActKH --> UCKH03
ActKH --> UCKH04
ActKH --> UCKH05
ActKH --> UCKH06
ActKH --> UCKH07
ActKH --> UCKH08

ActBank --> UCKH05
@enduml
""",
    "hinh_2_2_3_use_case_admin": """@startuml
skinparam dpi 300
skinparam monochrome true
skinparam shadowing false
skinparam defaultFontName "Times New Roman"
skinparam defaultFontSize 11
skinparam packageStyle rectangle
skinparam usecase {
    BackgroundColor #FFFFFF
    BorderColor #0F172A
    BorderThickness 1.2
}
skinparam actor {
    BackgroundColor #FFFFFF
    BorderColor #0F172A
}

left to right direction

actor "Quản trị viên\\n(Admin)" as ActAD
actor "Nhân viên Kinh doanh\\n(KinhDoanh)" as ActKD
actor "Cổng Webhook\\nNAPAS 247" as ActBank <<Automated>>

rectangle "Phân hệ Quản trị & Vận hành (Admin & Operations)" {
    usecase "UC-AD01: Quản trị người dùng & Phân quyền" as UCAD01
    usecase "UC-AD02: Quản lý danh mục & Thiết bị Serial" as UCAD02
    usecase "UC-AD03: Thẩm định & Duyệt hợp đồng thuê" as UCAD03
    usecase "UC-AD04: Cấu hình mã khuyến mãi (Voucher)" as UCAD04
    usecase "UC-AD05: Giám sát công nợ & Tuổi nợ 4 cấp" as UCAD05
    usecase "UC-AD06: Cấu hình chính sách lãi phạt & Ân hạn" as UCAD06
    usecase "UC-AD07: Đối soát biến động số dư Webhook" as UCAD07
    usecase "UC-AD08: Lập phiếu chi hoàn trả tiền cọc" as UCAD08
    usecase "UC-AD09: Xuất báo cáo tài chính BI Excel" as UCAD09
}

ActAD --> UCAD01
ActAD --> UCAD02
ActAD --> UCAD03
ActAD --> UCAD04
ActAD --> UCAD05
ActAD --> UCAD06
ActAD --> UCAD07
ActAD --> UCAD08
ActAD --> UCAD09

ActKD --> UCAD02
ActKD --> UCAD03
ActKD --> UCAD04
ActKD --> UCAD05
ActKD --> UCAD08
ActKD --> UCAD09

ActBank --> UCAD07
@enduml
""",
    "hinh_2_2_4_use_case_bao_tri": """@startuml
skinparam dpi 300
skinparam monochrome true
skinparam shadowing false
skinparam defaultFontName "Times New Roman"
skinparam defaultFontSize 11
skinparam packageStyle rectangle
skinparam usecase {
    BackgroundColor #FFFFFF
    BorderColor #0F172A
    BorderThickness 1.2
}
skinparam actor {
    BackgroundColor #FFFFFF
    BorderColor #0F172A
}

left to right direction

actor "Quản trị viên\\n(Admin / Điều phối)" as ActAD
actor "Kỹ thuật viên\\n(KyThuat)" as ActKT
actor "Khách hàng\\n(KhachHang)" as ActKH

rectangle "Phân hệ Bảo trì & Kỹ thuật (Maintenance Portal)" {
    usecase "UC-BT01: Tiếp nhận yêu cầu sự cố máy" as UCBT01
    usecase "UC-BT02: Điều phối & Phân công kỹ thuật viên" as UCBT02
    usecase "UC-BT03: Kích hoạt SLA tạm dừng tính tiền" as UCBT03
    usecase "UC-BT04: Kiểm tra tại chỗ, sửa chữa & Đổi máy" as UCBT04
    usecase "UC-BT05: Đồng kiểm & Ký biên bản bàn giao" as UCBT05
    usecase "UC-BT06: Nghiệm thu hoàn tất & Cập nhật kho" as UCBT06
}

ActKH --> UCBT01
ActKH --> UCBT05

ActAD --> UCBT01
ActAD --> UCBT02
ActAD --> UCBT03

ActKT --> UCBT01
ActKT --> UCBT04
ActKT --> UCBT05
ActKT --> UCBT06
@enduml
"""
}

def render_diagrams():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "figures")
    os.makedirs(out_dir, exist_ok=True)
    
    for name, code in PLANTUML_DIAGRAMS.items():
        # Render PNG
        png_url = "https://kroki.io/plantuml/png"
        req = urllib.request.Request(
            png_url,
            data=code.encode("utf-8"),
            headers={"Content-Type": "text/plain; charset=utf-8", "User-Agent": "Mozilla/5.0"}
        )
        png_path = os.path.join(out_dir, f"{name}.png")
        with urllib.request.urlopen(req, timeout=15) as resp:
            png_bytes = resp.read()
            with open(png_path, "wb") as f:
                f.write(png_bytes)
        print(f"[OK] Generated PNG: {png_path} ({len(png_bytes)} bytes)")
        
        # Render SVG
        svg_url = "https://kroki.io/plantuml/svg"
        req_svg = urllib.request.Request(
            svg_url,
            data=code.encode("utf-8"),
            headers={"Content-Type": "text/plain; charset=utf-8", "User-Agent": "Mozilla/5.0"}
        )
        svg_path = os.path.join(out_dir, f"{name}.svg")
        with urllib.request.urlopen(req_svg, timeout=15) as resp:
            svg_bytes = resp.read()
            with open(svg_path, "wb") as f:
                f.write(svg_bytes)
        print(f"[OK] Generated SVG: {svg_path} ({len(svg_bytes)} bytes)")

if __name__ == "__main__":
    render_diagrams()
