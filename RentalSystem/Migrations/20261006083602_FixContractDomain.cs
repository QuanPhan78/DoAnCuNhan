using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace RentalSystem.Migrations
{
    /// <inheritdoc />
    public partial class FixContractDomain : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "HinhAnhBienLai",
                table: "KyHanThanhToans",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "MaGiaoDichChuyenKhoan",
                table: "KyHanThanhToans",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "NgayGuiBienLai",
                table: "KyHanThanhToans",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "TrangThaiXacNhan",
                table: "KyHanThanhToans",
                type: "int",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<string>(
                name: "AnhCCCD_Sau",
                table: "HopDongs",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "AnhCCCD_Truoc",
                table: "HopDongs",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "GhiChuHoanCoc",
                table: "HopDongs",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "HanChotKy",
                table: "HopDongs",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "LyDoGiaHan",
                table: "HopDongs",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "LyDoHuy",
                table: "HopDongs",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "NgayHoanCoc",
                table: "HopDongs",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "NgayYeuCauHuy",
                table: "HopDongs",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "SoNgayGiaHan",
                table: "HopDongs",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<decimal>(
                name: "TienCocThucHoan",
                table: "HopDongs",
                type: "decimal(18,2)",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "TrangThaiGiaHan",
                table: "HopDongs",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "TrangThaiHoanCoc",
                table: "HopDongs",
                type: "int",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<bool>(
                name: "YeuCauGiaHan",
                table: "HopDongs",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<bool>(
                name: "YeuCauHuy",
                table: "HopDongs",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.CreateTable(
                name: "BienBanBanGiaos",
                columns: table => new
                {
                    MaBienBan = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaHopDong = table.Column<int>(type: "int", nullable: false),
                    LoaiBienBan = table.Column<int>(type: "int", nullable: false),
                    NgayLap = table.Column<DateTime>(type: "datetime2", nullable: false),
                    MaNhanVienLap = table.Column<int>(type: "int", nullable: false),
                    PhuKienKemTheo = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    TinhTrangNgoaiQuan = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    HinhAnh1 = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    HinhAnh2 = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    HinhAnh3 = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    HinhAnh4 = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ChuKyXacNhan = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    GhiChu = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_BienBanBanGiaos", x => x.MaBienBan);
                    table.ForeignKey(
                        name: "FK_BienBanBanGiaos_HopDongs_MaHopDong",
                        column: x => x.MaHopDong,
                        principalTable: "HopDongs",
                        principalColumn: "MaHopDong",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_BienBanBanGiaos_NguoiDungs_MaNhanVienLap",
                        column: x => x.MaNhanVienLap,
                        principalTable: "NguoiDungs",
                        principalColumn: "MaNguoiDung",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "PhieuChis",
                columns: table => new
                {
                    MaPhieuChi = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaHopDong = table.Column<int>(type: "int", nullable: false),
                    LoaiChi = table.Column<int>(type: "int", nullable: false),
                    SoTien = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    NgayChi = table.Column<DateTime>(type: "datetime2", nullable: false),
                    HinhThucChi = table.Column<int>(type: "int", nullable: false),
                    MaNhanVienChi = table.Column<int>(type: "int", nullable: false),
                    MaGiaoDichNganHang = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    GhiChu = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_PhieuChis", x => x.MaPhieuChi);
                    table.ForeignKey(
                        name: "FK_PhieuChis_HopDongs_MaHopDong",
                        column: x => x.MaHopDong,
                        principalTable: "HopDongs",
                        principalColumn: "MaHopDong",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_PhieuChis_NguoiDungs_MaNhanVienChi",
                        column: x => x.MaNhanVienChi,
                        principalTable: "NguoiDungs",
                        principalColumn: "MaNguoiDung",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_BienBanBanGiaos_MaHopDong",
                table: "BienBanBanGiaos",
                column: "MaHopDong");

            migrationBuilder.CreateIndex(
                name: "IX_BienBanBanGiaos_MaNhanVienLap",
                table: "BienBanBanGiaos",
                column: "MaNhanVienLap");

            migrationBuilder.CreateIndex(
                name: "IX_PhieuChis_MaHopDong",
                table: "PhieuChis",
                column: "MaHopDong");

            migrationBuilder.CreateIndex(
                name: "IX_PhieuChis_MaNhanVienChi",
                table: "PhieuChis",
                column: "MaNhanVienChi");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "BienBanBanGiaos");

            migrationBuilder.DropTable(
                name: "PhieuChis");

            migrationBuilder.DropColumn(
                name: "HinhAnhBienLai",
                table: "KyHanThanhToans");

            migrationBuilder.DropColumn(
                name: "MaGiaoDichChuyenKhoan",
                table: "KyHanThanhToans");

            migrationBuilder.DropColumn(
                name: "NgayGuiBienLai",
                table: "KyHanThanhToans");

            migrationBuilder.DropColumn(
                name: "TrangThaiXacNhan",
                table: "KyHanThanhToans");

            migrationBuilder.DropColumn(
                name: "AnhCCCD_Sau",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "AnhCCCD_Truoc",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "GhiChuHoanCoc",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "HanChotKy",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "LyDoGiaHan",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "LyDoHuy",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "NgayHoanCoc",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "NgayYeuCauHuy",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "SoNgayGiaHan",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "TienCocThucHoan",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "TrangThaiGiaHan",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "TrangThaiHoanCoc",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "YeuCauGiaHan",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "YeuCauHuy",
                table: "HopDongs");
        }
    }
}
