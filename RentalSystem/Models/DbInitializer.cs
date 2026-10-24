using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Common;
using RentalSystem.Models;

namespace RentalSystem.Models
{
    public static class DbInitializer
    {
        /// <summary>
        /// Khởi tạo dữ liệu mẫu chuẩn nghiệp vụ cho toàn bộ hệ thống RentalSystem.
        /// </summary>
        /// <param name="context">DbContext của ứng dụng</param>
        /// <param name="forceReload">Nếu true, luôn xóa và nạp lại toàn bộ dữ liệu mẫu</param>
        public static void Initialize(ApplicationDbContext context, bool forceReload = false)
        {
            context.Database.EnsureCreated();

            // Nếu đã có đủ dữ liệu chuẩn và không yêu cầu reload thì bỏ qua
            if (!forceReload && context.HopDongs.Count() >= 7 && context.ThietBis.Count() >= 20 && context.KyHanThanhToans.Count() >= 10)
            {
                return;
            }

            ClearData(context);
            Seed(context);
        }

        /// <summary>
        /// Làm sạch toàn bộ dữ liệu hiện có để chuẩn bị nạp mới, xử lý đúng ràng buộc khóa ngoại.
        /// </summary>
        public static void ClearData(ApplicationDbContext context)
        {
            if (context.Database.IsSqlServer())
            {
                context.Database.ExecuteSqlRaw(@"
                    ALTER TABLE [ChiTietHopDongs] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [LichSuNhacNos] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [PhanCongCongViecs] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [YeuCauGiaHans] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [BienBanBanGiaos] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [PhieuChis] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [PhieuThus] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [PhieuBaoTris] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [KyHanThanhToans] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [HopDongs] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [KhuyenMais] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [LichSuThietBis] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [ThietBis] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [SanPhams] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [LoaiThietBis] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [ThongBaos] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [NguoiDungs] NOCHECK CONSTRAINT ALL;
                    ALTER TABLE [VaiTros] NOCHECK CONSTRAINT ALL;

                    DELETE FROM [ChiTietHopDongs];
                    DELETE FROM [LichSuNhacNos];
                    DELETE FROM [PhanCongCongViecs];
                    DELETE FROM [YeuCauGiaHans];
                    DELETE FROM [BienBanBanGiaos];
                    DELETE FROM [PhieuChis];
                    DELETE FROM [PhieuThus];
                    DELETE FROM [PhieuBaoTris];
                    DELETE FROM [KyHanThanhToans];
                    DELETE FROM [HopDongs];
                    DELETE FROM [KhuyenMais];
                    DELETE FROM [LichSuThietBis];
                    DELETE FROM [ThietBis];
                    DELETE FROM [SanPhams];
                    DELETE FROM [LoaiThietBis];
                    DELETE FROM [ThongBaos];
                    DELETE FROM [NguoiDungs];
                    DELETE FROM [VaiTros];

                    DBCC CHECKIDENT ('[VaiTros]', RESEED, 0);
                    DBCC CHECKIDENT ('[NguoiDungs]', RESEED, 0);
                    DBCC CHECKIDENT ('[LoaiThietBis]', RESEED, 0);
                    DBCC CHECKIDENT ('[SanPhams]', RESEED, 0);
                    DBCC CHECKIDENT ('[ThietBis]', RESEED, 0);
                    DBCC CHECKIDENT ('[KhuyenMais]', RESEED, 0);
                    DBCC CHECKIDENT ('[HopDongs]', RESEED, 0);
                    DBCC CHECKIDENT ('[KyHanThanhToans]', RESEED, 0);
                    DBCC CHECKIDENT ('[PhieuThus]', RESEED, 0);
                    DBCC CHECKIDENT ('[PhieuChis]', RESEED, 0);
                    DBCC CHECKIDENT ('[PhieuBaoTris]', RESEED, 0);
                    DBCC CHECKIDENT ('[BienBanBanGiaos]', RESEED, 0);
                    DBCC CHECKIDENT ('[ThongBaos]', RESEED, 0);
                    DBCC CHECKIDENT ('[LichSuNhacNos]', RESEED, 0);
                    DBCC CHECKIDENT ('[YeuCauGiaHans]', RESEED, 0);
                    DBCC CHECKIDENT ('[PhanCongCongViecs]', RESEED, 0);
                    DBCC CHECKIDENT ('[LichSuThietBis]', RESEED, 0);

                    ALTER TABLE [ChiTietHopDongs] CHECK CONSTRAINT ALL;
                    ALTER TABLE [LichSuNhacNos] CHECK CONSTRAINT ALL;
                    ALTER TABLE [PhanCongCongViecs] CHECK CONSTRAINT ALL;
                    ALTER TABLE [YeuCauGiaHans] CHECK CONSTRAINT ALL;
                    ALTER TABLE [BienBanBanGiaos] CHECK CONSTRAINT ALL;
                    ALTER TABLE [PhieuChis] CHECK CONSTRAINT ALL;
                    ALTER TABLE [PhieuThus] CHECK CONSTRAINT ALL;
                    ALTER TABLE [PhieuBaoTris] CHECK CONSTRAINT ALL;
                    ALTER TABLE [KyHanThanhToans] CHECK CONSTRAINT ALL;
                    ALTER TABLE [HopDongs] CHECK CONSTRAINT ALL;
                    ALTER TABLE [KhuyenMais] CHECK CONSTRAINT ALL;
                    ALTER TABLE [LichSuThietBis] CHECK CONSTRAINT ALL;
                    ALTER TABLE [ThietBis] CHECK CONSTRAINT ALL;
                    ALTER TABLE [SanPhams] CHECK CONSTRAINT ALL;
                    ALTER TABLE [LoaiThietBis] CHECK CONSTRAINT ALL;
                    ALTER TABLE [ThongBaos] CHECK CONSTRAINT ALL;
                    ALTER TABLE [NguoiDungs] CHECK CONSTRAINT ALL;
                    ALTER TABLE [VaiTros] CHECK CONSTRAINT ALL;
                ");
            }
            else
            {
                context.ChiTietHopDongs.RemoveRange(context.ChiTietHopDongs);
                context.LichSuNhacNos.RemoveRange(context.LichSuNhacNos);
                context.PhanCongCongViecs.RemoveRange(context.PhanCongCongViecs);
                context.YeuCauGiaHans.RemoveRange(context.YeuCauGiaHans);
                context.BienBanBanGiaos.RemoveRange(context.BienBanBanGiaos);
                context.PhieuChis.RemoveRange(context.PhieuChis);
                context.PhieuThus.RemoveRange(context.PhieuThus);
                context.PhieuBaoTris.RemoveRange(context.PhieuBaoTris);
                context.KyHanThanhToans.RemoveRange(context.KyHanThanhToans);
                context.HopDongs.RemoveRange(context.HopDongs);
                context.KhuyenMais.RemoveRange(context.KhuyenMais);
                context.LichSuThietBis.RemoveRange(context.LichSuThietBis);
                context.ThietBis.RemoveRange(context.ThietBis);
                context.SanPhams.RemoveRange(context.SanPhams);
                context.LoaiThietBis.RemoveRange(context.LoaiThietBis);
                context.ThongBaos.RemoveRange(context.ThongBaos);
                context.NguoiDungs.RemoveRange(context.NguoiDungs);
                context.VaiTros.RemoveRange(context.VaiTros);
                context.SaveChanges();
            }
        }

        /// <summary>
        /// Nạp toàn bộ dữ liệu mẫu nghiệp vụ phong phú vào CSDL.
        /// </summary>
        public static void Seed(ApplicationDbContext context)
        {
            var now = DateTime.Now;

            // ==========================================
            // 1. VAI TRÒ & NGƯỜI DÙNG (VaiTro, NguoiDung)
            // ==========================================
            var vaiTroAdmin = new VaiTro { TenVaiTro = "Admin" };
            var vaiTroKinhDoanh = new VaiTro { TenVaiTro = "KinhDoanh" };
            var vaiTroKyThuat = new VaiTro { TenVaiTro = "KyThuat" };
            var vaiTroKhachHang = new VaiTro { TenVaiTro = "KhachHang" };

            context.VaiTros.AddRange(vaiTroAdmin, vaiTroKinhDoanh, vaiTroKyThuat, vaiTroKhachHang);
            context.SaveChanges();

            var uAdmin = new NguoiDung
            {
                MaVaiTro = vaiTroAdmin.MaVaiTro,
                HoTen = "Quản Trị Viên",
                SoDienThoai = "0123456789",
                Email = "admin@rentalsystem.com",
                MatKhau = "Admin@123",
                CCCD = "001090001234",
                DiaChi = "Trung tâm Hệ thống, 123 Lê Duẩn, P. Bến Nghé, Q.1, TP.HCM",
                TrangThai = true
            };

            var uKinhDoanh = new NguoiDung
            {
                MaVaiTro = vaiTroKinhDoanh.MaVaiTro,
                HoTen = "Trần Thùy Linh",
                SoDienThoai = "0909111222",
                Email = "sale.linh@rentalsystem.com",
                MatKhau = "Linh@123",
                CCCD = "079195000111",
                DiaChi = "45 Lê Lợi, P. Bến Nghé, Q.1, TP.HCM",
                TrangThai = true
            };

            var uKyThuat1 = new NguoiDung
            {
                MaVaiTro = vaiTroKyThuat.MaVaiTro,
                HoTen = "Lê Anh Tuấn",
                SoDienThoai = "0909333444",
                Email = "kt.tuan@rentalsystem.com",
                MatKhau = "Tuan@123",
                CCCD = "079192000222",
                DiaChi = "88 Cách Mạng Tháng 8, P.6, Q.3, TP.HCM",
                TrangThai = true
            };

            var uKyThuat2 = new NguoiDung
            {
                MaVaiTro = vaiTroKyThuat.MaVaiTro,
                HoTen = "Phạm Hoàng Minh",
                SoDienThoai = "0909555666",
                Email = "kt.minh@rentalsystem.com",
                MatKhau = "Minh@123",
                CCCD = "079194000333",
                DiaChi = "12 Hoàng Hoa Thám, P.7, Bình Thạnh, TP.HCM",
                TrangThai = true
            };

            var uKhach1 = new NguoiDung
            {
                MaVaiTro = vaiTroKhachHang.MaVaiTro,
                HoTen = "Nguyễn Văn An",
                SoDienThoai = "0987654321",
                Email = "khach@gmail.com",
                MatKhau = "123456",
                CCCD = "079200001234",
                DiaChi = "123 Nguyễn Trãi, P. Bến Thành, Q.1, TP.HCM",
                TrangThai = true
            };

            var uKhach2 = new NguoiDung
            {
                MaVaiTro = vaiTroKhachHang.MaVaiTro,
                HoTen = "Phan Minh Quân",
                SoDienThoai = "0783406516",
                Email = "okkk@gmail.com",
                MatKhau = "123456",
                CCCD = "079201004567",
                DiaChi = "456 Võ Văn Tần, P.5, Q.3, TP.HCM",
                TrangThai = true
            };

            var uKhach3 = new NguoiDung
            {
                MaVaiTro = vaiTroKhachHang.MaVaiTro,
                HoTen = "Công ty TNHH Giải Pháp Phong Vũ",
                SoDienThoai = "02838999999",
                Email = "cty.phongvu@gmail.com",
                MatKhau = "123456",
                CCCD = "079093009999",
                DiaChi = "Tầng 5 Tòa nhà PV, 264 Nguyễn Đình Chiểu, P. Võ Thị Sáu, Q.3, TP.HCM",
                TrangThai = true
            };

            context.NguoiDungs.AddRange(uAdmin, uKinhDoanh, uKyThuat1, uKyThuat2, uKhach1, uKhach2, uKhach3);
            context.SaveChanges();

            // ==========================================
            // 2. DANH MỤC & SẢN PHẨM (LoaiThietBi, SanPham)
            // ==========================================
            var lPc = new LoaiThietBi { TenLoai = "Máy tính bàn" };
            var lLaptop = new LoaiThietBi { TenLoai = "Laptop" };
            var lMayLanh = new LoaiThietBi { TenLoai = "Máy lạnh" };
            var lMayIn = new LoaiThietBi { TenLoai = "Máy in" };

            context.LoaiThietBis.AddRange(lPc, lLaptop, lMayLanh, lMayIn);
            context.SaveChanges();

            var spPcDell = new SanPham
            {
                MaLoai = lPc.MaLoai,
                TenSanPham = "Bộ PC Dell OptiPlex 7010",
                CauHinh = "Intel Core i5-13500, 16GB RAM DDR5, SSD 512GB, Màn hình 24 inch FHD",
                MoTa = "Máy tính bàn Dell OptiPlex 7010 dòng doanh nghiệp, thiết kế nhỏ gọn, bền bỉ, phù hợp cho văn phòng, phòng học, sự kiện hội nghị.",
                GiaThueNgay = 150000m,
                TienCoc = 8000000m,
                HinhAnh = "/images/sanpham/may-tinh.png"
            };

            var spPcHPP = new SanPham
            {
                MaLoai = lPc.MaLoai,
                TenSanPham = "Bộ PC HP ProDesk 400 G9",
                CauHinh = "Intel Core i7-12700, 16GB RAM, SSD 256GB, Màn hình 22 inch",
                MoTa = "PC HP ProDesk hiệu năng cao, dáng đứng tiết kiệm diện tích, lý tưởng cho thuê theo tháng cho doanh nghiệp vừa và nhỏ.",
                GiaThueNgay = 180000m,
                TienCoc = 10000000m,
                HinhAnh = "/images/sanpham/may-tinh.png"
            };

            var spThinkPad = new SanPham
            {
                MaLoai = lLaptop.MaLoai,
                TenSanPham = "Laptop Lenovo ThinkPad T14 Gen 3",
                CauHinh = "Intel Core i5-1240P, 16GB RAM DDR4, SSD 512GB NVMe, Màn hình 14 inch WUXGA IPS chống chói",
                MoTa = "Dòng laptop doanh nhân siêu bền bỉ, bàn phím gõ êm, pin trâu, bảo mật vân tay, thích hợp cho kỹ sư, chuyên gia và quản lý.",
                GiaThueNgay = 160000m,
                TienCoc = 7000000m,
                HinhAnh = "/images/sanpham/laptop.png"
            };

            var spDellLat = new SanPham
            {
                MaLoai = lLaptop.MaLoai,
                TenSanPham = "Laptop Dell Latitude 5430",
                CauHinh = "Intel Core i7-1265U, 16GB RAM DDR4, SSD 512GB, Màn hình 14 inch FHD IPS",
                MoTa = "Laptop văn phòng mỏng nhẹ, pin lâu, camera FHD lọc tạp âm tốt, phù hợp hội thảo, làm việc từ xa, dự án di động.",
                GiaThueNgay = 170000m,
                TienCoc = 8000000m,
                HinhAnh = "/images/sanpham/laptop.png"
            };

            var spDaikin = new SanPham
            {
                MaLoai = lMayLanh.MaLoai,
                TenSanPham = "Máy lạnh Daikin FTKZ35VVMV (1.5HP)",
                CauHinh = "Inverter, 1.5 HP, Gas R-32, Làm lạnh nhanh Powerful, Chế độ Eco tiết kiệm điện",
                MoTa = "Máy lạnh Daikin Inverter cao cấp, vận hành êm ái, phù hợp cho thuê phòng họp, văn phòng tạm, sự kiện ngoài trời có mái che.",
                GiaThueNgay = 200000m,
                TienCoc = 5000000m,
                HinhAnh = "/images/sanpham/may-lanh.png"
            };

            var spLgTuDung = new SanPham
            {
                MaLoai = lMayLanh.MaLoai,
                TenSanPham = "Máy lạnh tủ đứng LG APNQ48GT3E4 (5HP)",
                CauHinh = "Inverter, 5 HP, 48.000 BTU, Làm mát diện tích lớn 60-80m²",
                MoTa = "Máy lạnh tủ đứng công suất lớn LG, chuyên dùng cho thuê sự kiện, hội trường, showroom, nhà xưởng. Lắp đặt nhanh trong 30 phút.",
                GiaThueNgay = 500000m,
                TienCoc = 15000000m,
                HinhAnh = "/images/sanpham/may-lanh.png"
            };

            var spHPM404 = new SanPham
            {
                MaLoai = lMayIn.MaLoai,
                TenSanPham = "Máy in HP LaserJet Pro M404dn",
                CauHinh = "In Laser trắng đen, tốc độ 40 trang/phút, In 2 mặt tự động, Kết nối LAN Gigabit",
                MoTa = "Máy in HP LaserJet tốc độ cao, bền bỉ, chi phí mực thấp. Lý tưởng cho thuê tại văn phòng dự án, phòng thi, hội thảo.",
                GiaThueNgay = 100000m,
                TienCoc = 3000000m,
                HinhAnh = "/images/sanpham/may-in.png"
            };

            var spCanonG3020 = new SanPham
            {
                MaLoai = lMayIn.MaLoai,
                TenSanPham = "Máy in màu Canon PIXMA G3020",
                CauHinh = "In phun màu, In - Scan - Copy, Kết nối Wifi, Hệ thống bình mực liên tục chính hãng",
                MoTa = "Máy in phun màu Canon đa năng với hệ thống mực liên tục tiết kiệm. Phù hợp cho thuê in ấn tài liệu màu, poster nhỏ tại sự kiện.",
                GiaThueNgay = 80000m,
                TienCoc = 2000000m,
                HinhAnh = "/images/sanpham/may-in.png"
            };

            context.SanPhams.AddRange(spPcDell, spPcHPP, spThinkPad, spDellLat, spDaikin, spLgTuDung, spHPM404, spCanonG3020);
            context.SaveChanges();

            // ==========================================
            // 3. KHO THIẾT BỊ VẬT LÝ (ThietBi) - 24 máy phủ đủ 5 trạng thái (0,1,2,3,4)
            // ==========================================
            var tb1 = new ThietBi { MaSanPham = spPcDell.MaSanPham, SoSerial = "DELL-OPT-001", TinhTrangMay = "Mới 99%, hoạt động ổn định", TrangThai = 1 }; // Cho thuê HĐ 2
            var tb2 = new ThietBi { MaSanPham = spPcDell.MaSanPham, SoSerial = "DELL-OPT-002", TinhTrangMay = "Mới 98%, nguyên tem niêm phong", TrangThai = 1 }; // Cho thuê HĐ 3
            var tb3 = new ThietBi { MaSanPham = spPcDell.MaSanPham, SoSerial = "DELL-OPT-003", TinhTrangMay = "Mới 100%, nguyên thùng", TrangThai = 0 }; // Sẵn sàng
            var tb4 = new ThietBi { MaSanPham = spPcDell.MaSanPham, SoSerial = "DELL-OPT-004", TinhTrangMay = "Chập mainboard do sét đánh, rã xác thanh lý", TrangThai = 4 }; // Hỏng thanh lý

            var tb5 = new ThietBi { MaSanPham = spPcHPP.MaSanPham, SoSerial = "HP-PRO-001", TinhTrangMay = "Mới 98%, chạy mượt", TrangThai = 1 }; // Cho thuê HĐ 3
            var tb6 = new ThietBi { MaSanPham = spPcHPP.MaSanPham, SoSerial = "HP-PRO-002", TinhTrangMay = "Mới 99%, đã vệ sinh chuẩn bị xuất", TrangThai = 3 }; // Giữ chỗ HĐ 1
            var tb7 = new ThietBi { MaSanPham = spPcHPP.MaSanPham, SoSerial = "HP-PRO-003", TinhTrangMay = "Mới 100%, đầy đủ phụ kiện", TrangThai = 0 }; // Sẵn sàng

            var tb8 = new ThietBi { MaSanPham = spThinkPad.MaSanPham, SoSerial = "THINKPAD-T14-001", TinhTrangMay = "Mới 98%, pin khỏe 96%", TrangThai = 1 }; // Cho thuê HĐ 4
            var tb9 = new ThietBi { MaSanPham = spThinkPad.MaSanPham, SoSerial = "THINKPAD-T14-002", TinhTrangMay = "Bể vỏ mặt lưng và viền LCD do rơi, đang sửa chữa", TrangThai = 2 }; // Bảo trì sự cố HĐ 6
            var tb10 = new ThietBi { MaSanPham = spThinkPad.MaSanPham, SoSerial = "THINKPAD-T14-003", TinhTrangMay = "Mới 100%, máy đẹp", TrangThai = 0 }; // Sẵn sàng

            var tb11 = new ThietBi { MaSanPham = spDellLat.MaSanPham, SoSerial = "DELL-LAT-001", TinhTrangMay = "Mới 99%, pin 98%", TrangThai = 1 }; // Cho thuê HĐ 5
            var tb12 = new ThietBi { MaSanPham = spDellLat.MaSanPham, SoSerial = "DELL-LAT-002", TinhTrangMay = "Mới 99%, cấu hình cao", TrangThai = 0 }; // Sẵn sàng
            var tb13 = new ThietBi { MaSanPham = spDellLat.MaSanPham, SoSerial = "DELL-LAT-003", TinhTrangMay = "Mới 99%, đã kiểm tra kỹ thuật", TrangThai = 3 }; // Giữ chỗ HĐ 1

            var tb14 = new ThietBi { MaSanPham = spDaikin.MaSanPham, SoSerial = "DK-15HP-001", TinhTrangMay = "Làm lạnh tốt, gas R-32 đầy đủ", TrangThai = 1 }; // Cho thuê HĐ 3
            var tb15 = new ThietBi { MaSanPham = spDaikin.MaSanPham, SoSerial = "DK-15HP-002", TinhTrangMay = "Máy đẹp, đã vệ sinh lưới lọc", TrangThai = 0 }; // Sẵn sàng
            var tb16 = new ThietBi { MaSanPham = spDaikin.MaSanPham, SoSerial = "DK-15HP-003", TinhTrangMay = "Bảo dưỡng xịt rửa dàn tản nhiệt, nạp bổ sung gas kho", TrangThai = 2 }; // Bảo dưỡng kho định kỳ

            var tb17 = new ThietBi { MaSanPham = spLgTuDung.MaSanPham, SoSerial = "LG-5HP-001", TinhTrangMay = "Mới 98%, công suất làm lạnh cực mạnh", TrangThai = 0 }; // Sẵn sàng
            var tb18 = new ThietBi { MaSanPham = spLgTuDung.MaSanPham, SoSerial = "LG-5HP-002", TinhTrangMay = "Hoạt động hoàn hảo, sẵn sàng cho sự kiện", TrangThai = 0 }; // Sẵn sàng

            var tb19 = new ThietBi { MaSanPham = spHPM404.MaSanPham, SoSerial = "HP-M404-001", TinhTrangMay = "Mới 98%, mực đầy, in sắc nét", TrangThai = 1 }; // Cho thuê HĐ 5
            var tb20 = new ThietBi { MaSanPham = spHPM404.MaSanPham, SoSerial = "HP-M404-002", TinhTrangMay = "Mới 100%, nguyên hộp", TrangThai = 0 }; // Sẵn sàng
            var tb21 = new ThietBi { MaSanPham = spHPM404.MaSanPham, SoSerial = "HP-M404-003", TinhTrangMay = "Cháy cuộn sấy và hỏng formatter, thanh lý linh kiện", TrangThai = 4 }; // Hỏng thanh lý

            var tb22 = new ThietBi { MaSanPham = spCanonG3020.MaSanPham, SoSerial = "CANON-G3020-001", TinhTrangMay = "In màu chuẩn đẹp, đầu phun thông thoáng", TrangThai = 1 }; // Cho thuê HĐ 4
            var tb23 = new ThietBi { MaSanPham = spCanonG3020.MaSanPham, SoSerial = "CANON-G3020-002", TinhTrangMay = "Mới 100%, 4 bình mực nguyên seal", TrangThai = 0 }; // Sẵn sàng
            var tb24 = new ThietBi { MaSanPham = spCanonG3020.MaSanPham, SoSerial = "CANON-G3020-003", TinhTrangMay = "Mới 98%, in đẹp, wifi tốt, đã nghiệm thu", TrangThai = 0 }; // Sẵn sàng (vừa nghiệm thu xong)

            context.ThietBis.AddRange(
                tb1, tb2, tb3, tb4, tb5, tb6, tb7, tb8, tb9, tb10,
                tb11, tb12, tb13, tb14, tb15, tb16, tb17, tb18, tb19, tb20,
                tb21, tb22, tb23, tb24
            );
            context.SaveChanges();

            // ==========================================
            // 4. VOUCHER KHUYẾN MÃI (KhuyenMai)
            // ==========================================
            var kmWelcome = new KhuyenMai
            {
                Code = "WELCOME10",
                PhanTramGiam = 10,
                NgayBatDau = now.AddMonths(-3),
                NgayKetThuc = now.AddMonths(3),
                SoLuong = 100,
                KichHoat = true,
                MoTa = "Giảm ngay 10% cho khách hàng mới thuê lần đầu"
            };

            var kmSummer = new KhuyenMai
            {
                Code = "SUMMER20",
                PhanTramGiam = 20,
                NgayBatDau = now.AddMonths(-2),
                NgayKetThuc = now.AddMonths(2),
                SoLuong = 50,
                KichHoat = true,
                MoTa = "Ưu đãi rực rỡ mùa hè giảm 20% chi phí thuê"
            };

            var kmEnterprise = new KhuyenMai
            {
                Code = "ENTERPRISE15",
                PhanTramGiam = 15,
                NgayBatDau = now.AddMonths(-1),
                NgayKetThuc = now.AddMonths(4),
                SoLuong = 30,
                KichHoat = true,
                MoTa = "Chiết khấu 15% đặc quyền cho khách hàng doanh nghiệp"
            };

            var kmVip = new KhuyenMai
            {
                Code = "VIPRENTAL",
                PhanTramGiam = 25,
                NgayBatDau = now.AddMonths(-1),
                NgayKetThuc = now.AddMonths(5),
                SoLuong = 20,
                KichHoat = true,
                MoTa = "Voucher VIP giảm 25% cho hợp đồng thuê thiết bị dài hạn"
            };

            context.KhuyenMais.AddRange(kmWelcome, kmSummer, kmEnterprise, kmVip);
            context.SaveChanges();

            // ==========================================
            // 5. VÒNG ĐỜI HỢP ĐỒNG (HopDong & ChiTietHopDong)
            // ==========================================

            // HĐ 1: Chờ duyệt cọc (TrangThai = 0)
            var hd1 = new HopDong
            {
                MaKhachHang = uKhach2.MaNguoiDung, // Phan Minh Quân
                MaNhanVien = uKinhDoanh.MaNguoiDung,
                NgayBatDau = now.AddDays(1).Date,
                NgayKetThuc = now.AddDays(6).Date,
                TongTien = 1750000m,
                TienDaCoc = 0m,
                TienCocBaoDamMay = 18000000m,
                TrangThai = 0, // Chờ duyệt
                SoKyHan = 1,
                TrangThaiThanhToan = 0,
                AnhCMND = "/uploads/cmnd/cmnd_default.png",
                ChuKyKhachHang = "/uploads/signatures/kh_sig.png",
                ChuKyNhanVien = "/uploads/signatures/nv_sig.png",
                HanChotKy = now.AddHours(24),
                GhiChu = "Đơn thuê thiết bị đào tạo 5 ngày. Đang chờ khách hoàn tất đóng cọc trực tuyến."
            };

            // HĐ 2: Đang thuê trả thẳng (TrangThai = 1, Đã thanh toán đủ)
            var hd2 = new HopDong
            {
                MaKhachHang = uKhach1.MaNguoiDung, // Nguyễn Văn An
                MaNhanVien = uKinhDoanh.MaNguoiDung,
                NgayBatDau = now.AddDays(-5).Date,
                NgayKetThuc = now.AddDays(25).Date,
                TongTien = 4500000m,
                TienDaCoc = 8000000m,
                TienCocBaoDamMay = 8000000m,
                TrangThai = 1, // Đang hiệu lực
                SoKyHan = 1,
                TrangThaiThanhToan = 2, // Đã thanh toán đủ
                NgayKy = now.AddDays(-5).Date,
                AnhCMND = "/uploads/cmnd/cmnd_default.png",
                ChuKyKhachHang = "/uploads/signatures/kh_sig.png",
                ChuKyNhanVien = "/uploads/signatures/nv_sig.png",
                GhiChu = "Hợp đồng thuê trả thẳng trọn gói 1 tháng. Đã thanh toán 100% tiền cọc và tiền thuê qua VNPay."
            };

            // HĐ 3: Đang thuê trả góp nhiều kỳ, thanh toán đúng hạn (TrangThai = 1, Còn nợ)
            var hd3 = new HopDong
            {
                MaKhachHang = uKhach3.MaNguoiDung, // Cty Phong Vũ
                MaNhanVien = uKinhDoanh.MaNguoiDung,
                MaKhuyenMai = kmEnterprise.MaKM,
                NgayBatDau = now.AddDays(-60).Date,
                NgayKetThuc = now.AddDays(30).Date,
                TongTien = 40500000m,
                TienDaCoc = 23000000m,
                TienCocBaoDamMay = 23000000m,
                TrangThai = 1,
                SoKyHan = 3,
                TrangThaiThanhToan = 1, // Còn nợ (còn kỳ 3)
                NgayKy = now.AddDays(-60).Date,
                AnhCMND = "/uploads/cmnd/cmnd_default.png",
                ChuKyKhachHang = "/uploads/signatures/kh_sig.png",
                ChuKyNhanVien = "/uploads/signatures/nv_sig.png",
                GhiChu = "Hợp đồng thuê thiết bị doanh nghiệp thanh toán trả góp 3 đợt. Doanh nghiệp thanh toán đúng hạn."
            };

            // HĐ 4: Đang thuê có kỳ hạn quá hạn nợ >20 ngày kèm tiền phạt trễ hạn (TrangThai = 1, Còn nợ)
            var hd4 = new HopDong
            {
                MaKhachHang = uKhach1.MaNguoiDung, // Nguyễn Văn An
                MaNhanVien = uKinhDoanh.MaNguoiDung,
                NgayBatDau = now.AddDays(-110).Date,
                NgayKetThuc = now.AddDays(10).Date,
                TongTien = 28800000m,
                TienDaCoc = 9000000m,
                TienCocBaoDamMay = 9000000m,
                TrangThai = 1,
                SoKyHan = 4,
                TrangThaiThanhToan = 1,
                NgayKy = now.AddDays(-110).Date,
                AnhCMND = "/uploads/cmnd/cmnd_default.png",
                ChuKyKhachHang = "/uploads/signatures/kh_sig.png",
                ChuKyNhanVien = "/uploads/signatures/nv_sig.png",
                GhiChu = "Hợp đồng phát sinh nhiều đợt quá hạn nợ. Khách hàng đang có kỳ hạn trễ hạn cần đôn đốc thu hồi."
            };

            // HĐ 5: Đang thuê có Yêu cầu gia hạn hợp đồng chờ duyệt (TrangThai = 1)
            var hd5 = new HopDong
            {
                MaKhachHang = uKhach3.MaNguoiDung, // Cty Phong Vũ
                MaNhanVien = uKinhDoanh.MaNguoiDung,
                NgayBatDau = now.AddDays(-25).Date,
                NgayKetThuc = now.AddDays(5).Date,
                TongTien = 8100000m,
                TienDaCoc = 11000000m,
                TienCocBaoDamMay = 11000000m,
                TrangThai = 1,
                SoKyHan = 1,
                TrangThaiThanhToan = 2,
                NgayKy = now.AddDays(-25).Date,
                AnhCMND = "/uploads/cmnd/cmnd_default.png",
                ChuKyKhachHang = "/uploads/signatures/kh_sig.png",
                ChuKyNhanVien = "/uploads/signatures/nv_sig.png",
                YeuCauGiaHan = true,
                SoNgayGiaHan = 30,
                TrangThaiGiaHan = 0, // 0: Chờ duyệt
                LyDoGiaHan = "Dự án CNTT của đối tác kéo dài thêm 1 tháng, công ty đề xuất gia hạn thêm 30 ngày thuê.",
                GhiChu = "Hợp đồng đang có yêu cầu gia hạn thêm 30 ngày chờ ban quản lý phê duyệt."
            };

            // HĐ 6: Đang thuê phát sinh sự cố bảo trì có phí bồi thường và tạm dừng tiền thuê (TrangThai = 1)
            var hd6 = new HopDong
            {
                MaKhachHang = uKhach2.MaNguoiDung, // Phan Minh Quân
                MaNhanVien = uKinhDoanh.MaNguoiDung,
                NgayBatDau = now.AddDays(-20).Date,
                NgayKetThuc = now.AddDays(10).Date,
                TongTien = 4800000m,
                TienDaCoc = 7000000m,
                TienCocBaoDamMay = 7000000m,
                TrangThai = 1,
                SoKyHan = 1,
                TrangThaiThanhToan = 1, // Còn nợ chi phí bồi thường
                TienGiamTruBaoTri = 640000m,
                NgayKy = now.AddDays(-20).Date,
                AnhCMND = "/uploads/cmnd/cmnd_default.png",
                ChuKyKhachHang = "/uploads/signatures/kh_sig.png",
                ChuKyNhanVien = "/uploads/signatures/nv_sig.png",
                GhiChu = "Hợp đồng phát sinh sự cố rơi vỡ laptop. Đã lập phiếu bảo trì tính phí bồi thường và tạm dừng tiền thuê 4 ngày."
            };

            // HĐ 7: Đã trả máy chờ quyết toán công nợ cọc (TrangThai = 4)
            var hd7 = new HopDong
            {
                MaKhachHang = uKhach1.MaNguoiDung, // Nguyễn Văn An
                MaNhanVien = uKinhDoanh.MaNguoiDung,
                NgayBatDau = now.AddDays(-35).Date,
                NgayKetThuc = now.AddDays(-5).Date,
                TongTien = 4500000m,
                TienDaCoc = 8000000m,
                TienCocBaoDamMay = 8000000m,
                TrangThai = 4, // 4: Đã trả máy (Chờ quyết toán công nợ)
                SoKyHan = 1,
                TrangThaiThanhToan = 2,
                TrangThaiHoanCoc = 0, // Chưa hoàn cọc
                NgayKy = now.AddDays(-35).Date,
                AnhCMND = "/uploads/cmnd/cmnd_default.png",
                ChuKyKhachHang = "/uploads/signatures/kh_sig.png",
                ChuKyNhanVien = "/uploads/signatures/nv_sig.png",
                GhiChu = "Khách hàng đã bàn giao trả lại đầy đủ máy tại kho. Đang chờ kế toán đối soát quyết toán hoàn cọc 8.000.000 VNĐ."
            };

            // HĐ 8: Đã hoàn tất chu kỳ thuê trong tháng hiện tại (TrangThai = 2)
            var hd8 = new HopDong
            {
                MaKhachHang = uKhach3.MaNguoiDung, // Cty Phong Vũ
                MaNhanVien = uKinhDoanh.MaNguoiDung,
                NgayBatDau = now.AddDays(-20).Date,
                NgayKetThuc = now.AddDays(-5).Date,
                TongTien = 9500000m,
                TienDaCoc = 15000000m,
                TienCocBaoDamMay = 15000000m,
                TrangThai = 2, // 2: Hoàn tất
                SoKyHan = 1,
                TrangThaiThanhToan = 2,
                TrangThaiHoanCoc = 1, // Đã hoàn cọc
                TienCocThucHoan = 15000000m,
                NgayHoanCoc = now.AddDays(-4).Date,
                GhiChuHoanCoc = "Đã hoàn trả 100% tiền cọc 15.000.000 VNĐ qua tài khoản MB của Công ty Phong Vũ.",
                NgayKy = now.AddDays(-20).Date,
                AnhCMND = "/uploads/cmnd/cmnd_default.png",
                ChuKyKhachHang = "/uploads/signatures/kh_sig.png",
                ChuKyNhanVien = "/uploads/signatures/nv_sig.png",
                GhiChu = "Hợp đồng thuê ngắn hạn cho dự án hội chợ triển lãm. Đã nghiệm thu và hoàn tất quyết toán."
            };

            // HĐ 9: Đã hủy hoàn cọc (TrangThai = 3)
            var hd9 = new HopDong
            {
                MaKhachHang = uKhach2.MaNguoiDung, // Phan Minh Quân
                MaNhanVien = uKinhDoanh.MaNguoiDung,
                NgayBatDau = now.AddDays(-15).Date,
                NgayKetThuc = now.AddDays(-5).Date,
                TongTien = 3000000m,
                TienDaCoc = 5000000m,
                TienCocBaoDamMay = 5000000m,
                TrangThai = 3, // 3: Đã hủy
                SoKyHan = 1,
                TrangThaiThanhToan = 0,
                YeuCauHuy = true,
                LyDoHuy = "Khách hàng đổi địa điểm tổ chức sự kiện đột xuất, đề nghị hủy đơn thuê trước 3 ngày.",
                NgayYeuCauHuy = now.AddDays(-14).Date,
                TrangThaiHoanCoc = 1, // Đã hoàn cọc
                TienCocThucHoan = 5000000m,
                NgayHoanCoc = now.AddDays(-13).Date,
                GhiChuHoanCoc = "Đã hoàn trả 5.000.000 VNĐ tiền cọc cho khách hàng Phan Minh Quân.",
                AnhCMND = "/uploads/cmnd/cmnd_default.png",
                ChuKyKhachHang = "/uploads/signatures/kh_sig.png",
                ChuKyNhanVien = "/uploads/signatures/nv_sig.png",
                GhiChu = "Hợp đồng hủy trước ngày nhận thiết bị, thực hiện hoàn trả tiền cọc theo quy định."
            };

            // HĐ 10: Đã hoàn tất chu kỳ thuê ở 1 tháng trước (TrangThai = 2) - Phục vụ biểu đồ doanh thu
            var hd10 = new HopDong
            {
                MaKhachHang = uKhach3.MaNguoiDung, // Cty Phong Vũ
                MaNhanVien = uKinhDoanh.MaNguoiDung,
                NgayBatDau = now.AddMonths(-1).Date,
                NgayKetThuc = now.AddMonths(-1).AddDays(25).Date,
                TongTien = 12500000m,
                TienDaCoc = 15000000m,
                TienCocBaoDamMay = 15000000m,
                TrangThai = 2,
                SoKyHan = 1,
                TrangThaiThanhToan = 2,
                TrangThaiHoanCoc = 1,
                TienCocThucHoan = 15000000m,
                NgayHoanCoc = now.AddMonths(-1).AddDays(26).Date,
                GhiChuHoanCoc = "Đã hoàn trả 100% tiền cọc cho khách doanh nghiệp.",
                NgayKy = now.AddMonths(-1).Date,
                AnhCMND = "/uploads/cmnd/cmnd_default.png",
                ChuKyKhachHang = "/uploads/signatures/kh_sig.png",
                ChuKyNhanVien = "/uploads/signatures/nv_sig.png",
                GhiChu = "Đơn thuê máy trọn gói cho chi nhánh Phong Vũ tháng trước."
            };

            // HĐ 11: Đã hoàn tất chu kỳ thuê ở 2 tháng trước (TrangThai = 2) - Phục vụ biểu đồ doanh thu
            var hd11 = new HopDong
            {
                MaKhachHang = uKhach1.MaNguoiDung, // Nguyễn Văn An
                MaNhanVien = uKinhDoanh.MaNguoiDung,
                NgayBatDau = now.AddMonths(-2).Date,
                NgayKetThuc = now.AddMonths(-2).AddDays(20).Date,
                TongTien = 8000000m,
                TienDaCoc = 8000000m,
                TienCocBaoDamMay = 8000000m,
                TrangThai = 2,
                SoKyHan = 1,
                TrangThaiThanhToan = 2,
                TrangThaiHoanCoc = 1,
                TienCocThucHoan = 8000000m,
                NgayHoanCoc = now.AddMonths(-2).AddDays(21).Date,
                GhiChuHoanCoc = "Đã hoàn cọc đầy đủ cho khách.",
                NgayKy = now.AddMonths(-2).Date,
                AnhCMND = "/uploads/cmnd/cmnd_default.png",
                ChuKyKhachHang = "/uploads/signatures/kh_sig.png",
                ChuKyNhanVien = "/uploads/signatures/nv_sig.png",
                GhiChu = "Đơn thuê bộ PC Dell văn phòng 2 tháng trước đã kết thúc trọn vẹn."
            };

            context.HopDongs.AddRange(hd1, hd2, hd3, hd4, hd5, hd6, hd7, hd8, hd9, hd10, hd11);
            context.SaveChanges();

            // Chi tiết thiết bị thuê (ChiTietHopDong)
            context.ChiTietHopDongs.AddRange(
                // HĐ 1: Giữ chỗ HP Pro + Dell Lat
                new ChiTietHopDong { MaHopDong = hd1.MaHopDong, MaThietBi = tb6.MaThietBi, GiaChotThu = 180000m },
                new ChiTietHopDong { MaHopDong = hd1.MaHopDong, MaThietBi = tb13.MaThietBi, GiaChotThu = 170000m },

                // HĐ 2: Dell OptiPlex
                new ChiTietHopDong { MaHopDong = hd2.MaHopDong, MaThietBi = tb1.MaThietBi, GiaChotThu = 150000m },

                // HĐ 3: Dell OptiPlex + HP Pro + Daikin
                new ChiTietHopDong { MaHopDong = hd3.MaHopDong, MaThietBi = tb2.MaThietBi, GiaChotThu = 150000m },
                new ChiTietHopDong { MaHopDong = hd3.MaHopDong, MaThietBi = tb5.MaThietBi, GiaChotThu = 180000m },
                new ChiTietHopDong { MaHopDong = hd3.MaHopDong, MaThietBi = tb14.MaThietBi, GiaChotThu = 200000m },

                // HĐ 4: ThinkPad + Canon G3020
                new ChiTietHopDong { MaHopDong = hd4.MaHopDong, MaThietBi = tb8.MaThietBi, GiaChotThu = 160000m },
                new ChiTietHopDong { MaHopDong = hd4.MaHopDong, MaThietBi = tb22.MaThietBi, GiaChotThu = 80000m },

                // HĐ 5: Dell Latitude + HP M404
                new ChiTietHopDong { MaHopDong = hd5.MaHopDong, MaThietBi = tb11.MaThietBi, GiaChotThu = 170000m },
                new ChiTietHopDong { MaHopDong = hd5.MaHopDong, MaThietBi = tb19.MaThietBi, GiaChotThu = 100000m },

                // HĐ 6: ThinkPad T14 (Bảo trì)
                new ChiTietHopDong { MaHopDong = hd6.MaHopDong, MaThietBi = tb9.MaThietBi, GiaChotThu = 160000m },

                // HĐ 7: Dell OptiPlex
                new ChiTietHopDong { MaHopDong = hd7.MaHopDong, MaThietBi = tb3.MaThietBi, GiaChotThu = 150000m },

                // HĐ 8: Daikin + LG
                new ChiTietHopDong { MaHopDong = hd8.MaHopDong, MaThietBi = tb15.MaThietBi, GiaChotThu = 200000m },

                // HĐ 9: Canon G3020
                new ChiTietHopDong { MaHopDong = hd9.MaHopDong, MaThietBi = tb23.MaThietBi, GiaChotThu = 80000m },

                // HĐ 10: Dell OptiPlex
                new ChiTietHopDong { MaHopDong = hd10.MaHopDong, MaThietBi = tb3.MaThietBi, GiaChotThu = 150000m },

                // HĐ 11: HP ProDesk
                new ChiTietHopDong { MaHopDong = hd11.MaHopDong, MaThietBi = tb7.MaThietBi, GiaChotThu = 180000m }
            );
            context.SaveChanges();

            // ==========================================
            // 6. KỲ HẠN THANH TOÁN (KyHanThanhToan)
            // ==========================================
            var kyHans = new List<KyHanThanhToan>();

            // HĐ 1: 1 kỳ hạn chưa trả (Chờ cọc)
            var kHd1 = new KyHanThanhToan
            {
                MaHopDong = hd1.MaHopDong,
                SoKyHan = 1,
                NgayDenHan = now.AddDays(1).Date,
                SoTienPhai = 1750000m,
                SoTienDaTra = 0m,
                TrangThai = 0, // Chưa trả
                GhiChu = "Thanh toán đợt 1 tiền thuê đơn hàng HD" + hd1.MaHopDong
            };
            kyHans.Add(kHd1);

            // HĐ 2: 1 kỳ hạn đã trả đủ
            var kHd2 = new KyHanThanhToan
            {
                MaHopDong = hd2.MaHopDong,
                SoKyHan = 1,
                NgayDenHan = now.AddDays(-5).Date,
                SoTienPhai = 4500000m,
                SoTienDaTra = 4500000m,
                TrangThai = 1, // Đã trả
                NgayThanhToan = now.AddDays(-5).Date,
                MaGiaoDichChuyenKhoan = "VNP14892011",
                TrangThaiXacNhan = 2,
                NgayGuiBienLai = now.AddDays(-5).Date,
                GhiChu = "Thanh toán trọn gói 1 kỳ qua VNPay"
            };
            kyHans.Add(kHd2);

            // HĐ 3: 3 kỳ hạn trả góp (Kỳ 1, Kỳ 2 đã trả đúng hạn, Kỳ 3 chưa tới hạn)
            var kHd3_1 = new KyHanThanhToan
            {
                MaHopDong = hd3.MaHopDong,
                SoKyHan = 1,
                NgayDenHan = now.AddDays(-60).Date,
                SoTienPhai = 13500000m,
                SoTienDaTra = 13500000m,
                TrangThai = 1,
                NgayThanhToan = now.AddDays(-60).Date,
                MaGiaoDichChuyenKhoan = "MB_TRF_9921",
                TrangThaiXacNhan = 2,
                NgayGuiBienLai = now.AddDays(-60).Date,
                GhiChu = "Thanh toán đợt 1 hợp đồng HD" + hd3.MaHopDong
            };
            var kHd3_2 = new KyHanThanhToan
            {
                MaHopDong = hd3.MaHopDong,
                SoKyHan = 2,
                NgayDenHan = now.AddDays(-30).Date,
                SoTienPhai = 13500000m,
                SoTienDaTra = 13500000m,
                TrangThai = 1,
                NgayThanhToan = now.AddDays(-30).Date,
                MaGiaoDichChuyenKhoan = "MB_TRF_9988",
                TrangThaiXacNhan = 2,
                NgayGuiBienLai = now.AddDays(-30).Date,
                GhiChu = "Thanh toán đợt 2 hợp đồng HD" + hd3.MaHopDong
            };
            var kHd3_3 = new KyHanThanhToan
            {
                MaHopDong = hd3.MaHopDong,
                SoKyHan = 3,
                NgayDenHan = now.AddDays(15).Date,
                SoTienPhai = 13500000m,
                SoTienDaTra = 0m,
                TrangThai = 0,
                GhiChu = "Đợt 3 hợp đồng HD" + hd3.MaHopDong + " (chưa tới hạn)"
            };
            kyHans.AddRange(new[] { kHd3_1, kHd3_2, kHd3_3 });

            // HĐ 4: 4 kỳ hạn trễ hạn tương ứng ĐỦ 4 NHÓM TUỔI NỢ (1-30, 31-60, 61-90, >90 ngày)
            // Nhóm 4 (>90 ngày): trễ 105 ngày
            var kHd4_1 = new KyHanThanhToan
            {
                MaHopDong = hd4.MaHopDong,
                SoKyHan = 1,
                NgayDenHan = now.AddDays(-105).Date,
                SoTienPhai = 7200000m,
                SoTienDaTra = 5000000m, // Còn nợ 2.200.000
                TrangThai = 2, // Trễ hạn
                SoNgayTreHan = 105,
                TienPhat = 231000m,
                PhiPhatTreHan = 231000m,
                NhomTuoiNo = 4, // >90 ngày
                GhiChu = "Khách thanh toán thiếu đợt 1, trễ hạn trên 90 ngày (Nợ nhóm 4)"
            };

            // Nhóm 3 (61-90 ngày): trễ 75 ngày
            var kHd4_2 = new KyHanThanhToan
            {
                MaHopDong = hd4.MaHopDong,
                SoKyHan = 2,
                NgayDenHan = now.AddDays(-75).Date,
                SoTienPhai = 7200000m,
                SoTienDaTra = 0m,
                TrangThai = 2,
                SoNgayTreHan = 75,
                TienPhat = 540000m,
                PhiPhatTreHan = 540000m,
                NhomTuoiNo = 3, // 61-90 ngày
                GhiChu = "Chưa thanh toán đợt 2, trễ hạn nhóm 3"
            };

            // Nhóm 2 (31-60 ngày): trễ 45 ngày
            var kHd4_3 = new KyHanThanhToan
            {
                MaHopDong = hd4.MaHopDong,
                SoKyHan = 3,
                NgayDenHan = now.AddDays(-45).Date,
                SoTienPhai = 7200000m,
                SoTienDaTra = 0m,
                TrangThai = 2,
                SoNgayTreHan = 45,
                TienPhat = 324000m,
                PhiPhatTreHan = 324000m,
                NhomTuoiNo = 2, // 31-60 ngày
                GhiChu = "Chưa thanh toán đợt 3, trễ hạn nhóm 2"
            };

            // Nhóm 1 (1-30 ngày): trễ 20 ngày (>20 ngày kèm phí phạt trễ hạn theo R1.5)
            var kHd4_4 = new KyHanThanhToan
            {
                MaHopDong = hd4.MaHopDong,
                SoKyHan = 4,
                NgayDenHan = now.AddDays(-20).Date,
                SoTienPhai = 7200000m,
                SoTienDaTra = 0m,
                TrangThai = 2,
                SoNgayTreHan = 20,
                TienPhat = 144000m,
                PhiPhatTreHan = 144000m,
                NhomTuoiNo = 1, // 1-30 ngày
                GhiChu = "Quá hạn nợ 20 ngày đợt 4 kèm tiền phạt trễ hạn"
            };
            kyHans.AddRange(new[] { kHd4_1, kHd4_2, kHd4_3, kHd4_4 });

            // HĐ 5: 1 kỳ hạn đã trả đủ
            var kHd5 = new KyHanThanhToan
            {
                MaHopDong = hd5.MaHopDong,
                SoKyHan = 1,
                NgayDenHan = now.AddDays(-25).Date,
                SoTienPhai = 8100000m,
                SoTienDaTra = 8100000m,
                TrangThai = 1,
                NgayThanhToan = now.AddDays(-25).Date,
                MaGiaoDichChuyenKhoan = "MB_HD5_OK",
                TrangThaiXacNhan = 2,
                NgayGuiBienLai = now.AddDays(-25).Date,
                GhiChu = "Thanh toán đợt 1 HĐ5 đầy đủ qua chuyển khoản"
            };
            kyHans.Add(kHd5);

            // HĐ 6: 1 kỳ hạn đã trả tiền thuê gốc (còn nợ chi phí bồi thường hư hại)
            var kHd6 = new KyHanThanhToan
            {
                MaHopDong = hd6.MaHopDong,
                SoKyHan = 1,
                NgayDenHan = now.AddDays(-20).Date,
                SoTienPhai = 4800000m,
                SoTienDaTra = 4800000m,
                TrangThai = 1,
                NgayThanhToan = now.AddDays(-20).Date,
                GhiChu = "Đã thu tiền thuê đợt 1, phát sinh sự cố bảo trì bồi thường chưa thu"
            };
            kyHans.Add(kHd6);

            // HĐ 7: 1 kỳ hạn đã trả
            var kHd7 = new KyHanThanhToan
            {
                MaHopDong = hd7.MaHopDong,
                SoKyHan = 1,
                NgayDenHan = now.AddDays(-35).Date,
                SoTienPhai = 4500000m,
                SoTienDaTra = 4500000m,
                TrangThai = 1,
                NgayThanhToan = now.AddDays(-35).Date,
                GhiChu = "Đã thanh toán đủ tiền thuê"
            };
            kyHans.Add(kHd7);

            // HĐ 8: 1 kỳ hạn hoàn tất
            var kHd8 = new KyHanThanhToan
            {
                MaHopDong = hd8.MaHopDong,
                SoKyHan = 1,
                NgayDenHan = now.AddDays(-20).Date,
                SoTienPhai = 9500000m,
                SoTienDaTra = 9500000m,
                TrangThai = 1,
                NgayThanhToan = now.AddDays(-20).Date,
                GhiChu = "Đã thanh toán đủ toàn bộ"
            };
            kyHans.Add(kHd8);

            // HĐ 9: 1 kỳ hạn đã hủy
            var kHd9 = new KyHanThanhToan
            {
                MaHopDong = hd9.MaHopDong,
                SoKyHan = 1,
                NgayDenHan = now.AddDays(-15).Date,
                SoTienPhai = 3000000m,
                SoTienDaTra = 0m,
                TrangThai = 3, // Đã hủy
                GhiChu = "Hủy kỳ hạn do hợp đồng bị hủy theo yêu cầu khách hàng"
            };
            kyHans.Add(kHd9);

            // HĐ 10: 1 kỳ hạn hoàn tất
            var kHd10 = new KyHanThanhToan
            {
                MaHopDong = hd10.MaHopDong,
                SoKyHan = 1,
                NgayDenHan = now.AddMonths(-1).Date,
                SoTienPhai = 12500000m,
                SoTienDaTra = 12500000m,
                TrangThai = 1,
                NgayThanhToan = now.AddMonths(-1).Date,
                GhiChu = "Đã thanh toán đủ"
            };
            kyHans.Add(kHd10);

            // HĐ 11: 1 kỳ hạn hoàn tất
            var kHd11 = new KyHanThanhToan
            {
                MaHopDong = hd11.MaHopDong,
                SoKyHan = 1,
                NgayDenHan = now.AddMonths(-2).Date,
                SoTienPhai = 8000000m,
                SoTienDaTra = 8000000m,
                TrangThai = 1,
                NgayThanhToan = now.AddMonths(-2).Date,
                GhiChu = "Đã thanh toán đủ"
            };
            kyHans.Add(kHd11);

            context.KyHanThanhToans.AddRange(kyHans);
            context.SaveChanges();

            // ==========================================
            // 7. PHIẾU THU & PHIẾU CHI (PhieuThu, PhieuChi)
            // ==========================================
            var phieuThus = new List<PhieuThu>
            {
                // HĐ 2: Thu cọc VNPay + Thu tiền thuê VNPay
                new PhieuThu
                {
                    MaHopDong = hd2.MaHopDong,
                    LoaiPhieu = 1, // Thu cọc
                    SoTien = 8000000m,
                    NgayGiaoDich = now.AddDays(-5),
                    HinhThucThanhToan = 2, // VNPay
                    MaGiaoDichNganHang = "VNP_DEP_HD2",
                    NganHangNhan = "VNPay Sandbox",
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu tiền cọc thiết bị PC Dell OptiPlex HĐ2 qua VNPay"
                },
                new PhieuThu
                {
                    MaHopDong = hd2.MaHopDong,
                    MaKyHan = kHd2.MaKyHan,
                    LoaiPhieu = 0, // Thu thuê
                    SoTien = 4500000m,
                    NgayGiaoDich = now.AddDays(-5),
                    HinhThucThanhToan = 2, // VNPay
                    MaGiaoDichNganHang = "VNP_RENT_HD2",
                    NganHangNhan = "VNPay Sandbox",
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu toàn bộ tiền thuê 30 ngày HĐ2 qua cổng VNPay"
                },

                // HĐ 3: Thu cọc VietQR + Thu đợt 1 + Thu đợt 2
                new PhieuThu
                {
                    MaHopDong = hd3.MaHopDong,
                    LoaiPhieu = 1,
                    SoTien = 23000000m,
                    NgayGiaoDich = now.AddDays(-60),
                    HinhThucThanhToan = 1, // Chuyển khoản VietQR
                    MaGiaoDichNganHang = "VCB_COC_HD3",
                    NganHangNhan = "Vietcombank (0071000123456)",
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu tiền cọc 3 thiết bị HĐ3 của Cty Phong Vũ qua VietQR"
                },
                new PhieuThu
                {
                    MaHopDong = hd3.MaHopDong,
                    MaKyHan = kHd3_1.MaKyHan,
                    LoaiPhieu = 0,
                    SoTien = 13500000m,
                    NgayGiaoDich = now.AddDays(-60),
                    HinhThucThanhToan = 1,
                    MaGiaoDichNganHang = "MB_KY1_HD3",
                    NganHangNhan = "MBBank (0783406516)",
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu đợt 1 tiền thuê HĐ3 qua chuyển khoản VietQR"
                },
                new PhieuThu
                {
                    MaHopDong = hd3.MaHopDong,
                    MaKyHan = kHd3_2.MaKyHan,
                    LoaiPhieu = 0,
                    SoTien = 13500000m,
                    NgayGiaoDich = now.AddDays(-30),
                    HinhThucThanhToan = 1,
                    MaGiaoDichNganHang = "MB_KY2_HD3",
                    NganHangNhan = "MBBank (0783406516)",
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu đợt 2 tiền thuê HĐ3 qua chuyển khoản VietQR"
                },

                // HĐ 4: Thu cọc Tiền mặt + Thu trả 1 phần đợt 1
                new PhieuThu
                {
                    MaHopDong = hd4.MaHopDong,
                    LoaiPhieu = 1,
                    SoTien = 9000000m,
                    NgayGiaoDich = now.AddDays(-110),
                    HinhThucThanhToan = 0, // Tiền mặt
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu cọc tiền mặt tại quầy cho HĐ4"
                },
                new PhieuThu
                {
                    MaHopDong = hd4.MaHopDong,
                    MaKyHan = kHd4_1.MaKyHan,
                    LoaiPhieu = 0,
                    SoTien = 5000000m,
                    NgayGiaoDich = now.AddDays(-100),
                    HinhThucThanhToan = 0,
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Khách nộp tiền mặt đợt 1 (trả thiếu 2.200.000 VNĐ)"
                },

                // HĐ 5: Thu cọc + Thu tiền thuê đợt 1
                new PhieuThu
                {
                    MaHopDong = hd5.MaHopDong,
                    LoaiPhieu = 1,
                    SoTien = 11000000m,
                    NgayGiaoDich = now.AddDays(-25),
                    HinhThucThanhToan = 1,
                    MaGiaoDichNganHang = "TCB_DEP_HD5",
                    NganHangNhan = "Techcombank",
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu cọc hợp đồng HD5 chuyển khoản"
                },
                new PhieuThu
                {
                    MaHopDong = hd5.MaHopDong,
                    MaKyHan = kHd5.MaKyHan,
                    LoaiPhieu = 0,
                    SoTien = 8100000m,
                    NgayGiaoDich = now.AddDays(-25),
                    HinhThucThanhToan = 1,
                    MaGiaoDichNganHang = "TCB_RENT_HD5",
                    NganHangNhan = "Techcombank",
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu tiền thuê kỳ 1 HĐ5"
                },

                // HĐ 6: Thu cọc + Thu tiền thuê (Tiền mặt)
                new PhieuThu
                {
                    MaHopDong = hd6.MaHopDong,
                    LoaiPhieu = 1,
                    SoTien = 7000000m,
                    NgayGiaoDich = now.AddDays(-20),
                    HinhThucThanhToan = 0,
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu tiền cọc laptop ThinkPad HĐ6 tiền mặt"
                },
                new PhieuThu
                {
                    MaHopDong = hd6.MaHopDong,
                    MaKyHan = kHd6.MaKyHan,
                    LoaiPhieu = 0,
                    SoTien = 4800000m,
                    NgayGiaoDich = now.AddDays(-20),
                    HinhThucThanhToan = 0,
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu tiền thuê 30 ngày HĐ6 tiền mặt"
                },

                // HĐ 7: Thu cọc + Thu tiền thuê
                new PhieuThu
                {
                    MaHopDong = hd7.MaHopDong,
                    LoaiPhieu = 1,
                    SoTien = 8000000m,
                    NgayGiaoDich = now.AddDays(-35),
                    HinhThucThanhToan = 0,
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu tiền cọc HĐ7"
                },
                new PhieuThu
                {
                    MaHopDong = hd7.MaHopDong,
                    MaKyHan = kHd7.MaKyHan,
                    LoaiPhieu = 0,
                    SoTien = 4500000m,
                    NgayGiaoDich = now.AddDays(-35),
                    HinhThucThanhToan = 0,
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu tiền thuê HĐ7"
                },

                // HĐ 8: Thu cọc + Thu tiền thuê
                new PhieuThu
                {
                    MaHopDong = hd8.MaHopDong,
                    LoaiPhieu = 1,
                    SoTien = 15000000m,
                    NgayGiaoDich = now.AddDays(-20),
                    HinhThucThanhToan = 1,
                    MaGiaoDichNganHang = "MB_DEP_HD8",
                    NganHangNhan = "MBBank",
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu tiền cọc máy lạnh HĐ8"
                },
                new PhieuThu
                {
                    MaHopDong = hd8.MaHopDong,
                    MaKyHan = kHd8.MaKyHan,
                    LoaiPhieu = 0,
                    SoTien = 9500000m,
                    NgayGiaoDich = now.AddDays(-20),
                    HinhThucThanhToan = 1,
                    MaGiaoDichNganHang = "MB_RENT_HD8",
                    NganHangNhan = "MBBank",
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu tiền thuê sự kiện HĐ8"
                },

                // HĐ 9: Thu cọc ban đầu (sau đó khách hủy sẽ hoàn)
                new PhieuThu
                {
                    MaHopDong = hd9.MaHopDong,
                    LoaiPhieu = 1,
                    SoTien = 5000000m,
                    NgayGiaoDich = now.AddDays(-15),
                    HinhThucThanhToan = 0,
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu cọc HĐ9 trước khi khách yêu cầu hủy"
                },

                // HĐ 10: Thu cọc + Thu tiền thuê
                new PhieuThu
                {
                    MaHopDong = hd10.MaHopDong,
                    LoaiPhieu = 1,
                    SoTien = 15000000m,
                    NgayGiaoDich = now.AddMonths(-1),
                    HinhThucThanhToan = 1,
                    MaGiaoDichNganHang = "VCB_DEP_HD10",
                    NganHangNhan = "Vietcombank",
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu cọc hợp đồng HD10 tháng trước"
                },
                new PhieuThu
                {
                    MaHopDong = hd10.MaHopDong,
                    MaKyHan = kHd10.MaKyHan,
                    LoaiPhieu = 0,
                    SoTien = 12500000m,
                    NgayGiaoDich = now.AddMonths(-1),
                    HinhThucThanhToan = 1,
                    MaGiaoDichNganHang = "VCB_RENT_HD10",
                    NganHangNhan = "Vietcombank",
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu tiền thuê HĐ10 tháng trước"
                },

                // HĐ 11: Thu cọc + Thu tiền thuê
                new PhieuThu
                {
                    MaHopDong = hd11.MaHopDong,
                    LoaiPhieu = 1,
                    SoTien = 8000000m,
                    NgayGiaoDich = now.AddMonths(-2),
                    HinhThucThanhToan = 1,
                    MaGiaoDichNganHang = "BIDV_DEP_HD11",
                    NganHangNhan = "BIDV",
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu cọc HĐ11 2 tháng trước"
                },
                new PhieuThu
                {
                    MaHopDong = hd11.MaHopDong,
                    MaKyHan = kHd11.MaKyHan,
                    LoaiPhieu = 0,
                    SoTien = 8000000m,
                    NgayGiaoDich = now.AddMonths(-2),
                    HinhThucThanhToan = 1,
                    MaGiaoDichNganHang = "BIDV_RENT_HD11",
                    NganHangNhan = "BIDV",
                    MaNhanVienThu = uKinhDoanh.MaNguoiDung,
                    GhiChu = "Thu tiền thuê HĐ11 2 tháng trước"
                }
            };
            context.PhieuThus.AddRange(phieuThus);

            // Phiếu chi (PhieuChi) - Chi hoàn tiền cọc
            var phieuChis = new List<PhieuChi>
            {
                // Hoàn cọc HĐ 8
                new PhieuChi
                {
                    MaHopDong = hd8.MaHopDong,
                    LoaiChi = 0, // 0: Hoàn tiền cọc
                    SoTien = 15000000m,
                    NgayChi = now.AddDays(-4),
                    HinhThucChi = 1, // Chuyển khoản
                    MaNhanVienChi = uAdmin.MaNguoiDung,
                    MaGiaoDichNganHang = "MB_REF_HD8",
                    GhiChu = "Chi hoàn trả 100% tiền cọc hợp đồng HD8 cho Cty Phong Vũ"
                },

                // Hoàn cọc HĐ 9 (Do khách hủy đơn)
                new PhieuChi
                {
                    MaHopDong = hd9.MaHopDong,
                    LoaiChi = 0,
                    SoTien = 5000000m,
                    NgayChi = now.AddDays(-13),
                    HinhThucChi = 0, // Tiền mặt
                    MaNhanVienChi = uAdmin.MaNguoiDung,
                    GhiChu = "Chi hoàn tiền cọc do khách hủy hợp đồng HD9 hợp lệ trước ngày giao"
                },

                // Hoàn cọc HĐ 10
                new PhieuChi
                {
                    MaHopDong = hd10.MaHopDong,
                    LoaiChi = 0,
                    SoTien = 15000000m,
                    NgayChi = now.AddMonths(-1).AddDays(26),
                    HinhThucChi = 1,
                    MaNhanVienChi = uAdmin.MaNguoiDung,
                    MaGiaoDichNganHang = "VCB_REF_HD10",
                    GhiChu = "Chi hoàn tiền cọc HĐ10 tháng trước"
                },

                // Hoàn cọc HĐ 11
                new PhieuChi
                {
                    MaHopDong = hd11.MaHopDong,
                    LoaiChi = 0,
                    SoTien = 8000000m,
                    NgayChi = now.AddMonths(-2).AddDays(21),
                    HinhThucChi = 1,
                    MaNhanVienChi = uAdmin.MaNguoiDung,
                    MaGiaoDichNganHang = "BIDV_REF_HD11",
                    GhiChu = "Chi hoàn cọc HĐ11 2 tháng trước"
                }
            };
            context.PhieuChis.AddRange(phieuChis);
            context.SaveChanges();

            // ==========================================
            // 8. BẢO TRÌ & SỰ CỐ (PhieuBaoTri)
            // ==========================================
            var pb1 = new PhieuBaoTri
            {
                MaHopDong = hd6.MaHopDong,
                MaThietBi = tb9.MaThietBi, // THINKPAD-T14-002
                MaKyThuatVien = uKyThuat1.MaNguoiDung, // Lê Anh Tuấn
                MoTaLoi = "Khách hàng sơ ý làm rơi từ bàn làm việc, nứt vỡ vỏ mặt lưng A và cấn mẻ viền màn hình LCD.",
                NgayBaoLoi = now.AddDays(-6),
                GhiChuSuaChua = "Kỹ thuật Tuấn đã tiếp nhận máy, đặt vỏ mặt A chính hãng thay thế, kiểm tra màn hình không đứt cáp.",
                PhiDenBu = 1500000m, // Khách hàng chịu phí bồi thường
                ChiPhiSuaChua = 1200000m,
                TrangThai = 2, // 2: Đang sửa chữa
                LoaiTrachNhiem = 1, // Khách hàng
                NguyenNhan = "Tác động va đập vật lý do người sử dụng không cẩn thận",
                LinhKienThayThe = "Vỏ mặt lưng A ThinkPad T14 Gen 3 + Viền Bezel màn hình",
                DaGhiNhanCongNo = false,
                MucDoKhanCap = 2, // Khẩn cấp (12h)
                HanHoanThanh = now.AddDays(1),
                TamDungTinhTien = true,
                NgayBatDauBaoTri = now.AddDays(-6).Date,
                NgayKetThucBaoTri = now.AddDays(-2).Date,
                SoNgayTamDung = 4,
                TienGiamTru = 640000m,
                DaTruTien = true
            };

            var pb2 = new PhieuBaoTri
            {
                MaHopDong = null, // Bảo dưỡng tồn kho định kỳ
                MaThietBi = tb16.MaThietBi, // DK-15HP-003
                MaKyThuatVien = uKyThuat2.MaNguoiDung, // Phạm Hoàng Minh
                MoTaLoi = "Bảo dưỡng định kỳ quý dàn lạnh điều hòa Daikin tồn kho: vệ sinh lưới lọc, xịt rửa dàn tản nhiệt, nạp bổ sung gas R-32.",
                NgayBaoLoi = now.AddDays(-3),
                GhiChuSuaChua = "Đang tiến hành xịt rửa dàn lạnh, chuẩn bị đo đồng hồ áp suất nạp gas.",
                PhiDenBu = 0m,
                ChiPhiSuaChua = 350000m,
                TrangThai = 2, // 2: Đang sửa chữa/bảo dưỡng
                LoaiTrachNhiem = 2, // Công ty / Cửa hàng chịu
                NguyenNhan = "Bảo trì định kỳ máy tồn kho đảm bảo sẵn sàng cho đợt thuê mới",
                LinhKienThayThe = "Gas làm lạnh R-32 (0.4kg) + Dung dịch tẩy rửa dàn nhôm",
                MucDoKhanCap = 1, // Tiêu chuẩn
                HanHoanThanh = now.AddDays(2)
            };

            var pb3 = new PhieuBaoTri
            {
                MaHopDong = null,
                MaThietBi = tb24.MaThietBi, // CANON-G3020-003
                MaKyThuatVien = uKyThuat1.MaNguoiDung,
                MoTaLoi = "Vệ sinh hệ thống cấp mực và thông tắc đầu phun máy in màu Canon PIXMA",
                NgayBaoLoi = now.AddDays(-10),
                GhiChuSuaChua = "Đã ngâm dung dịch tẩy rửa đầu phun, test in 4 màu chuẩn 100%, bàn giao lại kho sẵn sàng cho thuê.",
                PhiDenBu = 0m,
                ChiPhiSuaChua = 200000m,
                TrangThai = 5, // 5: Đã nghiệm thu & Đóng phiếu
                LoaiTrachNhiem = 2,
                NguyenNhan = "Mực khô nghẽn đầu phun do để kho lâu ngày không in",
                LinhKienThayThe = "Dung dịch ngâm rửa chuyên dụng Canon",
                DaNghiemThu = true,
                NgayHoanThanh = now.AddDays(-8),
                NgayNghiemThu = now.AddDays(-8),
                DanhGiaSao = 5,
                YKienPhanHoi = "Máy in phục hồi xuất sắc, bản in sắc nét không lem"
            };

            context.PhieuBaoTris.AddRange(pb1, pb2, pb3);
            context.SaveChanges();

            // ==========================================
            // 9. BIÊN BẢN BÀN GIAO (BienBanBanGiao)
            // ==========================================
            var bienBans = new List<BienBanBanGiao>
            {
                // Biên bản xuất kho HĐ 2
                new BienBanBanGiao
                {
                    MaHopDong = hd2.MaHopDong,
                    LoaiBienBan = 0, // 0: Bàn giao xuất kho
                    NgayLap = now.AddDays(-5),
                    MaNhanVienLap = uKyThuat1.MaNguoiDung,
                    PhuKienKemTheo = "1 Thân máy PC Dell, 1 Màn hình 24 inch FHD, 1 Bàn phím Dell, 1 Chuột có dây, 1 Cáp DisplayPort, 2 Dây nguồn",
                    TinhTrangNgoaiQuan = "Máy mới 99%, thân vỏ không trầy xước, màn hình sáng đều không điểm chết, tem bảo đảm nguyên vẹn",
                    HinhAnh1 = "/uploads/bienban/bb_hd2_img1.jpg",
                    ChuKyXacNhan = "/uploads/signatures/kh_sig.png",
                    GhiChu = "Đã hướng dẫn khách sử dụng và test kiểm tra hệ điều hành Windows 11 Pro."
                },

                // Biên bản xuất kho HĐ 3
                new BienBanBanGiao
                {
                    MaHopDong = hd3.MaHopDong,
                    LoaiBienBan = 0,
                    NgayLap = now.AddDays(-60),
                    MaNhanVienLap = uKyThuat1.MaNguoiDung,
                    PhuKienKemTheo = "2 Bộ PC (Dell + HP), 1 Máy lạnh Daikin 1.5HP kèm ống đồng 5m và remote chính hãng",
                    TinhTrangNgoaiQuan = "Tất cả thiết bị hoạt động hoàn hảo, máy lạnh làm lạnh nhanh, tem niêm phong đầy đủ",
                    HinhAnh1 = "/uploads/bienban/bb_hd3_img1.jpg",
                    ChuKyXacNhan = "/uploads/signatures/kh_sig.png",
                    GhiChu = "Kỹ thuật đã lắp đặt cố định máy lạnh tại văn phòng dự án của khách."
                },

                // Biên bản xuất kho HĐ 4
                new BienBanBanGiao
                {
                    MaHopDong = hd4.MaHopDong,
                    LoaiBienBan = 0,
                    NgayLap = now.AddDays(-110),
                    MaNhanVienLap = uKyThuat2.MaNguoiDung,
                    PhuKienKemTheo = "1 Laptop ThinkPad T14 kèm củ sạc Type-C 65W, 1 Máy in màu Canon kèm cáp USB & dây nguồn",
                    TinhTrangNgoaiQuan = "Laptop vỏ nhung đẹp không cấn móp, máy in mực đầy 4 bình, in test màu tốt",
                    HinhAnh1 = "/uploads/bienban/bb_hd4_img1.jpg",
                    ChuKyXacNhan = "/uploads/signatures/kh_sig.png",
                    GhiChu = "Khách hàng nhận máy tại quầy giao dịch."
                },

                // Biên bản xuất kho HĐ 7
                new BienBanBanGiao
                {
                    MaHopDong = hd7.MaHopDong,
                    LoaiBienBan = 0,
                    NgayLap = now.AddDays(-35),
                    MaNhanVienLap = uKyThuat2.MaNguoiDung,
                    PhuKienKemTheo = "1 Bộ PC Dell OptiPlex, Màn hình 24 inch, Phím chuột, Dây nguồn",
                    TinhTrangNgoaiQuan = "Máy hoạt động tốt, ngoại quan 99%",
                    HinhAnh1 = "/uploads/bienban/bb_hd7_img1.jpg",
                    ChuKyXacNhan = "/uploads/signatures/kh_sig.png",
                    GhiChu = "Xuất kho bàn giao cho khách thuê."
                },

                // Biên bản thu hồi nhập kho HĐ 7 (Khách trả máy chờ quyết toán)
                new BienBanBanGiao
                {
                    MaHopDong = hd7.MaHopDong,
                    LoaiBienBan = 1, // 1: Thu hồi nhập kho
                    NgayLap = now.AddDays(-5),
                    MaNhanVienLap = uKyThuat2.MaNguoiDung,
                    PhuKienKemTheo = "Đầy đủ phụ kiện như lúc xuất kho: Phím, chuột, màn hình, cáp nối",
                    TinhTrangNgoaiQuan = "Thiết bị nguyên vẹn, không cấn trầy, màn hình sáng đẹp, linh kiện không bị tráo đổi",
                    HinhAnh1 = "/uploads/bienban/bb_hd7_return.jpg",
                    ChuKyXacNhan = "/uploads/signatures/kh_sig.png",
                    GhiChu = "Khách hoàn trả máy đúng hạn, thiết bị đạt tiêu chuẩn hoàn cọc 100%."
                },

                // Biên bản xuất kho HĐ 8
                new BienBanBanGiao
                {
                    MaHopDong = hd8.MaHopDong,
                    LoaiBienBan = 0,
                    NgayLap = now.AddDays(-20),
                    MaNhanVienLap = uKyThuat1.MaNguoiDung,
                    PhuKienKemTheo = "Máy lạnh Daikin và phụ kiện ống gas đi kèm",
                    TinhTrangNgoaiQuan = "Máy lạnh hoạt động êm, mát nhanh",
                    HinhAnh1 = "/uploads/bienban/bb_hd8_img1.jpg",
                    ChuKyXacNhan = "/uploads/signatures/kh_sig.png",
                    GhiChu = "Bàn giao sự kiện"
                },

                // Biên bản thu hồi nhập kho HĐ 8 (Đã hoàn tất chu kỳ)
                new BienBanBanGiao
                {
                    MaHopDong = hd8.MaHopDong,
                    LoaiBienBan = 1,
                    NgayLap = now.AddDays(-5),
                    MaNhanVienLap = uKyThuat1.MaNguoiDung,
                    PhuKienKemTheo = "Đầy đủ phụ kiện",
                    TinhTrangNgoaiQuan = "Tình trạng tốt, đã vệ sinh thu hồi về kho",
                    HinhAnh1 = "/uploads/bienban/bb_hd8_return.jpg",
                    ChuKyXacNhan = "/uploads/signatures/kh_sig.png",
                    GhiChu = "Thu hồi sự kiện hoàn tất"
                }
            };
            context.BienBanBanGiaos.AddRange(bienBans);
            context.SaveChanges();

            // ==========================================
            // 10. YÊU CẦU GIA HẠN HỢP ĐỒNG (YeuCauGiaHan)
            // ==========================================
            var yc1 = new YeuCauGiaHan
            {
                MaHopDong = hd5.MaHopDong,
                SoNgayGiaHan = 30,
                LyDo = "Dự án CNTT của đối tác kéo dài thêm 1 tháng, công ty đề xuất gia hạn thêm 30 ngày thuê.",
                NgayYeuCau = now.AddDays(-2),
                TrangThai = 0, // 0: Chờ duyệt
                ChiPhiPhatSinh = 8100000m,
                GhiChuAdmin = "Đang chờ Giám đốc kinh doanh xét duyệt hạn mức chiết khấu"
            };

            var yc2 = new YeuCauGiaHan
            {
                MaHopDong = hd3.MaHopDong,
                SoNgayGiaHan = 15,
                LyDo = "Cần thêm thiết bị cho giai đoạn nghiệm thu dự án chuyển đổi số",
                NgayYeuCau = now.AddDays(-12),
                TrangThai = 1, // 1: Đã duyệt
                NgayDuyet = now.AddDays(-10),
                MaNguoiDuyet = uAdmin.MaNguoiDung,
                ChiPhiPhatSinh = 3500000m,
                GhiChuAdmin = "Đã phê duyệt gia hạn 15 ngày theo chính sách khách hàng doanh nghiệp thân thiết."
            };

            context.YeuCauGiaHans.AddRange(yc1, yc2);
            context.SaveChanges();

            // ==========================================
            // 11. PHÂN CÔNG CÔNG VIỆC NỘI BỘ (PhanCongCongViec)
            // ==========================================
            var tasks = new List<PhanCongCongViec>
            {
                // Task 1: Giao máy HĐ2 cho KTV Lê Anh Tuấn (Hoàn thành)
                new PhanCongCongViec
                {
                    MaNhanVien = uKyThuat1.MaNguoiDung,
                    MaNguoiGiao = uKinhDoanh.MaNguoiDung,
                    MaHopDong = hd2.MaHopDong,
                    TieuDe = "Bàn giao và lắp đặt máy tính PC Dell cho khách hàng Nguyễn Văn An",
                    NoiDung = "Mang máy DELL-OPT-001 đến địa chỉ 123 Nguyễn Trãi, Q.1. Hướng dẫn khách kiểm tra tem và test màn hình, ký biên bản bàn giao.",
                    TrangThai = 2, // 2: Hoàn thành
                    NgayGiao = now.AddDays(-5),
                    HanHoanThanh = now.AddDays(-5),
                    NgayHoanThanh = now.AddDays(-5),
                    GhiChuTienDo = "Đã bàn giao lắp đặt hoàn tất, khách đã test máy chạy tốt và ký biên bản xuất kho."
                },

                // Task 2: Sửa chữa máy rơi vỡ HĐ6 cho KTV Lê Anh Tuấn (Đang làm)
                new PhanCongCongViec
                {
                    MaNhanVien = uKyThuat1.MaNguoiDung,
                    MaNguoiGiao = uAdmin.MaNguoiDung,
                    MaHopDong = hd6.MaHopDong,
                    MaPhieuBaoTri = pb1.MaPhieu,
                    TieuDe = "Xử lý sự cố rơi vỡ vỏ laptop ThinkPad T14 cho HĐ 6",
                    NoiDung = "Thay thế vỏ lưng mặt A và kiểm tra viền màn hình LCD máy THINKPAD-T14-002 của khách Phan Minh Quân.",
                    TrangThai = 1, // 1: Đang thực hiện
                    NgayGiao = now.AddDays(-5),
                    HanHoanThanh = now.AddDays(1),
                    GhiChuTienDo = "Đã nhận linh kiện vỏ mới từ nhà cung cấp, đang tháo lắp và chạy test áp lực màn hình."
                },

                // Task 3: Bảo dưỡng kho định kỳ cho KTV Phạm Hoàng Minh (Đang làm)
                new PhanCongCongViec
                {
                    MaNhanVien = uKyThuat2.MaNguoiDung,
                    MaNguoiGiao = uAdmin.MaNguoiDung,
                    MaPhieuBaoTri = pb2.MaPhieu,
                    TieuDe = "Bảo dưỡng định kỳ dàn lạnh Daikin 1.5HP trong kho",
                    NoiDung = "Thực hiện vệ sinh công nghiệp, xịt rửa dàn lạnh, đo áp suất gas R-32 máy DK-15HP-003 trong kho thiết bị.",
                    TrangThai = 1, // 1: Đang thực hiện
                    NgayGiao = now.AddDays(-2),
                    HanHoanThanh = now.AddDays(2),
                    GhiChuTienDo = "Đã rửa sạch lưới lọc và dàn nhôm tản nhiệt, chuẩn bị nạp bổ sung gas chiều nay."
                },

                // Task 4: Thu hồi kiểm tra máy HĐ7 cho KTV Phạm Hoàng Minh (Hoàn thành)
                new PhanCongCongViec
                {
                    MaNhanVien = uKyThuat2.MaNguoiDung,
                    MaNguoiGiao = uKinhDoanh.MaNguoiDung,
                    MaHopDong = hd7.MaHopDong,
                    TieuDe = "Kiểm tra kỹ thuật và tiếp nhận thiết bị hoàn trả từ khách hàng Nguyễn Văn An",
                    NoiDung = "Khách hoàn trả máy sau khi kết thúc chu kỳ thuê HĐ 7. Kiểm tra ngoại quan, linh kiện, phụ kiện và lập biên bản thu hồi nhập kho.",
                    TrangThai = 2, // 2: Hoàn thành
                    NgayGiao = now.AddDays(-2),
                    HanHoanThanh = now.AddDays(-1),
                    NgayHoanThanh = now.AddDays(-1),
                    GhiChuTienDo = "Máy bình thường, không trầy xước, đầy đủ phụ kiện. Đã lập biên bản thu hồi nhập kho."
                },

                // Task 5: Đôn đốc công nợ cho NVKD Trần Thùy Linh (Mới)
                new PhanCongCongViec
                {
                    MaNhanVien = uKinhDoanh.MaNguoiDung,
                    MaNguoiGiao = uAdmin.MaNguoiDung,
                    MaHopDong = hd4.MaHopDong,
                    TieuDe = "Đôn đốc và hỗ trợ khách hàng Nguyễn Văn An tất toán công nợ các kỳ hạn quá hạn",
                    NoiDung = "Liên hệ khách qua điện thoại 0987654321 thông báo tình trạng quá hạn nợ của hợp đồng HD" + hd4.MaHopDong + ", gửi thông tin VietQR để khách chuyển khoản thanh toán.",
                    TrangThai = 0, // 0: Mới
                    NgayGiao = now.AddDays(-1),
                    HanHoanThanh = now.AddDays(2),
                    GhiChuTienDo = "Đã lên danh sách gọi điện đôn đốc trong ca sáng."
                }
            };
            context.PhanCongCongViecs.AddRange(tasks);
            context.SaveChanges();

            // ==========================================
            // 12. LỊCH SỬ THIẾT BỊ (LichSuThietBi)
            // ==========================================
            var lichSus = new List<LichSuThietBi>
            {
                new LichSuThietBi
                {
                    MaThietBi = tb1.MaThietBi,
                    HanhDong = "Nhập kho ban đầu",
                    ThoiGian = now.AddMonths(-3),
                    MaNguoiThucHien = uAdmin.MaNguoiDung,
                    GhiChu = "Nhập kho thiết bị mới 100% nguyên đai nguyên kiện"
                },
                new LichSuThietBi
                {
                    MaThietBi = tb1.MaThietBi,
                    HanhDong = "Bàn giao xuất kho cho thuê",
                    ThoiGian = now.AddDays(-5),
                    MaNguoiThucHien = uKyThuat1.MaNguoiDung,
                    GhiChu = "Xuất kho bàn giao theo hợp đồng HD" + hd2.MaHopDong + " cho khách Nguyễn Văn An"
                },

                new LichSuThietBi
                {
                    MaThietBi = tb2.MaThietBi,
                    HanhDong = "Nhập kho ban đầu",
                    ThoiGian = now.AddMonths(-3),
                    MaNguoiThucHien = uAdmin.MaNguoiDung,
                    GhiChu = "Nhập lô máy tính văn phòng Dell OptiPlex"
                },
                new LichSuThietBi
                {
                    MaThietBi = tb2.MaThietBi,
                    HanhDong = "Bàn giao xuất kho cho doanh nghiệp",
                    ThoiGian = now.AddDays(-60),
                    MaNguoiThucHien = uKyThuat1.MaNguoiDung,
                    GhiChu = "Bàn giao theo hợp đồng HD" + hd3.MaHopDong + " cho Công ty Phong Vũ"
                },

                new LichSuThietBi
                {
                    MaThietBi = tb9.MaThietBi,
                    HanhDong = "Nhập kho ban đầu",
                    ThoiGian = now.AddMonths(-2),
                    MaNguoiThucHien = uAdmin.MaNguoiDung,
                    GhiChu = "Nhập laptop Lenovo ThinkPad T14 Gen 3"
                },
                new LichSuThietBi
                {
                    MaThietBi = tb9.MaThietBi,
                    HanhDong = "Bàn giao cho thuê",
                    ThoiGian = now.AddDays(-20),
                    MaNguoiThucHien = uKyThuat1.MaNguoiDung,
                    GhiChu = "Bàn giao theo hợp đồng HD" + hd6.MaHopDong + " cho khách Phan Minh Quân"
                },
                new LichSuThietBi
                {
                    MaThietBi = tb9.MaThietBi,
                    HanhDong = "Tiếp nhận bảo trì sự cố",
                    ThoiGian = now.AddDays(-6),
                    MaNguoiThucHien = uKyThuat1.MaNguoiDung,
                    GhiChu = "Khách làm rơi nứt vỡ vỏ, tiếp nhận sửa chữa theo Phiếu bảo trì #" + pb1.MaPhieu
                },

                new LichSuThietBi
                {
                    MaThietBi = tb16.MaThietBi,
                    HanhDong = "Đưa vào bảo dưỡng kho định kỳ",
                    ThoiGian = now.AddDays(-3),
                    MaNguoiThucHien = uKyThuat2.MaNguoiDung,
                    GhiChu = "Bảo dưỡng xịt rửa dàn lạnh, nạp gas R-32"
                },

                new LichSuThietBi
                {
                    MaThietBi = tb21.MaThietBi,
                    HanhDong = "Kiểm tra kỹ thuật & Đề xuất thanh lý",
                    ThoiGian = now.AddDays(-15),
                    MaNguoiThucHien = uKyThuat2.MaNguoiDung,
                    GhiChu = "Máy in HP M404 cháy cuộn sấy và hỏng bo mạch, chuyển trạng thái 4 chờ thanh lý linh kiện"
                }
            };
            context.LichSuThietBis.AddRange(lichSus);

            // ==========================================
            // 13. LỊCH SỬ NHẮC NỢ (LichSuNhacNo)
            // ==========================================
            var nhacNos = new List<LichSuNhacNo>
            {
                new LichSuNhacNo
                {
                    MaHopDong = hd4.MaHopDong,
                    MaKyHan = kHd4_1.MaKyHan,
                    NgayNhac = now.AddDays(-80),
                    HinhThucNhac = "SMS",
                    NoiDung = "RentalSystem nhắc quý khách: Kỳ 1 HĐ" + hd4.MaHopDong + " còn thiếu 2.200.000 VNĐ đã quá hạn. Vui lòng thanh toán sớm.",
                    NguoiGuiId = uKinhDoanh.MaNguoiDung,
                    SoTienNhac = 2200000m,
                    LanNhacThu = 1
                },
                new LichSuNhacNo
                {
                    MaHopDong = hd4.MaHopDong,
                    MaKyHan = kHd4_2.MaKyHan,
                    NgayNhac = now.AddDays(-50),
                    HinhThucNhac = "Email",
                    NoiDung = "Thông báo quá hạn thanh toán kỳ 2 hợp đồng thuê HD" + hd4.MaHopDong + " số tiền 7.200.000 VNĐ.",
                    NguoiGuiId = uKinhDoanh.MaNguoiDung,
                    SoTienNhac = 7200000m,
                    LanNhacThu = 2
                },
                new LichSuNhacNo
                {
                    MaHopDong = hd4.MaHopDong,
                    MaKyHan = kHd4_4.MaKyHan,
                    NgayNhac = now.AddDays(-2),
                    HinhThucNhac = "Thông báo hệ thống",
                    NoiDung = "Cảnh báo nợ quá hạn kỳ 4 hợp đồng HD" + hd4.MaHopDong + ". Tài khoản có nguy cơ bị khóa tính năng thuê mới nếu không thanh toán.",
                    NguoiGuiId = uAdmin.MaNguoiDung,
                    SoTienNhac = 7344000m, // Kèm tiền phạt
                    LanNhacThu = 3
                }
            };
            context.LichSuNhacNos.AddRange(nhacNos);

            // ==========================================
            // 14. THÔNG BÁO HỆ THỐNG (ThongBao)
            // ==========================================
            var thongBaos = new List<ThongBao>
            {
                new ThongBao
                {
                    MaNguoiDung = uKhach1.MaNguoiDung,
                    TieuDe = "Hợp đồng HD" + hd2.MaHopDong + " đã được kích hoạt thành công",
                    NoiDung = "Hợp đồng thuê máy tính Dell OptiPlex 7010 của bạn đã có hiệu lực. Kỹ thuật viên sẽ liên hệ bàn giao đúng hẹn.",
                    NgayTao = now.AddDays(-5),
                    DaDoc = true,
                    LoaiThongBao = "HopDong",
                    LienKet = "/Cart/MyContracts"
                },
                new ThongBao
                {
                    MaNguoiDung = uKhach1.MaNguoiDung,
                    TieuDe = "Cảnh báo quá hạn thanh toán hợp đồng HD" + hd4.MaHopDong,
                    NoiDung = "Bạn đang có các kỳ hạn thanh toán trễ hạn tại hợp đồng HD" + hd4.MaHopDong + ". Vui lòng vào Sổ công nợ để thanh toán.",
                    NgayTao = now.AddDays(-2),
                    DaDoc = false,
                    LoaiThongBao = "ThanhToan",
                    LienKet = "/Account/MyDebt"
                },
                new ThongBao
                {
                    MaNguoiDung = uKhach2.MaNguoiDung,
                    TieuDe = "Tiếp nhận phiếu bảo trì sự cố #" + pb1.MaPhieu,
                    NoiDung = "Phiếu bảo trì máy ThinkPad T14 của quý khách đã được kỹ thuật viên Lê Anh Tuấn tiếp nhận xử lý.",
                    NgayTao = now.AddDays(-6),
                    DaDoc = true,
                    LoaiThongBao = "BaoTri",
                    LienKet = "/BaoTri/ChiTiet/" + pb1.MaPhieu
                },
                new ThongBao
                {
                    MaNguoiDung = uKinhDoanh.MaNguoiDung,
                    TieuDe = "Yêu cầu gia hạn mới từ Công ty Phong Vũ",
                    NoiDung = "Hợp đồng HD" + hd5.MaHopDong + " có yêu cầu gia hạn thêm 30 ngày cần xem xét và phê duyệt.",
                    NgayTao = now.AddDays(-2),
                    DaDoc = false,
                    LoaiThongBao = "GiaHan",
                    LienKet = "/Admin/HopDong/YeuCauGiaHan"
                },
                new ThongBao
                {
                    MaNguoiDung = uKyThuat1.MaNguoiDung,
                    TieuDe = "Nhiệm vụ mới: Sửa chữa máy laptop ThinkPad T14",
                    NoiDung = "Bạn được phân công sửa chữa thay thế vỏ máy theo Phiếu bảo trì #" + pb1.MaPhieu + ".",
                    NgayTao = now.AddDays(-5),
                    DaDoc = true,
                    LoaiThongBao = "PhanCong",
                    LienKet = "/Admin/PhanCong/MyTasks"
                },
                new ThongBao
                {
                    MaNguoiDung = uAdmin.MaNguoiDung,
                    TieuDe = "Quyết toán hoàn tất hợp đồng HD" + hd8.MaHopDong,
                    NoiDung = "Hợp đồng HD" + hd8.MaHopDong + " của Công ty Phong Vũ đã hoàn tất thu hồi và chi hoàn cọc thành công.",
                    NgayTao = now.AddDays(-4),
                    DaDoc = true,
                    LoaiThongBao = "QuyetToan",
                    LienKet = "/Admin/HopDong/Details/" + hd8.MaHopDong
                }
            };
            context.ThongBaos.AddRange(thongBaos);
            context.SaveChanges();
        }
    }
}
