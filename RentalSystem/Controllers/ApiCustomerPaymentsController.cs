using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Common;
using RentalSystem.Models;
using RentalSystem.Services;

namespace RentalSystem.Controllers;

[ApiController]
[Authorize(AuthenticationSchemes = ApiTokens.Scheme, Roles = "KhachHang")]
public sealed class ApiCustomerPaymentsController(ApplicationDbContext db, IWebHostEnvironment env,
    IConfiguration config, IVnPayService vnPay) : ControllerBase
{
    [HttpGet("api/contracts/{id:int}/sign")]
    public async Task<IActionResult> SignInfo(int id)
    {
        var h = await db.HopDongs.FirstOrDefaultAsync(h => h.MaHopDong == id && h.MaKhachHang == User.UserId());
        if (h == null) return NotFound();
        return Ok(new { canSign = h.TrangThai == 0 && !h.YeuCauHuy && string.IsNullOrWhiteSpace(h.ChuKyKhachHang),
            maxInstallments = Math.Max(1, RentalBooking.RentalDays(h.NgayBatDau, h.NgayKetThuc) / 7),
            customerSigned = !string.IsNullOrWhiteSpace(h.ChuKyKhachHang),
            customerSignature = h.ChuKyKhachHang, staffSignature = h.ChuKyNhanVien });
    }

    [HttpPost("api/contracts/{id:int}/sign")]
    [RequestSizeLimit(11 * 1024 * 1024)]
    public async Task<IActionResult> Sign(int id, [FromForm] ContractSignatureUpload request)
    {
        try
        {
            var h = await ContractDocuments.SignAsync(db, env, User.UserId(), id, request.Installments,
                request.Front, request.Back, request.SignatureData, cancellation: HttpContext.RequestAborted);
            if (h == null) return NotFound();
            return Ok(new { success = true, customerSigned = true, installmentsCount = h.SoKyHan });
        }
        catch (RentalBookingException error) { return StatusCode(error.StatusCode, new { message = error.Message }); }
    }

    [HttpGet("api/contracts/{id:int}/renewals")]
    public async Task<IActionResult> Renewals(int id)
    {
        if (!await db.HopDongs.AnyAsync(h => h.MaHopDong == id && h.MaKhachHang == User.UserId())) return NotFound();
        return Ok(await db.YeuCauGiaHans.Where(y => y.MaHopDong == id).OrderByDescending(y => y.MaYeuCau)
            .Select(y => new { id = y.MaYeuCau, days = y.SoNgayGiaHan, notes = y.LyDo, statusCode = y.TrangThai,
                requestedAt = y.NgayYeuCau, reviewedAt = y.NgayDuyet, response = y.GhiChuAdmin }).ToListAsync());
    }

    [HttpGet("api/debts")]
    public async Task<IActionResult> Debts()
    {
        var rows = await db.KyHanThanhToans.Include(k => k.HopDong).Where(k => k.HopDong.MaKhachHang == User.UserId() &&
            k.HopDong.TrangThai != 3 && k.TrangThai != 3).OrderBy(k => k.NgayDenHan).ThenBy(k => k.MaKyHan).ToListAsync();
        RentalSystem.Areas.Admin.Controllers.HopDongController.CapNhatTreHanVaPhiPhat(rows.Where(k => !FirstContractPayment.IsPendingHandover(k.HopDong)));
        await db.SaveChangesAsync();
        var customerContracts = db.HopDongs.Where(h => h.MaKhachHang == User.UserId()).Select(h => h.MaHopDong);
        var settled = await db.ContractSettlements.Where(s => customerContracts.Contains(s.MaHopDong)).Select(s => s.MaHopDong).ToListAsync();
        var bank = BankTransfer.From(config);
        var receipts = await db.PhieuThus.Where(p => !p.DaHuy && p.HopDong.MaKhachHang == User.UserId()).ToListAsync();
        return Ok(rows.Select(k =>
        {
            bool first = FirstContractPayment.IsPendingHandover(k.HopDong);
            decimal balance = settled.Contains(k.MaHopDong) ? 0m : first
                ? (k.SoKyHan == 1 ? FirstContractPayment.Balance(k.HopDong,
                    receipts.Where(p => p.MaHopDong == k.MaHopDong), k).Total : 0m)
                : DebtCalculationHelper.GetInstallmentBalance(k);
            bool payable = balance > 0 && (first ? k.SoKyHan == 1 && !k.HopDong.YeuCauHuy &&
                !string.IsNullOrWhiteSpace(k.HopDong.ChuKyKhachHang) : k.TrangThai is 0 or 2);
            int days = !first && payable ? DebtCalculationHelper.DaysPastDue(k, DateTime.Today) : 0;
            string reference = first ? FirstContractPayment.TransferReference(k.MaHopDong) : $"HD{k.MaHopDong} KY{k.SoKyHan}";
            return new { id = k.MaKyHan, contractId = k.MaHopDong, period = k.SoKyHan, dueDate = k.NgayDenHan,
                amountDue = k.SoTienPhai, amountPaid = k.SoTienDaTra, penalty = k.TienPhat,
                balance, daysPastDue = days, agingTier = DebtCalculationHelper.CalculateAgingTier(days),
                agingLabel = DebtCalculationHelper.GetAgingTierName(DebtCalculationHelper.CalculateAgingTier(days)),
                statusCode = k.TrangThai, confirmationStatus = k.TrangThaiXacNhan,
                confirmationNote = k.GhiChu, reference, isFirstPayment = first, canPay = payable,
                canSendReceipt = payable && k.TrangThaiXacNhan != 1,
                canVnPay = payable && !first && VnPayConfigured(), bank, qrUrl = payable ? bank.QrUrl(balance, reference) : null };
        }));
    }

    [HttpPost("api/debts/{id:int}/receipt")]
    [RequestSizeLimit(6 * 1024 * 1024)]
    public async Task<IActionResult> Receipt(int id, [FromForm] PaymentReceiptUpload request)
    {
        try
        {
            var row = await ContractDocuments.ReceiptAsync(db, env, User.UserId(), id, request.Reference,
                request.Image, HttpContext.RequestAborted);
            if (row == null) return NotFound();
            return Ok(new { success = true, confirmationStatus = row.TrangThaiXacNhan });
        }
        catch (RentalBookingException error) { return StatusCode(error.StatusCode, new { message = error.Message }); }
    }

    private bool VnPayConfigured() => !string.IsNullOrWhiteSpace(config["Vnpay:TmnCode"]) &&
        !string.IsNullOrWhiteSpace(config["Vnpay:HashSecret"]) && !string.IsNullOrWhiteSpace(config["Vnpay:ReturnUrl"]);

    [HttpPost("api/debts/{id:int}/vnpay")]
    public async Task<IActionResult> VnPay(int id)
    {
        var row = await db.KyHanThanhToans.Include(k => k.HopDong).ThenInclude(h => h.KhachHang)
            .FirstOrDefaultAsync(k => k.MaKyHan == id && k.HopDong.MaKhachHang == User.UserId());
        if (row == null) return NotFound();
        if (!VnPayConfigured()) return StatusCode(503, new { message = "VNPay chưa được cấu hình. Vui lòng dùng chuyển khoản." });
        if (row.HopDong.TrangThai == 3 || !DebtCalculationHelper.IsPayableInstallment(row) ||
            await db.ContractSettlements.AnyAsync(s => s.MaHopDong == row.MaHopDong)) return Conflict(new { message = "Kỳ hạn không nhận thanh toán VNPay." });
        decimal amount = DebtCalculationHelper.GetInstallmentBalance(row);
        if (amount <= 0) return Conflict(new { message = "Kỳ hạn đã được thanh toán đủ." });
        string url = vnPay.CreatePaymentUrl(HttpContext, new VnPaymentRequestModel
        {
            ContractId = row.MaHopDong, InstallmentId = row.MaKyHan, Amount = amount,
            FullName = row.HopDong.KhachHang.HoTen, Description = $"Thanh toan HD{row.MaHopDong} Ky{row.SoKyHan}",
            CreatedDate = DateTime.Now,
            IsMobile = true
        });
        return Ok(new { url });
    }
}

public sealed class ContractSignatureUpload
{
    public int Installments { get; set; } = 1;
    public IFormFile? Front { get; set; }
    public IFormFile? Back { get; set; }
    public string? SignatureData { get; set; }
}
public sealed class PaymentReceiptUpload
{
    public string? Reference { get; set; }
    public IFormFile? Image { get; set; }
}
