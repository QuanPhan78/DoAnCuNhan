"""
================================================================================
HÌNH 2.1.1. 1: SƠ ĐỒ NGUYÊN LÝ KIỂM SOÁT TƯƠNG TRANH GIỮ CHỖ MÁY BẰNG SEMAPHORESLIM ĐA TẦNG
Dự án: RentalSystem - Khóa luận Tốt nghiệp HUIT 2025
Tiêu chuẩn: Academic Grayscale A4 Print-Ready (300 DPI, Segoe UI, Zero In-Image Noise)
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
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch

# Colors: Academic Grayscale Palette
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
             text_color=COLOR_TEXT_MAIN, fontsize=10.5, bold=False, align='center', zorder=3):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.08",
                         facecolor=bg, edgecolor=border, linewidth=1.3, zorder=zorder)
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
    
    # Canvas khổ A4 tỉ lệ chuẩn: W = 14.5 cm ~ 6.0 in, H = 8.5 in
    fig, ax = plt.subplots(figsize=(14.2, 8.6), dpi=300)
    fig.patch.set_facecolor(COLOR_CANVAS_BG)
    ax.set_facecolor(COLOR_CANVAS_BG)
    ax.axis('off')
    ax.set_xlim(0, 14.2)
    ax.set_ylim(0, 8.6)
    
    # --------------------------------------------------------------------------
    # CỘT 1: YÊU CẦU ĐỒNG THỜI (CONCURRENT CLIENT REQUESTS)
    # --------------------------------------------------------------------------
    draw_box(ax, 0.5, 7.8, 2.6, 0.55, "YÊU CẦU ĐỒNG THỜI", bg=COLOR_HEADER_BG,
             text_color=COLOR_HEADER_TEXT, fontsize=11.0, bold=True)
    
    draw_box(ax, 0.5, 6.2, 2.6, 1.1,
             "Khách hàng 1 (Web)\nCheckout Máy Gaming i7\n[Thời gian: T0]",
             bg=COLOR_CARD_BG, fontsize=10.0)
    
    draw_box(ax, 0.5, 4.7, 2.6, 1.1,
             "Khách hàng 2 (Mobile)\nCheckout Máy Gaming i7\n[Thời gian: T0 + 2ms]",
             bg=COLOR_CARD_BG, fontsize=10.0)
    
    draw_box(ax, 0.5, 3.2, 2.6, 1.1,
             "Kinh Doanh (Tại quầy)\nTạo đơn thuê trực tiếp\n[Thời gian: T0 + 5ms]",
             bg=COLOR_CARD_BG, fontsize=10.0)
    
    draw_box(ax, 0.5, 1.7, 2.6, 1.1,
             "Khách hàng N...\n(Đồng thời gửi HTTP POST)\n[Áp lực tải cao]",
             bg=COLOR_ACCENT_BG, fontsize=10.0)
    
    # --------------------------------------------------------------------------
    # CỘT 2: CỔNG KHÓA BẤT ĐỒNG BỘ SEMAPHORESLIM(1, 1)
    # --------------------------------------------------------------------------
    draw_box(ax, 3.8, 7.8, 2.8, 0.55, "CỔNG KHÓA ĐƠN TIẾN TRÌNH", bg=COLOR_HEADER_BG,
             text_color=COLOR_HEADER_TEXT, fontsize=11.0, bold=True)
    
    gate_text = (
        "CartController.InventoryLock\n"
        "= new SemaphoreSlim(1, 1)\n\n"
        "await InventoryLock.WaitAsync()\n\n"
        "[Hàng đợi ThreadPool]\n"
        "• Request 1: Cấp quyền (Count = 0)\n"
        "• Request 2..N: Đợi nhả luồng\n"
        "  (Không chiếm dụng chu kỳ CPU)\n"
        "• Bảo vệ toàn vẹn tuyệt đối"
    )
    draw_box(ax, 3.8, 2.2, 2.8, 5.1, gate_text, bg=COLOR_ACCENT_BG, fontsize=10.0, align='center')
    
    # Mũi tên từ Yêu cầu đồng thời sang Cổng khóa
    draw_arrow(ax, 3.1, 6.75, 3.8, 6.0, "Req 1", fontsize=9.5)
    draw_arrow(ax, 3.1, 5.25, 3.8, 5.2, "Req 2", fontsize=9.5)
    draw_arrow(ax, 3.1, 3.75, 3.8, 4.4, "Req 3", fontsize=9.5)
    draw_arrow(ax, 3.1, 2.25, 3.8, 3.6, "Req N", fontsize=9.5)
    
    # --------------------------------------------------------------------------
    # CỘT 3: VÙNG GĂNG CƠ SỞ DỮ LIỆU (CRITICAL SECTION)
    # --------------------------------------------------------------------------
    draw_box(ax, 7.2, 7.8, 3.8, 0.55, "VÙNG GĂNG CƠ SỞ DỮ LIỆU", bg=COLOR_HEADER_BG,
             text_color=COLOR_HEADER_TEXT, fontsize=11.0, bold=True)
    
    # Khung bao Critical Section
    cs_border = FancyBboxPatch((7.2, 1.2), 3.8, 6.2, boxstyle="round,pad=0.06,rounding_size=0.1",
                               facecolor=COLOR_CARD_BG, edgecolor=COLOR_BORDER_SOLID,
                               linewidth=1.4, linestyle='-', zorder=2)
    ax.add_patch(cs_border)
    
    draw_box(ax, 7.4, 6.1, 3.4, 1.0,
             "Kiểm tra tồn kho khả dụng:\n"
             "CountAsync(t => t.TrangThai != 2 &&\n"
             "!Overlaps(NgayBatDau, NgayKetThuc))",
             bg=COLOR_ACCENT_BG, fontsize=9.5)
    
    # Thoi quyết định (Diamond)
    dia = Polygon([[9.1, 5.6], [10.2, 4.9], [9.1, 4.2], [8.0, 4.9]],
                  facecolor=COLOR_ACCENT_ALT, edgecolor=COLOR_BORDER_SOLID, linewidth=1.3, zorder=3)
    ax.add_patch(dia)
    ax.text(9.1, 4.9, "Đủ số lượng\nkhả dụng?", fontsize=10.0, fontweight='bold',
            color=COLOR_TEXT_MAIN, fontfamily=FONT_FAMILY, ha='center', va='center', zorder=4)
    
    draw_arrow(ax, 9.1, 6.1, 9.1, 5.6)
    
    # Nhánh Đủ máy (Yes)
    draw_box(ax, 9.2, 1.6, 1.6, 2.0,
             "[Đủ máy]\n\n"
             "• Gán Serial máy\n"
             "• ThietBi: TrangThai=3\n"
             "  (Giữ chỗ 24h)\n"
             "• HanChotKy = Now+24h\n"
             "• Tạo HopDong\n"
             "• Xóa Session",
             bg=COLOR_CARD_BG, fontsize=9.0, align='center')
    
    # Nhánh Hết máy (No)
    draw_box(ax, 7.4, 1.6, 1.6, 2.0,
             "[Hết máy]\n\n"
             "• Xung đột tồn kho\n"
             "• Báo lỗi hết máy\n"
             "• Cập nhật giỏ hàng\n"
             "• Rollback giao dịch",
             bg=COLOR_ACCENT_BG, fontsize=9.0, align='center')
    
    draw_arrow(ax, 9.65, 4.3, 10.0, 3.6, "Có", fontsize=10.0)
    draw_arrow(ax, 8.55, 4.3, 8.2, 3.6, "Không", fontsize=10.0)
    draw_arrow(ax, 6.6, 4.75, 7.2, 4.75, "Trao quyền", fontsize=10.0)
    
    # --------------------------------------------------------------------------
    # CỘT 4: HOÀN TRẢ KHÓA & PHẢN HỒI CLIENT
    # --------------------------------------------------------------------------
    draw_box(ax, 11.5, 7.8, 2.3, 0.55, "GIẢI PHÓNG & KẾT QUẢ", bg=COLOR_HEADER_BG,
             text_color=COLOR_HEADER_TEXT, fontsize=11.0, bold=True)
    
    draw_box(ax, 11.5, 5.3, 2.3, 1.9,
             "finally {\n"
             "  InventoryLock.Release();\n"
             "}\n\n"
             "• Luôn hoàn trả khóa\n"
             "  dù xảy ra ngoại lệ\n"
             "• Count hồi phục = 1\n"
             "• Đánh thức luồng kế tiếp",
             bg=COLOR_ACCENT_BG, fontsize=9.5)
    
    draw_box(ax, 11.5, 3.4, 2.3, 1.4,
             "HTTP 200 OK\n\n"
             "Chuyển hướng đến trang\n"
             "ký hợp đồng điện tử\n"
             "& thanh toán VietQR",
             bg=COLOR_CARD_BG, fontsize=9.5)
    
    draw_box(ax, 11.5, 1.7, 2.3, 1.3,
             "HTTP Redirect\n\n"
             "Thông báo máy đã được\n"
             "đặt kín lịch trong\n"
             "khoảng thời gian chọn",
             bg=COLOR_ACCENT_BG, fontsize=9.5)
    
    draw_arrow(ax, 10.8, 5.5, 11.5, 6.0, "Hoàn tất", fontsize=9.5)
    draw_arrow(ax, 10.8, 2.6, 11.5, 3.9)
    draw_arrow(ax, 9.0, 1.6, 11.5, 2.2)
    
    plt.tight_layout()
    
    png_path = os.path.join(output_dir, 'hinh_2_1_1_1_semaphore_concurrency.png')
    svg_path = os.path.join(output_dir, 'hinh_2_1_1_1_semaphore_concurrency.svg')
    
    plt.savefig(png_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.savefig(svg_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Đã tạo thành công STT 01: {png_path} và {svg_path}")

if __name__ == '__main__':
    generate_diagram()
