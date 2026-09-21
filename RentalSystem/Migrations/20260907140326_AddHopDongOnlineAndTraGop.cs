using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace RentalSystem.Migrations
{
    /// <inheritdoc />
    public partial class AddHopDongOnlineAndTraGop : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "AnhCMND",
                table: "HopDongs",
                type: "nvarchar(max)",
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "ChuKyKhachHang",
                table: "HopDongs",
                type: "nvarchar(max)",
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "ChuKyNhanVien",
                table: "HopDongs",
                type: "nvarchar(max)",
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "GhiChu",
                table: "HopDongs",
                type: "nvarchar(max)",
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<DateTime>(
                name: "NgayKy",
                table: "HopDongs",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "TrangThaiThanhToan",
                table: "HopDongs",
                type: "int",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.CreateTable(
                name: "KyHanThanhToans",
                columns: table => new
                {
                    MaKyHan = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaHopDong = table.Column<int>(type: "int", nullable: false),
                    SoKyHan = table.Column<int>(type: "int", nullable: false),
                    NgayDenHan = table.Column<DateTime>(type: "datetime2", nullable: false),
                    SoTienPhai = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    SoTienDaTra = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    TrangThai = table.Column<int>(type: "int", nullable: false),
                    NgayThanhToan = table.Column<DateTime>(type: "datetime2", nullable: true),
                    GhiChu = table.Column<string>(type: "nvarchar(max)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_KyHanThanhToans", x => x.MaKyHan);
                    table.ForeignKey(
                        name: "FK_KyHanThanhToans_HopDongs_MaHopDong",
                        column: x => x.MaHopDong,
                        principalTable: "HopDongs",
                        principalColumn: "MaHopDong",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_KyHanThanhToans_MaHopDong",
                table: "KyHanThanhToans",
                column: "MaHopDong");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "KyHanThanhToans");

            migrationBuilder.DropColumn(
                name: "AnhCMND",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "ChuKyKhachHang",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "ChuKyNhanVien",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "GhiChu",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "NgayKy",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "TrangThaiThanhToan",
                table: "HopDongs");
        }
    }
}
