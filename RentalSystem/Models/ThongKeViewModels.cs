using System;
using System.Collections.Generic;

namespace RentalSystem.Models
{
    public class ThongKeFilterModel
    {
        public string Range { get; set; } = "this_month"; // today, this_month, this_quarter, this_year, custom
        public DateTime? TuNgay { get; set; }
        public DateTime? DenNgay { get; set; }
        public DateTime EffectiveFrom { get; set; }
        public DateTime EffectiveTo { get; set; }
        public string RangeDisplayName { get; set; } = string.Empty;
    }

    public class PaymentMethodStat
    {
        public int HinhThuc { get; set; }
        public string TenPhuongThuc { get; set; } = string.Empty;
        public string IconClass { get; set; } = "fas fa-money-bill-wave";
        public decimal SoTien { get; set; }
        public int SoGiaoDich { get; set; }
        public double TyTrong { get; set; }
    }

    public class CategoryRevenueStat
    {
        public int MaLoai { get; set; }
        public string TenLoai { get; set; } = string.Empty;
        public int SoLuongMay { get; set; }
        public int SoLuotThue { get; set; }
        public decimal DoanhThu { get; set; }
        public double TyTrong { get; set; }
    }

    public class TopProductStat
    {
        public int MaSanPham { get; set; }
        public string TenSanPham { get; set; } = string.Empty;
        public string TenDanhMuc { get; set; } = string.Empty;
        public int TongMayKho { get; set; }
        public int SoMayDangThue { get; set; }
        public int SoLuotThue { get; set; }
        public decimal DoanhThu { get; set; }
        public double TyLeKhaiThac { get; set; }
    }

    public class FleetStatusStat
    {
        public int SanSang { get; set; }
        public int DangChoThue { get; set; }
        public int BaoTriSuaChua { get; set; }
        public int GiuCho { get; set; }
        public int HongThanhLy { get; set; }
        public int TongMay { get; set; }
        public double TyLeKhaiThac { get; set; }
    }

    public class FinancialMetricsStat
    {
        public decimal DoanhThuThuan { get; set; }
        public decimal TongThucThu { get; set; }
        public decimal TongChiHoan { get; set; }
        public decimal TienCocDangGiu { get; set; }
        public int SoHopDongHieuLuc { get; set; }
        public int TongSoHopDongTrongKy { get; set; }
        public int TongPhieuBaoTri { get; set; }
        public int BaoTriHoanTat { get; set; }
        public int BaoTriDangXuLy { get; set; }
        public double TyLeXuLyBaoTri { get; set; }

        // Kỳ hạn thanh toán (KyHanThanhToan) đến hạn trong kỳ
        public int TongKyHanTrongKy { get; set; }
        public int KyHanDaHoanTat { get; set; }
        public decimal TongTienKyHanPhaiThu { get; set; }
        public decimal TongTienKyHanDaThu { get; set; }
    }

    public class TimeSeriesPoint
    {
        public string Label { get; set; } = string.Empty;
        public decimal DoanhThu { get; set; }
        public decimal ChiPhi { get; set; }
    }

    public class ThongKeDashboardViewModel
    {
        public ThongKeFilterModel Filter { get; set; } = new();
        public FinancialMetricsStat Financial { get; set; } = new();
        public FleetStatusStat Fleet { get; set; } = new();
        public List<PaymentMethodStat> PaymentMethods { get; set; } = new();
        public List<CategoryRevenueStat> Categories { get; set; } = new();
        public List<TopProductStat> TopProducts { get; set; } = new();
        public List<TimeSeriesPoint> TimeSeries { get; set; } = new();

        // JSON serialized helpers for Chart.js rendering
        public string TimeSeriesLabelsJson { get; set; } = "[]";
        public string TimeSeriesRevenueJson { get; set; } = "[]";
        public string TimeSeriesExpenseJson { get; set; } = "[]";

        public string CategoryLabelsJson { get; set; } = "[]";
        public string CategoryValuesJson { get; set; } = "[]";

        public string FleetLabelsJson { get; set; } = "[]";
        public string FleetValuesJson { get; set; } = "[]";
    }
}
