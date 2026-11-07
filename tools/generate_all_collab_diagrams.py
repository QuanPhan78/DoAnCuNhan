# -*- coding: utf-8 -*-
"""
Generate high-resolution (300 DPI) 16:9 3-Layer Collaboration Diagrams (STT 3.4.1.3 to 3.4.7.3)
Architecture: Presentation (Boundary) -> Control (Logic) -> Data (Entity)
Colors: Executive Navy (#0f2b5c), Royal Blue (#1e3a8a), Crisp Slate (#e2e8f0), Pure White (#ffffff)
"""
import os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'figures')

NAVY_PRIMARY = '#0f2b5c'
ROYAL_BLUE   = '#1e3a8a'
ACCENT_BLUE  = '#2563eb'
BG_CANVAS    = '#ffffff'
CARD_BG      = '#ffffff'
CARD_BORDER  = '#64748b'
HEADER_BG    = '#0f2b5c'
HEADER_TEXT  = '#ffffff'
TEXT_MAIN    = '#0f172a'
TEXT_MUTED   = '#334155'
LINE_COLOR   = '#0f2b5c'

font_hdr = {'fontname': 'Segoe UI', 'fontsize': 10.5, 'weight': 'bold'}
font_step = {'fontname': 'Segoe UI', 'fontsize': 9.2, 'weight': 'normal'}
font_msg = {'fontname': 'Segoe UI', 'fontsize': 8.8, 'weight': 'bold'}
font_layer = {'fontname': 'Segoe UI', 'fontsize': 9.5, 'weight': 'bold'}

def draw_card(ax, x, y, w, h, title, role_badge, steps, badge_bg='#e2e8f0', badge_txt='#0f172a'):
    # shadow
    shadow = FancyBboxPatch((x + 0.04, y - 0.04), w, h, boxstyle="round,pad=0.03,rounding_size=0.12",
                            facecolor='#e2e8f0', edgecolor='none', zorder=1)
    ax.add_patch(shadow)
    
    # card
    card = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.12",
                          facecolor=CARD_BG, edgecolor=CARD_BORDER, linewidth=1.4, zorder=2)
    ax.add_patch(card)
    
    # header
    hh = 0.55
    hdr = FancyBboxPatch((x, y + h - hh), w, hh, boxstyle="round,pad=0.03,rounding_size=0.12",
                         facecolor=HEADER_BG, edgecolor=HEADER_BG, zorder=3)
    ax.add_patch(hdr)
    sq = patches.Rectangle((x, y + h - hh), w, hh / 2.0, facecolor=HEADER_BG, edgecolor=HEADER_BG, zorder=3)
    ax.add_patch(sq)
    
    ax.text(x + w / 2.0, y + h - hh / 2.0, title, color=HEADER_TEXT, ha='center', va='center', zorder=4, **font_hdr)
    
    # badge
    bw, bh = w * 0.75, 0.28
    bx = x + (w - bw) / 2.0
    by = y + h - hh - 0.38
    b_patch = FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.02,rounding_size=0.08",
                             facecolor=badge_bg, edgecolor='none', zorder=4)
    ax.add_patch(b_patch)
    ax.text(bx + bw / 2.0, by + bh / 2.0, role_badge, color=badge_txt, ha='center', va='center', zorder=5,
            fontname='Segoe UI', fontsize=8.0, weight='bold')
    
    # steps
    ly = by - 0.35
    for st in steps:
        ax.plot(x + 0.22, ly, marker='o', markersize=3.2, color=ACCENT_BLUE, zorder=5)
        ax.text(x + 0.36, ly, st, color=TEXT_MAIN, ha='left', va='center', zorder=5, **font_step)
        ly -= 0.38

def draw_arrow(ax, p1, p2, label, label_pos=(0, 0), rad=0.0):
    conn = f"arc3,rad={rad}" if rad != 0 else "arc3,rad=0"
    arr = FancyArrowPatch(p1, p2, connectionstyle=conn, arrowstyle='-|>',
                          mutation_scale=15, linewidth=1.8, color=ROYAL_BLUE, zorder=6)
    ax.add_patch(arr)
    mx = (p1[0] + p2[0]) / 2.0 + label_pos[0]
    my = (p1[1] + p2[1]) / 2.0 + label_pos[1]
    ax.text(mx, my, label, color=NAVY_PRIMARY, ha='center', va='center', zorder=7,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", edgecolor="#cbd5e1", alpha=0.92, lw=0.8),
            **font_msg)

