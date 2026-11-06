using System;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Common
{
    public static class DebtCalculationHelper
    {
        
        /// Tính phí phạt trễ hạn dựa trên số tiền chưa trả và số ngày quá hạn (sau thời gian ân hạn 3 ngày).
       
        public static decimal CalculateLateFee(decimal unpaidAmount, DateTime dueDate, DateTime asOfDate)
        {
            if (unpaidAmount <= 0)
                return 0m;

            int daysPastDue = (int)(asOfDate.Date - dueDate.Date).TotalDays;
            if (daysPastDue <= 3)
                return 0m;

            return Math.Round(unpaidAmount * 0.001m * daysPastDue, 0);
        }

        public static decimal GetInstallmentBalance(KyHanThanhToan installment)
        {
            decimal penalty = Math.Max(installment.TienPhat, installment.PhiPhatTreHan);
            return Math.Max(0m, installment.SoTienPhai - installment.SoTienDaTra + penalty);
        }

        
        /// Phân loại nhóm tuổi nợ theo số ngày quá hạn thanh toán.
        
        public static int CalculateAgingTier(int overdueDays)
        {
            if (overdueDays <= 0)
                return 0; // Đúng hạn
            if (overdueDays <= 30)
                return 1; // Cần chú ý
            if (overdueDays <= 60)
                return 2; // Dưới tiêu chuẩn
            if (overdueDays <= 90)
                return 3; // Nghi ngờ
            return 4;     // Trên 90 ngày
        }

        public static string GetAgingTierName(int tier) => tier switch
        {
            0 => "Chưa quá hạn",
            1 => "1–30 ngày",
            2 => "31–60 ngày",
            3 => "61–90 ngày",
            4 => "Trên 90 ngày",
            _ => "Chưa xác định"
        };

        public static bool IsPayableInstallment(KyHanThanhToan installment) =>
            installment.TrangThai is 0 or 2 &&
            (installment.HopDong == null || !FirstContractPayment.IsPendingHandover(installment.HopDong));

        public static int DaysPastDue(KyHanThanhToan installment, DateTime today) =>
            Math.Max(0, (today.Date - installment.NgayDenHan.Date).Days);

        /// Tính tổng công nợ hợp đồng bao gồm tiền thuê và chi phí đền bù hư hại bảo trì.
        public static (decimal totalReceivable, decimal totalCollected, decimal remainingDebt) CalculateContractDebt(HopDong hopDong)
        {
            if (hopDong == null)
                return (0m, 0m, 0m);

            decimal totalReceivable = hopDong.TongTien + (hopDong.PhieuBaoTris?.Sum(b => b.PhiDenBu) ?? 0m);
            decimal totalCollected = hopDong.PhieuThus?
                .Where(p => !p.DaHuy && (p.LoaiPhieu == 0 || p.LoaiPhieu == 2))
                .Sum(p => p.SoTien) ?? 0m;

            decimal remainingDebt = totalReceivable - totalCollected;
            return (totalReceivable, totalCollected, remainingDebt);
        }

        /// Quyết toán tiền đặt cọc và xác định số tiền hoàn cọc hoặc khoản nợ còn thiếu.

        public static (decimal refund, decimal remainingDebt) CalculateDepositSettlement(HopDong hopDong, decimal unpaidRent, decimal unpaidDamages)
        {
            if (hopDong == null)
                return (0m, 0m);

            decimal tienCoc = hopDong.YeuCauThanhToanLanDau ? hopDong.TienDaCoc
                : hopDong.TienCocBaoDamMay > 0 ? hopDong.TienCocBaoDamMay : hopDong.TienDaCoc;
            decimal refund = tienCoc - unpaidRent - unpaidDamages;
            decimal remainingDebt = refund < 0 ? Math.Abs(refund) : 0m;

            return (refund, remainingDebt);
        }


        /// Overload tự động tính unpaidRent và unpaidDamages từ dữ liệu liên kết của hợp đồng.

        public static (decimal refund, decimal remainingDebt) CalculateDepositSettlement(HopDong hopDong)
        {
            if (hopDong == null)
                return (0m, 0m);

            decimal unpaidRent = hopDong.KyHanThanhToans?
                .Where(k => k.TrangThai != 1 && k.TrangThai != 3)
                .Sum(k => Math.Max(0m, k.SoTienPhai - k.SoTienDaTra + k.TienPhat)) ?? 0m;

            decimal totalDamages = hopDong.PhieuBaoTris?.Sum(b => b.PhiDenBu) ?? 0m;
            decimal paidDamages = hopDong.PhieuThus?
                .Where(p => !p.DaHuy && p.LoaiPhieu == 2)
                .Sum(p => p.SoTien) ?? 0m;
            decimal unpaidDamages = Math.Max(0m, totalDamages - paidDamages);

            return CalculateDepositSettlement(hopDong, unpaidRent, unpaidDamages);
        }


        // Cùng quy tắc cho màn công nợ và luồng đặt thuê.
        public static string? RentalRestrictionReason(IEnumerable<KyHanThanhToan> installments, DateTime now)
        {
            var overdue = installments
                .Where(k => k.HopDong?.TrangThai != 3 &&
                    IsPayableInstallment(k) && DaysPastDue(k, now) > 0)
                .ToList();

            foreach (var installment in overdue)
            {
                int days = DaysPastDue(installment, now);
                if (days > 15)
                    return $"Kỳ hạn hợp đồng HD{installment.MaHopDong} đã trễ {days} ngày (giới hạn 15 ngày). Vui lòng thanh toán trước khi tiếp tục thuê.";
            }

            decimal balance = overdue.Sum(k => Math.Max(0m, k.SoTienPhai - k.SoTienDaTra + k.TienPhat));
            return balance > 3_000_000m
                ? $"Tổng nợ quá hạn {balance:N0} đồng đã vượt 3.000.000 đồng. Vui lòng thanh toán trước khi tiếp tục thuê."
                : null;
        }

        private static IQueryable<KyHanThanhToan> CustomerUnpaidInstallments(int customerId, ApplicationDbContext context) =>
            context.KyHanThanhToans.Include(k => k.HopDong)
                .Where(k => k.HopDong.MaKhachHang == customerId && k.HopDong.TrangThai != 3 &&
                    k.TrangThai != 1 && k.TrangThai != 3);

        public static bool IsCustomerBlacklisted(int customerId, ApplicationDbContext context, out string reason)
        {
            reason = customerId > 0 && context != null
                ? RentalRestrictionReason(CustomerUnpaidInstallments(customerId, context).ToList(), DateTime.Now) ?? ""
                : "";
            return reason.Length > 0;
        }

        public static async Task<(bool isBlacklisted, string reason)> IsCustomerBlacklistedAsync(int customerId, ApplicationDbContext context)
        {
            if (customerId <= 0 || context == null)
                return (false, "");

            var installments = await CustomerUnpaidInstallments(customerId, context).ToListAsync();
            var reason = RentalRestrictionReason(installments, DateTime.Now);
            return (reason != null, reason ?? "");
        }
    }
}
