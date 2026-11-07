using ClosedXML.Excel;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Common;
using RentalSystem.Models;
using System.IO;

namespace RentalSystem.Areas.Admin.Controllers
{
    // Controller quản lý công nợ khách hàng trong phân hệ Quản trị (Admin).
    // Cho phép các bộ phận Admin, Kinh doanh và Kế toán theo dõi tiến độ thanh toán,
    // các hợp đồng còn thiếu tiền hoặc sắp đến hạn thanh toán các kỳ.
    [Area("Admin")]
    [Authorize(Roles = "Admin,KinhDoanh,KeToan")]
    public class CongNoController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly IConfiguration _configuration;

        public CongNoController(ApplicationDbContext context, IConfiguration? configuration = null)
        {
            _context = context;
            _configuration = configuration ?? new ConfigurationBuilder().Build();
        }

        // Danh sách công nợ hệ thống và bộ lọc tìm kiếm
        // Nghiệp vụ: Chỉ lấy các hợp đồng chưa trả đủ tiền và loại trừ các đơn đã bị hủy (TrangThai != 3).
        public async Task<IActionResult> Index(
            string? search = null, 
            int? agingTier = null, 
            DateTime? tuNgay = null, 
            DateTime? denNgay = null, 
            string? activeTab = null,
            bool dueSoon = false)
        {
            var hopDongs = await _context.HopDongs
                .Include(h => h.KhachHang)
                .Include(h => h.KyHanThanhToans)
                    .ThenInclude(k => k.LichSuNhacNos)
                .Include(h => h.PhieuBaoTris)
                .Include(h => h.PhieuThus)
                .Where(h => h.TrangThai != 3) // Loại trừ đơn đã bị hủy
                .OrderByDescending(h => h.NgayBatDau)
                .ToListAsync();

            // Cập nhật tự động trạng thái quá hạn và phí phạt trễ hạn
            var allKyHans = hopDongs.SelectMany(h => h.KyHanThanhToans ?? Enumerable.Empty<KyHanThanhToan>()).ToList();
            HopDongController.CapNhatTreHanVaPhiPhat(allKyHans);
            await _context.SaveChangesAsync();

            // Thống kê các chỉ số công nợ toàn hệ thống
            decimal tongCongNo = 0m;
            decimal tongPhaiThuToanHeThong = 0m;
            decimal tongDaThuToanHeThong = 0m;

            foreach (var h in hopDongs)
            {
                decimal phiDenBu = h.PhieuBaoTris?.Sum(b => b.PhiDenBu) ?? 0m;
                decimal phaiThu = h.TongTien + phiDenBu;
                decimal daThu = (h.YeuCauThanhToanLanDau ? 0m : h.TienDaCoc) + (h.PhieuThus?.Where(pt => !pt.DaHuy && (pt.LoaiPhieu == 0 || pt.LoaiPhieu == 2)).Sum(pt => pt.SoTien)
                    ?? h.KyHanThanhToans?.Sum(k => k.SoTienDaTra) ?? 0m);
                decimal conNo = Math.Max(0m, phaiThu - daThu);

                tongPhaiThuToanHeThong += phaiThu;
                tongDaThuToanHeThong += daThu;
                tongCongNo += conNo;
            }

            var now = DateTime.Now;
            var overdueKyHansAll = allKyHans
                .Where(k => DebtCalculationHelper.IsPayableInstallment(k) &&
                    DebtCalculationHelper.DaysPastDue(k, now) > 0);
            var tiers = overdueKyHansAll.Where(k => DebtCalculationHelper.GetInstallmentBalance(k) > 0).ToList();
            ViewBag.SoKhoanNoXau = tiers.Count(k => DebtCalculationHelper.DaysPastDue(k, now) > 90);
            ViewBag.AgingTier1Count = tiers.Count(k => DebtCalculationHelper.CalculateAgingTier(DebtCalculationHelper.DaysPastDue(k, now)) == 1);
            ViewBag.AgingTier2Count = tiers.Count(k => DebtCalculationHelper.CalculateAgingTier(DebtCalculationHelper.DaysPastDue(k, now)) == 2);
            ViewBag.AgingTier3Count = tiers.Count(k => DebtCalculationHelper.CalculateAgingTier(DebtCalculationHelper.DaysPastDue(k, now)) == 3);
            ViewBag.AgingTier4Count = ViewBag.SoKhoanNoXau;
            ViewBag.TongCongNo = tongCongNo;
            ViewBag.TongNoQuaHan = overdueKyHansAll.Sum(k => Math.Max(0m, k.SoTienPhai - k.SoTienDaTra) + k.TienPhat);
            ViewBag.TyLeThuHoi = tongPhaiThuToanHeThong > 0
                ? Math.Min(100m, Math.Max(0m, Math.Round(tongDaThuToanHeThong / tongPhaiThuToanHeThong * 100m, 1)))
                : 100m;

            bool showUpcoming = agingTier == 0 ||
                (!agingTier.HasValue && activeTab == "upcoming");
            dueSoon = dueSoon && showUpcoming;
            var restrictedCustomers = hopDongs
                .GroupBy(h => h.MaKhachHang)
                .Select(group => (Customer: group.Key, Reason: DebtCalculationHelper.RentalRestrictionReason(
                    group.SelectMany(h => h.KyHanThanhToans ?? Array.Empty<KyHanThanhToan>()), now)))
                .Where(entry => entry.Reason != null)
                .ToDictionary(entry => entry.Customer, entry => entry.Reason!);
            var congNoList = FilterContracts(hopDongs, search, agingTier, tuNgay, denNgay, dueSoon, now).ToList();

            ViewBag.Installments = congNoList.SelectMany(h => h.KyHanThanhToans ?? Array.Empty<KyHanThanhToan>())
                .Where(k => DebtCalculationHelper.IsPayableInstallment(k) &&
                    DebtCalculationHelper.GetInstallmentBalance(k) > 0 &&
                    (DebtCalculationHelper.DaysPastDue(k, now) == 0) == showUpcoming &&
                    MatchesInstallmentFilter(k, agingTier, dueSoon, now))
                .OrderBy(k => k.NgayDenHan)
                .ToList();
            ViewBag.RestrictedCustomers = restrictedCustomers;
            ViewBag.Today = now.Date;
            ViewBag.Search = search;
            ViewBag.AgingTier = agingTier;
            ViewBag.TuNgay = tuNgay?.ToString("yyyy-MM-dd");
            ViewBag.DenNgay = denNgay?.ToString("yyyy-MM-dd");
            ViewBag.ActiveTab = showUpcoming ? "upcoming" : "overdue";
            ViewBag.DueSoon = dueSoon;

            return View(congNoList);
        }

