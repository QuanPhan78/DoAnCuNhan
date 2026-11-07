"""
================================================================================
RENTALSYSTEM GRADUATION THESIS (HUIT STANDARD)
FIGURE 4.2.6: EF CORE MIGRATIONS TIMELINE DIAGRAM
Academic Grayscale | 300 DPI | Zero In-Image Noise
================================================================================
"""

import os
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

def generate_migration_timeline(output_dir=r"d:\DoAnCuNhan\figures"):
    os.makedirs(output_dir, exist_ok=True)
    out_png = os.path.join(output_dir, "hinh_4_4_migration_timeline.png")
    out_svg = os.path.join(output_dir, "hinh_4_4_migration_timeline.svg")

    # Kích thước chuẩn in ấn A4: 6.2 x 7.8 inches, 300 DPI
    fig, ax = plt.subplots(figsize=(6.2, 7.8), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    ax.axis('off')
    ax.set_xlim(0, 10.0)
    ax.set_ylim(0, 12.5)

    # 6 Mốc phát triển cơ sở dữ liệu Entity Framework Core (18 bảng chuẩn)
    milestones = [
        ("M1", "20250101_InitialCreate",
         "Khởi tạo nền tảng CSDL & 4 Role RBAC",
         "NguoiDungs, VaiTros, LoaiThietBis, SanPhams\nCấu trúc tài khoản & phân quyền Cookie Auth", 11.2),
        ("M2", "20250215_ContractAndSerial",
         "Phân hệ Hợp đồng & Quản lý Kho máy Serial",
         "HopDongs, ChiTietHopDongs, ThietBis, LichSuThietBis\nKiểm soát 5 trạng thái thiết bị & Giữ chỗ 24h", 9.4),
        ("M3", "20250410_OpenBankingWebhook",
         "Đường ống Tài chính & Tích hợp VietQR",
         "KyHanThanhToans, PhieuThus, PhieuChis\nGạch nợ thác nước 4 tầng, Idempotency Guard", 7.6),
        ("M4", "20250620_MaintenanceAndSLA",
         "Phân hệ Bảo trì & Điều phối Kỹ thuật hiện trường",
         "PhieuBaoTris, PhanCongCongViecs\nTheo dõi SLA đồng hồ đếm giờ & Nghiệm thu", 5.8),
        ("M5", "20250815_CanvasAndMagicBytes",
         "Hợp đồng điện tử & Xác thực ảnh nhị phân",
         "ChuKyKhachHang, ChuKyNhanVien, AnhCCCD_Truoc/Sau\nDeep Byte Inspection (PNG 89PNG, JPG, WEBP)", 4.0),
        ("M6", "20251030_Final18TablesPolish",
         "Hoàn thiện chuẩn mực 18 Bảng CSDL Cốt lõi",
         "ThongBaos, LichSuNhacNos, YeuCauGiaHans\n4 Nhóm tuổi nợ, Phạt trễ 0.1%/ngày, Khóa nợ xấu", 2.2)
    ]

    # Trục thời gian đứng (Timeline Spine)
    spine_x = 1.6
    ax.plot([spine_x, spine_x], [1.2, 11.8], color='#000000', linewidth=2.0, zorder=2)

    for code, migration_name, title, detail, y in milestones:
        # Nút mốc (Node Circle) trên trục
        node_circle = patches.Circle((spine_x, y), 0.35, facecolor='#27272a', edgecolor='#000000', linewidth=1.5, zorder=4)
        ax.add_patch(node_circle)
        ax.text(spine_x, y, code, fontsize=10.0, fontweight='bold', color='#ffffff',
                fontfamily='Segoe UI', ha='center', va='center', zorder=5)

        # Nhãn tên Migration (Bên trái trục)
        ax.text(spine_x - 0.55, y, migration_name[:16] + "\n" + migration_name[16:],
                fontsize=8.5, fontweight='bold', color='#3f3f46',
                fontfamily='Segoe UI', ha='right', va='center')

        # Thẻ nội dung (Content Card) bên phải trục
        card_w = 6.9
        card_h = 1.35
        card_box = patches.FancyBboxPatch((spine_x + 0.6, y - card_h / 2.0), card_w, card_h,
                                          boxstyle="round,pad=0.04,rounding_size=0.1",
                                          facecolor='#ffffff', edgecolor='#000000', linewidth=1.2, zorder=3)
        ax.add_patch(card_box)

        # Tiêu đề mốc
        ax.text(spine_x + 0.8, y + 0.35, title, fontsize=10.5, fontweight='bold',
                color='#000000', fontfamily='Segoe UI', va='center', zorder=4)

        # Chi tiết kỹ thuật & Bảng bổ sung
        ax.text(spine_x + 0.8, y - 0.2, detail, fontsize=9.2,
                color='#27272a', fontfamily='Segoe UI', va='center', zorder=4)

    # Khung tổng kết kiến trúc CSDL ở đáy canvas
    summary_box = patches.FancyBboxPatch((0.4, 0.3), 9.2, 0.75,
                                         boxstyle="round,pad=0.04,rounding_size=0.1",
                                         facecolor='#f4f4f5', edgecolor='#000000', linewidth=1.2, zorder=3)
    ax.add_patch(summary_box)
    ax.text(5.0, 0.78, "TỔNG KẾT: 18 BẢNG QUAN HỆ CHUẨN MỰC TRONG ENTITY FRAMEWORK CORE 9",
            fontsize=10.0, fontweight='bold', fontfamily='Segoe UI', ha='center', va='center')
    ax.text(5.0, 0.5, "Không sử dụng Identity mặc định | Tối ưu hóa chỉ mục Index & Khóa ngoại quan hệ 1-N",
            fontsize=9.0, color='#3f3f46', fontfamily='Segoe UI', ha='center', va='center')

    plt.tight_layout()
    plt.savefig(out_png, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.savefig(out_svg, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()

    # Chèn siêu dữ liệu DPI 300 bằng Pillow
    with Image.open(out_png) as img:
        img.save(out_png, dpi=(300, 300))

    print(f"[OK] Generated Migration Timeline -> {out_png}")
    print(f"[OK] Generated Migration Timeline Vector -> {out_svg}")

if __name__ == "__main__":
    generate_migration_timeline()
