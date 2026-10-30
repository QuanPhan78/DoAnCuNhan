using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Areas.Admin.Controllers
{
    // Controller quản lý tiếp nhận, điều phối và xử lý sự cố thiết bị (Bảo trì).
    // Hỗ trợ phân công kỹ thuật viên, cập nhật trạng thái sửa chữa, tính phí bồi thường và bảo dưỡng thiết bị kho.
    [Area("Admin")]
    [Authorize(Roles = "Admin,KyThuat,KinhDoanh")]
    public class BaoTriController : Controller
    {
        private readonly ApplicationDbContext _context;

        public BaoTriController(ApplicationDbContext context)
        {
            _context = context;
        }

        // Danh sách toàn bộ phiếu yêu cầu bảo trì, sự cố thiết bị được gửi từ khách hàng hoặc nội bộ kho.
        public async Task<IActionResult> Index(int? trangThai = null, string filter = null)
        {
            var query = _context.PhieuBaoTris
                .Include(p => p.HopDong).ThenInclude(h => h.KhachHang)
                .Include(p => p.ThietBi).ThenInclude(t => t.SanPham)
                .Include(p => p.KyThuatVien)
                .AsQueryable();

            if (trangThai.HasValue)
            {
                query = query.Where(p => p.TrangThai == trangThai.Value);
            }

            if (filter == "overdue_sla")
            {
                var now = DateTime.Now;
                query = query.Where(p => p.TrangThai < 3 && p.HanHoanThanh.HasValue && p.HanHoanThanh.Value < now);
            }
            else if (filter == "near_sla")
            {
                var now = DateTime.Now;
                var warningThreshold = now.AddHours(12);
                query = query.Where(p => p.TrangThai < 3 && p.HanHoanThanh.HasValue && p.HanHoanThanh.Value >= now && p.HanHoanThanh.Value <= warningThreshold);
            }

            var allTickets = await _context.PhieuBaoTris.ToListAsync();
            var nowTime = DateTime.Now;
            ViewBag.CountAll = allTickets.Count;
            ViewBag.CountNew = allTickets.Count(p => p.TrangThai == 1);
            ViewBag.CountProcessing = allTickets.Count(p => p.TrangThai == 2);
            ViewBag.CountDone = allTickets.Count(p => p.TrangThai == 3);
            ViewBag.CountOverdue = allTickets.Count(p => p.TrangThai < 3 && p.HanHoanThanh.HasValue && p.HanHoanThanh.Value < nowTime);

            var data = await query.OrderByDescending(p => p.NgayBaoLoi).ToListAsync();
            ViewBag.CurrentTrangThai = trangThai;
            ViewBag.CurrentFilter = filter;
            return View(data);
        }

        // Lập phiếu bảo dưỡng định kỳ cho thiết bị tồn kho (không gắn hợp đồng)
        [Authorize(Roles = "Admin,KyThuat")]
        [HttpGet]
        public async Task<IActionResult> Create()
        {
            var thietBis = await _context.ThietBis
                .Include(t => t.SanPham)
                .Where(t => t.TrangThai == 0 || t.TrangThai == 2)
                .OrderBy(t => t.SoSerial)
                .ToListAsync();

            var kyThuatViens = await _context.NguoiDungs
                .Where(n => n.VaiTro.TenVaiTro == "KyThuat")
                .ToListAsync();

            ViewBag.ThietBis = thietBis;
            ViewBag.KyThuatViens = kyThuatViens;
            return View();
        }

        [Authorize(Roles = "Admin,KyThuat")]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create(int maThietBi, string moTaLoi, int? maKtv, int? mucDoKhanCap, decimal? chiPhiDuKien, DateTime? hanHoanThanh, string ghiChu)
        {
            if (string.IsNullOrWhiteSpace(moTaLoi))
            {
                TempData["Error"] = "Vui lòng nhập mô tả lỗi/yêu cầu bảo dưỡng!";
                return RedirectToAction(nameof(Create));
            }

            var thietBi = await _context.ThietBis.Include(t => t.SanPham).FirstOrDefaultAsync(t => t.MaThietBi == maThietBi);
            if (thietBi == null) return NotFound();

            var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            int? adminId = (claim != null && int.TryParse(claim.Value, out int aId)) ? aId : null;

            int urgency = mucDoKhanCap ?? 1;
            DateTime deadline = hanHoanThanh ?? DateTime.Now.AddHours(urgency == 2 ? 12 : (urgency == 3 ? 24 : 48));

            var phieu = new PhieuBaoTri
            {
                MaHopDong = null, // Bảo dưỡng nội bộ kho không gắn hợp đồng
                MaThietBi = maThietBi,
                MoTaLoi = moTaLoi.Trim(),
                NgayBaoLoi = DateTime.Now,
                GhiChuSuaChua = ghiChu ?? "",
                MaKyThuatVien = maKtv,
                ChiPhiSuaChua = chiPhiDuKien ?? 0,
                PhiDenBu = 0,
                LoaiTrachNhiem = 2, // 2: Cửa hàng chịu
                MucDoKhanCap = urgency,
                HanHoanThanh = deadline,
                TrangThai = 1
            };

            thietBi.TrangThai = 2; // Đang bảo dưỡng / Sửa chữa
            thietBi.TinhTrangMay = $"Bảo dưỡng nội bộ kho: {moTaLoi.Trim()}";

            _context.PhieuBaoTris.Add(phieu);
            await _context.SaveChangesAsync();

            // Ghi nhận lịch sử thiết bị
            _context.LichSuThietBis.Add(new LichSuThietBi
            {
                MaThietBi = maThietBi,
                HanhDong = $"Tạo phiếu bảo dưỡng nội bộ kho #{phieu.MaPhieu}. Lỗi/Yêu cầu: {moTaLoi.Trim()}",
                ThoiGian = DateTime.Now,
                MaNguoiThucHien = adminId,
                GhiChu = $"Bảo dưỡng nội bộ kho. SLA hoàn thành: {deadline:dd/MM/yyyy HH:mm}"
            });
            await _context.SaveChangesAsync();

            TempData["Success"] = $"Đã tạo phiếu bảo dưỡng kho #{phieu.MaPhieu} cho thiết bị {thietBi.SoSerial} thành công!";
            return RedirectToAction(nameof(Index));
        }

        // Xem chi tiết phiếu bảo trì, thông tin thiết bị lỗi, hợp đồng liên quan và phân công kỹ thuật viên.
        public async Task<IActionResult> Details(int id)
        {
            var phieu = await _context.PhieuBaoTris
                .Include(p => p.HopDong).ThenInclude(h => h.KhachHang)
                .Include(p => p.ThietBi).ThenInclude(t => t.SanPham)
                .Include(p => p.KyThuatVien)
                .FirstOrDefaultAsync(p => p.MaPhieu == id);

            if (phieu == null) return NotFound();

            // Nạp danh sách nhân viên có vai trò Kỹ Thuật (KyThuat) để phân công phụ trách
            ViewData["MaKyThuatVien"] = new SelectList(
                await _context.NguoiDungs.Where(n => n.VaiTro.TenVaiTro == "KyThuat").ToListAsync(), 
                "MaNguoiDung", "HoTen", phieu.MaKyThuatVien);

            // Nạp lịch sử thiết bị để hiển thị tiến trình
            ViewBag.LichSuThietBis = await _context.LichSuThietBis
                .Include(l => l.NguoiThucHien)
                .Where(l => l.MaThietBi == phieu.MaThietBi)
                .OrderByDescending(l => l.ThoiGian)
                .ToListAsync();

            // Thống kê số tiền bồi thường đã thu
            decimal daThu = 0;
            if (phieu.MaHopDong.HasValue)
            {
                daThu = await _context.PhieuThus
                    .Where(pt => pt.MaHopDong == phieu.MaHopDong.Value && pt.LoaiPhieu == 2 && !pt.DaHuy)
                    .SumAsync(pt => (decimal?)pt.SoTien) ?? 0m;
            }
            ViewBag.DaThuPhiDenBu = daThu;

            return View(phieu);
        }

        // Cập nhật tiến độ sửa chữa: 1=Mới tiếp nhận, 2=Đang sửa chữa, 3=Đã sửa xong, 4=Hỏng không thể khắc phục, 5=Đã nghiệm thu.
        [Authorize(Roles = "Admin,KyThuat")]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> UpdateStatus(
            int id, 
            int status, 
            int? maKtv, 
            string ghiChu, 
            decimal phiDenBu, 
            decimal? chiPhiSuaChua = null, 
            bool thuPhiNgay = false, 
            int hinhThuc = 0,
            int? loaiTrachNhiem = null,
            string nguyenNhan = null,
            string linhKienThayThe = null,
            bool tamDungTinhTien = false,
            int? soNgayTamDung = null,
            DateTime? hanHoanThanh = null)
        {
            // Ràng buộc giới hạn không âm cho phí đền bù và chi phí sửa chữa
            if (phiDenBu < 0 || (chiPhiSuaChua.HasValue && chiPhiSuaChua.Value < 0))
            {
                TempData["Error"] = "Phí đền bù và chi phí sửa chữa không thể là số âm!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            if (status < 1 || status > 5)
            {
                TempData["Error"] = "Trạng thái bảo trì không hợp lệ!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            var phieu = await _context.PhieuBaoTris
                .Include(p => p.HopDong)
                .Include(p => p.ThietBi)
                .FirstOrDefaultAsync(p => p.MaPhieu == id);
            if (phieu == null) return NotFound();

            var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            int? adminId = (claim != null && int.TryParse(claim.Value, out int aId)) ? aId : null;

            phieu.TrangThai = status;
            phieu.GhiChuSuaChua = ghiChu ?? "";
            phieu.PhiDenBu = phiDenBu;
            
            // Lưu chi phí sửa chữa thực tế
            if (chiPhiSuaChua.HasValue)
            {
                phieu.ChiPhiSuaChua = chiPhiSuaChua.Value;
            }

            // Phân định trách nhiệm chi phí và ghi nhận nguyên nhân
            if (loaiTrachNhiem.HasValue) phieu.LoaiTrachNhiem = loaiTrachNhiem.Value;
            if (!string.IsNullOrEmpty(nguyenNhan)) phieu.NguyenNhan = nguyenNhan;
            if (!string.IsNullOrEmpty(linhKienThayThe)) phieu.LinhKienThayThe = linhKienThayThe;
            if (hanHoanThanh.HasValue) phieu.HanHoanThanh = hanHoanThanh.Value;

            if (maKtv.HasValue)
            {
                phieu.MaKyThuatVien = maKtv.Value;
            }

            // Khi chuyển sang trạng thái 4: Hỏng không thể khắc phục / Thanh lý
            if (status == 4)
            {
                var tb = await _context.ThietBis.FindAsync(phieu.MaThietBi);
                if (tb != null)
                {
                    tb.TrangThai = 4; // 4: Hỏng không thể khắc phục / Thanh lý
                    tb.TinhTrangMay = $"Hỏng không thể khắc phục (Thanh lý) - Phiếu #{phieu.MaPhieu}";
                    _context.LichSuThietBis.Add(new LichSuThietBi
                    {
                        MaThietBi = tb.MaThietBi,
                        HanhDong = $"Xác nhận thiết bị hỏng không thể khắc phục theo phiếu #{phieu.MaPhieu} (TrangThai = 4)",
                        ThoiGian = DateTime.Now,
                        MaNguoiThucHien = adminId,
                        GhiChu = $"Lý do: {ghiChu}. Nguyên nhân: {nguyenNhan}"
                    });
                }
            }
            else if (status == 2) // Bắt đầu sửa chữa
            {
                phieu.NgayBatDauBaoTri ??= DateTime.Now;
                var tb = await _context.ThietBis.FindAsync(phieu.MaThietBi);
                if (tb != null && tb.TrangThai != 4)
                {
                    tb.TrangThai = 2; // Đang bảo dưỡng / Sửa chữa
                }
                _context.LichSuThietBis.Add(new LichSuThietBi
                {
                    MaThietBi = phieu.MaThietBi,
                    HanhDong = $"Kỹ thuật viên bắt đầu sửa chữa phiếu #{phieu.MaPhieu} (TrangThai = 2)",
                    ThoiGian = DateTime.Now,
                    MaNguoiThucHien = adminId,
                    GhiChu = ghiChu
                });
            }
            else if (status == 3) // Sửa xong
            {
                phieu.NgayHoanThanh = DateTime.Now;
                phieu.NgayKetThucBaoTri ??= DateTime.Now;

                // Tạm dừng tính tiền thuê trong thời gian thiết bị bảo trì
                if (tamDungTinhTien || phieu.TamDungTinhTien)
                {
                    phieu.TamDungTinhTien = true;
                    if (phieu.MaHopDong.HasValue && !phieu.DaTruTien)
                    {
                        var hopDong = await _context.HopDongs
                            .Include(h => h.KyHanThanhToans)
                            .FirstOrDefaultAsync(h => h.MaHopDong == phieu.MaHopDong.Value);

                        if (hopDong != null)
                        {
                            DateTime batDau = phieu.NgayBatDauBaoTri ?? phieu.NgayBaoLoi;
                            DateTime ketThuc = phieu.NgayKetThucBaoTri ?? DateTime.Now;
                            int pauseDays = soNgayTamDung ?? Math.Max(1, (int)Math.Ceiling((ketThuc - batDau).TotalDays));
                            phieu.SoNgayTamDung = pauseDays;

                            int totalContractDays = Math.Max(1, (int)(hopDong.NgayKetThuc.Date - hopDong.NgayBatDau.Date).TotalDays);
                            decimal deviceDailyRate = 0;
                            var ct = await _context.ChiTietHopDongs.FirstOrDefaultAsync(c => c.MaHopDong == hopDong.MaHopDong && c.MaThietBi == phieu.MaThietBi);
                            if (ct != null && ct.GiaChotThu > 0)
                            {
                                deviceDailyRate = ct.GiaChotThu / totalContractDays;
                            }
                            else
                            {
                                deviceDailyRate = hopDong.TongTien / totalContractDays;
                            }

                            decimal deduction = Math.Round((deviceDailyRate * pauseDays) / 1000m) * 1000m;
                            if (deduction > hopDong.TongTien) deduction = hopDong.TongTien;

                            phieu.TienGiamTru = deduction;
                            phieu.DaTruTien = true;
                            hopDong.TienGiamTruBaoTri += deduction;
                            hopDong.TongTien = Math.Max(0, hopDong.TongTien - deduction);

                            // Giảm trừ vào kỳ hạn thanh toán chưa trả gần nhất
                            var unpaidKyHans = hopDong.KyHanThanhToans
                                .Where(k => k.TrangThai != 1)
                                .OrderByDescending(k => k.SoKyHan)
                                .ToList();

                            decimal remainingDeduction = deduction;
                            foreach (var k in unpaidKyHans)
                            {
                                if (remainingDeduction <= 0) break;
                                decimal deductFromKy = Math.Min(k.SoTienPhai - k.SoTienDaTra, remainingDeduction);
                                k.SoTienPhai = Math.Max(0, k.SoTienPhai - deductFromKy);
                                k.GhiChu = (k.GhiChu ?? "") + $" [Giảm trừ {deductFromKy:N0}đ tiền thuê bảo trì phiếu #{phieu.MaPhieu}]";
                                remainingDeduction -= deductFromKy;
                            }

                            await HopDongController.SyncTrangThaiThanhToanHopDong(hopDong, _context);

                            _context.LichSuThietBis.Add(new LichSuThietBi
                            {
                                MaThietBi = phieu.MaThietBi,
                                HanhDong = $"Áp dụng miễn giảm tiền thuê bảo trì: {pauseDays} ngày (-{deduction:N0}đ) cho HĐ #{hopDong.MaHopDong}",
                                ThoiGian = DateTime.Now,
                                MaNguoiThucHien = adminId,
                                GhiChu = $"Khấu trừ thành công vào Hợp đồng #{hopDong.MaHopDong}"
                            });
                        }
                    }
                }

                _context.LichSuThietBis.Add(new LichSuThietBi
                {
                    MaThietBi = phieu.MaThietBi,
                    HanhDong = $"Hoàn thành sửa chữa phiếu #{phieu.MaPhieu} (TrangThai = 3). Chi phí: {phieu.ChiPhiSuaChua:N0}đ, Bồi thường: {phieu.PhiDenBu:N0}đ",
                    ThoiGian = DateTime.Now,
                    MaNguoiThucHien = adminId,
                    GhiChu = ghiChu
                });
            }

            // Tự động lập Phiếu Thu (LoaiPhieu = 2) khi chọn thu phí ngay
            if (thuPhiNgay && phiDenBu > 0 && phieu.MaHopDong.HasValue)
            {
                var phieuThu = new PhieuThu
                {
                    MaHopDong = phieu.MaHopDong.Value,
                    LoaiPhieu = 2, // 2: Thu phí BT / đền bù
                    SoTien = phiDenBu,
                    NgayGiaoDich = DateTime.Now,
                    HinhThucThanhToan = hinhThuc,
                    GhiChu = $"Thu phí đền bù bảo trì phiếu #{phieu.MaPhieu}"
                };
                _context.PhieuThus.Add(phieuThu);
                phieu.DaGhiNhanCongNo = true;
            }

            // Ghi nhận công nợ và phát thông báo khi có phí đền bù
            if (phiDenBu > 0 && phieu.MaHopDong.HasValue)
            {
                phieu.DaGhiNhanCongNo = true;
                var hopDong = await _context.HopDongs.FirstOrDefaultAsync(h => h.MaHopDong == phieu.MaHopDong.Value);
                if (hopDong != null)
                {
                    await HopDongController.SyncTrangThaiThanhToanHopDong(hopDong, _context);

                    _context.ThongBaos.Add(new ThongBao
                    {
                        MaNguoiDung = hopDong.MaKhachHang,
                        TieuDe = $"Phát sinh phí đền bù bảo trì phiếu #{phieu.MaPhieu}",
                        NoiDung = $"Thiết bị gặp sự cố phát sinh phí bồi thường/sửa chữa: {phiDenBu:N0} đ. Khoản phí đã được ghi nhận vào công nợ Hợp đồng #{hopDong.MaHopDong}.",
                        NgayTao = DateTime.Now,
                        LoaiThongBao = "BaoTri",
                        LienKet = $"/BaoTri/ChiTiet/{phieu.MaPhieu}"
                    });
                }
            }

            await _context.SaveChangesAsync();
            TempData["Success"] = "Cập nhật tiến độ bảo trì thành công!";
            return RedirectToAction(nameof(Details), new { id = id });
        }

        // Áp dụng tạm dừng tính tiền thuê trong thời gian bảo trì
        [Authorize(Roles = "Admin,KyThuat")]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> ApDungTamDungTienThue(int id, int soNgayTamDung)
        {
            if (soNgayTamDung <= 0)
            {
                TempData["Error"] = "Số ngày tạm dừng phải lớn hơn 0!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            var phieu = await _context.PhieuBaoTris
                .Include(p => p.HopDong).ThenInclude(h => h.KyHanThanhToans)
                .FirstOrDefaultAsync(p => p.MaPhieu == id);

            if (phieu == null) return NotFound();

            if (!phieu.MaHopDong.HasValue || phieu.HopDong == null)
            {
                TempData["Error"] = "Phiếu bảo dưỡng kho không thể áp dụng giảm trừ tiền thuê!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            if (phieu.DaTruTien)
            {
                TempData["Error"] = "Phiếu này đã được áp dụng giảm trừ tiền thuê trước đó!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            var hopDong = phieu.HopDong;
            int totalContractDays = Math.Max(1, (int)(hopDong.NgayKetThuc.Date - hopDong.NgayBatDau.Date).TotalDays);
            decimal deviceDailyRate = 0;
            var ct = await _context.ChiTietHopDongs.FirstOrDefaultAsync(c => c.MaHopDong == hopDong.MaHopDong && c.MaThietBi == phieu.MaThietBi);
            if (ct != null && ct.GiaChotThu > 0)
            {
                deviceDailyRate = ct.GiaChotThu / totalContractDays;
            }
            else
            {
                deviceDailyRate = hopDong.TongTien / totalContractDays;
            }

            decimal deduction = Math.Round((deviceDailyRate * soNgayTamDung) / 1000m) * 1000m;
            if (deduction > hopDong.TongTien) deduction = hopDong.TongTien;

            phieu.TamDungTinhTien = true;
            phieu.SoNgayTamDung = soNgayTamDung;
            phieu.TienGiamTru = deduction;
            phieu.DaTruTien = true;
            hopDong.TienGiamTruBaoTri += deduction;
            hopDong.TongTien = Math.Max(0, hopDong.TongTien - deduction);

            // Giảm trừ vào kỳ hạn thanh toán chưa trả
            var unpaidKyHans = hopDong.KyHanThanhToans
                .Where(k => k.TrangThai != 1)
                .OrderByDescending(k => k.SoKyHan)
                .ToList();

            decimal remainingDeduction = deduction;
            foreach (var k in unpaidKyHans)
            {
                if (remainingDeduction <= 0) break;
                decimal deductFromKy = Math.Min(k.SoTienPhai - k.SoTienDaTra, remainingDeduction);
                k.SoTienPhai = Math.Max(0, k.SoTienPhai - deductFromKy);
                k.GhiChu = (k.GhiChu ?? "") + $" [Giảm trừ {deductFromKy:N0}đ tiền thuê bảo trì phiếu #{phieu.MaPhieu}]";
                remainingDeduction -= deductFromKy;
            }

            await HopDongController.SyncTrangThaiThanhToanHopDong(hopDong, _context);

            var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            int? adminId = (claim != null && int.TryParse(claim.Value, out int aId)) ? aId : null;

            _context.LichSuThietBis.Add(new LichSuThietBi
            {
                MaThietBi = phieu.MaThietBi,
                HanhDong = $"Áp dụng miễn giảm tiền thuê bảo trì: {soNgayTamDung} ngày (-{deduction:N0}đ) cho HĐ #{hopDong.MaHopDong}",
                ThoiGian = DateTime.Now,
                MaNguoiThucHien = adminId,
                GhiChu = $"Khấu trừ thành công vào Hợp đồng #{hopDong.MaHopDong}"
            });

            await _context.SaveChangesAsync();
            TempData["Success"] = $"Đã áp dụng giảm trừ {deduction:N0}đ cho {soNgayTamDung} ngày bảo trì thành công!";
            return RedirectToAction(nameof(Details), new { id = id });
        }

        // Thu phí đền bù / sửa chữa thiết bị tạo Phiếu Thu (LoaiPhieu = 2)
        [Authorize(Roles = "Admin,KinhDoanh")]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> ThuPhiDenBu(int id, decimal soTien, int hinhThuc = 0, string ghiChu = null)
        {
            // Kiểm tra số tiền hợp lệ
            if (soTien <= 0)
            {
                TempData["Error"] = "Số tiền thu phí bảo trì/đền bù phải lớn hơn 0!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            var phieu = await _context.PhieuBaoTris.Include(p => p.HopDong).FirstOrDefaultAsync(p => p.MaPhieu == id);
            if (phieu == null) return NotFound();

            if (!phieu.MaHopDong.HasValue)
            {
                TempData["Error"] = "Không thể lập phiếu thu cho phiếu bảo dưỡng kho không gắn với hợp đồng!";
                return RedirectToAction(nameof(Details), new { id = id });
            }

            var claim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);
            int? adminId = (claim != null && int.TryParse(claim.Value, out int aId)) ? aId : null;

            var phieuThu = new PhieuThu
            {
                MaHopDong = phieu.MaHopDong.Value,
                LoaiPhieu = 2, // 2: Thu phí BT / đền bù
                SoTien = soTien,
                NgayGiaoDich = DateTime.Now,
                HinhThucThanhToan = hinhThuc,
                MaNhanVienThu = adminId,
                GhiChu = string.IsNullOrEmpty(ghiChu) ? $"Thu phí đền bù bảo trì phiếu #{phieu.MaPhieu}" : ghiChu
            };

            _context.PhieuThus.Add(phieuThu);
            phieu.DaGhiNhanCongNo = true;

            var hopDong = await _context.HopDongs.FirstOrDefaultAsync(h => h.MaHopDong == phieu.MaHopDong.Value);
            if (hopDong != null)
            {
                await HopDongController.SyncTrangThaiThanhToanHopDong(hopDong, _context);
            }

            _context.LichSuThietBis.Add(new LichSuThietBi
            {
                MaThietBi = phieu.MaThietBi,
                HanhDong = $"Thu tiền đền bù bảo trì {soTien:N0}đ phiếu #{phieu.MaPhieu}",
                ThoiGian = DateTime.Now,
                MaNguoiThucHien = adminId,
                GhiChu = $"Hình thức: {(hinhThuc == 0 ? "Tiền mặt" : "Chuyển khoản")}"
            });

            await _context.SaveChangesAsync();

            TempData["Success"] = $"Đã lập phiếu thu {soTien:N0}đ phí đền bù thành công!";
            return RedirectToAction(nameof(Details), new { id = id });
        }

        [Authorize(Roles = "Admin,KinhDoanh")]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> ThuPhiBaoTri(int id, decimal soTien, int hinhThuc = 0, string ghiChu = null)
        {
            return await ThuPhiDenBu(id, soTien, hinhThuc, ghiChu);
        }
    }
}