        private static bool MatchesInstallmentFilter(KyHanThanhToan installment, int? agingTier, bool dueSoon, DateTime today)
        {
            int days = DebtCalculationHelper.DaysPastDue(installment, today);
            return (!agingTier.HasValue || DebtCalculationHelper.CalculateAgingTier(days) == agingTier.Value) &&
                (!dueSoon || (days == 0 && installment.NgayDenHan.Date <= today.Date.AddDays(7)));
        }

        private static IEnumerable<HopDong> FilterContracts(IEnumerable<HopDong> contracts, string? search,
            int? agingTier, DateTime? from, DateTime? to, bool dueSoon, DateTime today)
        {
            string? term = search?.Trim();
            return contracts.Where(contract =>
            {
                decimal receivable = contract.TongTien + (contract.PhieuBaoTris?.Sum(b => b.PhiDenBu) ?? 0m);
                decimal collected = (contract.YeuCauThanhToanLanDau ? 0m : contract.TienDaCoc) +
                    (contract.PhieuThus?.Where(p => !p.DaHuy && (p.LoaiPhieu == 0 || p.LoaiPhieu == 2)).Sum(p => p.SoTien)
                        ?? contract.KyHanThanhToans?.Sum(k => k.SoTienDaTra) ?? 0m);
                if (receivable <= collected && contract.TrangThaiThanhToan == ContractPaymentStatus.Settled)
                    return false;

                var customer = contract.KhachHang;
                if (!string.IsNullOrEmpty(term) && !contract.MaHopDong.ToString().Contains(term) &&
                    customer?.HoTen?.Contains(term, StringComparison.OrdinalIgnoreCase) != true &&
                    customer?.SoDienThoai?.Contains(term, StringComparison.OrdinalIgnoreCase) != true &&
                    customer?.CCCD?.Contains(term, StringComparison.OrdinalIgnoreCase) != true)
                    return false;

                if ((from.HasValue && contract.NgayBatDau.Date < from.Value.Date) ||
                    (to.HasValue && contract.NgayBatDau.Date > to.Value.Date))
                    return false;

                return (!agingTier.HasValue && !dueSoon) || contract.KyHanThanhToans?.Any(k =>
                    DebtCalculationHelper.IsPayableInstallment(k) &&
                    DebtCalculationHelper.GetInstallmentBalance(k) > 0 &&
                    MatchesInstallmentFilter(k, agingTier, dueSoon, today)) == true;
            });
        }

