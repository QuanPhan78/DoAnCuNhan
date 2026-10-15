using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace RentalSystem.Migrations
{
    /// <inheritdoc />
    public partial class FixMaintenanceDomain : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_PhieuBaoTris_HopDongs_MaHopDong",
                table: "PhieuBaoTris");

            migrationBuilder.AlterColumn<int>(
                name: "MaHopDong",
                table: "PhieuBaoTris",
                type: "int",
                nullable: true,
                oldClrType: typeof(int),
                oldType: "int");

            migrationBuilder.AddColumn<decimal>(
                name: "ChiPhiSuaChua",
                table: "PhieuBaoTris",
                type: "decimal(18,2)",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "DaGhiNhanCongNo",
                table: "PhieuBaoTris",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<bool>(
                name: "DaNghiemThu",
                table: "PhieuBaoTris",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<bool>(
                name: "DaTruTien",
                table: "PhieuBaoTris",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<DateTime>(
                name: "HanHoanThanh",
                table: "PhieuBaoTris",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "HinhAnhLoi",
                table: "PhieuBaoTris",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "LinhKienThayThe",
                table: "PhieuBaoTris",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "LoaiTrachNhiem",
                table: "PhieuBaoTris",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "MucDoKhanCap",
                table: "PhieuBaoTris",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "NgayBatDauBaoTri",
                table: "PhieuBaoTris",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "NgayHoanThanh",
                table: "PhieuBaoTris",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "NgayKetThucBaoTri",
                table: "PhieuBaoTris",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "NgayNghiemThu",
                table: "PhieuBaoTris",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "NguyenNhan",
                table: "PhieuBaoTris",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "SoNgayTamDung",
                table: "PhieuBaoTris",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "TamDungTinhTien",
                table: "PhieuBaoTris",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<decimal>(
                name: "TienGiamTru",
                table: "PhieuBaoTris",
                type: "decimal(18,2)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "VideoLoi",
                table: "PhieuBaoTris",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "YKienPhanHoi",
                table: "PhieuBaoTris",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AlterColumn<int>(
                name: "MaNguoiThucHien",
                table: "LichSuThietBis",
                type: "int",
                nullable: true,
                oldClrType: typeof(int),
                oldType: "int");

            migrationBuilder.AddColumn<string>(
                name: "GhiChu",
                table: "LichSuThietBis",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<decimal>(
                name: "TienGiamTruBaoTri",
                table: "HopDongs",
                type: "decimal(18,2)",
                nullable: false,
                defaultValue: 0m);

            migrationBuilder.CreateTable(
                name: "ThongBaos",
                columns: table => new
                {
                    MaThongBao = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaNguoiDung = table.Column<int>(type: "int", nullable: false),
                    TieuDe = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: false),
                    NoiDung = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    NgayTao = table.Column<DateTime>(type: "datetime2", nullable: false),
                    DaDoc = table.Column<bool>(type: "bit", nullable: false),
                    LoaiThongBao = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    LienKet = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ThongBaos", x => x.MaThongBao);
                    table.ForeignKey(
                        name: "FK_ThongBaos_NguoiDungs_MaNguoiDung",
                        column: x => x.MaNguoiDung,
                        principalTable: "NguoiDungs",
                        principalColumn: "MaNguoiDung",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_ThongBaos_MaNguoiDung",
                table: "ThongBaos",
                column: "MaNguoiDung");

            migrationBuilder.AddForeignKey(
                name: "FK_PhieuBaoTris_HopDongs_MaHopDong",
                table: "PhieuBaoTris",
                column: "MaHopDong",
                principalTable: "HopDongs",
                principalColumn: "MaHopDong",
                onDelete: ReferentialAction.SetNull);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_PhieuBaoTris_HopDongs_MaHopDong",
                table: "PhieuBaoTris");

            migrationBuilder.DropTable(
                name: "ThongBaos");

            migrationBuilder.DropColumn(
                name: "ChiPhiSuaChua",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "DaGhiNhanCongNo",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "DaNghiemThu",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "DaTruTien",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "HanHoanThanh",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "HinhAnhLoi",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "LinhKienThayThe",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "LoaiTrachNhiem",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "MucDoKhanCap",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "NgayBatDauBaoTri",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "NgayHoanThanh",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "NgayKetThucBaoTri",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "NgayNghiemThu",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "NguyenNhan",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "SoNgayTamDung",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "TamDungTinhTien",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "TienGiamTru",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "VideoLoi",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "YKienPhanHoi",
                table: "PhieuBaoTris");

            migrationBuilder.DropColumn(
                name: "GhiChu",
                table: "LichSuThietBis");

            migrationBuilder.DropColumn(
                name: "TienGiamTruBaoTri",
                table: "HopDongs");

            migrationBuilder.AlterColumn<int>(
                name: "MaHopDong",
                table: "PhieuBaoTris",
                type: "int",
                nullable: false,
                defaultValue: 0,
                oldClrType: typeof(int),
                oldType: "int",
                oldNullable: true);

            migrationBuilder.AlterColumn<int>(
                name: "MaNguoiThucHien",
                table: "LichSuThietBis",
                type: "int",
                nullable: false,
                defaultValue: 0,
                oldClrType: typeof(int),
                oldType: "int",
                oldNullable: true);

            migrationBuilder.AddForeignKey(
                name: "FK_PhieuBaoTris_HopDongs_MaHopDong",
                table: "PhieuBaoTris",
                column: "MaHopDong",
                principalTable: "HopDongs",
                principalColumn: "MaHopDong",
                onDelete: ReferentialAction.Cascade);
        }
    }
}
