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
    // Trạng thái: 0: Sẵn sàng, 1: Đang cho thuê, 2: Bảo trì/sửa chữa, 3: Giữ chỗ, 4: Hỏng/Thanh lý
    public class ThietBi {
        [Key] public int MaThietBi { get; set; }
        [ForeignKey("SanPham")] public int MaSanPham { get; set; }
        public SanPham SanPham { get; set; }
        [Required, MaxLength(50)] public string SoSerial { get; set; }
        public string TinhTrangMay { get; set; }
        public int TrangThai { get; set; } 

        public ICollection<LichSuThietBi>? LichSuThietBis { get; set; }
        public ICollection<PhieuBaoTri>? PhieuBaoTris { get; set; }
    }
    public class LichSuThietBi {
        [Key] public int MaLichSu { get; set; }
        [ForeignKey("ThietBi")] public int MaThietBi { get; set; }
        public ThietBi ThietBi { get; set; }
        public string HanhDong { get; set; }
        public DateTime ThoiGian { get; set; } = DateTime.Now;
        [ForeignKey("NguoiDung")] public int? MaNguoiThucHien { get; set; }
        public NguoiDung? NguoiThucHien { get; set; }
        public string? GhiChu { get; set; }
    }
    public class KhuyenMai {
        [Key]
        [Column("MaKhuyenMai")]
        public int MaKM { get; set; }

        [Required, MaxLength(50)]
        [Column("MaCode")]
        public string Code { get; set; } = string.Empty;

        [Range(1, 100)]
        public int PhanTramGiam { get; set; }

        public DateTime NgayBatDau { get; set; } = DateTime.Now;
        public DateTime NgayKetThuc { get; set; } = DateTime.Now.AddMonths(1);

        public int SoLuong { get; set; } = 100;
        public bool KichHoat { get; set; } = true;
        public string? MoTa { get; set; }

        // Thuộc tính phụ trợ tương thích
        [NotMapped]
        public int MaKhuyenMai { get => MaKM; set => MaKM = value; }
        [NotMapped]
        public string MaCode { get => Code; set => Code = value; }

        public ICollection<HopDong>? HopDongs { get; set; }
    }
    // Hợp đồng thuê thiết bị
    public class HopDong {
        [Key] public int MaHopDong { get; set; }
        [ForeignKey("KhachHang")] public int MaKhachHang { get; set; }
        public NguoiDung KhachHang { get; set; }
        [ForeignKey("NhanVien")] public int MaNhanVien { get; set; }
        public NguoiDung NhanVien { get; set; }
        [ForeignKey("KhuyenMai")] public int? MaKhuyenMai { get; set; }
        public KhuyenMai? KhuyenMai { get; set; }
        public DateTime NgayBatDau { get; set; }
        public DateTime NgayKetThuc { get; set; }
        [Column(TypeName = "decimal(18,2)")] public decimal TienDaCoc { get; set; }
        [Column(TypeName = "decimal(18,2)")] public decimal TongTien { get; set; }
        public int TrangThai { get; set; } // 0: Chờ duyệt, 1: Đang hiệu lực, 2: Hoàn tất, 3: Đã hủy, 4: Đã trả máy (Chờ quyết toán công nợ)
        public int SoKyHan { get; set; } = 1; 

        // Thông tin ký số và ảnh xác minh
        public string AnhCMND { get; set; }
        public string? AnhCCCD_Truoc { get; set; }
        public string? AnhCCCD_Sau { get; set; }
        public string ChuKyKhachHang { get; set; }
        public string ChuKyNhanVien { get; set; }
        public DateTime? NgayKy { get; set; }
        public int TrangThaiThanhToan { get; set; } // 0: Chưa thanh toán, 1: Còn nợ, 2: Đã thanh toán đủ
        public string GhiChu { get; set; }

        // Hoàn cọc và quyết toán
        public int TrangThaiHoanCoc { get; set; } = 0; // 0: Chưa hoàn cọc, 1: Đã hoàn cọc, 2: Không hoàn cọc/Tịch thu
        [Column(TypeName = "decimal(18,2)")] public decimal? TienCocThucHoan { get; set; }
        public DateTime? NgayHoanCoc { get; set; }
        public string? GhiChuHoanCoc { get; set; }

        // Yêu cầu gia hạn hợp đồng
        public bool YeuCauGiaHan { get; set; } = false;
        public int? SoNgayGiaHan { get; set; }
        public int? TrangThaiGiaHan { get; set; } // 0: Chờ duyệt, 1: Đã duyệt, 2: Từ chối
        public string? LyDoGiaHan { get; set; }

        // Yêu cầu hủy hợp đồng
        public bool YeuCauHuy { get; set; } = false;
        public string? LyDoHuy { get; set; }
        public DateTime? NgayYeuCauHuy { get; set; }

        // Thời hạn giữ chỗ đơn hàng
        public DateTime? HanChotKy { get; set; }

        [Column(TypeName = "decimal(18,2)")] public decimal TienTraThua { get; set; } = 0;
        [Column(TypeName = "decimal(18,2)")] public decimal TienGiamTruBaoTri { get; set; } = 0;
        [Column(TypeName = "decimal(18,2)")] public decimal TienCocBaoDamMay { get; set; } = 0;
        [Column(TypeName = "decimal(18,2)")] public decimal TienThueTraTruoc { get; set; } = 0;

        public ICollection<KyHanThanhToan> KyHanThanhToans { get; set; }
        public ICollection<BienBanBanGiao>? BienBanBanGiaos { get; set; }
        public ICollection<PhieuChi>? PhieuChis { get; set; }
        public ICollection<PhieuThu>? PhieuThus { get; set; }
        public ICollection<PhieuBaoTri>? PhieuBaoTris { get; set; }
        public virtual ICollection<LichSuNhacNo>? LichSuNhacNos { get; set; }
        public ICollection<RentalSystem.Models.YeuCauGiaHan>? DanhSachYeuCauGiaHan { get; set; }
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
        public int TrangThai { get; set; } // 0: Chưa trả, 1: Đã trả, 2: Trễ hạn, 3: Đã hủy
        public DateTime? NgayThanhToan { get; set; }
        public string GhiChu { get; set; }

        // Thông tin biên lai chuyển khoản ngân hàng
        public string? MaGiaoDichChuyenKhoan { get; set; }
        public string? HinhAnhBienLai { get; set; }
        public int TrangThaiXacNhan { get; set; } = 0; // 0: Chưa gửi, 1: Chờ duyệt đối soát, 2: Đã duyệt
        public DateTime? NgayGuiBienLai { get; set; }

        [Column(TypeName = "decimal(18,2)")] public decimal PhiPhatTreHan { get; set; } = 0;
        [Column(TypeName = "decimal(18,2)")] public decimal TienPhat { get; set; } = 0;
        public int SoNgayTreHan { get; set; } = 0;
        public int NhomTuoiNo { get; set; } = 0; // 0: Đúng hạn, 1: 1-30d, 2: 31-60d, 3: 61-90d, 4: >90d
        public DateTime? NgayHenTraTiepTheo { get; set; }
        public string? GhiChuTraThieu { get; set; }
        public virtual ICollection<LichSuNhacNo>? LichSuNhacNos { get; set; }
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
        public int HinhThucThanhToan { get; set; } // 0=Tiền mặt, 1=Chuyển khoản, 2=Online/VNPay, 3=Khác
        public string GhiChu { get; set; }
        [ForeignKey("KyHanThanhToan")] public int? MaKyHan { get; set; }
        public KyHanThanhToan? KyHanThanhToan { get; set; }

        [ForeignKey("NhanVienThu")] public int? MaNhanVienThu { get; set; }
        public NguoiDung? NhanVienThu { get; set; }

        public string? MaGiaoDichNganHang { get; set; }
        public string? NganHangNhan { get; set; }
        public bool DaHuy { get; set; } = false;
        public string? LyDoHuy { get; set; }
        public DateTime? NgayHuy { get; set; }
    }
    public class PhieuBaoTri {
        [Key] public int MaPhieu { get; set; }
        [ForeignKey("HopDong")] public int? MaHopDong { get; set; }
        public HopDong? HopDong { get; set; }
        [ForeignKey("ThietBi")] public int MaThietBi { get; set; }
        public ThietBi ThietBi { get; set; }
        [ForeignKey("KyThuatVien")] public int? MaKyThuatVien { get; set; }
        public NguoiDung? KyThuatVien { get; set; }
        public string MoTaLoi { get; set; }
        public DateTime NgayBaoLoi { get; set; }
        public string GhiChuSuaChua { get; set; } = "";
        [Column(TypeName = "decimal(18,2)")] public decimal PhiDenBu { get; set; } = 0;
        public int? DanhGiaSao { get; set; }
        public int TrangThai { get; set; } 

        // Chi phí sửa chữa thực tế của đơn vị kỹ thuật
        [Column(TypeName = "decimal(18,2)")] public decimal? ChiPhiSuaChua { get; set; } = 0;

        // Hình ảnh / video minh chứng sự cố
        public string? HinhAnhLoi { get; set; }
        public string? VideoLoi { get; set; }

        // Phân định trách nhiệm và nguyên nhân sự cố
        public int? LoaiTrachNhiem { get; set; } // 1: Khách hàng, 2: Cửa hàng/Bảo hành
        public string? NguyenNhan { get; set; }
        public string? LinhKienThayThe { get; set; }
        public bool DaGhiNhanCongNo { get; set; } = false;

        // Mức độ ưu tiên và hạn xử lý
        public int? MucDoKhanCap { get; set; } = 1; // 1: Tiêu chuẩn (48h), 2: Khẩn cấp (12h), 3: Cao (24h)
        public DateTime? HanHoanThanh { get; set; }
        public DateTime? NgayHoanThanh { get; set; }

        // Nghiệm thu và phản hồi từ khách hàng
        public string? YKienPhanHoi { get; set; }
        public bool DaNghiemThu { get; set; } = false;
        public DateTime? NgayNghiemThu { get; set; }

        // Miễn giảm tiền thuê trong thời gian máy bảo trì
        public bool TamDungTinhTien { get; set; } = false;
        public DateTime? NgayBatDauBaoTri { get; set; }
        public DateTime? NgayKetThucBaoTri { get; set; }
        public int? SoNgayTamDung { get; set; } = 0;
        [Column(TypeName = "decimal(18,2)")] public decimal? TienGiamTru { get; set; } = 0;
        public bool DaTruTien { get; set; } = false;

        // Thuộc tính phụ trợ tương thích
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        public DateTime? NgayHenTraMay { get => HanHoanThanh; set => HanHoanThanh = value; }
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        public DateTime? HanXuLy { get => HanHoanThanh; set => HanHoanThanh = value; }
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        public decimal? TienMienGiamTamDung { get => TienGiamTru; set => TienGiamTru = value; }
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        public bool DaMienGiam { get => DaTruTien; set => DaTruTien = value; }
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        public string? PhanHoiKhachHang { get => YKienPhanHoi; set => YKienPhanHoi = value; }
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        public bool DaThuPhi { get => DaGhiNhanCongNo; set => DaGhiNhanCongNo = value; }
    }

    // Thông báo gửi người dùng
    public class ThongBao {
        [Key] public int MaThongBao { get; set; }
        [ForeignKey("NguoiDung")] public int MaNguoiDung { get; set; }
        public NguoiDung NguoiDung { get; set; }
        [Required, MaxLength(255)] public string TieuDe { get; set; }
        [Required] public string NoiDung { get; set; }
        public DateTime NgayTao { get; set; } = DateTime.Now;
        public bool DaDoc { get; set; } = false;
        public string? LoaiThongBao { get; set; }
        public string? LienKet { get; set; }
    }

    // Biên bản bàn giao và kiểm tra thiết bị khi xuất / nhập kho
    public class BienBanBanGiao {
        [Key] public int MaBienBan { get; set; }
        [ForeignKey("HopDong")] public int MaHopDong { get; set; }
        public HopDong HopDong { get; set; }
        public int LoaiBienBan { get; set; } // 0: Bàn giao xuất kho, 1: Thu hồi nhập kho
        public DateTime NgayLap { get; set; } = DateTime.Now;
        [ForeignKey("NhanVienLap")] public int MaNhanVienLap { get; set; }
        public NguoiDung NhanVienLap { get; set; }
        public string? PhuKienKemTheo { get; set; }
        public string? TinhTrangNgoaiQuan { get; set; }
        public string? HinhAnh1 { get; set; }
        public string? HinhAnh2 { get; set; }
        public string? HinhAnh3 { get; set; }
        public string? HinhAnh4 { get; set; }
        public string? ChuKyXacNhan { get; set; }
        public string? GhiChu { get; set; }
    }

    // Phiếu chi tiền (hoàn cọc hoặc chi trả khác)
    public class PhieuChi {
        [Key] public int MaPhieuChi { get; set; }
        [ForeignKey("HopDong")] public int MaHopDong { get; set; }
        public HopDong HopDong { get; set; }
        public int LoaiChi { get; set; } // 0: Hoàn tiền cọc, 1: Chi hoàn tiền thừa, 2: Chi khác
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        public int LoaiPhieu { get => LoaiChi; set => LoaiChi = value; }
        [Column(TypeName = "decimal(18,2)")] public decimal SoTien { get; set; }
        public DateTime NgayChi { get; set; } = DateTime.Now;
        public int HinhThucChi { get; set; } // 0: Tiền mặt, 1: Chuyển khoản, 2: Khác
        [ForeignKey("NhanVienChi")] public int MaNhanVienChi { get; set; }
        public NguoiDung NhanVienChi { get; set; }
        public string? MaGiaoDichNganHang { get; set; }
        public string? GhiChu { get; set; }
    }

    // Lịch sử gửi thông báo nhắc nợ kỳ hạn
    public class LichSuNhacNo
    {
        [Key]
        public int MaLichSuNhacNo { get; set; }
        public int MaHopDong { get; set; }
        [ForeignKey("MaHopDong")]
        public virtual HopDong? HopDong { get; set; }
        public int? MaKyHan { get; set; }
        [ForeignKey("MaKyHan")]
        public virtual KyHanThanhToan? KyHanThanhToan { get; set; }
        public DateTime NgayNhac { get; set; } = DateTime.Now;
        public string HinhThucNhac { get; set; } = "Thông báo hệ thống"; // "Thông báo hệ thống", "Email", "SMS"
        public string? NoiDung { get; set; }
        public int? NguoiGuiId { get; set; }
        [ForeignKey("NguoiGuiId")]
        public virtual NguoiDung? NguoiGui { get; set; }
        [Column(TypeName = "decimal(18,2)")]
        public decimal SoTienNhac { get; set; }
        public int LanNhacThu { get; set; } = 1;
    }

    // Quản lý yêu cầu gia hạn hợp đồng
    public class YeuCauGiaHan {
        [Key]
        public int MaYeuCau { get; set; }

        [ForeignKey("HopDong")]
        public int MaHopDong { get; set; }
        public HopDong? HopDong { get; set; }

        public int SoNgayGiaHan { get; set; }
        public string? LyDo { get; set; }
        public DateTime NgayYeuCau { get; set; } = DateTime.Now;

        // 0: Chờ duyệt, 1: Đã duyệt, 2: Từ chối
        public int TrangThai { get; set; } = 0;
        public DateTime? NgayDuyet { get; set; }

        [ForeignKey("NguoiDuyet")]
        public int? MaNguoiDuyet { get; set; }
        public NguoiDung? NguoiDuyet { get; set; }

        [Column(TypeName = "decimal(18,2)")]
        public decimal ChiPhiPhatSinh { get; set; } = 0;

        public string? GhiChuAdmin { get; set; }

        // Thuộc tính phụ trợ tương thích
        [NotMapped]
        public string? GhiChu { get => GhiChuAdmin; set => GhiChuAdmin = value; }
    }

    // Phân công và quản lý công việc nhân viên
    public class PhanCongCongViec {
        [Key]
        public int MaPhanCong { get; set; }

        [ForeignKey("NhanVien")]
        public int MaNhanVien { get; set; }
        public NguoiDung NhanVien { get; set; } = null!;

        [Required, MaxLength(255)]
        public string TieuDe { get; set; } = string.Empty;

        [Required]
        public string NoiDung { get; set; } = string.Empty;

        [ForeignKey("HopDong")]
        public int? MaHopDong { get; set; }
        public HopDong? HopDong { get; set; }

        [ForeignKey("PhieuBaoTri")]
        public int? MaPhieuBaoTri { get; set; }
        public PhieuBaoTri? PhieuBaoTri { get; set; }

        // 0: Mới, 1: Đang thực hiện, 2: Hoàn thành, 3: Đã hủy
        public int TrangThai { get; set; } = 0;

        public DateTime NgayGiao { get; set; } = DateTime.Now;
        public DateTime? HanHoanThanh { get; set; }
        public DateTime? NgayHoanThanh { get; set; }

        [ForeignKey("NguoiGiao")]
        public int? MaNguoiGiao { get; set; }
        public NguoiDung? NguoiGiao { get; set; }

        public string? GhiChuTienDo { get; set; }

        // Thuộc tính phụ trợ tương thích
        [NotMapped]
        public DateTime NgayTao { get => NgayGiao; set => NgayGiao = value; }
        [NotMapped]
        public string? GhiChu { get => GhiChuTienDo; set => GhiChuTienDo = value; }
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
        public DbSet<BienBanBanGiao> BienBanBanGiaos { get; set; }
        public DbSet<PhieuChi> PhieuChis { get; set; }
        public DbSet<ThongBao> ThongBaos { get; set; }
        public DbSet<LichSuNhacNo> LichSuNhacNos { get; set; }
        public DbSet<YeuCauGiaHan> YeuCauGiaHans { get; set; }
        public DbSet<PhanCongCongViec> PhanCongCongViecs { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<ChiTietHopDong>().HasKey(c => new { c.MaHopDong, c.MaThietBi });
            modelBuilder.Entity<HopDong>().HasOne(h => h.KhachHang).WithMany().HasForeignKey(h => h.MaKhachHang).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<HopDong>().HasOne(h => h.NhanVien).WithMany().HasForeignKey(h => h.MaNhanVien).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<PhieuBaoTri>().HasOne(p => p.HopDong).WithMany(h => h.PhieuBaoTris).HasForeignKey(p => p.MaHopDong).IsRequired(false).OnDelete(DeleteBehavior.SetNull);
            modelBuilder.Entity<PhieuBaoTri>().HasOne(p => p.KyThuatVien).WithMany().HasForeignKey(p => p.MaKyThuatVien).IsRequired(false).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<LichSuThietBi>().HasOne(l => l.NguoiThucHien).WithMany().HasForeignKey(l => l.MaNguoiThucHien).IsRequired(false).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<ThongBao>().HasOne(t => t.NguoiDung).WithMany().HasForeignKey(t => t.MaNguoiDung).OnDelete(DeleteBehavior.Cascade);
            modelBuilder.Entity<BienBanBanGiao>().HasOne(b => b.HopDong).WithMany(h => h.BienBanBanGiaos).HasForeignKey(b => b.MaHopDong).OnDelete(DeleteBehavior.Cascade);
            modelBuilder.Entity<BienBanBanGiao>().HasOne(b => b.NhanVienLap).WithMany().HasForeignKey(b => b.MaNhanVienLap).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<PhieuChi>().HasOne(p => p.HopDong).WithMany(h => h.PhieuChis).HasForeignKey(p => p.MaHopDong).OnDelete(DeleteBehavior.Cascade);
            modelBuilder.Entity<PhieuChi>().HasOne(p => p.NhanVienChi).WithMany().HasForeignKey(p => p.MaNhanVienChi).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<PhieuThu>().HasOne(p => p.NhanVienThu).WithMany().HasForeignKey(p => p.MaNhanVienThu).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<PhieuThu>().HasOne(p => p.KyHanThanhToan).WithMany().HasForeignKey(p => p.MaKyHan).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<LichSuNhacNo>().HasOne(l => l.HopDong).WithMany(h => h.LichSuNhacNos).HasForeignKey(l => l.MaHopDong).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<LichSuNhacNo>().HasOne(l => l.KyHanThanhToan).WithMany(k => k.LichSuNhacNos).HasForeignKey(l => l.MaKyHan).IsRequired(false).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<LichSuNhacNo>().HasOne(l => l.NguoiGui).WithMany().HasForeignKey(l => l.NguoiGuiId).IsRequired(false).OnDelete(DeleteBehavior.Restrict);

            modelBuilder.Entity<HopDong>()
                .HasOne(h => h.KhuyenMai)
                .WithMany(k => k.HopDongs)
                .HasForeignKey(h => h.MaKhuyenMai)
                .IsRequired(false)
                .OnDelete(DeleteBehavior.SetNull);

            modelBuilder.Entity<YeuCauGiaHan>()
                .HasOne(y => y.HopDong)
                .WithMany(h => h.DanhSachYeuCauGiaHan)
                .HasForeignKey(y => y.MaHopDong)
                .OnDelete(DeleteBehavior.Cascade);

            modelBuilder.Entity<YeuCauGiaHan>()
                .HasOne(y => y.NguoiDuyet)
                .WithMany()
                .HasForeignKey(y => y.MaNguoiDuyet)
                .IsRequired(false)
                .OnDelete(DeleteBehavior.Restrict);

            modelBuilder.Entity<PhanCongCongViec>()
                .HasOne(p => p.NhanVien)
                .WithMany()
                .HasForeignKey(p => p.MaNhanVien)
                .OnDelete(DeleteBehavior.Restrict);

            modelBuilder.Entity<PhanCongCongViec>()
                .HasOne(p => p.NguoiGiao)
                .WithMany()
                .HasForeignKey(p => p.MaNguoiGiao)
                .IsRequired(false)
                .OnDelete(DeleteBehavior.Restrict);

            modelBuilder.Entity<PhanCongCongViec>()
                .HasOne(p => p.HopDong)
                .WithMany()
                .HasForeignKey(p => p.MaHopDong)
                .IsRequired(false)
                .OnDelete(DeleteBehavior.SetNull);

            modelBuilder.Entity<PhanCongCongViec>()
                .HasOne(p => p.PhieuBaoTri)
                .WithMany()
                .HasForeignKey(p => p.MaPhieuBaoTri)
                .IsRequired(false)
                .OnDelete(DeleteBehavior.SetNull);
        }
    }
}
