using Microsoft.AspNetCore.Authorization;
using RentalSystem.Common;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System.Text.Json.Serialization;

namespace RentalSystem.Controllers
{
    [Route("api/contracts")]
    [ApiController]
    [Authorize(AuthenticationSchemes = ApiTokens.Scheme)]
    public class ApiContractsController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public ApiContractsController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: api/contracts
        [HttpGet]
        public async Task<IActionResult> GetContracts()
        {
            var hopDongs = await _context.HopDongs.VisibleContracts(User, _context)
                .Include(h => h.KhachHang)
                .Include(h => h.NhanVien)
                .OrderByDescending(h => h.MaHopDong)
                .ToListAsync();
            var contractIds = hopDongs.Select(h => h.MaHopDong).ToArray();

            // Load ChiTietHopDongs and KyHanThanhToans
            var chiTiets = await _context.ChiTietHopDongs
                .Where(c => contractIds.Contains(c.MaHopDong))
                .Include(c => c.ThietBi)
                .ThenInclude(t => t.SanPham)
                .ToListAsync();

            var kyHans = await _context.KyHanThanhToans
                .Where(k => contractIds.Contains(k.MaHopDong))
                .OrderBy(k => k.SoKyHan)
                .ToListAsync();

            var result = hopDongs.Select(h =>
            {
                var hDetails = chiTiets.Where(c => c.MaHopDong == h.MaHopDong).ToList();
                var hKyHans = kyHans.Where(k => k.MaHopDong == h.MaHopDong).ToList();

                var deviceNames = hDetails.Select(c => 
                    c.ThietBi?.SanPham != null 
                        ? $"{c.ThietBi.SanPham.TenSanPham} ({c.ThietBi.SoSerial})" 
                        : (c.ThietBi != null ? $"Thiết bị #{c.ThietBi.MaThietBi} ({c.ThietBi.SoSerial})" : $"Mã #{c.MaThietBi}")
                ).ToList();

                string statusText = ContractLifecycle.Label(h);

                string paymentStatusText = ContractPaymentStatus.Label(h.TrangThaiThanhToan);

                return new
                {
                    id = h.MaHopDong.ToString(),
                    contractCode = $"HD-{h.MaHopDong:D4}",
                    customerId = h.MaKhachHang.ToString(),
                    customerName = h.KhachHang?.HoTen ?? "Khách hàng",
                    customerPhone = h.KhachHang?.SoDienThoai ?? "",
                    deviceIds = deviceNames,
                    devices = hDetails.Select(c => new
                    {
                        deviceId = c.MaThietBi.ToString(),
                        serialNumber = c.ThietBi?.SoSerial ?? "",
                        productName = c.ThietBi?.SanPham?.TenSanPham ?? "Thiết bị"
                    }),
                    rentalStart = h.NgayBatDau.ToString("dd/MM/yyyy"),
                    rentalEnd = h.NgayKetThuc.ToString("dd/MM/yyyy"),
                    rentalType = "Theo ngày",
                    status = statusText,
                    statusCode = h.TrangThai,
                    cancellationRequested = h.TrangThai == 0 && h.YeuCauHuy,
                    cancellationReason = h.LyDoHuy,
                    cancellationRequestedAt = h.NgayYeuCauHuy,
                    totalAmount = (double)h.TongTien,
                    depositAmount = (double)h.TienDaCoc,
                    paymentStatus = paymentStatusText,
                    paymentStatusCode = h.TrangThaiThanhToan,
                    note = h.GhiChu ?? "",
                    installationDetails = (string?)null,
                    extensionDetails = "",
                    installmentsCount = h.SoKyHan,
                    createdAt = h.NgayBatDau.ToString("o"),
                    installments = hKyHans.Select(k => new
                    {
                        installmentId = k.MaKyHan,
                        periodNumber = k.SoKyHan,
                        dueDate = k.NgayDenHan.ToString("dd/MM/yyyy"),
                        amountDue = (double)k.SoTienPhai,
                        amountPaid = (double)k.SoTienDaTra,
                        status = k.TrangThai == 1 ? "Đã thanh toán" : (k.NgayDenHan < DateTime.Now ? "Quá hạn" : "Chưa thanh toán"),
                        statusCode = k.TrangThai
                    }).ToList()
                };
            }).ToList();

            return Ok(result);
        }

