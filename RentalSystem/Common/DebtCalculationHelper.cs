using System;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Common
{
    public static class DebtCalculationHelper
    {
        /// <summary>
        /// Tính phí phạt trễ hạn dựa trên số tiền chưa trả và số ngày quá hạn (sau thời gian ân hạn 3 ngày).
        /// </summary>
        public static decimal CalculateLateFee(decimal unpaidAmount, DateTime dueDate, DateTime asOfDate)
        {
            if (unpaidAmount <= 0)
                return 0m;

            int daysPastDue = (int)(asOfDate.Date - dueDate.Date).TotalDays;
            if (daysPastDue <= 3)
                return 0m;

            return Math.Round(unpaidAmount * 0.001m * daysPastDue, 0);
        }

        /// <summary>
        /// Phân loại nhóm tuổi nợ theo số ngày quá hạn thanh toán.
        /// </summary>
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
            return 4;     // Nợ xấu / Khóa thuê
        }

        public static string GetAgingTierName(int tier)
        {
            return tier switch
            {
                0 => "Đúng hạn",
                1 => "Nhóm 1 (Cần chú ý)",
                2 => "Nhóm 2 (Dưới tiêu chuẩn)",
                3 => "Nhóm 3 (Nghi ngờ)",
                4 => "Nhóm 4 (Nợ xấu / Khóa thuê)",
                _ => "Không xác định"
            };
        }

        public static string GetAgingBadgeClass(int tier)
        {
            return tier switch
            {
                0 => "badge bg-success",
                1 => "badge bg-info text-dark",
                2 => "badge bg-warning text-dark",
                3 => "badge bg-orange text-white",
                4 => "badge bg-danger",
                _ => "badge bg-secondary"
            };
        }

        /// <summary>
        /// Tính tổng công nợ hợp đồng bao gồm tiền thuê và chi phí đền bù hư hại bảo trì.
        /// </summary>
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

        /// <summary>
        /// Quyết toán tiền đặt cọc và xác định số tiền hoàn cọc hoặc khoản nợ còn thiếu.
        /// </summary>
        public static (decimal refund, decimal remainingDebt) CalculateDepositSettlement(HopDong hopDong, decimal unpaidRent, decimal unpaidDamages)
        {
            if (hopDong == null)
                return (0m, 0m);

            decimal tienCoc = hopDong.TienCocBaoDamMay > 0 ? hopDong.TienCocBaoDamMay : hopDong.TienDaCoc;
            decimal refund = tienCoc - unpaidRent - unpaidDamages;
            decimal remainingDebt = refund < 0 ? Math.Abs(refund) : 0m;

            return (refund, remainingDebt);
        }

        /// <summary>
        /// Overload tự động tính unpaidRent và unpaidDamages từ dữ liệu liên kết của hợp đồng.
        /// </summary>
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

        /// <summary>
        /// Kiểm tra khách hàng có thuộc diện nợ xấu bị hạn chế thuê tiếp hay không.
        /// Điều kiện: Có kỳ hạn trễ hạn > 15 ngày HOẶC tổng dư nợ quá hạn > 3.000.000 VNĐ.
        /// </summary>
        public static bool IsCustomerBlacklisted(int customerId, ApplicationDbContext context, out string reason)
        {
            reason = string.Empty;
            if (customerId <= 0 || context == null)
                return false;

            var unpaidInstallments = context.KyHanThanhToans
                .Include(k => k.HopDong)
                .Where(k => k.HopDong.MaKhachHang == customerId
                         && k.HopDong.TrangThai != 3
                         && k.TrangThai != 1
                         && k.TrangThai != 3)
                .ToList();

            var now = DateTime.Now;
            var overdueInstallments = unpaidInstallments
                .Where(k => k.TrangThai == 2 || (k.TrangThai == 0 && now > k.NgayDenHan))
                .ToList();

            if (!overdueInstallments.Any())
                return false;

            // Điều kiện 1: Có kỳ hạn trễ hạn quá 15 ngày
            var severeOverdue = overdueInstallments
                .Select(k => new
                {
                    Installment = k,
                    OverdueDays = Math.Max(k.SoNgayTreHan, (int)(now.Date - k.NgayDenHan.Date).TotalDays)
                })
                .FirstOrDefault(x => x.OverdueDays > 15);

            if (severeOverdue != null)
            {
                reason = $"Khách hàng có kỳ hạn thanh toán trễ hạn {severeOverdue.OverdueDays} ngày (vượt quá 15 ngày cho phép) tại Hợp đồng HD{severeOverdue.Installment.MaHopDong}. Vui lòng thanh toán trước khi tiếp tục thuê máy.";
                return true;
            }

            // Điều kiện 2: Tổng nợ quá hạn vượt hạn mức 3.000.000 VNĐ
            decimal totalOverdueBalance = overdueInstallments.Sum(k =>
                Math.Max(0m, k.SoTienPhai - k.SoTienDaTra + k.TienPhat));

            if (totalOverdueBalance > 3_000_000m)
            {
                reason = $"Khách hàng có tổng nợ quá hạn {totalOverdueBalance:N0} VNĐ (vượt quá hạn mức 3.000.000 VNĐ). Vui lòng thanh toán tại Sổ công nợ trước khi tiếp tục thuê máy.";
                return true;
            }

            return false;
        }

        public static async Task<(bool isBlacklisted, string reason)> IsCustomerBlacklistedAsync(int customerId, ApplicationDbContext context)
        {
            if (customerId <= 0 || context == null)
                return (false, string.Empty);

            var unpaidInstallments = await context.KyHanThanhToans
                .Include(k => k.HopDong)
                .Where(k => k.HopDong.MaKhachHang == customerId
                         && k.HopDong.TrangThai != 3
                         && k.TrangThai != 1
                         && k.TrangThai != 3)
                .ToListAsync();

            var now = DateTime.Now;
            var overdueInstallments = unpaidInstallments
                .Where(k => k.TrangThai == 2 || (k.TrangThai == 0 && now > k.NgayDenHan))
                .ToList();

            if (!overdueInstallments.Any())
                return (false, string.Empty);

            var severeOverdue = overdueInstallments
                .Select(k => new
                {
                    Installment = k,
                    OverdueDays = Math.Max(k.SoNgayTreHan, (int)(now.Date - k.NgayDenHan.Date).TotalDays)
                })
                .FirstOrDefault(x => x.OverdueDays > 15);

            if (severeOverdue != null)
            {
                return (true, $"Khách hàng có kỳ hạn thanh toán trễ hạn {severeOverdue.OverdueDays} ngày (vượt quá 15 ngày cho phép) tại Hợp đồng HD{severeOverdue.Installment.MaHopDong}. Vui lòng thanh toán trước khi tiếp tục thuê máy.");
            }

            decimal totalOverdueBalance = overdueInstallments.Sum(k =>
                Math.Max(0m, k.SoTienPhai - k.SoTienDaTra + k.TienPhat));

            if (totalOverdueBalance > 3_000_000m)
            {
                return (true, $"Khách hàng có tổng nợ quá hạn {totalOverdueBalance:N0} VNĐ (vượt quá hạn mức 3.000.000 VNĐ). Vui lòng thanh toán tại Sổ công nợ trước khi tiếp tục thuê máy.");
            }

            return (false, string.Empty);
        }
    }
}