collab_specs = [
    {
        "filename": "hinh_3_4_1_3_collab_3lop_dang_ky_xac_thuc.png",
        "title": "SƠ ĐỒ CỘNG TÁC 3 LỚP: ĐĂNG KÝ & XÁC THỰC",
        "nodes": [
            {"id": "User", "x": 0.5, "y": 5.4, "w": 3.8, "h": 2.2, "t": "1. Tác nhân: Khách hàng", "b": "ACTOR / USER", "bb": "#dbeafe", "bt": "#1e40af", "s": ["Gửi thông tin đăng nhập", "Nhận phản hồi trạng thái"]},
            {"id": "View", "x": 5.6, "y": 5.4, "w": 3.8, "h": 2.2, "t": "2. Giao diện: LoginView", "b": "BOUNDARY", "bb": "#fef3c7", "bt": "#92400e", "s": ["Form nhập Email & Mật khẩu", "Xác thực Client Validation"]},
            {"id": "Ctrl", "x": 10.7, "y": 5.4, "w": 3.8, "h": 2.2, "t": "3. Điều khiển: AccountCtrl", "b": "CONTROL", "bb": "#e0e7ff", "bt": "#3730a3", "s": ["POST /Account/Login", "So khớp băm mật khẩu"]},
            {"id": "Auth", "x": 10.7, "y": 0.6, "w": 3.8, "h": 2.2, "t": "4. Bảo mật: CookieAuth", "b": "SECURITY SERVICE", "bb": "#dcfce7", "bt": "#166534", "s": ["SignInAsync(Principal)", "Thiết lập Cookie Claims"]},
            {"id": "DB", "x": 5.6, "y": 0.6, "w": 3.8, "h": 2.2, "t": "5. Truy cập: AppDbContext", "b": "DATA ACCESS", "bb": "#f1f5f9", "bt": "#334155", "s": ["Truy vấn LINQ theo Email", "Include(VaiTro) đồng bộ"]},
            {"id": "Entity", "x": 0.5, "y": 0.6, "w": 3.8, "h": 2.2, "t": "6. Thực thể: NguoiDung", "b": "ENTITY", "bb": "#fee2e2", "bt": "#991b1b", "s": ["Bảng NguoiDungs", "Bảng VaiTros (RBAC)"]}
        ],
        "arrows": [
            {"from": (4.3, 6.5), "to": (5.6, 6.5), "lbl": "1: Submit Login Form\n8: Redirect Dashboard", "pos": (0, 0.35)},
            {"from": (9.4, 6.5), "to": (10.7, 6.5), "lbl": "2: POST /Account/Login\n7: Ok / RedirectResult", "pos": (0, 0.35)},
            {"from": (12.6, 5.4), "to": (12.6, 2.8), "lbl": "5: SignInAsync()\n6: Set-Cookie Claims", "pos": (0.8, 0)},
            {"from": (10.7, 5.8), "to": (9.4, 2.4), "lbl": "3: Query User by Email", "pos": (-0.2, 0.2)},
            {"from": (5.6, 1.7), "to": (4.3, 1.7), "lbl": "4: Load NguoiDung + VaiTro", "pos": (0, 0.3)}
        ]
    },
    {
        "filename": "hinh_3_4_2_3_collab_3lop_dat_thue_inventory.png",
        "title": "SƠ ĐỒ CỘNG TÁC 3 LỚP: ĐẶT THUÊ MÁY & KIỂM TRA TỒN KHO",
        "nodes": [
            {"id": "User", "x": 0.5, "y": 5.4, "w": 3.8, "h": 2.2, "t": "1. Tác nhân: Khách hàng", "b": "ACTOR / USER", "bb": "#dbeafe", "bt": "#1e40af", "s": ["Bấm Checkout giỏ hàng", "Nhận điều hướng ký HĐ"]},
            {"id": "View", "x": 5.6, "y": 5.4, "w": 3.8, "h": 2.2, "t": "2. Giao diện: CheckoutView", "b": "BOUNDARY", "bb": "#fef3c7", "bt": "#92400e", "s": ["Form chọn lịch thuê máy", "Hiển thị tiền cọc dự kiến"]},
            {"id": "Ctrl", "x": 10.7, "y": 5.4, "w": 3.8, "h": 2.2, "t": "3. Điều khiển: CartCtrl", "b": "CONTROL", "bb": "#e0e7ff", "bt": "#3730a3", "s": ["POST /Cart/Checkout", "Điều phối khóa tồn kho"]},
            {"id": "Lock", "x": 10.7, "y": 0.6, "w": 3.8, "h": 2.2, "t": "4. Khóa: SemaphoreSlim", "b": "CONCURRENCY LOCK", "bb": "#fee2e2", "bt": "#991b1b", "s": ["InventoryLock.WaitAsync()", "Release() trong finally"]},
            {"id": "DB", "x": 5.6, "y": 0.6, "w": 3.8, "h": 2.2, "t": "5. CSDL: AppDbContext", "b": "DATA ACCESS", "bb": "#f1f5f9", "bt": "#334155", "s": ["Kiểm tra giao thoa ngày", "SaveChangesAsync()"]},
            {"id": "Entity", "x": 0.5, "y": 0.6, "w": 3.8, "h": 2.2, "t": "6. Thực thể: HopDong", "b": "ENTITY", "bb": "#dcfce7", "bt": "#166534", "s": ["ThietBi.TrangThai = 3", "HopDong (Trạng thái = 0)"]}
        ],
        "arrows": [
            {"from": (4.3, 6.5), "to": (5.6, 6.5), "lbl": "1: Bấm Checkout\n10: Điều hướng SignContract", "pos": (0, 0.35)},
            {"from": (9.4, 6.5), "to": (10.7, 6.5), "lbl": "2: POST /Cart/Checkout\n9: RedirectResult", "pos": (0, 0.35)},
            {"from": (12.6, 5.4), "to": (12.6, 2.8), "lbl": "3: await WaitAsync()\n8: Lock.Release()", "pos": (0.75, 0)},
            {"from": (10.7, 5.8), "to": (9.4, 2.4), "lbl": "4: CheckAvailability()\n6: SaveChangesAsync()", "pos": (-0.2, 0.25)},
            {"from": (5.6, 1.7), "to": (4.3, 1.7), "lbl": "5: Cấp phát Serial tạm\n7: Tạo HĐ & Chi tiết HĐ", "pos": (0, 0.35)}
        ]
    },
    {
        "filename": "hinh_3_4_3_3_collab_3lop_thanh_toan_vietqr.png",
        "title": "SƠ ĐỒ CỘNG TÁC 3 LỚP: THANH TOÁN VIETQR & ĐỐI SOÁT WEBHOOK",
        "nodes": [
            {"id": "Bank", "x": 0.5, "y": 5.4, "w": 3.8, "h": 2.2, "t": "1. Tác nhân: Cổng NAPAS", "b": "BANKING SYSTEM", "bb": "#dbeafe", "bt": "#1e40af", "s": ["Biến động số dư tài khoản", "Bắn Webhook IPN"]},
            {"id": "Endp", "x": 5.6, "y": 5.4, "w": 3.8, "h": 2.2, "t": "2. Tiếp nhận: Webhook", "b": "BOUNDARY / ENDPOINT", "bb": "#fef3c7", "bt": "#92400e", "s": ["POST /Payment/BankingWebhook", "Xác thực Authorization Token"]},
            {"id": "Ctrl", "x": 10.7, "y": 5.4, "w": 3.8, "h": 2.2, "t": "3. Điều khiển: PaymentCtrl", "b": "CONTROL", "bb": "#e0e7ff", "bt": "#3730a3", "s": ["Bóc tách mã hợp đồng", "Phân bổ Waterfall gạch nợ"]},
            {"id": "Lock", "x": 10.7, "y": 0.6, "w": 3.8, "h": 2.2, "t": "4. Khóa: PaymentLock", "b": "CONCURRENCY LOCK", "bb": "#fee2e2", "bt": "#991b1b", "s": ["PaymentLock.WaitAsync()", "Idempotency Reference Check"]},
            {"id": "DB", "x": 5.6, "y": 0.6, "w": 3.8, "h": 2.2, "t": "5. CSDL: AppDbContext", "b": "DATA ACCESS", "bb": "#f1f5f9", "bt": "#334155", "s": ["BeginTransactionAsync", "Serializable Isolation Level"]},
            {"id": "Entity", "x": 0.5, "y": 0.6, "w": 3.8, "h": 2.2, "t": "6. Thực thể: PhieuThu", "b": "ENTITY", "bb": "#dcfce7", "bt": "#166534", "s": ["Tạo PhieuThu tự động", "Gạch nợ KyHanThanhToan"]}
        ],
        "arrows": [
            {"from": (4.3, 6.5), "to": (5.6, 6.5), "lbl": "1: POST /Payment/BankingWebhook\n10: HTTP 200 OK", "pos": (0, 0.35)},
            {"from": (9.4, 6.5), "to": (10.7, 6.5), "lbl": "2: BankingWebhook(payload)\n9: OkObjectResult", "pos": (0, 0.35)},
            {"from": (12.6, 5.4), "to": (12.6, 2.8), "lbl": "3: PaymentLock.WaitAsync()\n8: PaymentLock.Release()", "pos": (0.8, 0)},
            {"from": (10.7, 5.8), "to": (9.4, 2.4), "lbl": "4: Check Idempotency\n6: SaveChangesAsync()", "pos": (-0.2, 0.25)},
            {"from": (5.6, 1.7), "to": (4.3, 1.7), "lbl": "5: Waterfall gạch nợ kỳ hạn\n7: Sinh PhieuThu (MaNV=null)", "pos": (0, 0.35)}
        ]
    },
    {
        "filename": "hinh_3_4_4_3_collab_3lop_ban_giao_ky_so.png",
        "title": "SƠ ĐỒ CỘNG TÁC 3 LỚP: BÀN GIAO & KÝ BIÊN BẢN ĐIỆN TỬ",
        "nodes": [
            {"id": "User", "x": 0.5, "y": 5.4, "w": 3.8, "h": 2.2, "t": "1. Tác nhân: Khách hàng", "b": "ACTOR / USER", "bb": "#dbeafe", "bt": "#1e40af", "s": ["Ký trực tiếp trên Canvas", "Tải minh chứng CCCD"]},
            {"id": "View", "x": 5.6, "y": 5.4, "w": 3.8, "h": 2.2, "t": "2. Giao diện: SignView", "b": "BOUNDARY", "bb": "#fef3c7", "bt": "#92400e", "s": ["Vùng vẽ HTML5 Canvas", "Input tệp hình ảnh CCCD"]},
            {"id": "Ctrl", "x": 10.7, "y": 5.4, "w": 3.8, "h": 2.2, "t": "3. Điều khiển: HopDongCtrl", "b": "CONTROL", "bb": "#e0e7ff", "bt": "#3730a3", "s": ["POST /Cart/SignContract", "Lưu trữ tệp vật lý bảo mật"]},
            {"id": "Val", "x": 10.7, "y": 0.6, "w": 3.8, "h": 2.2, "t": "4. Trình kiểm: MagicBytes", "b": "VALIDATION SERVICE", "bb": "#fee2e2", "bt": "#991b1b", "s": ["Kiểm tra Base64 (<256KB)", "Kiểm tra PNG Magic Bytes"]},
            {"id": "DB", "x": 5.6, "y": 0.6, "w": 3.8, "h": 2.2, "t": "5. CSDL: AppDbContext", "b": "DATA ACCESS", "bb": "#f1f5f9", "bt": "#334155", "s": ["Ghi nhận BienBanBanGiao", "Lưu đường dẫn ảnh CCCD"]},
            {"id": "Entity", "x": 0.5, "y": 0.6, "w": 3.8, "h": 2.2, "t": "6. Thực thể: BienBan", "b": "ENTITY", "bb": "#dcfce7", "bt": "#166534", "s": ["BienBanBanGiao (Ký số)", "ThietBi.TrangThai = 1"]}
        ],
        "arrows": [
            {"from": (4.3, 6.5), "to": (5.6, 6.5), "lbl": "1: Ký số Canvas & Gửi ảnh\n10: Nhận biên bản bàn giao", "pos": (0, 0.35)},
            {"from": (9.4, 6.5), "to": (10.7, 6.5), "lbl": "2: POST /Cart/SignContract\n9: Chuyển hướng thành công", "pos": (0, 0.35)},
            {"from": (12.6, 5.4), "to": (12.6, 2.8), "lbl": "3: Xác thực PNG Header\n4: Kiểm tra dung lượng tệp", "pos": (0.8, 0)},
            {"from": (10.7, 5.8), "to": (9.4, 2.4), "lbl": "5: Lưu đường dẫn chữ ký\n7: await SaveChangesAsync()", "pos": (-0.2, 0.25)},
            {"from": (5.6, 1.7), "to": (4.3, 1.7), "lbl": "6: Cập nhật ChuKyKhachHang\n8: Chuyển máy sang Đang thuê", "pos": (0, 0.35)}
        ]
    },
    {
        "filename": "hinh_3_4_5_3_collab_3lop_bao_tri_su_co.png",
        "title": "SƠ ĐỒ CỘNG TÁC 3 LỚP: BÁO CÁO SỰ CỐ & PHÂN CÔNG BẢO TRÌ",
        "nodes": [
            {"id": "User", "x": 0.5, "y": 5.4, "w": 3.8, "h": 2.2, "t": "1. Tác nhân: Khách hàng", "b": "ACTOR / USER", "bb": "#dbeafe", "bt": "#1e40af", "s": ["Gửi báo hỏng & ảnh lỗi", "Nhận thông báo KTV đến"]},
            {"id": "View", "x": 5.6, "y": 5.4, "w": 3.8, "h": 2.2, "t": "2. Giao diện: TicketView", "b": "BOUNDARY", "bb": "#fef3c7", "bt": "#92400e", "s": ["Form nhập chi tiết sự cố", "Danh sách việc kỹ thuật"]},
            {"id": "Ctrl", "x": 10.7, "y": 5.4, "w": 3.8, "h": 2.2, "t": "3. Điều khiển: BaoTriCtrl", "b": "CONTROL", "bb": "#e0e7ff", "bt": "#3730a3", "s": ["Tiếp nhận ticket sự cố", "Điều phối Kỹ thuật viên"]},
            {"id": "Tech", "x": 10.7, "y": 0.6, "w": 3.8, "h": 2.2, "t": "4. Tác nhân: Kỹ thuật viên", "b": "ACTOR / TECHNICIAN", "bb": "#e0e7ff", "bt": "#3730a3", "s": ["Xem danh sách việc (MyTasks)", "Cập nhật kết quả xử lý"]},
            {"id": "DB", "x": 5.6, "y": 0.6, "w": 3.8, "h": 2.2, "t": "5. CSDL: AppDbContext", "b": "DATA ACCESS", "bb": "#f1f5f9", "bt": "#334155", "s": ["Lưu PhieuBaoTri", "Cập nhật PhanCongCongViec"]},
            {"id": "Entity", "x": 0.5, "y": 0.6, "w": 3.8, "h": 2.2, "t": "6. Thực thể: PhieuBaoTri", "b": "ENTITY", "bb": "#fee2e2", "bt": "#991b1b", "s": ["Kích hoạt TamDungTinhTien", "ThietBi.TrangThai = 2 (Lỗi)"]}
        ],
        "arrows": [
            {"from": (4.3, 6.5), "to": (5.6, 6.5), "lbl": "1: Gửi ticket báo sự cố\n10: Cập nhật tiến độ SLA", "pos": (0, 0.35)},
            {"from": (9.4, 6.5), "to": (10.7, 6.5), "lbl": "2: POST /BaoTri/TaoPhieu\n9: Phản hồi duyệt xử lý", "pos": (0, 0.35)},
            {"from": (12.6, 5.4), "to": (12.6, 2.8), "lbl": "5: Phân công nhân sự\n6: KTV tiếp nhận nhiệm vụ", "pos": (0.8, 0)},
            {"from": (10.7, 5.8), "to": (9.4, 2.4), "lbl": "3: Khởi tạo PhieuBaoTri\n7: Cập nhật trạng thái", "pos": (-0.2, 0.25)},
            {"from": (5.6, 1.7), "to": (4.3, 1.7), "lbl": "4: Bật cờ TamDungTinhTien\n8: Lưu lịch sử bảo trì", "pos": (0, 0.35)}
        ]
    },
    {
        "filename": "hinh_3_4_6_3_collab_3lop_gia_han_cong_no.png",
        "title": "SƠ ĐỒ CỘNG TÁC 3 LỚP: GIA HẠN HỢP ĐỒNG & PHÂN KỲ NỢ",
        "nodes": [
            {"id": "User", "x": 0.5, "y": 5.4, "w": 3.8, "h": 2.2, "t": "1. Tác nhân: Khách hàng", "b": "ACTOR / USER", "bb": "#dbeafe", "bt": "#1e40af", "s": ["Chọn ngày kết thúc mới", "Nhận lịch trả nợ bổ sung"]},
            {"id": "View", "x": 5.6, "y": 5.4, "w": 3.8, "h": 2.2, "t": "2. Giao diện: ExtensionView", "b": "BOUNDARY", "bb": "#fef3c7", "bt": "#92400e", "s": ["Form đăng ký gia hạn", "Duyệt yêu cầu gia hạn"]},
            {"id": "Ctrl", "x": 10.7, "y": 5.4, "w": 3.8, "h": 2.2, "t": "3. Điều khiển: HopDongCtrl", "b": "CONTROL", "bb": "#e0e7ff", "bt": "#3730a3", "s": ["POST /Account/Extension", "Kiểm tra xung đột lịch thuê"]},
            {"id": "Help", "x": 10.7, "y": 0.6, "w": 3.8, "h": 2.2, "t": "4. Thuật toán: DebtHelper", "b": "LOGIC SERVICE", "bb": "#fef3c7", "bt": "#92400e", "s": ["Tính toán phân kỳ trả góp", "Phân loại 4 nhóm tuổi nợ"]},
            {"id": "DB", "x": 5.6, "y": 0.6, "w": 3.8, "h": 2.2, "t": "5. CSDL: AppDbContext", "b": "DATA ACCESS", "bb": "#f1f5f9", "bt": "#334155", "s": ["Lưu YeuCauGiaHan", "await SaveChangesAsync()"]},
            {"id": "Entity", "x": 0.5, "y": 0.6, "w": 3.8, "h": 2.2, "t": "6. Thực thể: KyHanThanhToan", "b": "ENTITY", "bb": "#dcfce7", "bt": "#166534", "s": ["Kéo dài HopDong.NgayKetThuc", "Sinh KyHanThanhToan mới"]}
        ],
        "arrows": [
            {"from": (4.3, 6.5), "to": (5.6, 6.5), "lbl": "1: Gửi yêu cầu gia hạn\n10: Nhận kết quả gia hạn", "pos": (0, 0.35)},
            {"from": (9.4, 6.5), "to": (10.7, 6.5), "lbl": "2: POST /RequestExtension\n9: Phản hồi duyệt thành công", "pos": (0, 0.35)},
            {"from": (12.6, 5.4), "to": (12.6, 2.8), "lbl": "4: Tính toán lại phân kỳ nợ\n5: Kiểm tra quá hạn Tier 0-4", "pos": (0.8, 0)},
            {"from": (10.7, 5.8), "to": (9.4, 2.4), "lbl": "3: Lưu YeuCauGiaHan\n7: Cập nhật CSDL", "pos": (-0.2, 0.25)},
            {"from": (5.6, 1.7), "to": (4.3, 1.7), "lbl": "6: Cập nhật ngày kết thúc\n8: Bổ sung các kỳ trả góp mới", "pos": (0, 0.35)}
        ]
    },
    {
        "filename": "hinh_3_4_7_3_collab_3lop_tra_may_hoan_coc.png",
        "title": "SƠ ĐỒ CỘNG TÁC 3 LỚP: TRẢ MÁY, NGHIỆM THU & HOÀN CỌC",
        "nodes": [
            {"id": "User", "x": 0.5, "y": 5.4, "w": 3.8, "h": 2.2, "t": "1. Tác nhân: Khách hàng", "b": "ACTOR / USER", "bb": "#dbeafe", "bt": "#1e40af", "s": ["Bàn giao lại thiết bị vật lý", "Nhận tiền cọc hoàn trả"]},
            {"id": "View", "x": 5.6, "y": 5.4, "w": 3.8, "h": 2.2, "t": "2. Giao diện: ReturnView", "b": "BOUNDARY", "bb": "#fef3c7", "bt": "#92400e", "s": ["Biên bản nghiệm thu hoàn trả", "Xác nhận ngoại quan linh kiện"]},
            {"id": "Ctrl", "x": 10.7, "y": 5.4, "w": 3.8, "h": 2.2, "t": "3. Điều khiển: HopDongCtrl", "b": "CONTROL", "bb": "#e0e7ff", "bt": "#3730a3", "s": ["Duyệt nghiệm thu thiết bị", "Quyết toán hoàn tiền cọc"]},
            {"id": "Help", "x": 10.7, "y": 0.6, "w": 3.8, "h": 2.2, "t": "4. Thuật toán: DebtHelper", "b": "LOGIC SERVICE", "bb": "#fef3c7", "bt": "#92400e", "s": ["Tính cọc trừ hư hỏng/phạt", "Xác định số tiền thực chi"]},
            {"id": "DB", "x": 5.6, "y": 0.6, "w": 3.8, "h": 2.2, "t": "5. CSDL: AppDbContext", "b": "DATA ACCESS", "bb": "#f1f5f9", "bt": "#334155", "s": ["Tạo Phiếu chi (PhieuChi)", "await SaveChangesAsync()"]},
            {"id": "Entity", "x": 0.5, "y": 0.6, "w": 3.8, "h": 2.2, "t": "6. Thực thể: ThietBi & HĐ", "b": "ENTITY", "bb": "#dcfce7", "bt": "#166534", "s": ["ThietBi.TrangThai = 0 (Sẵn)", "HopDong.TrangThai = 2 (Xong)"]}
        ],
        "arrows": [
            {"from": (4.3, 6.5), "to": (5.6, 6.5), "lbl": "1: Trả máy tại quầy\n10: Nhận tiền hoàn cọc", "pos": (0, 0.35)},
            {"from": (9.4, 6.5), "to": (10.7, 6.5), "lbl": "2: Gửi biên bản nghiệm thu\n9: Xuất phiếu chi hoàn cọc", "pos": (0, 0.35)},
            {"from": (12.6, 5.4), "to": (12.6, 2.8), "lbl": "4: Quyết toán nợ & Hư hỏng\n5: Tính toán số tiền hoàn", "pos": (0.8, 0)},
            {"from": (10.7, 5.8), "to": (9.4, 2.4), "lbl": "3: Xác nhận hoàn tất HĐ\n7: Ghi nhận PhieuChi vào DB", "pos": (-0.2, 0.25)},
            {"from": (5.6, 1.7), "to": (4.3, 1.7), "lbl": "6: Chuyển máy về kho sẵn sàng\n8: Cập nhật HĐ hoàn tất", "pos": (0, 0.35)}
        ]
    }
]

