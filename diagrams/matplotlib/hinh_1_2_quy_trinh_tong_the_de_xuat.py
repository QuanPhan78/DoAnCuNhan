# -*- coding: utf-8 -*-
"""
Generate Hinh 1.2. 1: So do luong quy trinh nghiep vu tong the sau khi tin hoc hoa
Resolution: 300 DPI
Colors: Executive Navy & Pure White (#0f2b5c, #1e3a8a, #f8fafc, #ffffff, #e2e8f0)
No internal title/subtitle as requested by user.
"""
import sys, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

sys.stdout.reconfigure(encoding='utf-8')

# Palette
NAVY_PRIMARY = '#0f2b5c'
ROYAL_BLUE   = '#1e3a8a'
ACCENT_BLUE  = '#2563eb'
BG_CANVAS    = '#ffffff'
CARD_BG      = '#ffffff'
CARD_BORDER  = '#94a3b8'
HEADER_BG    = '#0f2b5c'
HEADER_TEXT  = '#ffffff'
TEXT_MAIN    = '#0f172a'
TEXT_MUTED   = '#334155'
LINE_COLOR   = '#1e3a8a'

stages = [
    {
        "id": 1,
        "title": "GIAI ĐOẠN 1: ĐẶT THUÊ TRỰC TUYẾN",
        "badge": "KHÁCH HÀNG / WEB CLIENT",
        "badge_bg": "#dbeafe",
        "badge_text": "#1e40af",
        "steps": [
            "1. Duyệt danh mục sản phẩm & cấu hình",
            "2. Chọn số lượng, thời gian thuê máy",
            "3. Thêm vào giỏ hàng & áp mã giảm giá",
            "4. SemaphoreSlim khóa giữ chỗ kho máy",
            "5. Khởi tạo hợp đồng (Trạng thái Chờ ký)"
        ]
    },
    {
        "id": 2,
        "title": "GIAI ĐOẠN 2: KÝ SỐ & THẨM ĐỊNH",
        "badge": "XÁC THỰC PHÁP LÝ",
        "badge_bg": "#fef3c7",
        "badge_text": "#92400e",
        "steps": [
            "1. Chọn kế hoạch phân kỳ (trả góp 3-5 kỳ)",
            "2. Ký hợp đồng điện tử trên HTML5 Canvas",
            "3. Tải minh chứng ảnh CCCD hai mặt",
            "4. Xác thực Magic Bytes (PNG / JPEG)",
            "5. Chuyển hợp đồng sang trạng thái Chờ duyệt"
        ]
    },
    {
        "id": 3,
        "title": "GIAI ĐOẠN 3: DUYỆT & GIAO THIẾT BỊ",
        "badge": "KINH DOANH & KHO",
        "badge_bg": "#e0e7ff",
        "badge_text": "#3730a3",
        "steps": [
            "1. Kinh doanh kiểm tra chữ ký & hồ sơ CCCD",
            "2. Phân công thiết bị vật lý theo số Serial",
            "3. Đổi trạng thái máy: Sẵn sàng → Giữ chỗ",
            "4. Lập Biên bản bàn giao điện tử",
            "5. Bàn giao máy & khách xác nhận nhận thiết bị"
        ]
    },
    {
        "id": 4,
        "title": "GIAI ĐOẠN 4: THANH TOÁN & ĐỐI SOÁT",
        "badge": "OPEN BANKING / TỰ ĐỘNG",
        "badge_bg": "#dcfce7",
        "badge_text": "#166534",
        "steps": [
            "1. Quét mã VietQR động chuẩn NAPAS 247",
            "2. Webhook ngân hàng bắt biến động số dư",
            "3. Giao dịch Serializable thực thi thuật toán gạch nợ",
            "4. Tự động gạch nợ kỳ hạn & sinh Phiếu thu",
            "5. Phân loại 4 nhóm tuổi nợ nếu phát sinh quá hạn"
        ]
    },
    {
        "id": 5,
        "title": "GIAI ĐOẠN 5: BẢO TRÌ & QUYẾT TOÁN",
        "badge": "KỸ THUẬT & TÀI CHÍNH",
        "badge_bg": "#fee2e2",
        "badge_text": "#991b1b",
        "steps": [
            "1. Khách gửi ticket báo sự cố kỹ thuật trực tuyến",
            "2. Phân công Kỹ thuật viên xử lý tận nơi",
            "3. Kích hoạt cờ TamDungTinhTien nếu bảo trì >24h",
            "4. Thu hồi máy, nghiệm thu ngoại quan & linh kiện",
            "5. Quyết toán chi phí phát sinh & hoàn cọc (Phiếu chi)"
        ]
    }
]

fig, ax = plt.subplots(figsize=(15, 9.2), dpi=300)
ax.set_facecolor(BG_CANVAS)
fig.patch.set_facecolor(BG_CANVAS)
ax.set_xlim(0, 15)
ax.set_ylim(0, 9.2)
ax.axis('off')

# Layout coordinates
# Row 1 (Top): Stages 1, 2, 3
# Row 2 (Bottom): Stages 5, 4 (so flow is 1 -> 2 -> 3 -> 4 -> 5)
card_w = 4.45
card_h = 3.8
header_h = 0.65

positions = {
    1: (0.45, 4.9),
    2: (5.27, 4.9),
    3: (10.10, 4.9),
    4: (7.70, 0.4),
    5: (2.85, 0.4)
}

font_title = {'fontname': 'Segoe UI', 'fontsize': 10.5, 'weight': 'bold'}
font_step = {'fontname': 'Segoe UI', 'fontsize': 9.2, 'weight': 'normal'}
font_badge = {'fontname': 'Segoe UI', 'fontsize': 7.5, 'weight': 'bold'}

