"""
================================================================================
HÌNH 2.1.3. 1: SƠ ĐỒ THUẬT TOÁN PHÂN KỲ TRẢ GÓP VÀ CHUYỂN TRẠNG THÁI 4 CẤP ĐỘ TUỔI NỢ
Dự án: RentalSystem - Khóa luận Tốt nghiệp HUIT 2025
Tiêu chuẩn: Academic Grayscale A4 Print-Ready (300 DPI, Segoe UI, Zero In-Image Noise)
Ground-Truth: DebtCalculationHelper.cs, 4 cấp tuổi nợ + Cấp 0, Ân hạn 3 ngày, Phạt 0.1%/ngày
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
    
    # Canvas chuẩn khổ in Word A4: rộng 14.2 cm (~5.6 in), cao 8.8 in
    fig, ax = setup_canvas(14.2, 8.8)
    
    # --------------------------------------------------------------------------
    # PHẦN 1: THUẬT TOÁN PHÂN KỲ THANH TOÁN TRẢ GÓP (AMORTIZATION SCHEDULE)
    # --------------------------------------------------------------------------
    draw_box(ax, 0.6, 8.0, 13.0, 0.52, "THUẬT TOÁN PHÂN KỲ THANH TOÁN (AMORTIZATION SCHEDULE)",
             bg=COLOR_HEADER_BG, text_color=COLOR_HEADER_TEXT, fontsize=11.0, bold=True)
    
    # Khối 1: Đầu vào hợp đồng
    draw_box(ax, 0.6, 5.8, 3.8, 2.0,
             "THÔNG SỐ HỢP ĐỒNG ĐẦU VÀO:\n\n"
             "• Tổng tiền thuê thiết bị (T)\n"
             "• Tiền đặt cọc máy (Bảo toàn)\n"
             "• Tiền trả trước đợt 1 (T_pre)\n"
             "• Số kỳ hạn phân chia (N)\n"
             "• Khoảng thời gian: [Start, End]",
             bg=COLOR_CARD_BG, border=COLOR_BORDER_SOLID, fontsize=9.8, align='left')
    
    # Khối 2: Công thức chia đều & Làm tròn
    draw_box(ax, 5.0, 5.8, 4.4, 2.0,
             "CÔNG THỨC CHIA ĐỀU & LÀM TRÒN:\n\n"
             "• Tiền còn lại: T_rem = T - T_pre\n"
             "• Tiền mỗi kỳ: P_base =\n"
             "  round(T_rem / (N * 1000)) * 1000\n"
             "• Cân đối kỳ cuối (chống lệch số lẻ):\n"
             "  P_N = T_rem - Sum(P_1 .. P_N-1)",
             bg=COLOR_ACCENT_BG, border=COLOR_BORDER_SOLID, fontsize=9.8, align='left')
    
    # Khối 3: Sinh lịch hạn kỳ
    draw_box(ax, 10.0, 5.8, 3.6, 2.0,
             "LỊCH ĐẾN HẠN PHÂN KỲ (D_i):\n\n"
             "• Kỳ 1: D_1 = NgayBatDau\n"
             "• Kỳ i: D_i = D_1 +\n"
             "  round((i-1)/(N-1) * Tổng ngày)\n"
             "• Tự động khởi tạo N bản ghi\n"
             "  trong bảng KyHanThanhToan",
             bg=COLOR_CARD_BG, border=COLOR_BORDER_SOLID, fontsize=9.8, align='left')
    
    draw_arrow(ax, 4.4, 6.8, 5.0, 6.8)
    draw_arrow(ax, 9.4, 6.8, 10.0, 6.8)
    
    # --------------------------------------------------------------------------
    # PHẦN 2: CHUYỂN TRẠNG THÁI 4 CẤP ĐỘ TUỔI NỢ & CHÍNH SÁCH KIỂM SOÁT
    # --------------------------------------------------------------------------
    draw_box(ax, 0.6, 4.9, 13.0, 0.52, "CHUYỂN TRẠNG THÁI 4 CẤP ĐỘ TUỔI NỢ (AGING BUCKETS & POLICY)",
             bg=COLOR_HEADER_BG, text_color=COLOR_HEADER_TEXT, fontsize=11.0, bold=True)
    
    # 5 Nhóm tuổi nợ theo DebtCalculationHelper.CalculateAgingTier
    buckets = [
        ("CẤP 0: ĐÚNG HẠN\n(Current)",
         "Quá hạn <= 0 ngày",
         "• Trạng thái bình thường\n• Cho phép tạo hợp đồng mới\n• Nhắc lịch hẹn tự động\n• Chưa áp dụng lãi phạt",
         COLOR_CARD_BG),
        ("CẤP 1: CẦN CHÚ Ý\n(Special Mention)",
         "Quá hạn 1 - 30 ngày",
         "• Ân hạn phạt 3 ngày đầu\n• Gửi email & SMS nhắc nợ\n• Đính kèm mã VietQR nhanh\n• Phạt 0.1%/ngày từ ngày 4",
         COLOR_ACCENT_BG),
        ("CẤP 2: DƯỚI TIÊU CHUẨN\n(Substandard)",
         "Quá hạn 31 - 60 ngày",
         "• Lãi phạt: 0.1%/ngày nợ\n• Kinh doanh gọi điện trực tiếp\n• Cảnh báo tạm dừng hợp đồng\n• Giới hạn chức năng thuê",
         COLOR_ACCENT_ALT),
        ("CẤP 3: NỢ NGHI NGỜ\n(Doubtful)",
         "Quá hạn 61 - 90 ngày",
         "• Tạm dừng bảo trì SLA tại chỗ\n• Cảnh báo thu hồi thiết bị\n• Không cho phép gia hạn thuê\n• Chuyển tổ đôn đốc công nợ",
         '#d4d4d8'),
        ("CẤP 4: NỢ XẤU\n(Bad Debt / Blacklist)",
         "Quá hạn > 90 ngày\nhoặc Nợ > 3.000.000đ",
         "• KHÓA TÀI KHOẢN TOÀN HỆ THỐNG\n• Đưa vào danh sách Blacklist\n• Niêm phong thiết bị từ xa\n• Chuyển hồ sơ xử lý pháp lý",
         '#a1a1aa')
    ]
    
    x = 0.6
    w = 2.45
    for title, condition, policy, bg in buckets:
        draw_box(ax, x, 1.4, w, 3.2,
                 f"{title}\n\n[{condition}]\n\n{policy}",
                 bg=bg, border=COLOR_BORDER_SOLID, fontsize=9.2, align='center')
        if x > 0.6:
            draw_arrow(ax, x - 0.18, 3.0, x, 3.0, color=COLOR_BORDER_SOLID)
        x += 2.64
    
    # --------------------------------------------------------------------------
    # CÔNG THỨC TÍNH PHẠT VÀ GHI CHÚ PHÁP LÝ Ở ĐÁY CANVAS
    # --------------------------------------------------------------------------
    formula_text = (
        "Công thức tính phí phạt chậm trả (áp dụng từ ngày thứ 4 quá hạn):\n"
        "LateFee = round((SoTienPhai - SoTienDaTra) * 0.001 * daysPastDue) | "
        "Ân hạn: GracePeriodDays = 3 ngày | Lãi phạt: DailyLateFeeRate = 0.1%/ngày"
    )
    draw_box(ax, 0.6, 0.4, 13.0, 0.75, formula_text,
             bg=COLOR_CARD_BG, border=COLOR_BORDER_SOLID, fontsize=9.5, align='center')
    
    plt.tight_layout()
    
    png_path = os.path.join(output_dir, 'hinh_2_1_3_1_debt_aging_algorithm.png')
    svg_path = os.path.join(output_dir, 'hinh_2_1_3_1_debt_aging_algorithm.svg')
    
    plt.savefig(png_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.savefig(svg_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Đã tạo thành công STT 03: {png_path} và {svg_path}")

def setup_canvas(width=14.2, height=8.8):
    fig, ax = plt.subplots(figsize=(width, height), dpi=300)
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis('off')
    fig.patch.set_facecolor(COLOR_CANVAS_BG)
    ax.set_facecolor(COLOR_CANVAS_BG)
    return fig, ax

if __name__ == '__main__':
    generate_diagram()