        // GET: api/contracts/{id}
        [HttpGet("{id}")]
        public async Task<IActionResult> GetContractById(int id)
        {
            var h = await _context.HopDongs.VisibleContracts(User, _context)
                .Include(h => h.KhachHang)
                .Include(h => h.NhanVien)
                .FirstOrDefaultAsync(h => h.MaHopDong == id);

            if (h == null)
            {
                return NotFound(new { message = $"Không tìm thấy hợp đồng #{id}" });
            }

            var chiTiets = await _context.ChiTietHopDongs
                .Include(c => c.ThietBi)
                .ThenInclude(t => t.SanPham)
                .Where(c => c.MaHopDong == id)
                .ToListAsync();

            var kyHans = await _context.KyHanThanhToans
                .Where(k => k.MaHopDong == id)
                .OrderBy(k => k.SoKyHan)
                .ToListAsync();

            var deviceNames = chiTiets.Select(c => 
                c.ThietBi?.SanPham != null 
                    ? $"{c.ThietBi.SanPham.TenSanPham} ({c.ThietBi.SoSerial})" 
                    : (c.ThietBi != null ? $"Thiết bị #{c.ThietBi.MaThietBi} ({c.ThietBi.SoSerial})" : $"Mã #{c.MaThietBi}")
            ).ToList();

            string statusText = ContractLifecycle.Label(h);

            string paymentStatusText = ContractPaymentStatus.Label(h.TrangThaiThanhToan);

            var detail = new
            {
                id = h.MaHopDong.ToString(),
                contractCode = $"HD-{h.MaHopDong:D4}",
                customerId = h.MaKhachHang.ToString(),
                customerName = h.KhachHang?.HoTen ?? "Khách hàng",
                customerPhone = h.KhachHang?.SoDienThoai ?? "",
                customerEmail = h.KhachHang?.Email ?? "",
                customerAddress = h.KhachHang?.DiaChi ?? "",
                staffName = h.NhanVien?.HoTen ?? "Hệ thống",
                customerSigned = !string.IsNullOrWhiteSpace(h.ChuKyKhachHang),
                staffSigned = !string.IsNullOrWhiteSpace(h.ChuKyNhanVien),
                deviceIds = deviceNames,
                rentalStart = h.NgayBatDau.ToString("dd/MM/yyyy"),
                rentalEnd = h.NgayKetThuc.ToString("dd/MM/yyyy"),
                rentalType = "Theo ngày",
                status = statusText,
                statusCode = h.TrangThai,
                cancellationRequested = h.TrangThai == 0 && h.YeuCauHuy,
                cancellationReason = h.LyDoHuy,
                cancellationRequestedAt = h.NgayYeuCauHuy,
                totalAmount = (double)h.TongTien,
                depositAmount = (double)h.TienDaCoc,
                paymentStatus = paymentStatusText,
                paymentStatusCode = h.TrangThaiThanhToan,
                note = h.GhiChu ?? "",
                installationDetails = (string?)null,
                extensionDetails = "",
                installmentsCount = h.SoKyHan,
                devices = chiTiets.Select(c => new
                {
                    deviceId = c.MaThietBi.ToString(),
                    serialNumber = c.ThietBi?.SoSerial ?? "",
                    productName = c.ThietBi?.SanPham?.TenSanPham ?? "Thiết bị",
                    price = (double)c.GiaChotThu
                }).ToList(),
                installments = kyHans.Select(k => new
                {
                    installmentId = k.MaKyHan,
                    periodNumber = k.SoKyHan,
                    dueDate = k.NgayDenHan.ToString("dd/MM/yyyy"),
                    amountDue = (double)k.SoTienPhai,
                    amountPaid = (double)k.SoTienDaTra,
                    status = k.TrangThai == 1 ? "Đã thanh toán" : (k.NgayDenHan < DateTime.Now ? "Quá hạn" : "Chưa thanh toán"),
                    statusCode = k.TrangThai,
                    notes = k.GhiChu ?? ""
                }).ToList()
            };

            return Ok(detail);
        }

        // POST: api/contracts
        [Authorize(Roles = "KhachHang")]
        [HttpPost("quote")]
        public async Task<IActionResult> Quote([FromBody] CreateContractApiRequest request)
        {
            try
            {
                return Ok(await RentalBooking.QuoteAsync(_context, User.UserId(), request.ToRentalOrder(),
                    HttpContext.RequestAborted));
            }
            catch (RentalBookingException error)
            {
                return StatusCode(error.StatusCode, new { message = error.Message });
            }
        }

        [Authorize(Roles = "KhachHang")]
        [HttpPost]
        public async Task<IActionResult> CreateContract([FromBody] CreateContractApiRequest request)
        {
            try
            {
                var (contract, quote, deviceCount, customerName) = await RentalBooking.CreateAsync(
                    _context, User.UserId(), request.ToRentalOrder(), HttpContext.RequestAborted);
                return Ok(new
                {
                    success = true,
                    message = "Đã gửi yêu cầu thuê.",
                    contractId = contract.MaHopDong.ToString(),
                    contractCode = $"HD-{contract.MaHopDong:D4}",
                    customerId = contract.MaKhachHang.ToString(),
                    customerName,
                    quote.TotalAmount,
                    quote.RentalDays,
                    quote.DiscountAmount,
                    quote.PromoCode,
                    depositAmount = contract.TienDaCoc,
                    installmentsCount = contract.SoKyHan,
                    status = ContractLifecycle.Label(contract),
                    statusCode = contract.TrangThai,
                    cancellationRequested = false,
                    paymentStatusCode = contract.TrangThaiThanhToan,
                    deviceCount
                });
            }
            catch (RentalBookingException error)
            {
                return StatusCode(error.StatusCode, new { message = error.Message });
            }
        }

