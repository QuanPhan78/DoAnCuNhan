using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace RentalSystem.Migrations
{
    /// <inheritdoc />
    public partial class InitialCreate : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "KhuyenMais",
                columns: table => new
                {
                    MaKhuyenMai = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaCode = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    PhanTramGiam = table.Column<int>(type: "int", nullable: false),
                    KichHoat = table.Column<bool>(type: "bit", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_KhuyenMais", x => x.MaKhuyenMai);
                });

            migrationBuilder.CreateTable(
                name: "LoaiThietBis",
                columns: table => new
                {
                    MaLoai = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    TenLoai = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_LoaiThietBis", x => x.MaLoai);
                });

            migrationBuilder.CreateTable(
                name: "VaiTros",
                columns: table => new
                {
                    MaVaiTro = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    TenVaiTro = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_VaiTros", x => x.MaVaiTro);
                });

            migrationBuilder.CreateTable(
                name: "SanPhams",
                columns: table => new
                {
                    MaSanPham = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaLoai = table.Column<int>(type: "int", nullable: false),
                    TenSanPham = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: false),
                    CauHinh = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    GiaThueNgay = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    TienCoc = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    HinhAnh = table.Column<string>(type: "nvarchar(max)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_SanPhams", x => x.MaSanPham);
                    table.ForeignKey(
                        name: "FK_SanPhams_LoaiThietBis_MaLoai",
                        column: x => x.MaLoai,
                        principalTable: "LoaiThietBis",
                        principalColumn: "MaLoai",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "NguoiDungs",
                columns: table => new
                {
                    MaNguoiDung = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaVaiTro = table.Column<int>(type: "int", nullable: false),
                    HoTen = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    SoDienThoai = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false),
                    Email = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    MatKhau = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    CCCD = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    DiaChi = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    TrangThai = table.Column<bool>(type: "bit", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_NguoiDungs", x => x.MaNguoiDung);
                    table.ForeignKey(
                        name: "FK_NguoiDungs_VaiTros_MaVaiTro",
                        column: x => x.MaVaiTro,
                        principalTable: "VaiTros",
                        principalColumn: "MaVaiTro",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "ThietBis",
                columns: table => new
                {
                    MaThietBi = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaSanPham = table.Column<int>(type: "int", nullable: false),
                    SoSerial = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false),
                    TinhTrangMay = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    TrangThai = table.Column<int>(type: "int", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ThietBis", x => x.MaThietBi);
                    table.ForeignKey(
                        name: "FK_ThietBis_SanPhams_MaSanPham",
                        column: x => x.MaSanPham,
                        principalTable: "SanPhams",
                        principalColumn: "MaSanPham",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "HopDongs",
                columns: table => new
                {
                    MaHopDong = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaKhachHang = table.Column<int>(type: "int", nullable: false),
                    MaNhanVien = table.Column<int>(type: "int", nullable: false),
                    MaKhuyenMai = table.Column<int>(type: "int", nullable: true),
                    NgayBatDau = table.Column<DateTime>(type: "datetime2", nullable: false),
                    NgayKetThuc = table.Column<DateTime>(type: "datetime2", nullable: false),
                    TienDaCoc = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    TongTien = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    TrangThai = table.Column<int>(type: "int", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_HopDongs", x => x.MaHopDong);
                    table.ForeignKey(
                        name: "FK_HopDongs_NguoiDungs_MaKhachHang",
                        column: x => x.MaKhachHang,
                        principalTable: "NguoiDungs",
                        principalColumn: "MaNguoiDung",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_HopDongs_NguoiDungs_MaNhanVien",
                        column: x => x.MaNhanVien,
                        principalTable: "NguoiDungs",
                        principalColumn: "MaNguoiDung",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "LichSuThietBis",
                columns: table => new
                {
                    MaLichSu = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaThietBi = table.Column<int>(type: "int", nullable: false),
                    HanhDong = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    ThoiGian = table.Column<DateTime>(type: "datetime2", nullable: false),
                    MaNguoiThucHien = table.Column<int>(type: "int", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_LichSuThietBis", x => x.MaLichSu);
                    table.ForeignKey(
                        name: "FK_LichSuThietBis_NguoiDungs_MaNguoiThucHien",
                        column: x => x.MaNguoiThucHien,
                        principalTable: "NguoiDungs",
                        principalColumn: "MaNguoiDung",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_LichSuThietBis_ThietBis_MaThietBi",
                        column: x => x.MaThietBi,
                        principalTable: "ThietBis",
                        principalColumn: "MaThietBi",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "ChiTietHopDongs",
                columns: table => new
                {
                    MaHopDong = table.Column<int>(type: "int", nullable: false),
                    MaThietBi = table.Column<int>(type: "int", nullable: false),
                    GiaChotThu = table.Column<decimal>(type: "decimal(18,2)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ChiTietHopDongs", x => new { x.MaHopDong, x.MaThietBi });
                    table.ForeignKey(
                        name: "FK_ChiTietHopDongs_HopDongs_MaHopDong",
                        column: x => x.MaHopDong,
                        principalTable: "HopDongs",
                        principalColumn: "MaHopDong",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_ChiTietHopDongs_ThietBis_MaThietBi",
                        column: x => x.MaThietBi,
                        principalTable: "ThietBis",
                        principalColumn: "MaThietBi",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "PhieuBaoTris",
                columns: table => new
                {
                    MaPhieu = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaHopDong = table.Column<int>(type: "int", nullable: false),
                    MaThietBi = table.Column<int>(type: "int", nullable: false),
                    MaKyThuatVien = table.Column<int>(type: "int", nullable: true),
                    MoTaLoi = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    NgayBaoLoi = table.Column<DateTime>(type: "datetime2", nullable: false),
                    GhiChuSuaChua = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    PhiDenBu = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    DanhGiaSao = table.Column<int>(type: "int", nullable: true),
                    TrangThai = table.Column<int>(type: "int", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_PhieuBaoTris", x => x.MaPhieu);
                    table.ForeignKey(
                        name: "FK_PhieuBaoTris_HopDongs_MaHopDong",
                        column: x => x.MaHopDong,
                        principalTable: "HopDongs",
                        principalColumn: "MaHopDong",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_PhieuBaoTris_NguoiDungs_MaKyThuatVien",
                        column: x => x.MaKyThuatVien,
                        principalTable: "NguoiDungs",
                        principalColumn: "MaNguoiDung",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_PhieuBaoTris_ThietBis_MaThietBi",
                        column: x => x.MaThietBi,
                        principalTable: "ThietBis",
                        principalColumn: "MaThietBi",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "PhieuThus",
                columns: table => new
                {
                    MaPhieuThu = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaHopDong = table.Column<int>(type: "int", nullable: false),
                    LoaiPhieu = table.Column<int>(type: "int", nullable: false),
                    SoTien = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    NgayGiaoDich = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_PhieuThus", x => x.MaPhieuThu);
                    table.ForeignKey(
                        name: "FK_PhieuThus_HopDongs_MaHopDong",
                        column: x => x.MaHopDong,
                        principalTable: "HopDongs",
                        principalColumn: "MaHopDong",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_ChiTietHopDongs_MaThietBi",
                table: "ChiTietHopDongs",
                column: "MaThietBi");

            migrationBuilder.CreateIndex(
                name: "IX_HopDongs_MaKhachHang",
                table: "HopDongs",
                column: "MaKhachHang");

            migrationBuilder.CreateIndex(
                name: "IX_HopDongs_MaNhanVien",
                table: "HopDongs",
                column: "MaNhanVien");

            migrationBuilder.CreateIndex(
                name: "IX_LichSuThietBis_MaNguoiThucHien",
                table: "LichSuThietBis",
                column: "MaNguoiThucHien");

            migrationBuilder.CreateIndex(
                name: "IX_LichSuThietBis_MaThietBi",
                table: "LichSuThietBis",
                column: "MaThietBi");

            migrationBuilder.CreateIndex(
                name: "IX_NguoiDungs_MaVaiTro",
                table: "NguoiDungs",
                column: "MaVaiTro");

            migrationBuilder.CreateIndex(
                name: "IX_PhieuBaoTris_MaHopDong",
                table: "PhieuBaoTris",
                column: "MaHopDong");

            migrationBuilder.CreateIndex(
                name: "IX_PhieuBaoTris_MaKyThuatVien",
                table: "PhieuBaoTris",
                column: "MaKyThuatVien");

            migrationBuilder.CreateIndex(
                name: "IX_PhieuBaoTris_MaThietBi",
                table: "PhieuBaoTris",
                column: "MaThietBi");

            migrationBuilder.CreateIndex(
                name: "IX_PhieuThus_MaHopDong",
                table: "PhieuThus",
                column: "MaHopDong");

            migrationBuilder.CreateIndex(
                name: "IX_SanPhams_MaLoai",
                table: "SanPhams",
                column: "MaLoai");

            migrationBuilder.CreateIndex(
                name: "IX_ThietBis_MaSanPham",
                table: "ThietBis",
                column: "MaSanPham");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "ChiTietHopDongs");

            migrationBuilder.DropTable(
                name: "KhuyenMais");

            migrationBuilder.DropTable(
                name: "LichSuThietBis");

            migrationBuilder.DropTable(
                name: "PhieuBaoTris");

            migrationBuilder.DropTable(
                name: "PhieuThus");

            migrationBuilder.DropTable(
                name: "ThietBis");

            migrationBuilder.DropTable(
                name: "HopDongs");

            migrationBuilder.DropTable(
                name: "SanPhams");

            migrationBuilder.DropTable(
                name: "NguoiDungs");

            migrationBuilder.DropTable(
                name: "LoaiThietBis");

            migrationBuilder.DropTable(
                name: "VaiTros");
        }
    }
}
