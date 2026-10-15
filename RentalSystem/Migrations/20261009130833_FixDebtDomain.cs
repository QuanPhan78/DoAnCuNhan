using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace RentalSystem.Migrations
{
    /// <inheritdoc />
    public partial class FixDebtDomain : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<int>(
                name: "NhomTuoiNo",
                table: "KyHanThanhToans",
                type: "int",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<decimal>(
                name: "TienPhat",
                table: "KyHanThanhToans",
                type: "decimal(18,2)",
                nullable: false,
                defaultValue: 0m);

            migrationBuilder.AddColumn<decimal>(
                name: "TienCocBaoDamMay",
                table: "HopDongs",
                type: "decimal(18,2)",
                nullable: false,
                defaultValue: 0m);

            migrationBuilder.AddColumn<decimal>(
                name: "TienThueTraTruoc",
                table: "HopDongs",
                type: "decimal(18,2)",
                nullable: false,
                defaultValue: 0m);

            migrationBuilder.CreateTable(
                name: "LichSuNhacNos",
                columns: table => new
                {
                    MaLichSuNhacNo = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaHopDong = table.Column<int>(type: "int", nullable: false),
                    MaKyHan = table.Column<int>(type: "int", nullable: true),
                    NgayNhac = table.Column<DateTime>(type: "datetime2", nullable: false),
                    HinhThucNhac = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    NoiDung = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    NguoiGuiId = table.Column<int>(type: "int", nullable: true),
                    SoTienNhac = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    LanNhacThu = table.Column<int>(type: "int", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_LichSuNhacNos", x => x.MaLichSuNhacNo);
                    table.ForeignKey(
                        name: "FK_LichSuNhacNos_HopDongs_MaHopDong",
                        column: x => x.MaHopDong,
                        principalTable: "HopDongs",
                        principalColumn: "MaHopDong",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_LichSuNhacNos_KyHanThanhToans_MaKyHan",
                        column: x => x.MaKyHan,
                        principalTable: "KyHanThanhToans",
                        principalColumn: "MaKyHan",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_LichSuNhacNos_NguoiDungs_NguoiGuiId",
                        column: x => x.NguoiGuiId,
                        principalTable: "NguoiDungs",
                        principalColumn: "MaNguoiDung",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_LichSuNhacNos_MaHopDong",
                table: "LichSuNhacNos",
                column: "MaHopDong");

            migrationBuilder.CreateIndex(
                name: "IX_LichSuNhacNos_MaKyHan",
                table: "LichSuNhacNos",
                column: "MaKyHan");

            migrationBuilder.CreateIndex(
                name: "IX_LichSuNhacNos_NguoiGuiId",
                table: "LichSuNhacNos",
                column: "NguoiGuiId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "LichSuNhacNos");

            migrationBuilder.DropColumn(
                name: "NhomTuoiNo",
                table: "KyHanThanhToans");

            migrationBuilder.DropColumn(
                name: "TienPhat",
                table: "KyHanThanhToans");

            migrationBuilder.DropColumn(
                name: "TienCocBaoDamMay",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "TienThueTraTruoc",
                table: "HopDongs");
        }
    }
}
