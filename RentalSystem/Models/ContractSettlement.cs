using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace RentalSystem.Models;

public class ContractSettlement
{
    [Key, DatabaseGenerated(DatabaseGeneratedOption.None)] public int MaHopDong { get; set; }
    public int LoaiQuyetToan { get; set; }
    public int MaNhanVien { get; set; }
    public DateTime NgayQuyetToan { get; set; }
    [Column(TypeName = "decimal(18,2)")] public decimal CocThucThu { get; set; }
    [Column(TypeName = "decimal(18,2)")] public decimal CocDaHoan { get; set; }
    [Column(TypeName = "decimal(18,2)")] public decimal CocCanTruThue { get; set; }
    [Column(TypeName = "decimal(18,2)")] public decimal CocCanTruBoiThuong { get; set; }
    [Column(TypeName = "decimal(18,2)")] public decimal HoanCoc { get; set; }
    [Column(TypeName = "decimal(18,2)")] public decimal HoanThue { get; set; }
    [Column(TypeName = "decimal(18,2)")] public decimal HoanThua { get; set; }
    [Column(TypeName = "decimal(18,2)")] public decimal HoanKhac { get; set; }
    public string ChiTietJson { get; set; } = "";
    [MaxLength(64)] public string MaBanXemTruoc { get; set; } = "";
}