for spec in collab_specs:
    fig, ax = plt.subplots(figsize=(15, 8.2), dpi=300)
    ax.set_facecolor(BG_CANVAS)
    fig.patch.set_facecolor(BG_CANVAS)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8.2)
    ax.axis('off')
    
    # Draw Layer division backgrounds (Subtle, professional)
    layer1_bg = patches.Rectangle((0.2, 4.8), 14.6, 3.2, facecolor='#f8fafc', edgecolor='#e2e8f0', linewidth=1.0, zorder=0)
    layer2_bg = patches.Rectangle((0.2, 0.2), 14.6, 4.4, facecolor='#ffffff', edgecolor='#e2e8f0', linewidth=1.0, zorder=0)
    ax.add_patch(layer1_bg)
    ax.add_patch(layer2_bg)
    
    # Layer labels on left
    ax.text(0.35, 7.7, "TẦNG BIÊN (BOUNDARY & PRESENTATION)", color='#64748b', **font_layer)
    ax.text(0.35, 4.3, "TẦNG ĐIỀU KHIỂN & THỰC THỂ (CONTROL & DATA ENTITY)", color='#64748b', **font_layer)
    
    # Draw nodes
    for n in spec["nodes"]:
        draw_card(ax, n["x"], n["y"], n["w"], n["h"], n["t"], n["b"], n["s"], n["bb"], n["bt"])
        
    # Draw arrows
    for arr in spec["arrows"]:
        draw_arrow(ax, arr["from"], arr["to"], arr["lbl"], arr["pos"])
        
    plt.tight_layout()
    out_file = os.path.join(OUTPUT_DIR, spec["filename"])
    plt.savefig(out_file, dpi=300, facecolor=BG_CANVAS, edgecolor='none')
    plt.close()
    print(f"Generated clean 16:9 diagram: {spec['filename']}")

print("\nALL 7 COLLABORATION DIAGRAMS GENERATED SUCCESSFULLY!")
