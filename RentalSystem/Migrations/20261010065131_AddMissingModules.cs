using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace RentalSystem.Migrations
{
    /// <inheritdoc />
    public partial class AddMissingModules : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AlterColumn<string>(
                name: "MaCode",
                table: "KhuyenMais",
                type: "nvarchar(50)",
                maxLength: 50,
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(max)");

            migrationBuilder.AddColumn<string>(
                name: "MoTa",
                table: "KhuyenMais",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "NgayBatDau",
                table: "KhuyenMais",
                type: "datetime2",
                nullable: false,
                defaultValue: new DateTime(1, 1, 1, 0, 0, 0, 0, DateTimeKind.Unspecified));

            migrationBuilder.AddColumn<DateTime>(
                name: "NgayKetThuc",
                table: "KhuyenMais",
                type: "datetime2",
                nullable: false,
                defaultValue: new DateTime(1, 1, 1, 0, 0, 0, 0, DateTimeKind.Unspecified));

            migrationBuilder.AddColumn<int>(
                name: "SoLuong",
                table: "KhuyenMais",
                type: "int",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.CreateTable(
                name: "PhanCongCongViecs",
                columns: table => new
                {
                    MaPhanCong = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaNhanVien = table.Column<int>(type: "int", nullable: false),
                    TieuDe = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: false),
                    NoiDung = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    MaHopDong = table.Column<int>(type: "int", nullable: true),
                    MaPhieuBaoTri = table.Column<int>(type: "int", nullable: true),
                    TrangThai = table.Column<int>(type: "int", nullable: false),
                    NgayGiao = table.Column<DateTime>(type: "datetime2", nullable: false),
                    HanHoanThanh = table.Column<DateTime>(type: "datetime2", nullable: true),
                    NgayHoanThanh = table.Column<DateTime>(type: "datetime2", nullable: true),
                    MaNguoiGiao = table.Column<int>(type: "int", nullable: true),
                    GhiChuTienDo = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_PhanCongCongViecs", x => x.MaPhanCong);
                    table.ForeignKey(
                        name: "FK_PhanCongCongViecs_HopDongs_MaHopDong",
                        column: x => x.MaHopDong,
                        principalTable: "HopDongs",
                        principalColumn: "MaHopDong",
                        onDelete: ReferentialAction.SetNull);
                    table.ForeignKey(
                        name: "FK_PhanCongCongViecs_NguoiDungs_MaNguoiGiao",
                        column: x => x.MaNguoiGiao,
                        principalTable: "NguoiDungs",
                        principalColumn: "MaNguoiDung",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_PhanCongCongViecs_NguoiDungs_MaNhanVien",
                        column: x => x.MaNhanVien,
                        principalTable: "NguoiDungs",
                        principalColumn: "MaNguoiDung",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_PhanCongCongViecs_PhieuBaoTris_MaPhieuBaoTri",
                        column: x => x.MaPhieuBaoTri,
                        principalTable: "PhieuBaoTris",
                        principalColumn: "MaPhieu",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateTable(
                name: "YeuCauGiaHans",
                columns: table => new
                {
                    MaYeuCau = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    MaHopDong = table.Column<int>(type: "int", nullable: false),
                    SoNgayGiaHan = table.Column<int>(type: "int", nullable: false),
                    LyDo = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    NgayYeuCau = table.Column<DateTime>(type: "datetime2", nullable: false),
                    TrangThai = table.Column<int>(type: "int", nullable: false),
                    NgayDuyet = table.Column<DateTime>(type: "datetime2", nullable: true),
                    MaNguoiDuyet = table.Column<int>(type: "int", nullable: true),
                    ChiPhiPhatSinh = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    GhiChuAdmin = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_YeuCauGiaHans", x => x.MaYeuCau);
                    table.ForeignKey(
                        name: "FK_YeuCauGiaHans_HopDongs_MaHopDong",
                        column: x => x.MaHopDong,
                        principalTable: "HopDongs",
                        principalColumn: "MaHopDong",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_YeuCauGiaHans_NguoiDungs_MaNguoiDuyet",
                        column: x => x.MaNguoiDuyet,
                        principalTable: "NguoiDungs",
                        principalColumn: "MaNguoiDung",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_HopDongs_MaKhuyenMai",
                table: "HopDongs",
                column: "MaKhuyenMai");

            migrationBuilder.CreateIndex(
                name: "IX_PhanCongCongViecs_MaHopDong",
                table: "PhanCongCongViecs",
                column: "MaHopDong");

            migrationBuilder.CreateIndex(
                name: "IX_PhanCongCongViecs_MaNguoiGiao",
                table: "PhanCongCongViecs",
                column: "MaNguoiGiao");

            migrationBuilder.CreateIndex(
                name: "IX_PhanCongCongViecs_MaNhanVien",
                table: "PhanCongCongViecs",
                column: "MaNhanVien");

            migrationBuilder.CreateIndex(
                name: "IX_PhanCongCongViecs_MaPhieuBaoTri",
                table: "PhanCongCongViecs",
                column: "MaPhieuBaoTri");

            migrationBuilder.CreateIndex(
                name: "IX_YeuCauGiaHans_MaHopDong",
                table: "YeuCauGiaHans",
                column: "MaHopDong");

            migrationBuilder.CreateIndex(
                name: "IX_YeuCauGiaHans_MaNguoiDuyet",
                table: "YeuCauGiaHans",
                column: "MaNguoiDuyet");

            migrationBuilder.AddForeignKey(
                name: "FK_HopDongs_KhuyenMais_MaKhuyenMai",
                table: "HopDongs",
                column: "MaKhuyenMai",
                principalTable: "KhuyenMais",
                principalColumn: "MaKhuyenMai",
                onDelete: ReferentialAction.SetNull);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_HopDongs_KhuyenMais_MaKhuyenMai",
                table: "HopDongs");

            migrationBuilder.DropTable(
                name: "PhanCongCongViecs");

            migrationBuilder.DropTable(
                name: "YeuCauGiaHans");

            migrationBuilder.DropIndex(
                name: "IX_HopDongs_MaKhuyenMai",
                table: "HopDongs");

            migrationBuilder.DropColumn(
                name: "MoTa",
                table: "KhuyenMais");

            migrationBuilder.DropColumn(
                name: "NgayBatDau",
                table: "KhuyenMais");

            migrationBuilder.DropColumn(
                name: "NgayKetThuc",
                table: "KhuyenMais");

            migrationBuilder.DropColumn(
                name: "SoLuong",
                table: "KhuyenMais");

            migrationBuilder.AlterColumn<string>(
                name: "MaCode",
                table: "KhuyenMais",
                type: "nvarchar(max)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(50)",
                oldMaxLength: 50);
        }
    }
}
