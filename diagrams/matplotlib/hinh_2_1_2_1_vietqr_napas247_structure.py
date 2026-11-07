"""
================================================================================
HÌNH 2.1.2. 1: CẤU TRÚC BẢN TIN VÀ GIẢI THUẬT SINH CHUỖI MÃ VIETQR ĐỘNG NAPAS 247
Dự án: RentalSystem - Khóa luận Tốt nghiệp HUIT 2025
Tiêu chuẩn: Academic Grayscale A4 Print-Ready (300 DPI, Segoe UI, Zero In-Image Noise)
Khắc phục khiếm khuyết: Triệt tiêu lỗi tràn chữ Tag 59, font >= 10pt, Dual Export (PNG & SVG)
================================================================================
"""

import os
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Academic Grayscale Palette
COLOR_CANVAS_BG     = '#ffffff'
COLOR_CARD_BG       = '#ffffff'
COLOR_ACCENT_BG     = '#f4f4f5'  # Zinc 100
COLOR_ACCENT_ALT    = '#e4e4e7'  # Zinc 200
COLOR_BORDER_SOLID  = '#000000'
COLOR_TEXT_MAIN     = '#000000'
COLOR_TEXT_MUTED    = '#3f3f46'  # Zinc 700
COLOR_HEADER_BG     = '#27272a'  # Zinc 800
COLOR_HEADER_TEXT   = '#ffffff'

FONT_FAMILY         = 'Segoe UI'

def draw_box(ax, x, y, w, h, text, bg=COLOR_CARD_BG, border=COLOR_BORDER_SOLID,
             text_color=COLOR_TEXT_MAIN, fontsize=10.0, bold=False, align='center', zorder=3):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.08",
                         facecolor=bg, edgecolor=border, linewidth=1.2, zorder=zorder)
    ax.add_patch(box)
    tx = x + w / 2.0 if align == 'center' else x + 0.15
    ty = y + h / 2.0
    ax.text(tx, ty, text, fontsize=fontsize, fontweight='bold' if bold else 'normal',
            color=text_color, fontfamily=FONT_FAMILY, ha=align, va='center', zorder=zorder+1)
    return box

def draw_arrow(ax, x1, y1, x2, y2, label="", color=COLOR_BORDER_SOLID, label_offset=(0, 0.14),
               fontsize=10.0, zorder=4):
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                            arrowstyle='-|>',
                            mutation_scale=12,
                            linewidth=1.4,
                            color=color,
                            zorder=zorder)
    ax.add_patch(arrow)
    if label:
        mx = (x1 + x2) / 2.0 + label_offset[0]
        my = (y1 + y2) / 2.0 + label_offset[1]
        ax.text(mx, my, label, fontsize=fontsize, color=COLOR_TEXT_MAIN,
                fontfamily=FONT_FAMILY, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.15', facecolor=COLOR_CARD_BG,
                          edgecolor=COLOR_BORDER_SOLID, linewidth=0.8),
                zorder=zorder+2)

