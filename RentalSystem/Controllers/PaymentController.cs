using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using RentalSystem.Areas.Admin.Controllers;
using RentalSystem.Common;
using RentalSystem.Models;
using RentalSystem.Services;

namespace RentalSystem.Controllers
{
    public class PaymentController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly IVnPayService _vnPayService;
        private readonly ILogger<PaymentController> _logger;

        public PaymentController(
            ApplicationDbContext context,
            IVnPayService vnPayService,
            ILogger<PaymentController> logger)
        {
            _context = context;
            _vnPayService = vnPayService;
            _logger = logger;
        }

        /// <summary>
        /// Tạo URL thanh toán VNPay và chuyển hướng khách hàng sang cổng VNPay
        /// </summary>
        [HttpGet, HttpPost]
        public async Task<IActionResult> CreatePaymentUrl(int maHopDong, int? maKyHan = null, decimal? soTien = null)
        {
            var hopDong = await _context.HopDongs
                .Include(h => h.KhachHang)
                .Include(h => h.KyHanThanhToans)
                .FirstOrDefaultAsync(h => h.MaHopDong == maHopDong);

            if (hopDong == null)
            {
                return NotFound("Không tìm thấy hợp đồng yêu cầu.");
            }

            decimal amountToPay = 0;
            if (soTien.HasValue && soTien.Value > 0)
            {
                amountToPay = soTien.Value;
            }
            else if (maKyHan.HasValue && maKyHan.Value > 0)
            {
                var kyHan = hopDong.KyHanThanhToans?.FirstOrDefault(k => k.MaKyHan == maKyHan.Value);
                if (kyHan == null)
                {
                    return NotFound("Không tìm thấy kỳ hạn thanh toán chỉ định.");
                }
                amountToPay = Math.Max(0, kyHan.SoTienPhai - kyHan.SoTienDaTra + kyHan.PhiPhatTreHan);
            }
            else
            {
                // Tìm kỳ hạn gần nhất chưa hoàn tất
                var nextKy = hopDong.KyHanThanhToans?
                    .OrderBy(k => k.SoKyHan)
                    .FirstOrDefault(k => k.TrangThai == 0 || k.TrangThai == 2);

                if (nextKy != null)
                {
                    maKyHan = nextKy.MaKyHan;
                    amountToPay = Math.Max(0, nextKy.SoTienPhai - nextKy.SoTienDaTra + nextKy.PhiPhatTreHan);
                }
                else if (hopDong.TienDaCoc > 0 && hopDong.TrangThaiThanhToan == 0)
                {
                    amountToPay = hopDong.TienDaCoc;
                }
                else
                {
                    decimal daThu = await _context.PhieuThus
                        .Where(p => p.MaHopDong == maHopDong && !p.DaHuy)
                        .SumAsync(p => (decimal?)p.SoTien) ?? 0;
                    amountToPay = Math.Max(0, hopDong.TongTien - daThu);
                }
            }

            if (amountToPay <= 0)
            {
                TempData["Warning"] = "Hợp đồng hoặc kỳ hạn này đã được thanh toán đủ!";
                return RedirectToAction("ContractDetail", "Cart", new { id = maHopDong });
            }

            string orderDesc = maKyHan.HasValue
                ? $"Thanh toan HD{maHopDong} Ky{maKyHan}"
                : $"Thanh toan HD{maHopDong}";

            var request = new VnPaymentRequestModel
            {
                ContractId = maHopDong,
                InstallmentId = maKyHan,
                FullName = hopDong.KhachHang?.HoTen ?? "Khach Hang",
                Description = orderDesc,
                Amount = amountToPay,
                CreatedDate = DateTime.Now
            };

            var paymentUrl = _vnPayService.CreatePaymentUrl(HttpContext, request);
            _logger.LogInformation("Redirecting user to VNPay URL for Contract #{ContractId}, Amount: {Amount}", maHopDong, amountToPay);
            return Redirect(paymentUrl);
        }

