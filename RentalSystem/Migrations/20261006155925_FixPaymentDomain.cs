using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace RentalSystem.Migrations
{
    /// <inheritdoc />
    public partial class FixPaymentDomain : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<bool>(
                name: "DaHuy",
                table: "PhieuThus",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<string>(
                name: "LyDoHuy",
                table: "PhieuThus",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "MaGiaoDichNganHang",
                table: "PhieuThus",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "MaNhanVienThu",
                table: "PhieuThus",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "NganHangNhan",
                table: "PhieuThus",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "NgayHuy",
                table: "PhieuThus",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "GhiChuTraThieu",
                table: "KyHanThanhToans",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "NgayHenTraTiepTheo",
                table: "KyHanThanhToans",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<decimal>(
                name: "PhiPhatTreHan",
                table: "KyHanThanhToans",
                type: "decimal(18,2)",
                nullable: false,
                defaultValue: 0m);

            migrationBuilder.AddColumn<int>(
                name: "SoNgayTreHan",
                table: "KyHanThanhToans",
                type: "int",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<decimal>(
                name: "TienTraThua",
                table: "HopDongs",
                type: "decimal(18,2)",
                nullable: false,
                defaultValue: 0m);

            migrationBuilder.CreateIndex(
                name: "IX_PhieuThus_MaKyHan",
                table: "PhieuThus",
                column: "MaKyHan");

            migrationBuilder.CreateIndex(
                name: "IX_PhieuThus_MaNhanVienThu",
                table: "PhieuThus",
                column: "MaNhanVienThu");

            migrationBuilder.AddForeignKey(
                name: "FK_PhieuThus_KyHanThanhToans_MaKyHan",
                table: "PhieuThus",
                column: "MaKyHan",
                principalTable: "KyHanThanhToans",
                principalColumn: "MaKyHan",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_PhieuThus_NguoiDungs_MaNhanVienThu",
                table: "PhieuThus",
                column: "MaNhanVienThu",
                principalTable: "NguoiDungs",
                principalColumn: "MaNguoiDung",
                onDelete: ReferentialAction.Restrict);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_PhieuThus_KyHanThanhToans_MaKyHan",
                table: "PhieuThus");

            migrationBuilder.DropForeignKey(
                name: "FK_PhieuThus_NguoiDungs_MaNhanVienThu",
                table: "PhieuThus");

            migrationBuilder.DropIndex(
                name: "IX_PhieuThus_MaKyHan",
                table: "PhieuThus");

            migrationBuilder.DropIndex(
                name: "IX_PhieuThus_MaNhanVienThu",
                table: "PhieuThus");

            migrationBuilder.DropColumn(
                name: "DaHuy",
                table: "PhieuThus");

            migrationBuilder.DropColumn(
                name: "LyDoHuy",
                table: "PhieuThus");

            migrationBuilder.DropColumn(
                name: "MaGiaoDichNganHang",
                table: "PhieuThus");

            migrationBuilder.DropColumn(
                name: "MaNhanVienThu",
                table: "PhieuThus");

            migrationBuilder.DropColumn(
                name: "NganHangNhan",
                table: "PhieuThus");

            migrationBuilder.DropColumn(
                name: "NgayHuy",
                table: "PhieuThus");

            migrationBuilder.DropColumn(
                name: "GhiChuTraThieu",
                table: "KyHanThanhToans");

            migrationBuilder.DropColumn(
                name: "NgayHenTraTiepTheo",
                table: "KyHanThanhToans");

            migrationBuilder.DropColumn(
                name: "PhiPhatTreHan",
                table: "KyHanThanhToans");

            migrationBuilder.DropColumn(
                name: "SoNgayTreHan",
                table: "KyHanThanhToans");

            migrationBuilder.DropColumn(
                name: "TienTraThua",
                table: "HopDongs");
        }
    }
}