def generate_diagram(output_dir=r'd:\DoAnCuNhan\figures'):
    os.makedirs(output_dir, exist_ok=True)
    
    # Kích thước canvas: rộng 15.5 cm (~6.1 in), cao 8.4 in
    fig, ax = plt.subplots(figsize=(15.5, 8.4), dpi=300)
    fig.patch.set_facecolor(COLOR_CANVAS_BG)
    ax.set_facecolor(COLOR_CANVAS_BG)
    ax.axis('off')
    ax.set_xlim(0, 15.5)
    ax.set_ylim(0, 8.4)
    
    # --------------------------------------------------------------------------
    # BẢNG PHÂN RÃ CẤU TRÚC TLV (TAG-LENGTH-VALUE) EMVCo CHUẨN NAPAS 247
    # --------------------------------------------------------------------------
    header_y = 7.8
    draw_box(ax, 0.4, header_y, 1.1, 0.46, "TAG (ID)", bg=COLOR_HEADER_BG, text_color=COLOR_HEADER_TEXT, fontsize=10.5, bold=True)
    draw_box(ax, 1.6, header_y, 0.7, 0.46, "LEN", bg=COLOR_HEADER_BG, text_color=COLOR_HEADER_TEXT, fontsize=10.5, bold=True)
    draw_box(ax, 2.4, header_y, 3.2, 0.46, "VALUE (NỘI DUNG EMVCo)", bg=COLOR_HEADER_BG, text_color=COLOR_HEADER_TEXT, fontsize=10.5, bold=True)
    draw_box(ax, 5.7, header_y, 3.2, 0.46, "Ý NGHĨA KỸ THUẬT / QUY CHUẨN", bg=COLOR_HEADER_BG, text_color=COLOR_HEADER_TEXT, fontsize=10.5, bold=True)
    
    # 10 Tags dữ liệu EMVCo chuẩn NAPAS 247 của RentalSystem
    # Đã mở rộng w_val = 3.2 để Tag 59 và Tag 38 hiển thị hoàn hảo không tràn viền
    tags_data = [
        ("Tag 00", "02", "01", "Payload Format Indicator (Phiên bản EMVCo)", 7.15),
        ("Tag 01", "02", "12", "Point of Initiation (12: Mã động Dynamic QR)", 6.55),
        ("Tag 38", "57", "0010A0000007270124...MBBank", "Merchant Account Info (Cổng NAPAS 247)", 5.95),
        ("Tag 53", "03", "704", "Transaction Currency (704: Việt Nam Đồng)", 5.35),
        ("Tag 54", "07", "2500000", "Transaction Amount (Số tiền cọc hoặc kỳ nợ)", 4.75),
        ("Tag 58", "02", "VN", "Country Code (Mã quốc gia Việt Nam)", 4.15),
        ("Tag 59", "23", "RENTALSYSTEM ENTERPRISE", "Merchant Name (Chủ tài khoản thụ hưởng)", 3.55),
        ("Tag 60", "15", "TP HO CHI MINH", "Merchant City (Thành phố mở tài khoản)", 2.95),
        ("Tag 62", "14", "0810HD105 KY2", "Additional Data (Cú pháp tự động đối soát)", 2.35),
        ("Tag 63", "04", "CRC16-CCITT", "Checksum bảo toàn chuỗi dữ liệu EMVCo", 1.75)
    ]
    
    for tag, length, val, desc, y in tags_data:
        # Cột Tag (Than chì đậm, chữ trắng)
        draw_box(ax, 0.4, y, 1.1, 0.48, tag, bg=COLOR_HEADER_BG, border='none', text_color=COLOR_HEADER_TEXT, fontsize=10.0, bold=True)
        # Cột Length (Nền xám nhạt Zinc 100)
        draw_box(ax, 1.6, y, 0.7, 0.48, length, bg=COLOR_ACCENT_BG, border=COLOR_BORDER_SOLID, fontsize=10.0)
        # Cột Value (Trắng, chữ đen đậm, rộng 3.2 - triệt tiêu 100% lỗi tràn chữ)
        draw_box(ax, 2.4, y, 3.2, 0.48, val, bg=COLOR_CARD_BG, border=COLOR_BORDER_SOLID, fontsize=9.8, bold=True)
        # Cột Ý nghĩa kỹ thuật
        draw_box(ax, 5.7, y, 3.2, 0.48, desc, bg=COLOR_CARD_BG, border=COLOR_BORDER_SOLID, fontsize=9.5, align='center')
    
    # --------------------------------------------------------------------------
    # KHỐI PHẢI TRÊN: GIẢI THUẬT KIỂM TOÀN VẸN CRC16-CCITT (TAG 63)
    # --------------------------------------------------------------------------
    draw_box(ax, 9.3, 7.8, 5.8, 0.55, "GIẢI THUẬT KIỂM TOÀN VẸN CRC16-CCITT (TAG 63)",
             bg=COLOR_HEADER_BG, text_color=COLOR_HEADER_TEXT, fontsize=10.5, bold=True)
    
    crc_info = (
        "• Đa thức sinh chuẩn EMVCo: G(x) = x^16 + x^12 + x^5 + 1\n"
        "  - Mã biểu diễn Hexadecimal: 0x1021\n"
        "  - Giá trị thanh ghi khởi tạo: 0xFFFF\n\n"
        "• Quy trình tính toán mã kiểm tra:\n"
        "  1. Ghép nối toàn bộ chuỗi ký tự từ Tag 00 đến '6304'.\n"
        "  2. Quét tuần tự từng byte, thực hiện phép dịch bit XOR.\n"
        "  3. Kết xuất giá trị 16-bit Hexadecimal (4 ký tự in hoa).\n"
        "  4. Nối kết quả vào cuối chuỗi (Ví dụ: '...6304F8D2').\n\n"
        "• Cơ chế chống gian lận: Mọi can thiệp sửa đổi số tiền (Tag 54)\n"
        "  hoặc số tài khoản (Tag 38) sẽ khiến mã CRC16 sai lệch,\n"
        "  ứng dụng ngân hàng sẽ lập tức từ chối giao dịch."
    )
    draw_box(ax, 9.3, 4.3, 5.8, 3.4, crc_info, bg=COLOR_CARD_BG, border=COLOR_BORDER_SOLID, fontsize=9.8, align='left')
    
    # --------------------------------------------------------------------------
    # KHỐI PHẢI DƯỚI: ĐƯỜNG ỐNG ĐỐI SOÁT TỰ ĐỘNG WEBHOOK 24/7 (WATERFALL)
    # --------------------------------------------------------------------------
    draw_box(ax, 9.3, 3.6, 5.8, 0.55, "ĐỐI SOÁT TỰ ĐỘNG OPEN BANKING WEBHOOK 24/7",
             bg=COLOR_HEADER_BG, text_color=COLOR_HEADER_TEXT, fontsize=10.5, bold=True)
    
    webhook_info = (
        "1. Khách hàng chuyển khoản qua ứng dụng Mobile Banking.\n"
        "2. Cổng NAPAS 247 phát Webhook POST /Payment/BankingWebhook.\n"
        "3. SemaphoreSlim PaymentLock tiếp nhận giao dịch đơn luồng.\n"
        "4. Regex Parser bóc tách số hợp đồng từ nội dung: HD{MaHopDong}.\n"
        "5. Idempotency Guard kiểm tra mã giao dịch ngân hàng chống trùng.\n"
        "6. Thuật toán thác nước: Gạch nợ kỳ hạn -> Xóa phạt -> Bồi thường.\n"
        "7. Khởi tạo PhieuThu với MaNhanVienThu = null (Tự động 100%).\n"
        "8. Hợp đồng chuyển sang Đã đặt cọc / Đang thuê trong 3 giây."
    )
    draw_box(ax, 9.3, 0.4, 5.8, 3.1, webhook_info, bg=COLOR_ACCENT_BG, border=COLOR_BORDER_SOLID, fontsize=9.6, align='left')
    
    # Mũi tên kết nối Tag 62 sang Webhook
    draw_arrow(ax, 8.9, 2.59, 9.3, 2.59, "Webhook Cú pháp", fontsize=9.5)
    # Mũi tên kết nối Tag 63 sang CRC16
    draw_arrow(ax, 8.9, 1.99, 9.3, 4.5, "Kiểm toàn vẹn", fontsize=9.5)
    
    # Ghi chú tiêu chuẩn đáy canvas
    ax.text(4.6, 0.8,
            "Chuẩn tương thích: EMVCo QR Code Specification for Payment Systems & Quyết định 2132/QĐ-NHNN",
            fontsize=9.5, fontstyle='italic', color=COLOR_TEXT_MUTED, fontfamily=FONT_FAMILY, ha='center')
    
    plt.tight_layout()
    
    png_path = os.path.join(output_dir, 'hinh_2_1_2_1_vietqr_napas247_structure.png')
    svg_path = os.path.join(output_dir, 'hinh_2_1_2_1_vietqr_napas247_structure.svg')
    
    plt.savefig(png_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.savefig(svg_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Đã tạo thành công STT 02: {png_path} và {svg_path}")

if __name__ == '__main__':
    generate_diagram()