        /// <summary>
        /// Endpoint tiếp nhận khi người dùng hoàn tất thanh toán và được VNPay redirect về web
        /// </summary>
        [HttpGet]
        public async Task<IActionResult> PaymentCallback()
        {
            var response = _vnPayService.PaymentExecute(Request.Query);

            if (!response.IsValidSignature)
            {
                _logger.LogWarning("VNPay callback with invalid signature for OrderId: {OrderId}", response.OrderId);
                TempData["Error"] = "Chữ ký bảo mật VNPay không hợp lệ hoặc giao dịch đã bị can thiệp!";
                if (response.ContractId > 0)
                {
                    return RedirectToAction("ContractDetail", "Cart", new { id = response.ContractId });
                }
                return RedirectToAction("Index", "Home");
            }

            if (response.VnPayResponseCode != "00")
            {
                _logger.LogWarning("VNPay payment failed or cancelled with response code {Code} for OrderId: {OrderId}", response.VnPayResponseCode, response.OrderId);
                TempData["Error"] = $"Giao dịch VNPay không thành công hoặc đã bị hủy (Mã phản hồi: {response.VnPayResponseCode}).";
                if (response.ContractId > 0)
                {
                    return RedirectToAction("ContractDetail", "Cart", new { id = response.ContractId });
                }
                return RedirectToAction("Index", "Home");
            }

            // Cập nhật thanh toán (bỏ qua nếu IPN đã xử lý trước)
            var (rspCode, message) = await ProcessPaymentAsync(response);

            if (rspCode == "00" || rspCode == "02")
            {
                TempData["Success"] = $"Thanh toán thành công {response.Amount:N0} VNĐ qua cổng trực tuyến VNPay! (Mã GD: {response.TransactionId})";
            }
            else
            {
                TempData["Warning"] = $"VNPay xác nhận thành công nhưng hệ thống báo: {message}";
            }

            if (response.ContractId > 0)
            {
                return RedirectToAction("ContractDetail", "Cart", new { id = response.ContractId });
            }

            return RedirectToAction("Index", "Home");
        }

