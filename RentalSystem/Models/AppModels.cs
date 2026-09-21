using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Microsoft.EntityFrameworkCore;

namespace RentalSystem.Models
{
    public class VaiTro {
        [Key] public int MaVaiTro { get; set; }
        [Required, MaxLength(50)] public string TenVaiTro { get; set; }
    }
    public class NguoiDung {
        [Key] public int MaNguoiDung { get; set; }
        [ForeignKey("VaiTro")] public int MaVaiTro { get; set; }
        public VaiTro VaiTro { get; set; }
        [Required, MaxLength(100)] public string HoTen { get; set; }
        [Required, MaxLength(20)] public string SoDienThoai { get; set; }
        public string Email { get; set; }
        public string MatKhau { get; set; }
        public string CCCD { get; set; }
        public string DiaChi { get; set; }
        public bool TrangThai { get; set; }
    }
    public class LoaiThietBi {
        [Key] public int MaLoai { get; set; }
        [Required, MaxLength(100)] public string TenLoai { get; set; }
    }
    public class SanPham {
        [Key] public int MaSanPham { get; set; }
        [ForeignKey("LoaiThietBi")] public int MaLoai { get; set; }
        public LoaiThietBi LoaiThietBi { get; set; }
        [Required, MaxLength(255)] public string TenSanPham { get; set; }
        public string CauHinh { get; set; }
        public string MoTa { get; set; }
        [Column(TypeName = "decimal(18,2)")] public decimal GiaThueNgay { get; set; }
        [Column(TypeName = "decimal(18,2)")] public decimal TienCoc { get; set; }
        public string HinhAnh { get; set; }
    }
    // Đại diện cho từng Máy vật lý cụ thể (phân biệt qua Số Serial).
    // Chu trình trạng thái (State machine): 
    // 0 (Sẵn sàng) -> 3 (Khóa giữ chỗ) -> 1 (Đang cho thuê) -> 0 (Thu hồi về kho)
    public class ThietBi {
        [Key] public int MaThietBi { get; set; }
        [ForeignKey("SanPham")] public int MaSanPham { get; set; }
        public SanPham SanPham { get; set; }
        [Required, MaxLength(50)] public string SoSerial { get; set; }
        public string TinhTrangMay { get; set; }
        public int TrangThai { get; set; } 
    }
    public class LichSuThietBi {
        [Key] public int MaLichSu { get; set; }
        [ForeignKey("ThietBi")] public int MaThietBi { get; set; }
        public ThietBi ThietBi { get; set; }
        public string HanhDong { get; set; }
        public DateTime ThoiGian { get; set; }
        [ForeignKey("NguoiDung")] public int MaNguoiThucHien { get; set; }
        public NguoiDung NguoiThucHien { get; set; }
    }
    public class KhuyenMai {
        [Key] public int MaKhuyenMai { get; set; }
        public string MaCode { get; set; }
        public int PhanTramGiam { get; set; }
        public bool KichHoat { get; set; }
    }
    // Thực thể nòng cốt lưu trữ Giao dịch thuê thiết bị.
    // Liên kết với Khách hàng, Nhân viên, Lịch trả góp và thông tin Chữ ký số Base64.
    public class HopDong {
        [Key] public int MaHopDong { get; set; }
        [ForeignKey("KhachHang")] public int MaKhachHang { get; set; }
        public NguoiDung KhachHang { get; set; }
        [ForeignKey("NhanVien")] public int MaNhanVien { get; set; }
        public NguoiDung NhanVien { get; set; }
        public int? MaKhuyenMai { get; set; } 
        public DateTime NgayBatDau { get; set; }
        public DateTime NgayKetThuc { get; set; }
        [Column(TypeName = "decimal(18,2)")] public decimal TienDaCoc { get; set; }
        [Column(TypeName = "decimal(18,2)")] public decimal TongTien { get; set; }
        public int TrangThai { get; set; } 

        // Các trường mới cho Ký HĐ & Thanh toán
        public string AnhCMND { get; set; }
        public string ChuKyKhachHang { get; set; }
        public string ChuKyNhanVien { get; set; }
        public DateTime? NgayKy { get; set; }
        public int TrangThaiThanhToan { get; set; } // 0: Chưa thanh toán, 1: Còn nợ, 2: Đã thanh toán đủ
        public string GhiChu { get; set; }
        public ICollection<KyHanThanhToan> KyHanThanhToans { get; set; }
    }

