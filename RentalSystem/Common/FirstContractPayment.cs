using RentalSystem.Models;

namespace RentalSystem.Common;

public static class FirstContractPayment
{
    public const string ReceiptNote = "Thanh toán lần đầu";
    public const int ExcessReceipt = 3;

    public static bool IsPendingHandover(HopDong contract) =>
        contract.YeuCauThanhToanLanDau && contract.TrangThai == 0;

    public static string TransferReference(int contractId) => $"HD{contractId} LD";

    public static (decimal Deposit, decimal Rent, decimal Total) Balance(
        HopDong contract, IEnumerable<PhieuThu>? receipts, KyHanThanhToan? first)
    {
        decimal depositPaid = receipts?.Where(p => p.LoaiPhieu == 1 && !p.DaHuy).Sum(p => p.SoTien) ?? 0m;
        decimal deposit = Math.Max(0m, contract.TienCocBaoDamMay - depositPaid);
        decimal rent = first == null ? 0m : Math.Max(0m, first.SoTienPhai - first.SoTienDaTra);
        return (deposit, rent, deposit + rent);
    }

    public static IReadOnlyList<KyHanThanhToan> CreateSchedule(HopDong contract)
    {
        int days = Math.Max(1, (contract.NgayKetThuc.Date - contract.NgayBatDau.Date).Days);
        int count = Math.Clamp(contract.SoKyHan, 1, Math.Max(1, days / 7));
        decimal rent = Math.Max(0m, contract.TongTien);
        decimal baseAmount = decimal.Floor(rent / count);
        decimal advance = Math.Max(0m, contract.TienThueTraTruoc);
        var schedule = new List<KyHanThanhToan>(count);
        for (int index = 0; index < count; index++)
        {
            decimal amount = index == count - 1 ? rent - baseAmount * index : baseAmount;
            decimal appliedAdvance = Math.Min(advance, amount);
            advance -= appliedAdvance;
            decimal due = amount - appliedAdvance;
            schedule.Add(new KyHanThanhToan
            {
                MaHopDong = contract.MaHopDong,
                SoKyHan = index + 1,
                NgayDenHan = contract.NgayBatDau.Date.AddDays(index == 0 ? 0 : Math.Round((double)index * days / (count - 1))),
                SoTienPhai = due,
                TrangThai = due == 0 ? 1 : 0,
                GhiChu = index == 0 ? "Thu trước khi giao máy" : $"Kỳ {index + 1}"
            });
        }
        return schedule;
    }
}