        // Xuất báo cáo công nợ ra file Excel (.xlsx)
        [HttpGet]
        public async Task<IActionResult> ExportExcel(string? search = null, int? agingTier = null, DateTime? tuNgay = null, DateTime? denNgay = null, bool dueSoon = false)
        {
            var hopDongs = await _context.HopDongs
                .Include(h => h.KhachHang)
                .Include(h => h.KyHanThanhToans)
                    .ThenInclude(k => k.LichSuNhacNos)
                .Include(h => h.PhieuBaoTris)
                .Include(h => h.PhieuThus)
                .Where(h => h.TrangThai != 3) // Loại trừ đơn đã bị hủy
                .OrderByDescending(h => h.NgayBatDau)
                .ToListAsync();

            var allKyHans = hopDongs.SelectMany(h => h.KyHanThanhToans ?? Enumerable.Empty<KyHanThanhToan>()).ToList();
            HopDongController.CapNhatTreHanVaPhiPhat(allKyHans);
            await _context.SaveChangesAsync();

            var today = DateTime.Today;
            var listData = FilterContracts(hopDongs, search, agingTier, tuNgay, denNgay, dueSoon, today);

            using var workbook = new XLWorkbook();
            var worksheet = workbook.Worksheets.Add("Báo Cáo Công Nợ");
            worksheet.ShowGridLines = true;

            // Metadata tiêu đề báo cáo
            worksheet.Cell(1, 1).Value = "HỆ THỐNG QUẢN LÝ CHO THUÊ THIẾT BỊ RENTAL SYSTEM";
            worksheet.Cell(1, 1).Style.Font.Bold = true;
            worksheet.Cell(1, 1).Style.Font.FontSize = 12;
            worksheet.Cell(1, 1).Style.Font.FontColor = XLColor.FromHtml("#595959");

            worksheet.Cell(2, 1).Value = "BÁO CÁO TỔNG HỢP CÔNG NỢ VÀ THEO DÕI TUỔI NỢ KHÁCH HÀNG";
            worksheet.Cell(2, 1).Style.Font.Bold = true;
            worksheet.Cell(2, 1).Style.Font.FontSize = 16;
            worksheet.Cell(2, 1).Style.Font.FontColor = XLColor.FromHtml("#1F4E79");

            worksheet.Cell(3, 1).Value = $"Thời gian xuất: {DateTime.Now:dd/MM/yyyy HH:mm:ss} | Người xuất: {(User.Identity?.Name ?? "Ban Quản Trị")}";
            worksheet.Cell(3, 1).Style.Font.Italic = true;
            worksheet.Cell(3, 1).Style.Font.FontSize = 10;
            worksheet.Cell(3, 1).Style.Font.FontColor = XLColor.FromHtml("#7F7F7F");

            // Tiêu đề bảng (Dòng 5)
            int headerRow = 5;
            string[] headers = new[]
            {
                "STT", "Mã HĐ", "Khách Hàng", "Số Điện Thoại", "CCCD/CMND",
                "Ngày Bắt Đầu", "Ngày Kết Thúc", "Tổng Tiền Thuê", "Phí Bồi Thường Hư Hại",
                "Tổng Phải Thu", "Đã Thu (Gồm Cọc)", "Còn Nợ", "Quá Hạn (Ngày)",
                "Phí Phạt Trễ Hạn", "Tuổi nợ cao nhất", "Trạng thái thanh toán", "Hạn Trả Gần Nhất"
            };

            for (int col = 1; col <= headers.Length; col++)
            {
                var cell = worksheet.Cell(headerRow, col);
                cell.Value = headers[col - 1];
                cell.Style.Font.Bold = true;
                cell.Style.Font.FontSize = 11;
                cell.Style.Font.FontColor = XLColor.White;
                cell.Style.Fill.BackgroundColor = XLColor.FromHtml("#1F4E79");
                cell.Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                cell.Style.Alignment.Vertical = XLAlignmentVerticalValues.Center;
                cell.Style.Border.OutsideBorder = XLBorderStyleValues.Thin;
                cell.Style.Border.OutsideBorderColor = XLColor.FromHtml("#102A45");
            }
            worksheet.Row(headerRow).Height = 28;

            int currentRow = headerRow + 1;
            int stt = 1;
            decimal sumTongTien = 0m, sumPhiDenBu = 0m, sumTongPhaiThu = 0m, sumDaThu = 0m, sumConNo = 0m, sumPhiPhat = 0m;

            foreach (var hd in listData)
            {
                decimal phiDenBu = hd.PhieuBaoTris?.Sum(b => b.PhiDenBu) ?? 0m;
                decimal tongPhaiThu = hd.TongTien + phiDenBu;
                decimal daThu = (hd.YeuCauThanhToanLanDau ? 0m : hd.TienDaCoc) + (hd.PhieuThus?.Where(pt => !pt.DaHuy && (pt.LoaiPhieu == 0 || pt.LoaiPhieu == 2)).Sum(pt => pt.SoTien)
                    ?? hd.KyHanThanhToans?.Sum(k => k.SoTienDaTra) ?? 0m);
                decimal conNo = Math.Max(0m, tongPhaiThu - daThu);

                var unpaidKyHans = (hd.KyHanThanhToans ?? Array.Empty<KyHanThanhToan>())
                    .Where(DebtCalculationHelper.IsPayableInstallment)
                    .OrderBy(k => k.NgayDenHan)
                    .ToList();
                var overdueKyHans = unpaidKyHans.Where(k => DebtCalculationHelper.DaysPastDue(k, today) > 0).ToList();
                int maxDaysPastDue = overdueKyHans.Select(k => DebtCalculationHelper.DaysPastDue(k, today)).DefaultIfEmpty().Max();
                decimal phiPhat = overdueKyHans.Sum(k => k.TienPhat);
                int tier = DebtCalculationHelper.CalculateAgingTier(maxDaysPastDue);
                string agingTierName = DebtCalculationHelper.GetAgingTierName(tier);
                string nearestDueDate = unpaidKyHans.FirstOrDefault()?.NgayDenHan.ToString("dd/MM/yyyy") ?? "—";
                string statusText = ContractPaymentStatus.Label(hd.TrangThaiThanhToan);

                worksheet.Cell(currentRow, 1).Value = stt++;
                worksheet.Cell(currentRow, 2).Value = $"HD{hd.MaHopDong}";
                worksheet.Cell(currentRow, 3).Value = hd.KhachHang?.HoTen ?? "N/A";
                worksheet.Cell(currentRow, 4).Value = hd.KhachHang?.SoDienThoai ?? "";
                worksheet.Cell(currentRow, 5).Value = hd.KhachHang?.CCCD ?? "";
                worksheet.Cell(currentRow, 6).Value = hd.NgayBatDau.ToString("dd/MM/yyyy");
                worksheet.Cell(currentRow, 7).Value = hd.NgayKetThuc.ToString("dd/MM/yyyy");
                worksheet.Cell(currentRow, 8).Value = hd.TongTien;
                worksheet.Cell(currentRow, 9).Value = phiDenBu;
                worksheet.Cell(currentRow, 10).Value = tongPhaiThu;
                worksheet.Cell(currentRow, 11).Value = daThu;
                worksheet.Cell(currentRow, 12).Value = conNo;
                worksheet.Cell(currentRow, 13).Value = maxDaysPastDue;
                worksheet.Cell(currentRow, 14).Value = phiPhat;
                worksheet.Cell(currentRow, 15).Value = agingTierName;
                worksheet.Cell(currentRow, 16).Value = statusText;
                worksheet.Cell(currentRow, 17).Value = nearestDueDate;

                // Định dạng số tiền
                worksheet.Cell(currentRow, 8).Style.NumberFormat.Format = "#,##0";
                worksheet.Cell(currentRow, 9).Style.NumberFormat.Format = "#,##0";
                worksheet.Cell(currentRow, 10).Style.NumberFormat.Format = "#,##0";
                worksheet.Cell(currentRow, 11).Style.NumberFormat.Format = "#,##0";
                worksheet.Cell(currentRow, 12).Style.NumberFormat.Format = "#,##0";
                worksheet.Cell(currentRow, 13).Style.NumberFormat.Format = "#,##0";
                worksheet.Cell(currentRow, 14).Style.NumberFormat.Format = "#,##0";

                // Căn lề
                worksheet.Cell(currentRow, 1).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                worksheet.Cell(currentRow, 2).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                worksheet.Cell(currentRow, 3).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Left;
                worksheet.Cell(currentRow, 4).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                worksheet.Cell(currentRow, 5).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                worksheet.Cell(currentRow, 6).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                worksheet.Cell(currentRow, 7).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                worksheet.Cell(currentRow, 13).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                worksheet.Cell(currentRow, 15).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                worksheet.Cell(currentRow, 16).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                worksheet.Cell(currentRow, 17).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;

                // Nổi bật có điều kiện theo nhóm tuổi nợ
                if (tier == 4)
                {
                    worksheet.Row(currentRow).Style.Fill.BackgroundColor = XLColor.FromHtml("#FDE8E8");
                    worksheet.Cell(currentRow, 12).Style.Font.Bold = true;
                    worksheet.Cell(currentRow, 12).Style.Font.FontColor = XLColor.Red;
                }
                else if (tier == 3)
                {
                    worksheet.Row(currentRow).Style.Fill.BackgroundColor = XLColor.FromHtml("#FFF4E5");
                }
                else if (stt % 2 == 0) // Màu xen kẽ
                {
                    worksheet.Row(currentRow).Style.Fill.BackgroundColor = XLColor.FromHtml("#F8F9FA");
                }

                for (int c = 1; c <= headers.Length; c++)
                {
                    worksheet.Cell(currentRow, c).Style.Border.OutsideBorder = XLBorderStyleValues.Thin;
                    worksheet.Cell(currentRow, c).Style.Border.OutsideBorderColor = XLColor.FromHtml("#E0E0E0");
                }

                sumTongTien += hd.TongTien;
                sumPhiDenBu += phiDenBu;
                sumTongPhaiThu += tongPhaiThu;
                sumDaThu += daThu;
                sumConNo += conNo;
                sumPhiPhat += phiPhat;

                currentRow++;
            }

            // Dòng TỔNG CỘNG
            worksheet.Range(currentRow, 1, currentRow, 7).Merge();
            worksheet.Cell(currentRow, 1).Value = "TỔNG CỘNG";
            worksheet.Cell(currentRow, 1).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
            worksheet.Cell(currentRow, 1).Style.Font.Bold = true;

            worksheet.Cell(currentRow, 8).Value = sumTongTien;
            worksheet.Cell(currentRow, 9).Value = sumPhiDenBu;
            worksheet.Cell(currentRow, 10).Value = sumTongPhaiThu;
            worksheet.Cell(currentRow, 11).Value = sumDaThu;
            worksheet.Cell(currentRow, 12).Value = sumConNo;
            worksheet.Cell(currentRow, 14).Value = sumPhiPhat;

            for (int col = 8; col <= 14; col++)
            {
                if (col != 13)
                {
                    worksheet.Cell(currentRow, col).Style.NumberFormat.Format = "#,##0";
                    worksheet.Cell(currentRow, col).Style.Font.Bold = true;
                }
            }

            var totalRowRange = worksheet.Range(currentRow, 1, currentRow, headers.Length);
            totalRowRange.Style.Font.Bold = true;
            totalRowRange.Style.Fill.BackgroundColor = XLColor.FromHtml("#D9E1F2");
            totalRowRange.Style.Border.TopBorder = XLBorderStyleValues.Thin;
            totalRowRange.Style.Border.BottomBorder = XLBorderStyleValues.Double;

            // Tự căn chỉnh kích thước cột & cố định dòng tiêu đề
            worksheet.Columns().AdjustToContents();
            worksheet.SheetView.FreezeRows(headerRow);

            using var stream = new MemoryStream();
            workbook.SaveAs(stream);
            var content = stream.ToArray();
            string fileName = $"BaoCaoCongNo_{DateTime.Now:yyyyMMdd_HHmmss}.xlsx";
            return File(content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", fileName);
        }

        // Gửi thông báo nhắc nợ kỳ hạn thanh toán kèm mã VietQR và lưu lịch sử nhắc nợ
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> GuiNhacNo(int maKyHan)
        {
            var bank = RentalSystem.Services.BankTransfer.From(_configuration);
            var kyHan = await _context.KyHanThanhToans
                .Include(k => k.HopDong)
                .ThenInclude(h => h.KhachHang)
                .FirstOrDefaultAsync(k => k.MaKyHan == maKyHan);

            if (kyHan == null || kyHan.HopDong == null)
            {
                return Json(new { success = false, message = "Kỳ hạn không tồn tại" });
            }

            if (!DebtCalculationHelper.IsPayableInstallment(kyHan) || DebtCalculationHelper.GetInstallmentBalance(kyHan) <= 0)
            {
                return Json(new { success = false, message = "Kỳ hạn không còn khoản cần nhắc nợ." });
            }

            int count = await _context.LichSuNhacNos.CountAsync(l => l.MaKyHan == maKyHan);
            int lanNhacThu = count + 1;

            decimal soTienNhac = (kyHan.SoTienPhai - kyHan.SoTienDaTra) + kyHan.TienPhat;
            long soTienNhacLong = (long)Math.Max(0m, soTienNhac);

            string vietQrUrl = bank.QrUrl(soTienNhacLong, $"HD{kyHan.HopDong.MaHopDong} KY{kyHan.SoKyHan}");

            int? nguoiGuiId = null;
            var userIdClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            if (userIdClaim != null && int.TryParse(userIdClaim.Value, out int adminId))
            {
                nguoiGuiId = adminId;
            }

            var lichSu = new LichSuNhacNo
            {
                MaHopDong = kyHan.MaHopDong,
                MaKyHan = kyHan.MaKyHan,
                NgayNhac = DateTime.Now,
                HinhThucNhac = "Thông báo hệ thống & VietQR",
                SoTienNhac = soTienNhac,
                LanNhacThu = lanNhacThu,
                NoiDung = $"Nhắc nợ kỳ hạn {kyHan.SoKyHan} hợp đồng HD{kyHan.HopDong.MaHopDong}. Số tiền: {soTienNhac:N0}đ (Gốc: {(kyHan.SoTienPhai - kyHan.SoTienDaTra):N0}đ, Phạt: {kyHan.TienPhat:N0}đ). {bank.BankName}: {bank.AccountNumber} - {bank.AccountName}.",
                NguoiGuiId = nguoiGuiId
            };
            _context.LichSuNhacNos.Add(lichSu);

            var thongBao = new ThongBao
            {
                MaNguoiDung = kyHan.HopDong.MaKhachHang,
                TieuDe = $"[Nhắc nợ] Kỳ hạn {kyHan.SoKyHan} hợp đồng HD{kyHan.HopDong.MaHopDong}",
                NoiDung = $"Kỳ hạn {kyHan.SoKyHan} của bạn đã quá hạn hoặc sắp đến hạn. Số tiền cần thanh toán: {soTienNhac:N0}đ. Vui lòng thanh toán qua {bank.BankName} {bank.AccountNumber} ({bank.AccountName}) hoặc kiểm tra Sổ công nợ.",
                NgayTao = DateTime.Now,
                DaDoc = false,
                LoaiThongBao = "NhacNo",
                LienKet = "/Account/MyDebt"
            };
            _context.ThongBaos.Add(thongBao);

            await _context.SaveChangesAsync();

            return Json(new 
            { 
                success = true, 
                lanNhac = lanNhacThu, 
                message = $"Đã gửi thông báo nhắc nợ lần {lanNhacThu} thành công!",
                vietQrUrl = vietQrUrl
            });
        }
    }
}
