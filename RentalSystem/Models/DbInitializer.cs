using System;
using System.Linq;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using Microsoft.Extensions.DependencyInjection;

namespace RentalSystem.Models
{
    public static class DbInitializer
    {
        public static void Initialize(ApplicationDbContext context)
        {
            if (context.VaiTros.Any())
            {
                return;   
            }

            // 1. Tạo 4 Vai Trò
            var vaiTros = new VaiTro[]
            {
                new VaiTro{TenVaiTro="Admin"},
                new VaiTro{TenVaiTro="KinhDoanh"},
                new VaiTro{TenVaiTro="KyThuat"},
                new VaiTro{TenVaiTro="KhachHang"}
            };
            context.VaiTros.AddRange(vaiTros);
            context.SaveChanges();

            // 2. Tạo tài khoản Admin + 1 Khách hàng mẫu
            var admin = new NguoiDung
            {
                MaVaiTro = context.VaiTros.Single(v => v.TenVaiTro == "Admin").MaVaiTro,
                HoTen = "Quản Trị Viên",
                SoDienThoai = "0123456789",
                Email = "admin@rentalsystem.com",
                MatKhau = "Admin@123", 
                CCCD = "000000000000",
                DiaChi = "Trung tâm Hệ thống",
                TrangThai = true
            };
            context.NguoiDungs.Add(admin);

            var khachHang = new NguoiDung
            {
                MaVaiTro = context.VaiTros.Single(v => v.TenVaiTro == "KhachHang").MaVaiTro,
                HoTen = "Nguyễn Văn An",
                SoDienThoai = "0987654321",
                Email = "khach@gmail.com",
                MatKhau = "123456",
                CCCD = "079200001234",
                DiaChi = "123 Nguyễn Trãi, Q.1, TP.HCM",
                TrangThai = true
            };
            context.NguoiDungs.Add(khachHang);
            context.SaveChanges();

            // 3. Tạo 3 Danh mục thiết bị: Máy tính bàn, Máy lạnh, Máy in
            var loaiThietBis = new LoaiThietBi[]
            {
                new LoaiThietBi{TenLoai="Máy tính bàn"},
                new LoaiThietBi{TenLoai="Máy lạnh"},
                new LoaiThietBi{TenLoai="Máy in"}
            };
            context.LoaiThietBis.AddRange(loaiThietBis);
            context.SaveChanges();

            // 4. Tạo 6 Sản phẩm mẫu
            var sanPhams = new SanPham[]
            {
                // -- Máy tính bàn --
                new SanPham{
                    MaLoai = context.LoaiThietBis.Single(l => l.TenLoai == "Máy tính bàn").MaLoai,
                    TenSanPham = "Bộ PC Dell OptiPlex 7010",
                    CauHinh = "Intel Core i5-13500, 16GB RAM DDR5, SSD 512GB, Màn hình 24 inch FHD",
                    MoTa = "Máy tính bàn Dell OptiPlex 7010 dòng doanh nghiệp, thiết kế nhỏ gọn, bền bỉ, phù hợp cho văn phòng, phòng học, sự kiện hội nghị.",
                    GiaThueNgay = 150000,
                    TienCoc = 8000000,
                    HinhAnh = "/images/sanpham/may-tinh.png"
                },
                new SanPham{
                    MaLoai = context.LoaiThietBis.Single(l => l.TenLoai == "Máy tính bàn").MaLoai,
                    TenSanPham = "Bộ PC HP ProDesk 400 G9",
                    CauHinh = "Intel Core i7-12700, 16GB RAM, SSD 256GB, Màn hình 22 inch",
                    MoTa = "PC HP ProDesk hiệu năng cao, dáng đứng tiết kiệm diện tích, lý tưởng cho thuê theo tháng cho doanh nghiệp vừa và nhỏ.",
                    GiaThueNgay = 180000,
                    TienCoc = 10000000,
                    HinhAnh = "/images/sanpham/may-tinh.png"
                },
                // -- Máy lạnh --
                new SanPham{
                    MaLoai = context.LoaiThietBis.Single(l => l.TenLoai == "Máy lạnh").MaLoai,
                    TenSanPham = "Máy lạnh Daikin FTKZ35VVMV (1.5HP)",
                    CauHinh = "Inverter, 1.5 HP, Gas R-32, Làm lạnh nhanh, Chế độ Eco tiết kiệm điện",
                    MoTa = "Máy lạnh Daikin Inverter cao cấp, vận hành êm ái, phù hợp cho thuê phòng họp, văn phòng tạm, sự kiện ngoài trời có mái che.",
                    GiaThueNgay = 200000,
                    TienCoc = 5000000,
                    HinhAnh = "/images/sanpham/may-lanh.png"
                },
                new SanPham{
                    MaLoai = context.LoaiThietBis.Single(l => l.TenLoai == "Máy lạnh").MaLoai,
                    TenSanPham = "Máy lạnh tủ đứng LG APNQ48GT3E4 (5HP)",
                    CauHinh = "Inverter, 5 HP, 48.000 BTU, Làm lạnh diện tích lớn 60-80m²",
                    MoTa = "Máy lạnh tủ đứng công suất lớn LG, chuyên dùng cho thuê sự kiện, hội trường, showroom, nhà xưởng. Lắp đặt nhanh trong 30 phút.",
                    GiaThueNgay = 500000,
                    TienCoc = 15000000,
                    HinhAnh = "/images/sanpham/may-lanh.png"
                },
                // -- Máy in --
                new SanPham{
                    MaLoai = context.LoaiThietBis.Single(l => l.TenLoai == "Máy in").MaLoai,
                    TenSanPham = "Máy in HP LaserJet Pro M404dn",
                    CauHinh = "In Laser trắng đen, tốc độ 40 trang/phút, In 2 mặt tự động, Kết nối LAN",
                    MoTa = "Máy in HP LaserJet tốc độ cao, bền bỉ, chi phí mực thấp. Lý tưởng cho thuê tại văn phòng dự án, phòng thi, hội thảo.",
                    GiaThueNgay = 100000,
                    TienCoc = 3000000,
                    HinhAnh = "/images/sanpham/may-in.png"
                },
                new SanPham{
                    MaLoai = context.LoaiThietBis.Single(l => l.TenLoai == "Máy in").MaLoai,
                    TenSanPham = "Máy in màu Canon PIXMA G3020",
                    CauHinh = "In phun màu, In - Scan - Copy, Kết nối Wifi, Hệ thống mực liên tục",
                    MoTa = "Máy in phun màu Canon đa năng với hệ thống mực liên tục tiết kiệm. Phù hợp cho thuê in ấn tài liệu màu, poster nhỏ tại sự kiện.",
                    GiaThueNgay = 80000,
                    TienCoc = 2000000,
                    HinhAnh = "/images/sanpham/may-in.png"
                }
            };
            context.SanPhams.AddRange(sanPhams);
            context.SaveChanges();
            
            // 5. Thêm máy vật lý trong kho (Serial)
            var thietBis = new ThietBi[]
            {
                // Máy tính bàn Dell
                new ThietBi { MaSanPham = sanPhams[0].MaSanPham, SoSerial = "DELL-OPT-001", TinhTrangMay = "Mới 100%", TrangThai = 0 },
                new ThietBi { MaSanPham = sanPhams[0].MaSanPham, SoSerial = "DELL-OPT-002", TinhTrangMay = "Mới 99%", TrangThai = 0 },
                new ThietBi { MaSanPham = sanPhams[0].MaSanPham, SoSerial = "DELL-OPT-003", TinhTrangMay = "Mới 98%", TrangThai = 0 },
                // Máy tính bàn HP
                new ThietBi { MaSanPham = sanPhams[1].MaSanPham, SoSerial = "HP-PRO-001", TinhTrangMay = "Mới 100%", TrangThai = 0 },
                new ThietBi { MaSanPham = sanPhams[1].MaSanPham, SoSerial = "HP-PRO-002", TinhTrangMay = "Mới 97%", TrangThai = 0 },
                // Máy lạnh Daikin
                new ThietBi { MaSanPham = sanPhams[2].MaSanPham, SoSerial = "DK-15HP-001", TinhTrangMay = "Hoạt động tốt", TrangThai = 0 },
                new ThietBi { MaSanPham = sanPhams[2].MaSanPham, SoSerial = "DK-15HP-002", TinhTrangMay = "Hoạt động tốt", TrangThai = 0 },
                // Máy lạnh LG tủ đứng
                new ThietBi { MaSanPham = sanPhams[3].MaSanPham, SoSerial = "LG-5HP-001", TinhTrangMay = "Mới 100%", TrangThai = 0 },
                // Máy in HP
                new ThietBi { MaSanPham = sanPhams[4].MaSanPham, SoSerial = "HP-M404-001", TinhTrangMay = "Mới, mực đầy", TrangThai = 0 },
                new ThietBi { MaSanPham = sanPhams[4].MaSanPham, SoSerial = "HP-M404-002", TinhTrangMay = "Mới, mực đầy", TrangThai = 0 },
                // Máy in Canon
                new ThietBi { MaSanPham = sanPhams[5].MaSanPham, SoSerial = "CANON-G3020-001", TinhTrangMay = "Mới 100%", TrangThai = 0 }
            };
            context.ThietBis.AddRange(thietBis);
            context.SaveChanges();
        }
    }
}
