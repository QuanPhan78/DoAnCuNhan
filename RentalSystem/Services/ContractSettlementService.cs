using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Common;
using RentalSystem.Models;

namespace RentalSystem.Services;

public sealed class SettlementPreview
{
    public int ContractId { get; set; }
    public int Kind { get; set; } // 0: return, 1: early return, 2: cancellation
    public DateTime? ReturnDate { get; set; }
    public decimal EarlyFee { get; set; }
    public decimal RentObligation { get; set; }
    public decimal DepositReceived { get; set; }
    public decimal DepositRefunded { get; set; }
    public decimal RentDue { get; set; }
    public decimal DamagesDue { get; set; }
    public decimal DepositToRent { get; set; }
    public decimal DepositToDamages { get; set; }
    public decimal ExcessToRent { get; set; }
    public decimal ExcessToDamages { get; set; }
    public decimal RentCreditToDamages { get; set; }
    public decimal RefundDeposit { get; set; }
    public decimal RefundRent { get; set; }
    public decimal RefundExcess { get; set; }
    public decimal RefundOther { get; set; }
    public decimal AdditionalDue { get; set; }
    public decimal TotalRefund => RefundDeposit + RefundRent + RefundExcess + RefundOther;
    public bool Completed { get; set; }
    public string? Error { get; set; }
    public string Token { get; set; } = "";
}

public sealed record SettlementResult(bool Success, string Message, SettlementPreview Preview);

public static class ContractSettlementService
{
    private static IQueryable<HopDong> Query(ApplicationDbContext db) => db.HopDongs
        .Include(h => h.PhieuThus).Include(h => h.PhieuChis)
        .Include(h => h.KyHanThanhToans).Include(h => h.PhieuBaoTris);

    public static async Task<SettlementPreview?> PreviewAsync(ApplicationDbContext db, int id, int kind,
        DateTime? returnDate = null, decimal earlyFee = 0)
    {
        var h = await Query(db).FirstOrDefaultAsync(h => h.MaHopDong == id);
        if (h == null) return null;
        if (kind == 0) RentalSystem.Areas.Admin.Controllers.HopDongController.CapNhatTreHanVaPhiPhat(h.KyHanThanhToans);
        var saved = await db.ContractSettlements.AsNoTracking().FirstOrDefaultAsync(s => s.MaHopDong == id);
        if (saved != null)
        {
            var q = JsonSerializer.Deserialize<SettlementPreview>(saved.ChiTietJson)!;
            q.Completed = true;
            return q;
        }
        return Calculate(h, kind, returnDate, earlyFee);
    }