for s in stages:
    sid = s["id"]
    x, y = positions[sid]
    
    # Outer card with soft shadow effect (outer box slightly shifted)
    shadow = FancyBboxPatch((x + 0.04, y - 0.04), card_w, card_h,
                            boxstyle="round,pad=0.03,rounding_size=0.12",
                            facecolor='#e2e8f0', edgecolor='none', zorder=1)
    ax.add_patch(shadow)
    
    # Main card
    card = FancyBboxPatch((x, y), card_w, card_h,
                          boxstyle="round,pad=0.03,rounding_size=0.12",
                          facecolor=CARD_BG, edgecolor=CARD_BORDER, linewidth=1.4, zorder=2)
    ax.add_patch(card)
    
    # Header box
    hdr = FancyBboxPatch((x, y + card_h - header_h), card_w, header_h,
                         boxstyle="round,pad=0.03,rounding_size=0.12",
                         facecolor=HEADER_BG, edgecolor=HEADER_BG, zorder=3)
    ax.add_patch(hdr)
    
    # Square bottom of header
    sq = patches.Rectangle((x, y + card_h - header_h), card_w, header_h / 2,
                           facecolor=HEADER_BG, edgecolor=HEADER_BG, zorder=3)
    ax.add_patch(sq)
    
    # Header text
    ax.text(x + card_w / 2.0, y + card_h - header_h / 2.0, s["title"],
            color=HEADER_TEXT, ha='center', va='center', zorder=4, **font_title)
    
    # Badge (Role/Category)
    bw, bh = 2.4, 0.32
    bx = x + (card_w - bw) / 2.0
    by = y + card_h - header_h - 0.42
    badge_patch = FancyBboxPatch((bx, by), bw, bh,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=s["badge_bg"], edgecolor='none', zorder=4)
    ax.add_patch(badge_patch)
    ax.text(bx + bw / 2.0, by + bh / 2.0, s["badge"],
            color=s["badge_text"], ha='center', va='center', zorder=5, **font_badge)
    
    # Step items
    line_y = by - 0.35
    for step in s["steps"]:
        # bullet dot
        ax.plot(x + 0.28, line_y, marker='o', markersize=3.8, color=ACCENT_BLUE, zorder=5)
        ax.text(x + 0.42, line_y, step, color=TEXT_MAIN, ha='left', va='center', zorder=5, **font_step)
        line_y -= 0.46

# Connecting Arrows
# Arrow 1 -> 2
a1 = FancyArrowPatch((0.45 + card_w, 4.9 + card_h / 2.0),
                     (5.27, 4.9 + card_h / 2.0),
                     arrowstyle='-|>', mutation_scale=16,
                     linewidth=2.0, color=LINE_COLOR, zorder=6)
ax.add_patch(a1)
ax.text((0.45 + card_w + 5.27) / 2.0, 4.9 + card_h / 2.0 + 0.2, "Khởi tạo\nhợp đồng",
        ha='center', va='bottom', color=ROYAL_BLUE, fontname='Segoe UI', fontsize=8.0, weight='bold')

# Arrow 2 -> 3
a2 = FancyArrowPatch((5.27 + card_w, 4.9 + card_h / 2.0),
                     (10.10, 4.9 + card_h / 2.0),
                     arrowstyle='-|>', mutation_scale=16,
                     linewidth=2.0, color=LINE_COLOR, zorder=6)
ax.add_patch(a2)
ax.text((5.27 + card_w + 10.10) / 2.0, 4.9 + card_h / 2.0 + 0.2, "Ký số &\ntải CCCD",
        ha='center', va='bottom', color=ROYAL_BLUE, fontname='Segoe UI', fontsize=8.0, weight='bold')

# Arrow 3 -> 4 (Down and Left to Stage 4)
# Route: from right bottom of Stage 3 down to Stage 4 top
a3 = FancyArrowPatch((10.10 + card_w / 2.0, 4.9),
                     (7.70 + card_w / 2.0 + 0.8, 0.4 + card_h),
                     connectionstyle="arc3,rad=0.25",
                     arrowstyle='-|>', mutation_scale=16,
                     linewidth=2.0, color=LINE_COLOR, zorder=6)
ax.add_patch(a3)
ax.text(10.7, 2.7, "Bàn giao máy &\nSinh lịch nợ",
        ha='left', va='center', color=ROYAL_BLUE, fontname='Segoe UI', fontsize=8.0, weight='bold')

# Arrow 4 -> 5 (Right to Left: Stage 4 to Stage 5)
a4 = FancyArrowPatch((7.70, 0.4 + card_h / 2.0),
                     (2.85 + card_w, 0.4 + card_h / 2.0),
                     arrowstyle='-|>', mutation_scale=16,
                     linewidth=2.0, color=LINE_COLOR, zorder=6)
ax.add_patch(a4)
ax.text((7.70 + 2.85 + card_w) / 2.0, 0.4 + card_h / 2.0 + 0.2, "Đối soát thanh toán\n& Vận hành thuê",
        ha='center', va='bottom', color=ROYAL_BLUE, fontname='Segoe UI', fontsize=8.0, weight='bold')

plt.tight_layout()
output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                           'figures', 'hinh_1_2_quy_trinh_tong_the_de_xuat.png')
plt.savefig(output_path, dpi=300, facecolor=BG_CANVAS, edgecolor='none')
plt.close()

print(f"Generated clean high-res diagram without title to: {output_path}")