        [Authorize(Roles = "KhachHang")]
        [HttpPost("{id}/cancellation-request")]
        [HttpPut("{id}/cancel")]
        public async Task<IActionResult> RequestCancellation(int id,
            [FromBody(EmptyBodyBehavior = Microsoft.AspNetCore.Mvc.ModelBinding.EmptyBodyBehavior.Allow)]
            CancelContractApiRequest? request)
        {
            try
            {
                var contract = await ContractLifecycle.RequestCancellationAsync(_context, User.UserId(), id,
                    request?.Reason, HttpContext.RequestAborted);
                if (contract == null)
                    return NotFound(new { message = "Không tìm thấy hợp đồng của bạn." });

                return Ok(new
                {
                    success = true,
                    message = "Đã gửi yêu cầu hủy. Vui lòng chờ duyệt.",
                    status = ContractLifecycle.Label(contract),
                    statusCode = contract.TrangThai,
                    cancellationRequested = true,
                    cancellationReason = contract.LyDoHuy,
                    cancellationRequestedAt = contract.NgayYeuCauHuy
                });
            }
            catch (RentalBookingException error)
            {
                return StatusCode(error.StatusCode, new { message = error.Message });
            }
        }

        // POST: api/contracts/{id}/renew
        [Authorize(Roles = "KhachHang")]
        [HttpPost("{id}/renew")]
        public async Task<IActionResult> RenewContract(int id, [FromBody] RenewContractApiRequest request)
        {
            int customerId = User.UserId();
            var hopDong = await _context.HopDongs.FirstOrDefaultAsync(h =>
                h.MaHopDong == id && h.MaKhachHang == customerId);
            if (hopDong == null)
            {
                return NotFound(new { message = $"Không tìm thấy hợp đồng #{id}" });
            }

            string renewalNote = $"[Yêu cầu gia hạn {DateTime.Now:dd/MM/yyyy HH:mm}]: Thời gian '{request?.Duration}', ghi chú: '{request?.Notes}'";
            hopDong.GhiChu = string.IsNullOrEmpty(hopDong.GhiChu) ? renewalNote : $"{hopDong.GhiChu}\n{renewalNote}";

            await _context.SaveChangesAsync();
            return Ok(new
            {
                success = true,
                message = "Yêu cầu gia hạn hợp đồng đã được gửi thành công (Chờ xử lý).",
                contractId = id.ToString()
            });
        }
    }

    public class CreateContractApiRequest
    {
        public string? DeviceId { get; set; }
        public int? MaSanPham { get; set; }
        public int? ProductId { get; set; }
        public int Quantity { get; set; } = 1;
        public DateTime? StartDate { get; set; }
        public DateTime? EndDate { get; set; }
        public string? DeliveryAddress { get; set; }
        public string? Note { get; set; }
        public string? PromoCode { get; set; }
        public decimal? ExpectedTotal { get; set; }
        public List<ContractItemRequest?>? Items { get; set; }

        internal RentalOrder ToRentalOrder()
        {
            var lines = Items is { Count: > 0 }
                ? Items.Select(item => new RentalLine(
                    ResolveProduct(item?.ProductId ?? item?.MaSanPham, item?.DeviceId), item?.Quantity ?? 0)).ToArray()
                : new[] { new RentalLine(ResolveProduct(ProductId ?? MaSanPham, DeviceId), Quantity) };
            return new RentalOrder(StartDate, EndDate, DeliveryAddress, Note, PromoCode, lines, ExpectedTotal);
        }

        private static int ResolveProduct(int? productId, string? legacyDeviceId) =>
            productId ?? (int.TryParse(legacyDeviceId, out int parsed) ? parsed : 0);
    }

    public class ContractItemRequest
    {
        public int? ProductId { get; set; }
        public int? MaSanPham { get; set; }
        public string? DeviceId { get; set; }
        public int Quantity { get; set; } = 1;
    }

    public class CancelContractApiRequest
    {
        public string? Reason { get; set; }
    }

    public class RenewContractApiRequest
    {
        [JsonPropertyName("duration")]
        public string? Duration { get; set; }

        [JsonPropertyName("notes")]
        public string? Notes { get; set; }

        [JsonPropertyName("customerId")]
        public string? CustomerId { get; set; }
    }
}
