namespace RentalSystem.Models
{
    public class CartItem
    {
        public int MaSanPham { get; set; }
        public string TenSanPham { get; set; } = string.Empty;
        public string HinhAnh { get; set; } = string.Empty;
        public decimal GiaThueNgay { get; set; }
        public int SoLuong { get; set; }
        public decimal ThanhTien => GiaThueNgay * SoLuong;
    }
}