    // Lịch trình trả góp (hoặc thanh toán theo tháng) được sinh tự động khi duyệt đơn.
    public class KyHanThanhToan {
        [Key] public int MaKyHan { get; set; }
        [ForeignKey("HopDong")] public int MaHopDong { get; set; }
        public HopDong HopDong { get; set; }
        public int SoKyHan { get; set; }
        public DateTime NgayDenHan { get; set; }
        [Column(TypeName = "decimal(18,2)")] public decimal SoTienPhai { get; set; }
        [Column(TypeName = "decimal(18,2)")] public decimal SoTienDaTra { get; set; }
        public int TrangThai { get; set; } // 0: Chưa trả, 1: Đã trả, 2: Trễ hạn
        public DateTime? NgayThanhToan { get; set; }
        public string GhiChu { get; set; }
    }

    public class ChiTietHopDong {
        [Key, Column(Order = 0), ForeignKey("HopDong")] public int MaHopDong { get; set; }
        public HopDong HopDong { get; set; }
        [Key, Column(Order = 1), ForeignKey("ThietBi")] public int MaThietBi { get; set; }
        public ThietBi ThietBi { get; set; }
        [Column(TypeName = "decimal(18,2)")] public decimal GiaChotThu { get; set; }
    }
    public class PhieuThu {
        [Key] public int MaPhieuThu { get; set; }
        [ForeignKey("HopDong")] public int MaHopDong { get; set; }
        public HopDong HopDong { get; set; }
        public int LoaiPhieu { get; set; } // 0=Thu thuê, 1=Thu cọc, 2=Thu phí BT
        [Column(TypeName = "decimal(18,2)")] public decimal SoTien { get; set; }
        public DateTime NgayGiaoDich { get; set; }
        public int HinhThucThanhToan { get; set; } // 0=Tiền mặt, 1=Chuyển khoản, 2=Khác
        public string GhiChu { get; set; }
        public int? MaKyHan { get; set; }
    }
    public class PhieuBaoTri {
        [Key] public int MaPhieu { get; set; }
        [ForeignKey("HopDong")] public int MaHopDong { get; set; }
        public HopDong HopDong { get; set; }
        [ForeignKey("ThietBi")] public int MaThietBi { get; set; }
        public ThietBi ThietBi { get; set; }
        [ForeignKey("KyThuatVien")] public int? MaKyThuatVien { get; set; }
        public NguoiDung KyThuatVien { get; set; }
        public string MoTaLoi { get; set; }
        public DateTime NgayBaoLoi { get; set; }
        public string GhiChuSuaChua { get; set; }
        [Column(TypeName = "decimal(18,2)")] public decimal PhiDenBu { get; set; }
        public int? DanhGiaSao { get; set; }
        public int TrangThai { get; set; } 
    }

    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options) { }

        public DbSet<VaiTro> VaiTros { get; set; }
        public DbSet<NguoiDung> NguoiDungs { get; set; }
        public DbSet<LoaiThietBi> LoaiThietBis { get; set; }
        public DbSet<SanPham> SanPhams { get; set; }
        public DbSet<ThietBi> ThietBis { get; set; }
        public DbSet<LichSuThietBi> LichSuThietBis { get; set; }
        public DbSet<KhuyenMai> KhuyenMais { get; set; }
        public DbSet<HopDong> HopDongs { get; set; }
        public DbSet<KyHanThanhToan> KyHanThanhToans { get; set; }
        public DbSet<ChiTietHopDong> ChiTietHopDongs { get; set; }
        public DbSet<PhieuThu> PhieuThus { get; set; }
        public DbSet<PhieuBaoTri> PhieuBaoTris { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<ChiTietHopDong>().HasKey(c => new { c.MaHopDong, c.MaThietBi });
            modelBuilder.Entity<HopDong>().HasOne(h => h.KhachHang).WithMany().HasForeignKey(h => h.MaKhachHang).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<HopDong>().HasOne(h => h.NhanVien).WithMany().HasForeignKey(h => h.MaNhanVien).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<PhieuBaoTri>().HasOne(p => p.KyThuatVien).WithMany().HasForeignKey(p => p.MaKyThuatVien).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<LichSuThietBi>().HasOne(l => l.NguoiThucHien).WithMany().HasForeignKey(l => l.MaNguoiThucHien).OnDelete(DeleteBehavior.Restrict);
        }
    }
}