    private static SettlementPreview Calculate(HopDong h, int kind, DateTime? date, decimal fee)
    {
        var q = new SettlementPreview { ContractId = h.MaHopDong, Kind = kind, ReturnDate = date?.Date, EarlyFee = fee };
        if (kind is < 0 or > 2) q.Error = "Loại quyết toán không hợp lệ.";
        else if (h.TrangThai is 2 or 3) q.Error = "Hợp đồng lịch sử đã kết thúc; không quyết toán lại.";
        else if (kind == 2 && h.TrangThai != 0) q.Error = "Chỉ có thể hủy hợp đồng đang chờ giao.";
        else if (kind == 0 && h.TrangThai != 4) q.Error = "Cần tiếp nhận trả máy trước khi quyết toán.";
        else if (kind == 1 && (h.TrangThai != 1 || date == null || date.Value.Date < h.NgayBatDau.Date || date.Value.Date > h.NgayKetThuc.Date || fee < 0))
            q.Error = "Ngày trả trước hạn hoặc phí không hợp lệ; hợp đồng phải đang thuê.";
        else if (h.PhieuBaoTris?.Any(p => p.TrangThai is 1 or 2) == true)
            q.Error = "Hợp đồng còn phiếu bảo trì/sự cố đang xử lý; cần hoàn tất trước khi quyết toán.";

        var receipts = (h.PhieuThus ?? []).Where(p => !p.DaHuy).ToList();
        var payments = h.PhieuChis ?? [];
        q.DepositReceived = receipts.Where(p => p.LoaiPhieu == 1).Sum(p => p.SoTien);
        q.DepositRefunded = payments.Where(p => p.LoaiChi == 0).Sum(p => p.SoTien);
        if (h.TienDaCoc > q.DepositReceived || (h.TienCocThucHoan ?? 0) > q.DepositRefunded || q.DepositRefunded > q.DepositReceived)
            q.Error ??= "Số cọc lịch sử chưa khớp phiếu thu/chi hợp lệ. Cần đối chiếu chứng từ trước khi quyết toán.";
        if (receipts.Any(p => p.SoTien < 0) || payments.Any(p => p.SoTien < 0))
            q.Error ??= "Chứng từ có số tiền âm; cần đối chiếu trước khi quyết toán.";
        decimal rentPaid = receipts.Where(p => p.LoaiPhieu == 0).Sum(p => p.SoTien);
        decimal damagesPaid = receipts.Where(p => p.LoaiPhieu == 2).Sum(p => p.SoTien);
        decimal excess = receipts.Where(p => p.LoaiPhieu == FirstContractPayment.ExcessReceipt).Sum(p => p.SoTien);
        q.RentObligation = kind == 2 ? 0 : h.TongTien;
        if (kind == 1 && q.Error == null)
        {
            int originalDays = Math.Max(1, (h.NgayKetThuc.Date - h.NgayBatDau.Date).Days);
            int actualDays = Math.Max(1, (date!.Value.Date - h.NgayBatDau.Date).Days);
            q.RentObligation = Math.Round(h.TongTien / originalDays * actualDays / 1000m) * 1000m + fee;
        }
        decimal late = kind == 0 ? (h.KyHanThanhToans ?? []).Where(k => k.TrangThai != 3).Sum(k => k.TienPhat) : 0;
        q.RentDue = Math.Max(0, q.RentObligation + late - rentPaid);
        q.DamagesDue = kind == 2 ? 0 : Math.Max(0, (h.PhieuBaoTris ?? []).Sum(p => p.PhiDenBu) - damagesPaid);
        decimal rentCredit = Math.Max(0, rentPaid - q.RentObligation - late);
        decimal oldNonDepositRefunds = payments.Where(p => p.LoaiChi == 1).Sum(p => p.SoTien);
        decimal deducted = Math.Min(excess, oldNonDepositRefunds);
        excess -= deducted; oldNonDepositRefunds -= deducted;
        rentCredit = Math.Max(0, rentCredit - oldNonDepositRefunds);
        decimal rentDebt = q.RentDue, damagesDebt = q.DamagesDue;
        q.ExcessToRent = Math.Min(excess, rentDebt); excess -= q.ExcessToRent; rentDebt -= q.ExcessToRent;
        q.ExcessToDamages = Math.Min(excess, damagesDebt); excess -= q.ExcessToDamages; damagesDebt -= q.ExcessToDamages;
        q.RentCreditToDamages = Math.Min(rentCredit, damagesDebt); rentCredit -= q.RentCreditToDamages; damagesDebt -= q.RentCreditToDamages;
        decimal deposit = Math.Max(0, q.DepositReceived - q.DepositRefunded);
        q.DepositToRent = Math.Min(deposit, rentDebt); deposit -= q.DepositToRent; rentDebt -= q.DepositToRent;
        q.DepositToDamages = Math.Min(deposit, damagesDebt); deposit -= q.DepositToDamages; damagesDebt -= q.DepositToDamages;
        q.AdditionalDue = rentDebt + damagesDebt;
        q.RefundDeposit = deposit; q.RefundRent = rentCredit; q.RefundExcess = excess;
        q.RefundOther = kind == 2 ? Math.Max(0, damagesPaid - payments.Where(p => p.LoaiChi == 2).Sum(p => p.SoTien)) : 0;
        // The fingerprint detects changed financial inputs, including changes with the same net refund.
        var fingerprint = new { q, h.TrangThai, h.TongTien, h.NgayBatDau, h.NgayKetThuc,
            receipts = receipts.OrderBy(p => p.MaPhieuThu).Select(p => new { p.MaPhieuThu, p.LoaiPhieu, p.SoTien }),
            payments = payments.OrderBy(p => p.MaPhieuChi).Select(p => new { p.MaPhieuChi, p.LoaiChi, p.SoTien }),
            periods = (h.KyHanThanhToans ?? []).OrderBy(k => k.MaKyHan).Select(k => new { k.MaKyHan, k.SoTienPhai, k.SoTienDaTra, k.TrangThai, k.TienPhat, k.PhiPhatTreHan }) };
        q.Token = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(JsonSerializer.Serialize(fingerprint))));
        return q;
    }

    public static async Task<SettlementResult> ExecuteAsync(ApplicationDbContext db, int id, int kind,
        int employee, string? expectedToken, DateTime? returnDate = null, decimal earlyFee = 0, int paymentMethod = 1, string? note = null)
    {
        await using var tx = await RentalBooking.BeginInventoryAsync(db);
        string key = $"RentalSystem.Settlement.{id}";
        await db.Database.ExecuteSqlInterpolatedAsync($"DECLARE @r int; EXEC @r=sys.sp_getapplock @Resource={key}, @LockMode='Exclusive', @LockOwner='Transaction', @LockTimeout=10000; IF @r<0 THROW 51015,N'Settlement lock unavailable.',1;");
        var h = await Query(db).FirstOrDefaultAsync(h => h.MaHopDong == id);
        if (h == null) return new(false, "Không tìm thấy hợp đồng.", new());
        var saved = await db.ContractSettlements.FirstOrDefaultAsync(s => s.MaHopDong == id);
        if (saved != null)
        {
            var old = JsonSerializer.Deserialize<SettlementPreview>(saved.ChiTietJson)!; old.Completed = true;
            return new(true, "Hợp đồng đã được quyết toán; không lập thêm chứng từ.", old);
        }
        if (kind == 0) RentalSystem.Areas.Admin.Controllers.HopDongController.CapNhatTreHanVaPhiPhat(h.KyHanThanhToans);
        var q = Calculate(h, kind, returnDate, earlyFee);
        if (q.Error != null) return new(false, q.Error, q);
        if (string.IsNullOrWhiteSpace(expectedToken) || !string.Equals(expectedToken, q.Token, StringComparison.Ordinal))
            return new(false, "Vui lòng xem và xác nhận lại quyết toán; thông tin có thể đã thay đổi.", q);
        if (paymentMethod is < 0 or > 2) return new(false, "Hình thức chi không hợp lệ.", q);
        if (q.AdditionalDue > 0 && kind != 1)
            return new(false, $"Còn phải thu thêm {q.AdditionalDue:N0} đ; hợp đồng vẫn chờ quyết toán.", q);

        if (kind == 1)
        {
            h.TongTien = q.RentObligation; h.NgayKetThuc = returnDate!.Value.Date;
            foreach (var k in h.KyHanThanhToans.Where(k => k.TrangThai != 1)) k.TrangThai = 3;
            h.TrangThai = 4;
            await ReleaseAsync(db, h, employee, $"Thanh lý sớm ngày {returnDate:dd/MM/yyyy}. {note}");
            if (q.AdditionalDue > 0)
            {
                // Preserve a payable schedule after recording the physical return; settle only after collection.
                db.KyHanThanhToans.Add(new KyHanThanhToan { MaHopDong=id, SoKyHan=h.KyHanThanhToans.Count+1,
                    NgayDenHan=DateTime.Today, SoTienPhai=q.RentDue, GhiChu="Công nợ sau trả máy trước hạn" });
                h.TrangThaiThanhToan=ContractPaymentStatus.Outstanding;
                await db.SaveChangesAsync(); await tx.CommitAsync();
                return new(false, $"Đã tiếp nhận trả máy. Còn phải thu thêm {q.AdditionalDue:N0} đ trước quyết toán.", q);
            }
        }
        void Receipt(int type, decimal amount, string source)
        {
            if (amount <= 0) return;
            db.PhieuThus.Add(new PhieuThu { MaHopDong=id, LoaiPhieu=type, SoTien=amount,
                HinhThucThanhToan=2, MaNhanVienThu=employee, NgayGiaoDich=DateTime.Now,
                GhiChu=$"Quyết toán: cấn trừ {source}" });
        }
        Receipt(0,q.DepositToRent,"cọc vào tiền thuê"); Receipt(2,q.DepositToDamages,"cọc vào bồi thường");
        Receipt(0,q.ExcessToRent,"tiền chuyển thừa vào thuê"); Receipt(2,q.ExcessToDamages,"tiền chuyển thừa vào bồi thường");
        void Disbursement(int type, decimal amount, string label)
        {
            if (amount <= 0) return;
            db.PhieuChis.Add(new PhieuChi { MaHopDong=id, LoaiChi=type, SoTien=amount,
                NgayChi=DateTime.Now, HinhThucChi=paymentMethod, MaNhanVienChi=employee,
                GhiChu=$"Quyết toán HD{id}: {label}. {note}" });
        }
        Disbursement(0,q.RefundDeposit,"hoàn cọc"); Disbursement(1,q.RefundRent,"hoàn tiền thuê");
        Disbursement(1,q.RefundExcess,"hoàn tiền chuyển thừa"); Disbursement(2,q.RefundOther,"hoàn khoản khác khi hủy");
        if (kind == 2)
            foreach (var k in h.KyHanThanhToans.Where(k => k.TrangThai != 1)) k.TrangThai=3;
        else
            foreach (var k in h.KyHanThanhToans.Where(k => k.TrangThai != 3))
            {
                k.SoTienDaTra=k.SoTienPhai; k.TrangThai=1; k.NgayThanhToan=DateTime.Now;
                k.TienPhat=0;
            }
        h.TrangThai=kind==2 ? 3 : 2;
        h.TrangThaiThanhToan=ContractPaymentStatus.Settled;
        h.TrangThaiHoanCoc=q.DepositRefunded+q.RefundDeposit>0 ? 1 : 2;
        h.TienCocThucHoan=q.DepositRefunded+q.RefundDeposit;
        h.TienTraThua=0; h.NgayHoanCoc=DateTime.Now; h.GhiChuHoanCoc="Đã quyết toán; xem chi tiết và chứng từ.";
        await ReleaseAsync(db,h,employee,kind==2 ? "Hủy hợp đồng" : "Quyết toán trả máy");
        q.Completed=true;
        db.ContractSettlements.Add(new ContractSettlement { MaHopDong=id, LoaiQuyetToan=kind, MaNhanVien=employee,
            NgayQuyetToan=DateTime.Now, CocThucThu=q.DepositReceived, CocDaHoan=q.DepositRefunded,
            CocCanTruThue=q.DepositToRent, CocCanTruBoiThuong=q.DepositToDamages,
            HoanCoc=q.RefundDeposit, HoanThue=q.RefundRent, HoanThua=q.RefundExcess, HoanKhac=q.RefundOther,
            MaBanXemTruoc=q.Token, ChiTietJson=JsonSerializer.Serialize(q) });
        db.ThongBaos.Add(new ThongBao { MaNguoiDung=h.MaKhachHang, TieuDe=$"Quyết toán hợp đồng #{id}",
            NoiDung=$"Đã quyết toán. Tổng tiền hoàn: {q.TotalRefund:N0} đ.", LoaiThongBao="ThanhToan", LienKet=$"/Cart/ContractDetail/{id}" });
        await db.SaveChangesAsync(); await tx.CommitAsync();
        return new(true,$"Đã quyết toán. Hoàn cọc {q.RefundDeposit:N0} đ; tổng tiền hoàn {q.TotalRefund:N0} đ.",q);
    }

    private static async Task ReleaseAsync(ApplicationDbContext db, HopDong h, int employee, string note)
    {
        var details=await db.ChiTietHopDongs.Include(c=>c.ThietBi).Where(c=>c.MaHopDong==h.MaHopDong).ToListAsync();
        foreach(var c in details)
        {
            var t=c.ThietBi;
            bool broken=t.TrangThai==4 || await db.PhieuBaoTris.AnyAsync(p=>p.MaThietBi==t.MaThietBi && p.TrangThai==4);
            t.TrangThai=broken ? 4 : await ContractLifecycle.ReleasedDeviceStatusAsync(db,t,h.MaHopDong);
            db.LichSuThietBis.Add(new LichSuThietBi { MaThietBi=t.MaThietBi, MaNguoiThucHien=employee, HanhDong=note, GhiChu=$"Hợp đồng #{h.MaHopDong}" });
        }
        if(h.TrangThai!=3 && !await db.BienBanBanGiaos.AnyAsync(b=>b.MaHopDong==h.MaHopDong && b.LoaiBienBan==1) &&
            !db.BienBanBanGiaos.Local.Any(b=>b.MaHopDong==h.MaHopDong && b.LoaiBienBan==1))
            db.BienBanBanGiaos.Add(new BienBanBanGiao { MaHopDong=h.MaHopDong, LoaiBienBan=1, NgayLap=DateTime.Now,
                MaNhanVienLap=employee, PhuKienKemTheo="Theo kiểm tra thu hồi", TinhTrangNgoaiQuan="Đã tiếp nhận thiết bị", GhiChu=note });
    }
}
