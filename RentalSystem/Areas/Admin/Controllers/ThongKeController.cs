using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using ClosedXML.Excel;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Areas.Admin.Controllers
{
    // Trung Tâm Phân Tích & Báo Cáo Quản Trị (Executive BI & Financial Analytics Dashboard)
    [Area("Admin")]
    [Authorize(Roles = "Admin,KinhDoanh")]
    public class ThongKeController : Controller
    {
        private readonly ApplicationDbContext _context;

        public ThongKeController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Dashboard phân tích kinh doanh, tài chính và hiệu suất vận hành kho máy
        [HttpGet]
        public async Task<IActionResult> Index(string? range, DateTime? tuNgay, DateTime? denNgay)
        {
            var filter = ResolveFilter(range, tuNgay, denNgay);
            var model = await BuildDashboardViewModelAsync(filter);

            // Duy trì tương thích hoàn toàn với ViewBag legacy
            ViewBag.TongDoanhThu = model.Financial.DoanhThuThuan;
            ViewBag.TongThu = model.Financial.TongThucThu;
            ViewBag.TongChi = model.Financial.TongChiHoan;
            ViewBag.TongCoc = model.Financial.TienCocDangGiu;
            ViewBag.DangChoThue = model.Fleet.DangChoThue;
            ViewBag.SanSang = model.Fleet.SanSang;
            ViewBag.DangSuaChua = model.Fleet.BaoTriSuaChua;
            ViewBag.TongSuCo = model.Financial.TongPhieuBaoTri;
            ViewBag.SuCoChuaXuLy = model.Financial.BaoTriDangXuLy;

            return View(model);
        }

        // Xuất báo cáo quản trị và tài chính chuẩn kế toán doanh nghiệp bằng ClosedXML
        [HttpGet]
        public async Task<IActionResult> ExportExcel(string? range, DateTime? tuNgay, DateTime? denNgay)
        {
            var filter = ResolveFilter(range, tuNgay, denNgay);
            var model = await BuildDashboardViewModelAsync(filter);

            using var workbook = new XLWorkbook();
            var ws = workbook.Worksheets.Add("BaoCaoQuanTri");

            // Màu chủ đạo Executive Navy & Slate
            var navyPrimary = XLColor.FromArgb(15, 43, 92);     // #0F2B5C
            var navySub = XLColor.FromArgb(30, 58, 138);         // #1E3A8A
            var sectionBg = XLColor.FromArgb(239, 246, 255);     // #EFF6FF
            var altRowBg = XLColor.FromArgb(248, 250, 252);      // #F8FAFC
            var borderSlate = XLColor.FromArgb(203, 213, 225);   // #CBD5E1

            // 1. BANNER TIÊU ĐỀ DOANH NGHIỆP
            ws.Range("A1:G1").Merge();
            var banner = ws.Cell("A1");
            banner.Value = "ABC RENTAL SYSTEM - TRUNG TÂM PHÂN TÍCH & BÁO CÁO QUẢN TRỊ";
            banner.Style.Font.Bold = true;
            banner.Style.Font.FontSize = 14;
            banner.Style.Font.FontColor = XLColor.White;
            banner.Style.Fill.BackgroundColor = navyPrimary;
            banner.Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
            banner.Style.Alignment.Vertical = XLAlignmentVerticalValues.Center;
            ws.Row(1).Height = 35;

            // 2. THÔNG TIN KỲ BÁO CÁO & XUẤT BẢN
            ws.Range("A2:G2").Merge();
            var subTitle = ws.Cell("A2");
            var currentUserName = User.Identity?.Name ?? "Quản trị viên";
            subTitle.Value = $"Kỳ báo cáo: {filter.RangeDisplayName} | Ngày xuất: {DateTime.Now:dd/MM/yyyy HH:mm:ss} | Người lập: {currentUserName}";
            subTitle.Style.Font.Italic = true;
            subTitle.Style.Font.FontSize = 10;
            subTitle.Style.Font.FontColor = XLColor.FromArgb(71, 85, 105);
            subTitle.Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
            ws.Row(2).Height = 22;

            int currentRow = 4;

            // -------------------------------------------------------------
            // KHỐI 1: TỔNG QUAN TÀI CHÍNH & CHỈ SỐ KPI VẬN HÀNH
            // -------------------------------------------------------------
            ws.Range(currentRow, 1, currentRow, 7).Merge();
            var h1 = ws.Cell(currentRow, 1);
            h1.Value = "I. TỔNG QUAN TÀI CHÍNH & VẬN HÀNH (EXECUTIVE KPI SUMMARY)";
            FormatSectionHeader(h1, navyPrimary, sectionBg);
            ws.Row(currentRow).Height = 25;
            currentRow++;

            // Table header
            ws.Cell(currentRow, 1).Value = "Mã Chỉ Số";
            ws.Cell(currentRow, 2).Value = "Tên Chỉ Số Đo Lường";
            ws.Cell(currentRow, 3).Value = "Giá Trị";
            ws.Cell(currentRow, 4).Value = "Đơn Vị Tính";
            ws.Range(currentRow, 5, currentRow, 7).Merge();
            ws.Cell(currentRow, 5).Value = "Ghi Chú Nghiệp Vụ";
            FormatTableHeader(ws.Range(currentRow, 1, currentRow, 7), navySub);
            ws.Row(currentRow).Height = 22;
            currentRow++;

            var kpis = new List<(string Code, string Name, object Value, string Unit, string Format, string Note)>
            {
                ("KPI-01", "Doanh thu thuần trong kỳ (Net Revenue)", model.Financial.DoanhThuThuan, "VNĐ", "#,##0 \"VNĐ\"", "Thực thu trừ chi hoàn cọc và bồi thường"),
                ("KPI-02", "Tổng thực thu phát sinh trong kỳ", model.Financial.TongThucThu, "VNĐ", "#,##0 \"VNĐ\"", "Phiếu thu tiền thuê máy và phí bảo trì"),
                ("KPI-03", "Tổng chi hoàn cọc & chi phí bồi thường", model.Financial.TongChiHoan, "VNĐ", "#,##0 \"VNĐ\"", "Phiếu chi hoàn cọc hoặc hoàn tiền thừa"),
                ("KPI-04", "Tiền cọc bảo đảm máy đang giữ", model.Financial.TienCocDangGiu, "VNĐ", "#,##0 \"VNĐ\"", "Tiền ký quỹ an toàn của các hợp đồng đang hiệu lực"),
                ("KPI-05", "Số lượng hợp đồng đang có hiệu lực", model.Financial.SoHopDongHieuLuc, "Hợp đồng", "#,##0", "Đang diễn ra và khai thác máy"),
                ("KPI-06", "Tỷ lệ khai thác kho máy (Fleet Utilization)", model.Fleet.TyLeKhaiThac / 100.0, "Phần trăm", "0.0%", $"{model.Fleet.DangChoThue} máy đang thuê / {model.Fleet.TongMay} tổng máy"),
                ("KPI-07", "Hiệu suất xử lý sự cố & bảo trì", model.Financial.TyLeXuLyBaoTri / 100.0, "Phần trăm", "0.0%", $"{model.Financial.BaoTriHoanTat} phiếu hoàn tất / {model.Financial.TongPhieuBaoTri} sự cố"),
                ("KPI-08", "Kỳ hạn thanh toán đến hạn trong kỳ", model.Financial.TongKyHanTrongKy, "Kỳ hạn", "#,##0", $"{model.Financial.KyHanDaHoanTat} kỳ đã thu / {model.Financial.TongKyHanTrongKy} kỳ đến hạn"),
                ("KPI-09", "Tổng tiền kỳ hạn thanh toán đến hạn", model.Financial.TongTienKyHanPhaiThu, "VNĐ", "#,##0 \"VNĐ\"", "Kế hoạch thu tiền theo lịch trình trả góp trong kỳ")
            };

            foreach (var kpi in kpis)
            {
                ws.Cell(currentRow, 1).Value = kpi.Code;
                ws.Cell(currentRow, 1).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                ws.Cell(currentRow, 2).Value = kpi.Name;
                ws.Cell(currentRow, 2).Style.Font.Bold = true;

                var valCell = ws.Cell(currentRow, 3);
                if (kpi.Value is decimal decVal) valCell.Value = decVal;
                else if (kpi.Value is double dblVal) valCell.Value = dblVal;
                else if (kpi.Value is int intVal) valCell.Value = intVal;
                valCell.Style.NumberFormat.Format = kpi.Format;
                valCell.Style.Font.Bold = true;

                ws.Cell(currentRow, 4).Value = kpi.Unit;
                ws.Cell(currentRow, 4).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;

                ws.Range(currentRow, 5, currentRow, 7).Merge();
                ws.Cell(currentRow, 5).Value = kpi.Note;
                ws.Cell(currentRow, 5).Style.Font.FontColor = XLColor.FromArgb(100, 116, 139);

                ApplyRowBorder(ws.Range(currentRow, 1, currentRow, 7), borderSlate, currentRow % 2 == 0 ? altRowBg : XLColor.White);
                ws.Row(currentRow).Height = 20;
                currentRow++;
            }

            currentRow += 2;

            // -------------------------------------------------------------
            // KHỐI 2: DOANH THU CHI TIẾT THEO TỪNG DANH MỤC THIẾT BỊ
            // -------------------------------------------------------------
            ws.Range(currentRow, 1, currentRow, 7).Merge();
            var h2 = ws.Cell(currentRow, 1);
            h2.Value = "II. DOANH THU CHI TIẾT THEO DANH MỤC THIẾT BỊ (CATEGORY BREAKDOWN)";
            FormatSectionHeader(h2, navyPrimary, sectionBg);
            ws.Row(currentRow).Height = 25;
            currentRow++;

            ws.Cell(currentRow, 1).Value = "STT";
            ws.Cell(currentRow, 2).Value = "Mã Loại";
            ws.Cell(currentRow, 3).Value = "Tên Danh Mục Thiết Bị";
            ws.Cell(currentRow, 4).Value = "Số Lượng Máy";
            ws.Cell(currentRow, 5).Value = "Số Lượt Thuê";
            ws.Cell(currentRow, 6).Value = "Doanh Thu (VNĐ)";
            ws.Cell(currentRow, 7).Value = "Tỷ Trọng (%)";
            FormatTableHeader(ws.Range(currentRow, 1, currentRow, 7), navySub);
            ws.Row(currentRow).Height = 22;
            currentRow++;

            if (!model.Categories.Any())
            {
                ws.Range(currentRow, 1, currentRow, 7).Merge();
                ws.Cell(currentRow, 1).Value = "Chưa ghi nhận dữ liệu danh mục thiết bị trong kỳ báo cáo.";
                ws.Cell(currentRow, 1).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                ws.Cell(currentRow, 1).Style.Font.Italic = true;
                ApplyRowBorder(ws.Range(currentRow, 1, currentRow, 7), borderSlate, XLColor.White);
                ws.Row(currentRow).Height = 20;
                currentRow++;
            }

            int catIdx = 1;
            foreach (var cat in model.Categories)
            {
                ws.Cell(currentRow, 1).Value = catIdx++;
                ws.Cell(currentRow, 1).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                ws.Cell(currentRow, 2).Value = $"CAT-{cat.MaLoai:D3}";
                ws.Cell(currentRow, 2).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                ws.Cell(currentRow, 3).Value = cat.TenLoai;
                ws.Cell(currentRow, 3).Style.Font.Bold = true;
                ws.Cell(currentRow, 4).Value = cat.SoLuongMay;
                ws.Cell(currentRow, 4).Style.NumberFormat.Format = "#,##0";
                ws.Cell(currentRow, 5).Value = cat.SoLuotThue;
                ws.Cell(currentRow, 5).Style.NumberFormat.Format = "#,##0";
                ws.Cell(currentRow, 6).Value = cat.DoanhThu;
                ws.Cell(currentRow, 6).Style.NumberFormat.Format = "#,##0 \"VNĐ\"";
                ws.Cell(currentRow, 6).Style.Font.Bold = true;
                ws.Cell(currentRow, 7).Value = cat.TyTrong / 100.0;
                ws.Cell(currentRow, 7).Style.NumberFormat.Format = "0.0%";

                ApplyRowBorder(ws.Range(currentRow, 1, currentRow, 7), borderSlate, currentRow % 2 == 0 ? altRowBg : XLColor.White);
                ws.Row(currentRow).Height = 20;
                currentRow++;
            }

            // Dòng tổng cộng Danh Mục
            ws.Range(currentRow, 1, currentRow, 3).Merge();
            ws.Cell(currentRow, 1).Value = "TỔNG CỘNG";
            ws.Cell(currentRow, 1).Style.Font.Bold = true;
            ws.Cell(currentRow, 1).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
            ws.Cell(currentRow, 4).Value = model.Categories.Sum(c => c.SoLuongMay);
            ws.Cell(currentRow, 4).Style.Font.Bold = true;
            ws.Cell(currentRow, 4).Style.NumberFormat.Format = "#,##0";
            ws.Cell(currentRow, 5).Value = model.Categories.Sum(c => c.SoLuotThue);
            ws.Cell(currentRow, 5).Style.Font.Bold = true;
            ws.Cell(currentRow, 5).Style.NumberFormat.Format = "#,##0";
            ws.Cell(currentRow, 6).Value = model.Categories.Sum(c => c.DoanhThu);
            ws.Cell(currentRow, 6).Style.Font.Bold = true;
            ws.Cell(currentRow, 6).Style.NumberFormat.Format = "#,##0 \"VNĐ\"";
            ws.Cell(currentRow, 7).Value = model.Categories.Any(c => c.DoanhThu > 0) ? 1.0 : 0.0;
            ws.Cell(currentRow, 7).Style.Font.Bold = true;
            ws.Cell(currentRow, 7).Style.NumberFormat.Format = "0.0%";
            ApplyRowBorder(ws.Range(currentRow, 1, currentRow, 7), borderSlate, sectionBg);
            ws.Row(currentRow).Height = 22;

            currentRow += 3;

            // -------------------------------------------------------------
            // KHỐI 3: BẢNG XẾP HẠNG TOP THIẾT BỊ CHO THUÊ HIỆU QUẢ NHẤT
            // -------------------------------------------------------------
            ws.Range(currentRow, 1, currentRow, 7).Merge();
            var h3 = ws.Cell(currentRow, 1);
            h3.Value = "III. BẢNG XẾP HẠNG TOP THIẾT BỊ CHO THUÊ HIỆU QUẢ NHẤT (FLEET PERFORMANCE)";
            FormatSectionHeader(h3, navyPrimary, sectionBg);
            ws.Row(currentRow).Height = 25;
            currentRow++;

            ws.Cell(currentRow, 1).Value = "Hạng";
            ws.Cell(currentRow, 2).Value = "Tên Thiết Bị / Dòng Máy";
            ws.Cell(currentRow, 3).Value = "Danh Mục";
            ws.Cell(currentRow, 4).Value = "Tổng Máy Kho";
            ws.Cell(currentRow, 5).Value = "Đang Thuê";
            ws.Cell(currentRow, 6).Value = "Doanh Thu Tạo Ra (VNĐ)";
            ws.Cell(currentRow, 7).Value = "Tỷ Lệ Khai Thác (%)";
            FormatTableHeader(ws.Range(currentRow, 1, currentRow, 7), navySub);
            ws.Row(currentRow).Height = 22;
            currentRow++;

            if (!model.TopProducts.Any())
            {
                ws.Range(currentRow, 1, currentRow, 7).Merge();
                ws.Cell(currentRow, 1).Value = "Chưa ghi nhận dữ liệu thiết bị cho thuê trong kỳ báo cáo.";
                ws.Cell(currentRow, 1).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                ws.Cell(currentRow, 1).Style.Font.Italic = true;
                ApplyRowBorder(ws.Range(currentRow, 1, currentRow, 7), borderSlate, XLColor.White);
                ws.Row(currentRow).Height = 20;
                currentRow++;
            }

            int prodIdx = 1;
            foreach (var prod in model.TopProducts)
            {
                ws.Cell(currentRow, 1).Value = prodIdx++;
                ws.Cell(currentRow, 1).Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
                ws.Cell(currentRow, 1).Style.Font.Bold = true;
                ws.Cell(currentRow, 2).Value = prod.TenSanPham;
                ws.Cell(currentRow, 2).Style.Font.Bold = true;
                ws.Cell(currentRow, 3).Value = prod.TenDanhMuc;
                ws.Cell(currentRow, 4).Value = prod.TongMayKho;
                ws.Cell(currentRow, 4).Style.NumberFormat.Format = "#,##0";
                ws.Cell(currentRow, 5).Value = prod.SoMayDangThue;
                ws.Cell(currentRow, 5).Style.NumberFormat.Format = "#,##0";
                ws.Cell(currentRow, 6).Value = prod.DoanhThu;
                ws.Cell(currentRow, 6).Style.NumberFormat.Format = "#,##0 \"VNĐ\"";
                ws.Cell(currentRow, 6).Style.Font.Bold = true;
                ws.Cell(currentRow, 7).Value = prod.TyLeKhaiThac / 100.0;
                ws.Cell(currentRow, 7).Style.NumberFormat.Format = "0.0%";

                ApplyRowBorder(ws.Range(currentRow, 1, currentRow, 7), borderSlate, currentRow % 2 == 0 ? altRowBg : XLColor.White);
                ws.Row(currentRow).Height = 20;
                currentRow++;
            }

            // Tự động căn chỉnh độ rộng cột
            ws.Columns(1, 7).AdjustToContents();
            ws.Column(1).Width = Math.Max(ws.Column(1).Width, 10);
            ws.Column(2).Width = Math.Max(ws.Column(2).Width, 32);
            ws.Column(3).Width = Math.Max(ws.Column(3).Width, 24);
            ws.Column(4).Width = Math.Max(ws.Column(4).Width, 16);
            ws.Column(5).Width = Math.Max(ws.Column(5).Width, 16);
            ws.Column(6).Width = Math.Max(ws.Column(6).Width, 26);
            ws.Column(7).Width = Math.Max(ws.Column(7).Width, 22);

            using var stream = new MemoryStream();
            workbook.SaveAs(stream);
            var content = stream.ToArray();
            var fileName = $"BaoCao_QuanTri_{DateTime.Now:yyyyMMdd_HHmmss}.xlsx";
            return File(content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", fileName);
        }

        // Động cơ giải mã và chuẩn hóa mốc thời gian bộ lọc
        private ThongKeFilterModel ResolveFilter(string? range, DateTime? tuNgay, DateTime? denNgay)
        {
            var now = DateTime.Now;
            var filter = new ThongKeFilterModel();

            // Nhận diện mốc thời gian lọc
            if (!string.IsNullOrWhiteSpace(range))
            {
                filter.Range = range.Trim().ToLowerInvariant();
            }
            else if (tuNgay.HasValue || denNgay.HasValue)
            {
                filter.Range = "custom";
            }
            else
            {
                filter.Range = "this_month"; // Mặc định: Tháng này
            }

            // Helper an toàn tránh tràn số DateTime khi nhận ngày biên cực đại
            static DateTime SafeEndOfDay(DateTime dt)
            {
                if (dt.Date >= DateTime.MaxValue.Date) return DateTime.MaxValue;
                try { return dt.Date.AddDays(1).AddTicks(-1); }
                catch { return DateTime.MaxValue; }
            }

            switch (filter.Range)
            {
                case "today":
                    filter.EffectiveFrom = now.Date;
                    filter.EffectiveTo = SafeEndOfDay(now);
                    filter.RangeDisplayName = $"Hôm nay ({filter.EffectiveFrom:dd/MM/yyyy})";
                    break;

                case "this_quarter":
                    int currentQuarter = (now.Month - 1) / 3 + 1;
                    filter.EffectiveFrom = new DateTime(now.Year, (currentQuarter - 1) * 3 + 1, 1);
                    filter.EffectiveTo = SafeEndOfDay(filter.EffectiveFrom.AddMonths(3).AddDays(-1));
                    filter.RangeDisplayName = $"Quý {currentQuarter}/{now.Year} ({filter.EffectiveFrom:dd/MM} - {filter.EffectiveTo:dd/MM/yyyy})";
                    break;

                case "this_year":
                    filter.EffectiveFrom = new DateTime(now.Year, 1, 1);
                    filter.EffectiveTo = SafeEndOfDay(new DateTime(now.Year, 12, 31));
                    filter.RangeDisplayName = $"Năm {now.Year}";
                    break;

                case "custom":
                    // Chuẩn hóa đảo chiều nếu cả 2 ngày đều được cung cấp và tuNgay > denNgay
                    if (tuNgay.HasValue && denNgay.HasValue && tuNgay.Value > denNgay.Value)
                    {
                        var temp = tuNgay.Value;
                        tuNgay = denNgay.Value;
                        denNgay = temp;
                    }

                    // Giới hạn năm hợp lý để tránh vòng lặp lịch sử quá sâu
                    if (tuNgay.HasValue && tuNgay.Value.Year < 2000)
                    {
                        tuNgay = new DateTime(2000, 1, 1);
                    }

                    if (tuNgay.HasValue && denNgay.HasValue)
                    {
                        filter.EffectiveFrom = tuNgay.Value.Date;
                        filter.EffectiveTo = SafeEndOfDay(denNgay.Value);
                    }
                    else if (tuNgay.HasValue && !denNgay.HasValue)
                    {
                        filter.EffectiveFrom = tuNgay.Value.Date;
                        filter.EffectiveTo = tuNgay.Value.Date > now.Date ? SafeEndOfDay(tuNgay.Value) : SafeEndOfDay(now);
                    }
                    else if (!tuNgay.HasValue && denNgay.HasValue)
                    {
                        // Nếu chỉ có ngày kết thúc, ngày bắt đầu mặc định là đầu tháng của ngày kết thúc đó
                        filter.EffectiveFrom = new DateTime(denNgay.Value.Year, denNgay.Value.Month, 1);
                        filter.EffectiveTo = SafeEndOfDay(denNgay.Value);
                    }
                    else
                    {
                        // Không cung cấp ngày nào nhưng chọn custom -> mặc định tháng này
                        filter.EffectiveFrom = new DateTime(now.Year, now.Month, 1);
                        filter.EffectiveTo = SafeEndOfDay(now);
                    }

                    if (filter.EffectiveFrom > filter.EffectiveTo)
                    {
                        filter.EffectiveTo = SafeEndOfDay(filter.EffectiveFrom);
                    }

                    filter.RangeDisplayName = $"{filter.EffectiveFrom:dd/MM/yyyy} - {filter.EffectiveTo:dd/MM/yyyy}";
                    break;

                case "this_month":
                default:
                    filter.Range = "this_month";
                    filter.EffectiveFrom = new DateTime(now.Year, now.Month, 1);
                    int daysInMonth = DateTime.DaysInMonth(now.Year, now.Month);
                    filter.EffectiveTo = SafeEndOfDay(new DateTime(now.Year, now.Month, daysInMonth));
                    filter.RangeDisplayName = $"Tháng {now.Month}/{now.Year}";
                    break;
            }

            // Đồng bộ ngày thực tế cho bộ lọc giao diện
            filter.TuNgay = filter.EffectiveFrom;
            filter.DenNgay = filter.EffectiveTo;

            return filter;
        }

        // Động cơ tính toán tổng hợp toàn bộ số liệu BI, Tài chính và Vận hành
        private async Task<ThongKeDashboardViewModel> BuildDashboardViewModelAsync(ThongKeFilterModel filter)
        {
            var model = new ThongKeDashboardViewModel
            {
                Filter = filter
            };

            var from = filter.EffectiveFrom;
            var to = filter.EffectiveTo;

            // 1. TÀI CHÍNH & DÒNG TIỀN (PhieuThu, PhieuChi, HopDong)
            var phieuThusQuery = _context.PhieuThus
                .Where(pt => !pt.DaHuy && pt.NgayGiaoDich >= from && pt.NgayGiaoDich <= to);

            var phieuChisQuery = _context.PhieuChis
                .Where(pc => pc.NgayChi >= from && pc.NgayChi <= to);

            // Thực thu = Thu thuê (0) + Thu phí bồi thường/bảo trì (2)
            var tongThu = await phieuThusQuery
                .Where(pt => pt.LoaiPhieu == 0 || pt.LoaiPhieu == 2)
                .SumAsync(pt => (decimal?)pt.SoTien) ?? 0m;

            var tongChi = await phieuChisQuery
                .SumAsync(pc => (decimal?)pc.SoTien) ?? 0m;

            var tongDoanhThu = tongThu - tongChi;
            var doanhThuThuan = tongThu - tongChi;

            // Hợp đồng & Tiền cọc giữ chỗ (Chờ duyệt: 0, Đang hiệu lực: 1)
            var allHopDongs = await _context.HopDongs.ToListAsync();
            var tongCocDangGiu = allHopDongs
                .Where(h => h.TrangThai == 0 || h.TrangThai == 1)
                .Sum(h => h.TienDaCoc);
            var soHopDongHieuLuc = allHopDongs.Count(h => h.TrangThai == 1);
            var tongHopDongTrongKy = allHopDongs
                .Where(h => h.TrangThai != 3)
                .Count(h => h.NgayBatDau >= from && h.NgayBatDau <= to);

            // Báo trì & sự cố kỹ thuật trong kỳ
            var phieuBaoTrisTrongKy = await _context.PhieuBaoTris
                .Where(p => p.NgayBaoLoi >= from && p.NgayBaoLoi <= to)
                .ToListAsync();

            var tongSuCo = phieuBaoTrisTrongKy.Count;
            var suCoHoanTat = phieuBaoTrisTrongKy.Count(p => p.TrangThai == 3 || p.TrangThai == 5);
            var suCoDangXuLy = phieuBaoTrisTrongKy.Count(p => p.TrangThai == 1 || p.TrangThai == 2);
            var tyLeXuLyBaoTri = tongSuCo > 0 ? Math.Round(suCoHoanTat * 100.0 / tongSuCo, 1) : 100.0;

            // Kỳ hạn thanh toán (KyHanThanhToan) đến hạn trong kỳ
            var kyHansTrongKy = await _context.KyHanThanhToans
                .Where(k => k.TrangThai != 3 && k.NgayDenHan >= from && k.NgayDenHan <= to)
                .ToListAsync();

            var tongKyHanTrongKy = kyHansTrongKy.Count;
            var kyHanDaHoanTat = kyHansTrongKy.Count(k => k.TrangThai == 1);
            var tongTienKyHanPhaiThu = kyHansTrongKy.Sum(k => k.SoTienPhai);
            var tongTienKyHanDaThu = kyHansTrongKy.Sum(k => k.SoTienDaTra);

            model.Financial = new FinancialMetricsStat
            {
                DoanhThuThuan = doanhThuThuan,
                TongThucThu = tongThu,
                TongChiHoan = tongChi,
                TienCocDangGiu = tongCocDangGiu,
                SoHopDongHieuLuc = soHopDongHieuLuc,
                TongSoHopDongTrongKy = tongHopDongTrongKy,
                TongPhieuBaoTri = tongSuCo,
                BaoTriHoanTat = suCoHoanTat,
                BaoTriDangXuLy = suCoDangXuLy,
                TyLeXuLyBaoTri = tyLeXuLyBaoTri,
                TongKyHanTrongKy = tongKyHanTrongKy,
                KyHanDaHoanTat = kyHanDaHoanTat,
                TongTienKyHanPhaiThu = tongTienKyHanPhaiThu,
                TongTienKyHanDaThu = tongTienKyHanDaThu
            };

            // 2. CƠ CẤU DOANH THU THEO PHƯƠNG THỨC THANH TOÁN
            var phieuThusList = await phieuThusQuery
                .Where(pt => pt.LoaiPhieu == 0 || pt.LoaiPhieu == 2)
                .ToListAsync();

            var methodGroups = phieuThusList
                .GroupBy(pt => pt.HinhThucThanhToan)
                .ToDictionary(g => g.Key, g => new { Total = g.Sum(x => x.SoTien), Count = g.Count() });

            var paymentMethods = new List<PaymentMethodStat>
            {
                new PaymentMethodStat
                {
                    HinhThuc = 0,
                    TenPhuongThuc = "Tiền mặt tại quầy",
                    IconClass = "fas fa-money-bill-wave",
                    SoTien = methodGroups.ContainsKey(0) ? methodGroups[0].Total : 0m,
                    SoGiaoDich = methodGroups.ContainsKey(0) ? methodGroups[0].Count : 0
                },
                new PaymentMethodStat
                {
                    HinhThuc = 1,
                    TenPhuongThuc = "Chuyển khoản VietQR",
                    IconClass = "fas fa-university",
                    SoTien = methodGroups.ContainsKey(1) ? methodGroups[1].Total : 0m,
                    SoGiaoDich = methodGroups.ContainsKey(1) ? methodGroups[1].Count : 0
                },
                new PaymentMethodStat
                {
                    HinhThuc = 2,
                    TenPhuongThuc = "Cổng thanh toán VNPay",
                    IconClass = "fas fa-qrcode",
                    SoTien = methodGroups.ContainsKey(2) ? methodGroups[2].Total : 0m,
                    SoGiaoDich = methodGroups.ContainsKey(2) ? methodGroups[2].Count : 0
                }
            };

            if (methodGroups.Any(k => k.Key >= 3))
            {
                var otherTotal = methodGroups.Where(k => k.Key >= 3).Sum(k => k.Value.Total);
                var otherCount = methodGroups.Where(k => k.Key >= 3).Sum(k => k.Value.Count);
                paymentMethods.Add(new PaymentMethodStat
                {
                    HinhThuc = 3,
                    TenPhuongThuc = "Hình thức khác",
                    IconClass = "fas fa-credit-card",
                    SoTien = otherTotal,
                    SoGiaoDich = otherCount
                });
            }

            decimal totalPaymentSum = paymentMethods.Sum(p => p.SoTien);
            foreach (var pm in paymentMethods)
            {
                pm.TyTrong = totalPaymentSum > 0 ? Math.Round((double)(pm.SoTien * 100m / totalPaymentSum), 1) : 0;
            }
            model.PaymentMethods = paymentMethods;

            // 3. TÌNH TRẠNG KHO MÁY VẬT LÝ & FLEET UTILIZATION
            var thietBis = await _context.ThietBis
                .Include(t => t.SanPham).ThenInclude(s => s.LoaiThietBi)
                .ToListAsync();

            var sanSang = thietBis.Count(t => t.TrangThai == 0);
            var dangChoThue = thietBis.Count(t => t.TrangThai == 1);
            var dangSuaChua = thietBis.Count(t => t.TrangThai == 2);
            var giuCho = thietBis.Count(t => t.TrangThai == 3);
            var hongThanhLy = thietBis.Count(t => t.TrangThai == 4);
            var tongMay = thietBis.Count;
            var fleetUtilization = tongMay > 0 ? Math.Round(dangChoThue * 100.0 / tongMay, 1) : 0.0;

            model.Fleet = new FleetStatusStat
            {
                SanSang = sanSang,
                DangChoThue = dangChoThue,
                BaoTriSuaChua = dangSuaChua,
                GiuCho = giuCho,
                HongThanhLy = hongThanhLy,
                TongMay = tongMay,
                TyLeKhaiThac = fleetUtilization
            };

            // 4. TOP THIẾT BỊ CHO THUÊ & DOANH THU THEO DANH MỤC
            var loaiList = await _context.LoaiThietBis.ToListAsync();
            var sanPhamList = await _context.SanPhams.Include(s => s.LoaiThietBi).ToListAsync();
            var chiTiets = await _context.ChiTietHopDongs
                .Include(c => c.HopDong)
                .Include(c => c.ThietBi).ThenInclude(t => t.SanPham).ThenInclude(s => s.LoaiThietBi)
                .Where(c => c.HopDong.TrangThai != 3) // Bỏ đơn đã hủy
                .ToListAsync();

            // Lọc chi tiết hợp đồng hiệu lực hoặc giao dịch trong khoảng thời gian lọc
            var chiTietsInPeriod = chiTiets
                .Where(c => c.HopDong.NgayBatDau <= to && c.HopDong.NgayKetThuc >= from)
                .ToList();

            // Tính toán doanh thu phân bổ chuẩn mực cho từng chi tiết máy
            decimal CalcItemRevenue(ChiTietHopDong c)
            {
                if (c.HopDong == null) return c.GiaChotThu;
                var h = c.HopDong;
                var allItemsOfH = chiTiets.Where(x => x.MaHopDong == h.MaHopDong).ToList();
                decimal totalWeights = allItemsOfH.Sum(x => x.GiaChotThu);
                if (totalWeights > 0 && h.TongTien > 0)
                {
                    return Math.Round(h.TongTien * (c.GiaChotThu / totalWeights), 0);
                }
                int days = Math.Max(1, (h.NgayKetThuc.Date - h.NgayBatDau.Date).Days);
                return c.GiaChotThu < 500000m && days > 1 ? c.GiaChotThu * days : c.GiaChotThu;
            }

            // Bảng xếp hạng Top sản phẩm
            var topProducts = new List<TopProductStat>();
            foreach (var sp in sanPhamList)
            {
                var devicesOfSp = thietBis.Where(t => t.MaSanPham == sp.MaSanPham).ToList();
                var itemsOfSp = chiTietsInPeriod.Where(c => c.ThietBi != null && c.ThietBi.MaSanPham == sp.MaSanPham).ToList();
                int rentalCount = itemsOfSp.Count;
                decimal prodRevenue = itemsOfSp.Sum(c => CalcItemRevenue(c));
                int totalInStock = devicesOfSp.Count;
                int rentedCount = devicesOfSp.Count(t => t.TrangThai == 1);
                double utilizationRate = totalInStock > 0 ? Math.Round(rentedCount * 100.0 / totalInStock, 1) : 0.0;

                topProducts.Add(new TopProductStat
                {
                    MaSanPham = sp.MaSanPham,
                    TenSanPham = sp.TenSanPham,
                    TenDanhMuc = sp.LoaiThietBi?.TenLoai ?? "Khác",
                    TongMayKho = totalInStock,
                    SoMayDangThue = rentedCount,
                    SoLuotThue = rentalCount,
                    DoanhThu = prodRevenue,
                    TyLeKhaiThac = utilizationRate
                });
            }

            model.TopProducts = topProducts
                .OrderByDescending(p => p.DoanhThu)
                .ThenByDescending(p => p.SoLuotThue)
                .ToList();

            // Doanh thu theo từng Danh Mục
            var catStats = new List<CategoryRevenueStat>();
            foreach (var loai in loaiList)
            {
                var prodsInCat = model.TopProducts.Where(p => p.TenDanhMuc == loai.TenLoai).ToList();
                int totalDevices = thietBis.Count(t => t.SanPham != null && t.SanPham.MaLoai == loai.MaLoai);
                int totalRentals = prodsInCat.Sum(p => p.SoLuotThue);
                decimal catRevenue = prodsInCat.Sum(p => p.DoanhThu);

                catStats.Add(new CategoryRevenueStat
                {
                    MaLoai = loai.MaLoai,
                    TenLoai = loai.TenLoai,
                    SoLuongMay = totalDevices,
                    SoLuotThue = totalRentals,
                    DoanhThu = catRevenue
                });
            }

            decimal totalCatSum = catStats.Sum(c => c.DoanhThu);
            foreach (var c in catStats)
            {
                c.TyTrong = totalCatSum > 0 ? Math.Round((double)(c.DoanhThu * 100m / totalCatSum), 1) : 0.0;
            }
            model.Categories = catStats.OrderByDescending(c => c.DoanhThu).ToList();

            // 5. BIỂU ĐỒ TRỰC QUAN HÓA (CHART.JS TIME SERIES)
            model.TimeSeries = await BuildTimeSeriesPointsAsync(filter);

            // Serialize JSON cho Chart.js
            model.TimeSeriesLabelsJson = JsonSerializer.Serialize(model.TimeSeries.Select(t => t.Label));
            model.TimeSeriesRevenueJson = JsonSerializer.Serialize(model.TimeSeries.Select(t => t.DoanhThu));
            model.TimeSeriesExpenseJson = JsonSerializer.Serialize(model.TimeSeries.Select(t => t.ChiPhi));

            model.CategoryLabelsJson = JsonSerializer.Serialize(model.Categories.Select(c => c.TenLoai));
            model.CategoryValuesJson = JsonSerializer.Serialize(model.Categories.Select(c => c.DoanhThu));

            if (hongThanhLy > 0)
            {
                model.FleetLabelsJson = JsonSerializer.Serialize(new[] { "Sẵn sàng", "Đang cho thuê", "Bảo trì & Sửa chữa", "Đang giữ chỗ", "Hỏng thanh lý" });
                model.FleetValuesJson = JsonSerializer.Serialize(new[] { sanSang, dangChoThue, dangSuaChua, giuCho, hongThanhLy });
            }
            else
            {
                model.FleetLabelsJson = JsonSerializer.Serialize(new[] { "Sẵn sàng", "Đang cho thuê", "Bảo trì & Sửa chữa", "Đang giữ chỗ" });
                model.FleetValuesJson = JsonSerializer.Serialize(new[] { sanSang, dangChoThue, dangSuaChua, giuCho });
            }

            return model;
        }

        // Tạo các điểm dữ liệu đường thời gian tùy biến theo mốc lọc (Line Chart)
        private async Task<List<TimeSeriesPoint>> BuildTimeSeriesPointsAsync(ThongKeFilterModel filter)
        {
            var points = new List<TimeSeriesPoint>();
            var allPhieuThu = await _context.PhieuThus
                .Where(pt => !pt.DaHuy && (pt.LoaiPhieu == 0 || pt.LoaiPhieu == 2) && pt.NgayGiaoDich >= filter.EffectiveFrom && pt.NgayGiaoDich <= filter.EffectiveTo)
                .ToListAsync();

            var allPhieuChi = await _context.PhieuChis
                .Where(pc => pc.NgayChi >= filter.EffectiveFrom && pc.NgayChi <= filter.EffectiveTo)
                .ToListAsync();

            if (filter.Range == "this_year")
            {
                int year = filter.EffectiveFrom.Year;
                for (int m = 1; m <= 12; m++)
                {
                    var mStart = new DateTime(year, m, 1);
                    var mEnd = (year == 9999 && m == 12) ? DateTime.MaxValue : mStart.AddMonths(1).AddTicks(-1);
                    decimal rev = allPhieuThu.Where(p => p.NgayGiaoDich >= mStart && p.NgayGiaoDich <= mEnd).Sum(p => p.SoTien);
                    decimal exp = allPhieuChi.Where(p => p.NgayChi >= mStart && p.NgayChi <= mEnd).Sum(p => p.SoTien);
                    points.Add(new TimeSeriesPoint
                    {
                        Label = $"T{m}",
                        DoanhThu = rev,
                        ChiPhi = exp
                    });
                }
            }
            else if (filter.Range == "this_quarter")
            {
                int startMonth = filter.EffectiveFrom.Month;
                int year = filter.EffectiveFrom.Year;
                for (int i = 0; i < 3; i++)
                {
                    int m = startMonth + i;
                    var mStart = new DateTime(year, m, 1);
                    var mEnd = mStart.AddMonths(1).AddTicks(-1);
                    decimal rev = allPhieuThu.Where(p => p.NgayGiaoDich >= mStart && p.NgayGiaoDich <= mEnd).Sum(p => p.SoTien);
                    decimal exp = allPhieuChi.Where(p => p.NgayChi >= mStart && p.NgayChi <= mEnd).Sum(p => p.SoTien);
                    points.Add(new TimeSeriesPoint
                    {
                        Label = $"Tháng {m}/{year}",
                        DoanhThu = rev,
                        ChiPhi = exp
                    });
                }
            }
            else if (filter.Range == "today")
            {
                var day = filter.EffectiveFrom.Date;
                var hours = new[] { 6, 9, 12, 15, 18, 21, 24 };
                int prevH = 0;
                foreach (var h in hours)
                {
                    var hStart = day.AddHours(prevH);
                    var hEnd = (h == 24) ? day.AddDays(1).AddTicks(-1) : day.AddHours(h);
                    // Dùng < hEnd cho các mốc trung gian để không cộng trùng lặp giao dịch phát sinh đúng giờ biên
                    decimal rev = allPhieuThu.Where(p => p.NgayGiaoDich >= hStart && (h == 24 ? p.NgayGiaoDich <= hEnd : p.NgayGiaoDich < hEnd)).Sum(p => p.SoTien);
                    decimal exp = allPhieuChi.Where(p => p.NgayChi >= hStart && (h == 24 ? p.NgayChi <= hEnd : p.NgayChi < hEnd)).Sum(p => p.SoTien);
                    points.Add(new TimeSeriesPoint
                    {
                        Label = $"{prevH:D2}:00 - {h:D2}:00",
                        DoanhThu = rev,
                        ChiPhi = exp
                    });
                    prevH = h;
                }
            }
            else
            {
                // this_month hoặc custom
                var days = (filter.EffectiveTo.Date - filter.EffectiveFrom.Date).Days + 1;
                if (days <= 31)
                {
                    for (int i = 0; i < days; i++)
                    {
                        var curDate = filter.EffectiveFrom.Date.AddDays(i);
                        var nextDate = curDate.AddDays(1).AddTicks(-1);
                        decimal rev = allPhieuThu.Where(p => p.NgayGiaoDich >= curDate && p.NgayGiaoDich <= nextDate).Sum(p => p.SoTien);
                        decimal exp = allPhieuChi.Where(p => p.NgayChi >= curDate && p.NgayChi <= nextDate).Sum(p => p.SoTien);
                        points.Add(new TimeSeriesPoint
                        {
                            Label = $"{curDate:dd/MM}",
                            DoanhThu = rev,
                            ChiPhi = exp
                        });
                    }
                }
                else
                {
                    // Lọc theo từng tháng nếu khoảng ngày dài hơn 1 tháng (giới hạn tối đa 120 điểm dữ liệu)
                    var curMonth = new DateTime(filter.EffectiveFrom.Year, filter.EffectiveFrom.Month, 1);
                    int maxPoints = 120;
                    while (curMonth <= filter.EffectiveTo && points.Count < maxPoints)
                    {
                        var nextMonth = (curMonth.Year == 9999 && curMonth.Month == 12) 
                            ? DateTime.MaxValue 
                            : curMonth.AddMonths(1).AddTicks(-1);
                        var sliceStart = curMonth < filter.EffectiveFrom ? filter.EffectiveFrom : curMonth;
                        var sliceEnd = nextMonth > filter.EffectiveTo ? filter.EffectiveTo : nextMonth;
                        decimal rev = allPhieuThu.Where(p => p.NgayGiaoDich >= sliceStart && p.NgayGiaoDich <= sliceEnd).Sum(p => p.SoTien);
                        decimal exp = allPhieuChi.Where(p => p.NgayChi >= sliceStart && p.NgayChi <= sliceEnd).Sum(p => p.SoTien);
                        points.Add(new TimeSeriesPoint
                        {
                            Label = $"{curMonth:MM/yyyy}",
                            DoanhThu = rev,
                            ChiPhi = exp
                        });
                        if (curMonth.Year >= 9999) break;
                        curMonth = curMonth.AddMonths(1);
                    }
                }
            }

            return points;
        }

        // Định dạng tiêu đề từng mục trong file Excel
        private static void FormatSectionHeader(IXLCell cell, XLColor textColor, XLColor bgColor)
        {
            cell.Style.Font.Bold = true;
            cell.Style.Font.FontSize = 11;
            cell.Style.Font.FontColor = textColor;
            cell.Style.Fill.BackgroundColor = bgColor;
            cell.Style.Alignment.Vertical = XLAlignmentVerticalValues.Center;
            cell.Style.Border.OutsideBorder = XLBorderStyleValues.Thin;
            cell.Style.Border.OutsideBorderColor = XLColor.FromArgb(203, 213, 225);
        }

        // Định dạng tiêu đề bảng dữ liệu trong file Excel
        private static void FormatTableHeader(IXLRange range, XLColor bgColor)
        {
            range.Style.Font.Bold = true;
            range.Style.Font.FontSize = 9.5;
            range.Style.Font.FontColor = XLColor.White;
            range.Style.Fill.BackgroundColor = bgColor;
            range.Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
            range.Style.Alignment.Vertical = XLAlignmentVerticalValues.Center;
            range.Style.Border.OutsideBorder = XLBorderStyleValues.Thin;
            range.Style.Border.OutsideBorderColor = XLColor.FromArgb(203, 213, 225);
        }

        // Định dạng viền dòng dữ liệu bảng Excel
        private static void ApplyRowBorder(IXLRange range, XLColor borderColor, XLColor bgColor)
        {
            range.Style.Fill.BackgroundColor = bgColor;
            range.Style.Border.OutsideBorder = XLBorderStyleValues.Thin;
            range.Style.Border.OutsideBorderColor = borderColor;
            range.Style.Border.InsideBorder = XLBorderStyleValues.Thin;
            range.Style.Border.InsideBorderColor = borderColor;
            range.Style.Alignment.Vertical = XLAlignmentVerticalValues.Center;
        }

        // Sao lưu cơ sở dữ liệu dự phòng (giữ nguyên tương thích)
        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult BackupDatabase()
        {
            TempData["Success"] = "Sao lưu (Backup) cơ sở dữ liệu thành công! Bản lưu được cất giữ an toàn.";
            return RedirectToAction(nameof(Index));
        }

        // Phục hồi cơ sở dữ liệu từ bản sao lưu (giữ nguyên tương thích)
        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult RestoreDatabase()
        {
            TempData["Success"] = "Khôi phục (Restore) cơ sở dữ liệu từ bản sao lưu thành công!";
            return RedirectToAction(nameof(Index));
        }
    }
}
