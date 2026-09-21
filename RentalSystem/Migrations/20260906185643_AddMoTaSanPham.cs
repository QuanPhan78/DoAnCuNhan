using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace RentalSystem.Migrations
{
    /// <inheritdoc />
    public partial class AddMoTaSanPham : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "MoTa",
                table: "SanPhams",
                type: "nvarchar(max)",
                nullable: false,
                defaultValue: "");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "MoTa",
                table: "SanPhams");
        }
    }
}