        /// <summary>
        /// Server-to-server Webhook IPN từ VNPay để tự động cập nhật CSDL
        /// </summary>
        [HttpGet, HttpPost]
        public async Task<IActionResult> VnPayIPN()
        {
            try
            {
                IQueryCollection query = Request.Query;
                if (query.Count == 0 && Request.HasFormContentType)
                {
                    query = new QueryCollection(Request.Form.ToDictionary(k => k.Key, v => v.Value));
                }

                var response = _vnPayService.PaymentExecute(query);

                // Kiểm tra chữ ký hợp lệ
                if (!response.IsValidSignature)
                {
                    _logger.LogWarning("VNPay IPN: Invalid signature for OrderId: {OrderId}", response.OrderId);
                    return Json(new { RspCode = "97", Message = "Invalid signature" });
                }

                // Trường hợp thanh toán không thành công hoặc khách hủy
                if (response.VnPayResponseCode != "00")
                {
                    _logger.LogInformation("VNPay IPN: Payment status not success ({Code}) for OrderId: {OrderId}", response.VnPayResponseCode, response.OrderId);
                    return Json(new { RspCode = "00", Message = "Payment status acknowledged" });
                }

                // Ghi nhận thanh toán vào hệ thống
                var (rspCode, message) = await ProcessPaymentAsync(response);
                return Json(new { RspCode = rspCode, Message = message });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "VNPay IPN Exception");
                return Json(new { RspCode = "99", Message = "Unknown error" });
            }
        }

        // Xử lý ghi nhận thanh toán VNPay vào CSDL
        private async Task<(string rspCode, string message)> ProcessPaymentAsync(VnPaymentResponseModel response)
        {
            // Kiểm tra tính hợp lệ cơ bản
            if (response.Amount <= 0)
            {
                return ("04", "Invalid amount");
            }

            // Kiểm tra giao dịch đã được ghi nhận trước đó hay chưa
            if (!string.IsNullOrEmpty(response.TransactionId))
            {
                bool daGhiNhan = await _context.PhieuThus.AnyAsync(p => p.MaGiaoDichNganHang == response.TransactionId && !p.DaHuy);
                if (daGhiNhan)
                {
                    _logger.LogInformation("VNPay transaction {Txn} already processed previously.", response.TransactionId);
                    return ("02", "Order already confirmed");
                }
            }

            // Kiểm tra hợp đồng tồn tại
            var hopDong = await _context.HopDongs
                .Include(h => h.KyHanThanhToans)
                .FirstOrDefaultAsync(h => h.MaHopDong == response.ContractId);

            if (hopDong == null)
            {
                _logger.LogWarning("VNPay IPN: Contract #{ContractId} not found.", response.ContractId);
                return ("01", "Order not found");
            }

            // Xác định loại phiếu thu (0: Thu thuê kỳ hạn, 1: Thu cọc)
            int loaiPhieu = 0;
            if (response.InstallmentId == null || response.InstallmentId <= 0)
            {
                if (hopDong.TienDaCoc > 0 && hopDong.TrangThaiThanhToan == 0)
                {
                    loaiPhieu = 1; // Thu cọc
                }
            }

            // Tạo phiếu thu mới
            var phieuThu = new PhieuThu
            {
                MaHopDong = response.ContractId,
                LoaiPhieu = loaiPhieu,
                SoTien = response.Amount,
                NgayGiaoDich = DateTime.Now,
                HinhThucThanhToan = 2, // 2 = Online / VNPay
                MaKyHan = response.InstallmentId,
                MaGiaoDichNganHang = response.TransactionId,
                NganHangNhan = string.IsNullOrEmpty(response.BankCode) ? "VNPAY" : response.BankCode,
                GhiChu = $"Thanh toán trực tuyến cổng VNPay (Mã GD: {response.TransactionId}, Ngân hàng: {response.BankCode})",
                MaNhanVienThu = null, // Cổng thanh toán trực tuyến tự động
                DaHuy = false
            };
            _context.PhieuThus.Add(phieuThu);

            // Cập nhật trạng thái kỳ hạn
            if (response.InstallmentId.HasValue && response.InstallmentId > 0)
            {
                var kyHan = hopDong.KyHanThanhToans?.FirstOrDefault(k => k.MaKyHan == response.InstallmentId.Value);
                if (kyHan != null)
                {
                    kyHan.SoTienDaTra += response.Amount;
                    if (kyHan.SoTienDaTra >= kyHan.SoTienPhai)
                    {
                        kyHan.TrangThai = 1; // Đã trả
                    }
                    kyHan.NgayThanhToan = DateTime.Now;
                    kyHan.TrangThaiXacNhan = 2; // Đã xác nhận đối soát
                    kyHan.MaGiaoDichChuyenKhoan = response.TransactionId;
                }
            }
            else
            {
                // Nếu thanh toán chung cho hợp đồng, trừ dần vào các kỳ hạn chưa trả
                decimal remainingPaid = response.Amount;
                var unpaidKyHans = hopDong.KyHanThanhToans?
                    .Where(k => k.TrangThai != 1)
                    .OrderBy(k => k.SoKyHan)
                    .ToList();

                if (unpaidKyHans != null)
                {
                    foreach (var k in unpaidKyHans)
                    {
                        if (remainingPaid <= 0) break;
                        decimal canThu = Math.Max(0, k.SoTienPhai - k.SoTienDaTra);
                        if (remainingPaid >= canThu)
                        {
                            k.SoTienDaTra += canThu;
                            k.TrangThai = 1;
                            k.NgayThanhToan = DateTime.Now;
                            k.TrangThaiXacNhan = 2;
                            k.MaGiaoDichChuyenKhoan = response.TransactionId;
                            remainingPaid -= canThu;
                        }
                        else
                        {
                            k.SoTienDaTra += remainingPaid;
                            k.TrangThaiXacNhan = 2;
                            k.MaGiaoDichChuyenKhoan = response.TransactionId;
                            remainingPaid = 0;
                        }
                    }
                }
            }

            // Đồng bộ trạng thái thanh toán của hợp đồng
            if (hopDong.KyHanThanhToans != null && hopDong.KyHanThanhToans.Any())
            {
                if (hopDong.KyHanThanhToans.All(k => k.TrangThai == 1))
                {
                    hopDong.TrangThaiThanhToan = 2; // Đã thanh toán đủ (hoặc 3 khi áp dụng 4 cấp)
                }
                else if (hopDong.KyHanThanhToans.Any(k => k.SoTienDaTra > 0) || hopDong.TienDaCoc > 0)
                {
                    hopDong.TrangThaiThanhToan = 1; // Còn nợ
                }
            }
            else if (hopDong.TienDaCoc > 0)
            {
                hopDong.TrangThaiThanhToan = 1;
            }

            await _context.SaveChangesAsync();
            _logger.LogInformation("Successfully processed VNPay payment for Contract #{ContractId}, Amount: {Amount}, Receipt #{ReceiptId}", response.ContractId, response.Amount, phieuThu.MaPhieuThu);

            return ("00", "Confirm Success");
        }

        #region Xử lý Webhook biến động số dư ngân hàng

        /// <summary>
        /// Endpoint tiếp nhận Webhook biến động số dư từ cổng thanh toán / ngân hàng.
        /// Bóc tách mã hợp đồng từ nội dung chuyển khoản, phân bổ thanh toán các kỳ hạn và tạo phiếu thu.
        /// </summary>
        [HttpPost]
        [Route("Payment/BankingWebhook")]
        [Route("api/PaymentWebhook/Banking")]
        [IgnoreAntiforgeryToken]
        public async Task<IActionResult> BankingWebhook([FromBody] BankingWebhookModel payload)
        {
            if (payload == null)
            {
                _logger.LogWarning("BankingWebhook: Received null payload");
                return BadRequest(new { success = false, message = "Payload cannot be null" });
            }

            // Hỗ trợ trường hợp webhook gửi danh sách nhiều giao dịch
            if (payload.Data != null && payload.Data.Count > 0)
            {
                if (payload.Data.Count == 1)
                {
                    var singleModel = MapCassoItemToWebhookModel(payload.Data[0], payload);
                    return await ProcessSingleBankingTransactionAsync(singleModel);
                }

                var batchResults = new List<object>();
                foreach (var item in payload.Data)
                {
                    var singleModel = MapCassoItemToWebhookModel(item, payload);
                    var execResult = await ExecuteSingleReconciliationAsync(singleModel);
                    batchResults.Add(execResult.ResponseData);
                }

                return Ok(new
                {
                    success = true,
                    total = payload.Data.Count,
                    results = batchResults,
                    message = "Batch webhook processed"
                });
            }

            // Xử lý giao dịch đơn lẻ
            return await ProcessSingleBankingTransactionAsync(payload);
        }

        private static BankingWebhookModel MapCassoItemToWebhookModel(CassoTransactionModel item, BankingWebhookModel parent)
        {
            return new BankingWebhookModel
            {
                Id = item.Id,
                Tid = item.Tid,
                ReferenceCode = !string.IsNullOrWhiteSpace(item.Tid) ? item.Tid : item.Id?.ToString(),
                Content = item.Description,
                Description = item.Description,
                Amount = item.Amount,
                TransferAmount = item.Amount,
                AmountIn = item.Amount,
                Gateway = item.BankName ?? parent.Gateway ?? "MBBank",
                AccountNumber = item.Bank_account_id ?? item.Bank_sub_acc_id ?? item.SubAccId ?? parent.AccountNumber,
                TransactionDate = item.When,
                TransferType = (item.Amount.HasValue && item.Amount.Value < 0) ? "out" : "in"
            };
        }

        private async Task<IActionResult> ProcessSingleBankingTransactionAsync(BankingWebhookModel model)
        {
            var result = await ExecuteSingleReconciliationAsync(model);
            if (result.StatusCode == 400)
            {
                return BadRequest(result.ResponseData);
            }
            return Ok(result.ResponseData);
        }

        private async Task<BankingExecutionResult> ExecuteSingleReconciliationAsync(BankingWebhookModel model)
        {
            // Kiểm tra số tiền giao dịch hợp lệ
            decimal amount = model.TransferAmount ?? model.AmountIn ?? model.Amount ?? 0m;
            string transferType = model.TransferType ?? "in";

            if (string.Equals(transferType, "out", StringComparison.OrdinalIgnoreCase) || amount <= 0)
            {
                _logger.LogInformation("BankingWebhook: Ignored outgoing transfer or non-positive amount ({Amount}, type: {Type})", amount, transferType);
                return new BankingExecutionResult
                {
                    StatusCode = 200,
                    ResponseData = new
                    {
                        success = true,
                        ignored = true,
                        message = "Outgoing transfer or non-positive amount ignored"
                    }
                };
            }

            // Bóc tách mã hợp đồng và số kỳ hạn từ nội dung chuyển khoản
            string rawContent = string.Join(" ", new[] { model.Content, model.Description, model.Code }
                .Where(s => !string.IsNullOrWhiteSpace(s)));

            var hdRegex = new Regex(@"(?i)(?:HD|HĐ)[\s\-_:#]*([0-9]{1,10})");
            var matchHd = hdRegex.Match(rawContent);

            if (!matchHd.Success || !int.TryParse(matchHd.Groups[1].Value, out int maHopDong))
            {
                _logger.LogWarning("BankingWebhook: Could not extract valid contract ID from content '{Content}'", rawContent);
                return new BankingExecutionResult
                {
                    StatusCode = 200,
                    ResponseData = new
                    {
                        success = false,
                        message = $"Could not extract valid contract ID from content: {rawContent}"
                    }
                };
            }

            var kyRegex = new Regex(@"(?i)(?:KY|KỲ)[\s\-_:#]*([0-9]{1,3})");
            var matchKy = kyRegex.Match(rawContent);
            int? parsedSoKyHan = (matchKy.Success && int.TryParse(matchKy.Groups[1].Value, out int kNum)) ? kNum : null;

            // Chuẩn hóa mã giao dịch ngân hàng
            string referenceCode = !string.IsNullOrWhiteSpace(model.ReferenceCode)
                ? model.ReferenceCode.Trim()
                : (!string.IsNullOrWhiteSpace(model.ReferenceNumber)
                    ? model.ReferenceNumber.Trim()
                    : (!string.IsNullOrWhiteSpace(model.Tid)
                        ? model.Tid.Trim()
                        : (model.Id.HasValue ? model.Id.Value.ToString() : $"OB_{DateTime.Now:yyyyMMddHHmmss}_{maHopDong}")));

            string gateway = !string.IsNullOrWhiteSpace(model.Gateway) ? model.Gateway.Trim() : "OpenBanking";
            string content = !string.IsNullOrWhiteSpace(model.Content)
                ? model.Content.Trim()
                : (!string.IsNullOrWhiteSpace(model.Description)
                    ? model.Description.Trim()
                    : rawContent);

            // Khóa đồng bộ và mở giao dịch Serializable để tránh xử lý trùng
            await HopDongController.PaymentLock.WaitAsync();
            try
            {
                using var tx = await _context.Database.BeginTransactionAsync(System.Data.IsolationLevel.Serializable);
                try
                {
                    // Kiểm tra trùng lặp mã giao dịch ngân hàng
                    bool isDuplicate = await _context.PhieuThus.AnyAsync(p =>
                        (p.MaGiaoDichNganHang == referenceCode || (p.GhiChu != null && p.GhiChu.Contains(referenceCode)))
                        && !p.DaHuy);

                    if (isDuplicate)
                    {
                        _logger.LogInformation("BankingWebhook: Transaction {RefCode} already processed.", referenceCode);
                        return new BankingExecutionResult
                        {
                            StatusCode = 200,
                            ResponseData = new
                            {
                                success = true,
                                isDuplicate = true,
                                message = "Transaction already processed"
                            }
                        };
                    }

                    // Tải hợp đồng cùng kỳ hạn, phiếu bảo trì, khách hàng
                    var hd = await _context.HopDongs
                        .Include(h => h.KyHanThanhToans)
                        .Include(h => h.PhieuBaoTris)
                        .Include(h => h.KhachHang)
                        .FirstOrDefaultAsync(h => h.MaHopDong == maHopDong);

                    if (hd == null)
                    {
                        _logger.LogWarning("BankingWebhook: Contract #{ContractId} not found.", maHopDong);
                        return new BankingExecutionResult
                        {
                            StatusCode = 200,
                            ResponseData = new
                            {
                                success = false,
                                message = $"Contract #{maHopDong} not found"
                            }
                        };
                    }

                    decimal transferAmount = amount;
                    decimal tienConLai = transferAmount;
                    int? primaryKyHanId = null;
                    DateTime txnDate = DateTime.Now;
                    if (!string.IsNullOrWhiteSpace(model.TransactionDate) && DateTime.TryParse(model.TransactionDate, out DateTime parsedDate))
                    {
                        txnDate = parsedDate;
                    }

                    // Phân bổ số tiền thanh toán:
                    // 1) Nếu có kỳ hạn chỉ định trong nội dung, ưu tiên thanh toán trước (gốc + tiền phạt)
                    if (parsedSoKyHan.HasValue && hd.KyHanThanhToans != null)
                    {
                        var targetKy = hd.KyHanThanhToans.FirstOrDefault(k => k.SoKyHan == parsedSoKyHan.Value && k.TrangThai != 3);
                        if (targetKy != null)
                        {
                            primaryKyHanId = targetKy.MaKyHan;
                            if (targetKy.TrangThai != 1)
                            {
                                decimal penalty = Math.Max(targetKy.TienPhat, targetKy.PhiPhatTreHan);
                                decimal conThieu = Math.Max(0m, (targetKy.SoTienPhai - targetKy.SoTienDaTra) + penalty);

                                if (tienConLai >= conThieu)
                                {
                                    targetKy.SoTienDaTra = targetKy.SoTienPhai;
                                    targetKy.TrangThai = 1;
                                    targetKy.NgayThanhToan = txnDate;
                                    targetKy.TienPhat = 0;
                                    targetKy.PhiPhatTreHan = 0;
                                    targetKy.SoNgayTreHan = 0;
                                    targetKy.TrangThaiXacNhan = 2; // Đã duyệt đối soát
                                    targetKy.MaGiaoDichChuyenKhoan = referenceCode;
                                    targetKy.GhiChu = ((targetKy.GhiChu ?? "") + $" [Thanh toán tự động Open Banking ({gateway}): {transferAmount:N0}đ]").Trim();
                                    tienConLai -= conThieu;
                                }
                                else
                                {
                                    targetKy.SoTienDaTra += tienConLai;
                                    targetKy.TrangThai = (targetKy.NgayDenHan.Date < DateTime.Now.Date) ? 2 : 0;
                                    targetKy.TrangThaiXacNhan = 2;
                                    targetKy.MaGiaoDichChuyenKhoan = referenceCode;
                                    targetKy.GhiChu = ((targetKy.GhiChu ?? "") + $" [Thanh toán 1 phần Open Banking ({gateway}): {tienConLai:N0}đ]").Trim();
                                    tienConLai = 0;
                                }
                            }
                        }
                    }

                    // 2) Phân bổ số dư cho các kỳ hạn chưa thanh toán khác theo thứ tự SoKyHan tăng dần
                    if (tienConLai > 0 && hd.KyHanThanhToans != null)
                    {
                        var unpaidKyHans = hd.KyHanThanhToans
                            .Where(k => (k.TrangThai == 0 || k.TrangThai == 2) && (!primaryKyHanId.HasValue || k.MaKyHan != primaryKyHanId.Value))
                            .OrderBy(k => k.SoKyHan)
                            .ToList();

                        foreach (var nextKy in unpaidKyHans)
                        {
                            if (tienConLai <= 0) break;
                            if (!primaryKyHanId.HasValue) primaryKyHanId = nextKy.MaKyHan;

                            decimal nextPenalty = Math.Max(nextKy.TienPhat, nextKy.PhiPhatTreHan);
                            decimal nextUnpaid = Math.Max(0m, (nextKy.SoTienPhai - nextKy.SoTienDaTra) + nextPenalty);
                            if (nextUnpaid <= 0)
                            {
                                nextKy.TrangThai = 1;
                                nextKy.TienPhat = 0;
                                nextKy.PhiPhatTreHan = 0;
                                nextKy.SoNgayTreHan = 0;
                                continue;
                            }

                            if (tienConLai >= nextUnpaid)
                            {
                                nextKy.SoTienDaTra = nextKy.SoTienPhai;
                                nextKy.TrangThai = 1;
                                nextKy.NgayThanhToan = txnDate;
                                nextKy.TienPhat = 0;
                                nextKy.PhiPhatTreHan = 0;
                                nextKy.SoNgayTreHan = 0;
                                nextKy.TrangThaiXacNhan = 2;
                                nextKy.MaGiaoDichChuyenKhoan = referenceCode;
                                nextKy.GhiChu = ((nextKy.GhiChu ?? "") + $" [Gạch nợ tự động Open Banking ({gateway}): {nextUnpaid:N0}đ]").Trim();
                                tienConLai -= nextUnpaid;
                            }
                            else
                            {
                                nextKy.SoTienDaTra += tienConLai;
                                nextKy.TrangThai = (nextKy.NgayDenHan.Date < DateTime.Now.Date) ? 2 : 0;
                                nextKy.TrangThaiXacNhan = 2;
                                nextKy.MaGiaoDichChuyenKhoan = referenceCode;
                                nextKy.GhiChu = ((nextKy.GhiChu ?? "") + $" [Gạch nợ 1 phần Open Banking ({gateway}): {tienConLai:N0}đ]").Trim();
                                tienConLai = 0;
                                break;
                            }
                        }
                    }

                    // 3) Phân bổ số dư cho chi phí bồi thường hư hại bảo trì chưa thanh toán (PhieuBaoTris)
                    decimal damageDeducted = 0m;
                    if (tienConLai > 0)
                    {
                        decimal totalDamages = hd.PhieuBaoTris?.Sum(b => b.PhiDenBu) ?? 0m;
                        decimal paidDamages = await _context.PhieuThus
                            .Where(p => p.MaHopDong == hd.MaHopDong && p.LoaiPhieu == 2 && !p.DaHuy)
                            .SumAsync(p => (decimal?)p.SoTien) ?? 0m;
                        decimal unpaidDamages = Math.Max(0m, totalDamages - paidDamages);

                        if (unpaidDamages > 0)
                        {
                            damageDeducted = Math.Min(tienConLai, unpaidDamages);
                            tienConLai -= damageDeducted;
                        }
                    }

                    // 4) Số tiền thừa còn lại chuyển vào TienTraThua của Hợp Đồng
                    if (tienConLai > 0)
                    {
                        hd.TienTraThua += tienConLai;
                        hd.GhiChu = ((hd.GhiChu ?? "") + $" [Khách chuyển thừa {tienConLai:N0}đ qua Open Banking ({gateway}, GD: {referenceCode})]").Trim();
                    }

                    // Xác định LoaiPhieu (0: Thu thuê kỳ hạn, 1: Thu cọc, 2: Thu phí bảo trì)
                    int loaiPhieu = 0;
                    if ((hd.KyHanThanhToans == null || !hd.KyHanThanhToans.Any()) && hd.TienDaCoc > 0 && hd.TrangThaiThanhToan == 0)
                    {
                        loaiPhieu = 1; // Thu cọc
                        hd.TrangThaiThanhToan = 1; // Đã đặt cọc
                    }
                    else if (damageDeducted > 0 && transferAmount == damageDeducted && (hd.KyHanThanhToans == null || hd.KyHanThanhToans.All(k => k.TrangThai == 1)))
                    {
                        loaiPhieu = 2; // Thu phí bồi thường bảo trì
                    }

                    // Tạo PhieuThu
                    var phieuThu = new PhieuThu
                    {
                        MaHopDong = hd.MaHopDong,
                        LoaiPhieu = loaiPhieu,
                        SoTien = transferAmount,
                        NgayGiaoDich = txnDate,
                        HinhThucThanhToan = 1, // 1 = Chuyển khoản
                        MaKyHan = primaryKyHanId,
                        MaGiaoDichNganHang = referenceCode,
                        NganHangNhan = !string.IsNullOrWhiteSpace(model.Gateway) ? model.Gateway : "MBBank (0783406516)",
                        GhiChu = $"Tự động gạch nợ qua Open Banking Webhook ({gateway}): {content}",
                        MaNhanVienThu = null,
                        DaHuy = false
                    };
                    _context.PhieuThus.Add(phieuThu);

                    // Lưu phiếu thu trước để truy vấn trong SyncTrangThaiThanhToanHopDong thấy được
                    await _context.SaveChangesAsync();

                    // 5) Đồng bộ trạng thái hợp đồng qua HopDongController.SyncTrangThaiThanhToanHopDong(hd)
                    await HopDongController.SyncTrangThaiThanhToanHopDong(hd, _context);
                    await _context.SaveChangesAsync();

                    // Tạo thông báo cho khách hàng (ThongBao)
                    if (hd.KhachHang != null || hd.MaKhachHang > 0)
                    {
                        var thongBao = new ThongBao
                        {
                            MaNguoiDung = hd.MaKhachHang,
                            TieuDe = $"[Thanh toán tự động] Hợp đồng HD{hd.MaHopDong}",
                            NoiDung = $"Hệ thống đã tự động gạch nợ thành công số tiền {transferAmount:N0} VNĐ qua chuyển khoản ngân hàng ({gateway}, GD: {referenceCode}).",
                            NgayTao = DateTime.Now,
                            DaDoc = false,
                            LoaiThongBao = "ThanhToan",
                            LienKet = $"/Cart/ContractDetail/{hd.MaHopDong}"
                        };
                        _context.ThongBaos.Add(thongBao);
                        await _context.SaveChangesAsync();
                    }

                    await tx.CommitAsync();

                    // Tính toán dư nợ còn lại sau gạch nợ
                    decimal totalReceivable = hd.TongTien + (hd.PhieuBaoTris?.Sum(b => b.PhiDenBu) ?? 0m);
                    decimal totalCollected = await _context.PhieuThus
                        .Where(p => p.MaHopDong == hd.MaHopDong && !p.DaHuy && (p.LoaiPhieu == 0 || p.LoaiPhieu == 2))
                        .SumAsync(p => (decimal?)p.SoTien) ?? 0m;
                    decimal remainingDebt = Math.Max(0m, totalReceivable - totalCollected);

                    _logger.LogInformation("BankingWebhook: Reconciled Contract #{ContractId}, Amount: {Amount}, Receipt #{ReceiptId}, RemainingDebt: {Debt}",
                        hd.MaHopDong, transferAmount, phieuThu.MaPhieuThu, remainingDebt);

                    return new BankingExecutionResult
                    {
                        StatusCode = 200,
                        ResponseData = new
                        {
                            success = true,
                            maHopDong = hd.MaHopDong,
                            soTien = transferAmount,
                            remainingDebt = remainingDebt,
                            message = "Reconciliation successful"
                        }
                    };
                }
                catch (Exception ex)
                {
                    await tx.RollbackAsync();
                    _logger.LogError(ex, "BankingWebhook: Error reconciling transaction {RefCode} for HD #{ContractId}", referenceCode, maHopDong);
                    throw;
                }
            }
            finally
            {
                HopDongController.PaymentLock.Release();
            }
        }

        #endregion
    }

    #region Webhook Data Transfer Objects

    public class BankingExecutionResult
    {
        public int StatusCode { get; set; } = 200;
        public object ResponseData { get; set; }
    }

    public class BankingWebhookModel
    {
        public long? Id { get; set; }
        public string? Gateway { get; set; }
        public string? TransactionDate { get; set; }
        [System.Text.Json.Serialization.JsonPropertyName("transaction_date")]
        public string? TransactionDateSnake { get => TransactionDate; set => TransactionDate = value; }

        public string? AccountNumber { get; set; }
        [System.Text.Json.Serialization.JsonPropertyName("account_number")]
        public string? AccountNumberSnake { get => AccountNumber; set => AccountNumber = value; }

        public string? SubAccount { get; set; }
        [System.Text.Json.Serialization.JsonPropertyName("sub_account")]
        public string? SubAccountSnake { get => SubAccount; set => SubAccount = value; }

        public decimal? AmountIn { get; set; }
        [System.Text.Json.Serialization.JsonPropertyName("amount_in")]
        public decimal? AmountInSnake { get => AmountIn; set => AmountIn = value; }

        public decimal? TransferAmount { get; set; }
        [System.Text.Json.Serialization.JsonPropertyName("transfer_amount")]
        public decimal? TransferAmountSnake { get => TransferAmount; set => TransferAmount = value; }

        public decimal? Amount { get; set; }
        public decimal? AmountOut { get; set; }
        public decimal? Accumulated { get; set; }

        public string? Code { get; set; }
        public string? Content { get; set; }
        public string? Description { get; set; }

        public string? ReferenceCode { get; set; }
        [System.Text.Json.Serialization.JsonPropertyName("reference_code")]
        public string? ReferenceCodeSnake { get => ReferenceCode; set => ReferenceCode = value; }

        public string? ReferenceNumber { get; set; }
        [System.Text.Json.Serialization.JsonPropertyName("reference_number")]
        public string? ReferenceNumberSnake { get => ReferenceNumber; set => ReferenceNumber = value; }

        public string? Tid { get; set; }
        public string? TransferType { get; set; }
        [System.Text.Json.Serialization.JsonPropertyName("transfer_type")]
        public string? TransferTypeSnake { get => TransferType; set => TransferType = value; }

        public int? Error { get; set; }
        public List<CassoTransactionModel>? Data { get; set; }
    }

    public class CassoTransactionModel
    {
        public long? Id { get; set; }
        public string? Tid { get; set; }
        public string? Description { get; set; }
        public decimal? Amount { get; set; }
        public decimal? Cusum_balance { get; set; }
        public string? When { get; set; }
        public string? Bank_sub_acc_id { get; set; }
        public string? SubAccId { get; set; }
        public string? BankName { get; set; }
        public string? Bank_account_id { get; set; }
        public string? Corresponsive_name { get; set; }
    }

    #endregion
}
