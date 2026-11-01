using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;
using System.Text.Json.Serialization;

namespace RentalSystem.Controllers
{
    [Route("api/contracts")]
    [ApiController]
    public class ApiContractsController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public ApiContractsController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: api/contracts
        // Supports filtering by customerId/userId and role
        [HttpGet]
        public async Task<IActionResult> GetContracts([FromQuery] string? customerId, [FromQuery] string? userId, [FromQuery] string? role, [FromQuery] string? status)
        {
            IQueryable<HopDong> query = _context.HopDongs
                .Include(h => h.KhachHang)
                .Include(h => h.NhanVien);

            string? targetUserId = !string.IsNullOrEmpty(customerId) ? customerId : userId;

            // If user is a customer, only return their contracts
            if (!string.IsNullOrEmpty(targetUserId) && int.TryParse(targetUserId, out int parsedUserId))
            {
                if (string.Equals(role, "Admin", StringComparison.OrdinalIgnoreCase) || 
                    string.Equals(role, "KinhDoanh", StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(role, "Staff", StringComparison.OrdinalIgnoreCase))
                {
                    // Admin / Staff can see all contracts, or filtered if specified
                }
                else
                {
                    query = query.Where(h => h.MaKhachHang == parsedUserId);
                }
            }

            var hopDongs = await query.OrderByDescending(h => h.MaHopDong).ToListAsync();

            // Load ChiTietHopDongs and KyHanThanhToans
            var chiTiets = await _context.ChiTietHopDongs
                .Include(c => c.ThietBi)
                .ThenInclude(t => t.SanPham)
                .ToListAsync();

            var kyHans = await _context.KyHanThanhToans
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

                string statusText = h.TrangThai switch
                {
                    0 => "Chờ duyệt",
                    1 => "Đang hiệu lực",
                    2 => "Hoàn thành",
                    3 => "Đã hủy",
                    _ => "Chờ duyệt"
                };

                string paymentStatusText = h.TrangThaiThanhToan switch
                {
                    0 => "Chưa thanh toán",
                    1 => "Còn nợ",
                    2 => "Đã thanh toán đủ",
                    _ => "Chưa thanh toán"
                };

                return new
                {
                    id = h.MaHopDong.ToString(),
                    contractCode = $"HD-{h.MaHopDong:D4}",
                    customerId = h.MaKhachHang.ToString(),
                    customerName = h.KhachHang?.HoTen ?? "Khách hàng",
                    customerPhone = h.KhachHang?.SoDienThoai ?? "",
                    deviceIds = deviceNames,
                    rentalStart = h.NgayBatDau.ToString("dd/MM/yyyy"),
                    rentalEnd = h.NgayKetThuc.ToString("dd/MM/yyyy"),
                    rentalType = "Theo ngày",
                    status = statusText,
                    statusCode = h.TrangThai,
                    totalAmount = (double)h.TongTien,
                    depositAmount = (double)h.TienDaCoc,
                    paymentStatus = paymentStatusText,
                    paymentStatusCode = h.TrangThaiThanhToan,
                    note = h.GhiChu ?? "",
                    installationDetails = "Bàn giao tại quầy hoặc địa chỉ khách hàng",
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
            var h = await _context.HopDongs
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

            string statusText = h.TrangThai switch
            {
                0 => "Chờ duyệt",
                1 => "Đang hiệu lực",
                2 => "Hoàn thành",
                3 => "Đã hủy",
                _ => "Chờ duyệt"
            };

            string paymentStatusText = h.TrangThaiThanhToan switch
            {
                0 => "Chưa thanh toán",
                1 => "Còn nợ",
                2 => "Đã thanh toán đủ",
                _ => "Chưa thanh toán"
            };

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
                deviceIds = deviceNames,
                rentalStart = h.NgayBatDau.ToString("dd/MM/yyyy"),
                rentalEnd = h.NgayKetThuc.ToString("dd/MM/yyyy"),
                rentalType = "Theo ngày",
                status = statusText,
                statusCode = h.TrangThai,
                totalAmount = (double)h.TongTien,
                depositAmount = (double)h.TienDaCoc,
                paymentStatus = paymentStatusText,
                paymentStatusCode = h.TrangThaiThanhToan,
                note = h.GhiChu ?? "",
                installationDetails = "Bàn giao tại quầy hoặc địa chỉ khách hàng",
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
        // Endpoint tạo hợp đồng thật trong SQL Server (HopDongs, ChiTietHopDongs, KyHanThanhToans)
        [HttpPost]
        public async Task<IActionResult> CreateContract([FromBody] CreateContractApiRequest request)
        {
            if (request == null)
            {
                return BadRequest(new { message = "Dữ liệu hợp đồng không hợp lệ." });
            }

            // 1. Xác định Khách hàng
            int customerId = 0;
            if (!string.IsNullOrEmpty(request.CustomerId) && int.TryParse(request.CustomerId, out int cid))
            {
                customerId = cid;
            }
            else if (request.MaKhachHang.HasValue && request.MaKhachHang.Value > 0)
            {
                customerId = request.MaKhachHang.Value;
            }

            NguoiDung? khachHang = null;
            if (customerId > 0)
            {
                khachHang = await _context.NguoiDungs.FindAsync(customerId);
            }

            if (khachHang == null && !string.IsNullOrEmpty(request.CustomerPhone))
            {
                khachHang = await _context.NguoiDungs.FirstOrDefaultAsync(u => u.SoDienThoai == request.CustomerPhone);
            }

            if (khachHang == null && !string.IsNullOrEmpty(request.CustomerEmail))
            {
                khachHang = await _context.NguoiDungs.FirstOrDefaultAsync(u => u.Email == request.CustomerEmail);
            }

            // Nếu vẫn chưa tìm thấy khách hàng, tìm khách hàng mẫu đầu tiên hoặc tạo mới
            if (khachHang == null)
            {
                var roleKhachHang = await _context.VaiTros.FirstOrDefaultAsync(v => v.TenVaiTro == "KhachHang");
                khachHang = await _context.NguoiDungs.FirstOrDefaultAsync(u => u.MaVaiTro == (roleKhachHang != null ? roleKhachHang.MaVaiTro : 4));

                if (khachHang == null)
                {
                    khachHang = new NguoiDung
                    {
                        HoTen = !string.IsNullOrEmpty(request.CustomerName) ? request.CustomerName : "Khách Hàng Mới",
                        SoDienThoai = !string.IsNullOrEmpty(request.CustomerPhone) ? request.CustomerPhone : "0900000000",
                        Email = !string.IsNullOrEmpty(request.CustomerEmail) ? request.CustomerEmail : "khachhang@rentalsystem.com",
                        DiaChi = request.DeliveryAddress ?? "",
                        MatKhau = "123456",
                        MaVaiTro = roleKhachHang?.MaVaiTro ?? 4,
                        TrangThai = true,
                        CCCD = ""
                    };
                    _context.NguoiDungs.Add(khachHang);
                    await _context.SaveChangesAsync();
                }
            }

            // 2. Xác định Nhân viên phụ trách (Default admin hoặc nhân viên kinh doanh)
            var staff = await _context.NguoiDungs
                .FirstOrDefaultAsync(u => u.VaiTro.TenVaiTro == "KinhDoanh" || u.VaiTro.TenVaiTro == "Admin");
            int staffId = staff?.MaNguoiDung ?? 1;

            // 3. Thời gian thuê
            DateTime startDate = request.StartDate ?? DateTime.Now;
            DateTime endDate = request.EndDate ?? startDate.AddDays(1);
            if (endDate <= startDate)
            {
                endDate = startDate.AddDays(1);
            }

            var days = (endDate.Date - startDate.Date).TotalDays;
            if (days <= 0) days = 1;

            // 4. Xác định Sản phẩm và Thiết bị vật lý (ThietBis)
            // Lấy danh sách item từ request
            var items = request.Items ?? new List<ContractItemRequest>();
            if (!items.Any())
            {
                // Fallback nếu truyền trực tiếp qua top-level fields
                int spId = 0;
                if (!string.IsNullOrEmpty(request.DeviceId) && int.TryParse(request.DeviceId, out int did))
                {
                    spId = did;
                }
                else if (request.MaSanPham.HasValue)
                {
                    spId = request.MaSanPham.Value;
                }

                if (spId > 0)
                {
                    items.Add(new ContractItemRequest
                    {
                        DeviceId = spId.ToString(),
                        MaSanPham = spId,
                        Quantity = request.Quantity > 0 ? request.Quantity : 1,
                        RentalPrice = request.RentalPrice
                    });
                }
            }

            if (!items.Any())
            {
                // Nếu không có sản phẩm nào được chỉ định, lấy sản phẩm đầu tiên
                var firstSp = await _context.SanPhams.FirstOrDefaultAsync();
                if (firstSp != null)
                {
                    items.Add(new ContractItemRequest
                    {
                        DeviceId = firstSp.MaSanPham.ToString(),
                        MaSanPham = firstSp.MaSanPham,
                        Quantity = 1,
                        RentalPrice = firstSp.GiaThueNgay
                    });
                }
            }

            // Tính tổng tiền
            decimal totalMoney = 0;
            var allocatedDevices = new List<(ThietBi Device, decimal Price)>();

            foreach (var item in items)
            {
                int spId = item.MaSanPham ?? (int.TryParse(item.DeviceId, out int parsedSpId) ? parsedSpId : 1);
                var sanPham = await _context.SanPhams.FindAsync(spId);
                if (sanPham == null)
                {
                    sanPham = await _context.SanPhams.FirstOrDefaultAsync();
                    if (sanPham == null) continue;
                    spId = sanPham.MaSanPham;
                }

                int qty = item.Quantity > 0 ? item.Quantity : 1;
                decimal unitPricePerDay = item.RentalPrice ?? sanPham.GiaThueNgay;
                decimal itemTotal = unitPricePerDay * (decimal)days * qty;

                // Nếu có estimatedAmount từ app truyền lên cho toàn đơn và chỉ có 1 item, ưu tiên dùng
                if (request.EstimatedAmount.HasValue && request.EstimatedAmount.Value > 0 && items.Count == 1)
                {
                    itemTotal = request.EstimatedAmount.Value;
                }

                // Tìm các thiết bị vật lý trong kho cho sản phẩm này
                var freeDevices = await _context.ThietBis
                    .Where(t => t.MaSanPham == spId && t.TrangThai == 0)
                    .Take(qty)
                    .ToListAsync();

                // Nếu không đủ thiết bị sẵn sàng trong kho, lấy các thiết bị bất kỳ của sản phẩm hoặc tạo mới
                if (freeDevices.Count < qty)
                {
                    var extraDevices = await _context.ThietBis
                        .Where(t => t.MaSanPham == spId && !freeDevices.Select(f => f.MaThietBi).Contains(t.MaThietBi))
                        .Take(qty - freeDevices.Count)
                        .ToListAsync();
                    freeDevices.AddRange(extraDevices);
                }

                // Nếu vẫn không có thiết bị vật lý nào trong bảng ThietBis cho sản phẩm này, tạo tự động 1 đơn vị
                while (freeDevices.Count < qty)
                {
                    var newTb = new ThietBi
                    {
                        MaSanPham = spId,
                        SoSerial = $"DEV-{spId}-{Guid.NewGuid().ToString().Substring(0, 8).ToUpper()}",
                        TinhTrangMay = "Mới 99%",
                        TrangThai = 0
                    };
                    _context.ThietBis.Add(newTb);
                    await _context.SaveChangesAsync();
                    freeDevices.Add(newTb);
                }

                decimal pricePerUnit = itemTotal / qty;
                foreach (var dev in freeDevices.Take(qty))
                {
                    allocatedDevices.Add((dev, pricePerUnit));
                }

                totalMoney += itemTotal;
            }

            if (request.EstimatedAmount.HasValue && request.EstimatedAmount.Value > 0)
            {
                totalMoney = request.EstimatedAmount.Value;
            }

            decimal deposit = request.DepositAmount ?? 0;
            int installmentCount = request.InstallmentCount ?? (request.SoKyHan.HasValue && request.SoKyHan.Value > 0 ? request.SoKyHan.Value : 1);

            // 5. Tạo Hợp Đồng (HopDongs) trong SQL Server
            string noteText = "";
            if (!string.IsNullOrEmpty(request.DeliveryAddress))
            {
                noteText += $"Địa chỉ giao: {request.DeliveryAddress}. ";
            }
            if (!string.IsNullOrEmpty(request.Note))
            {
                noteText += request.Note;
            }

            var hopDong = new HopDong
            {
                MaKhachHang = khachHang.MaNguoiDung,
                MaNhanVien = staffId,
                NgayBatDau = startDate,
                NgayKetThuc = endDate,
                TongTien = totalMoney,
                TienDaCoc = deposit,
                TrangThai = 0, // 0 = Chờ duyệt (Khách bấm "Thuê ngay" trên app)
                SoKyHan = installmentCount,
                TrangThaiThanhToan = 0, // 0 = Chưa thanh toán
                GhiChu = noteText.Trim(),
                AnhCMND = "",
                ChuKyKhachHang = "",
                ChuKyNhanVien = "",
                NgayKy = DateTime.Now
            };

            _context.HopDongs.Add(hopDong);
            await _context.SaveChangesAsync(); // Sinh MaHopDong tự tăng

            // 6. Tạo Chi Tiết Hợp Đồng (ChiTietHopDongs) và cập nhật Trạng Thái Thiết Bị
            foreach (var item in allocatedDevices)
            {
                var chiTiet = new ChiTietHopDong
                {
                    MaHopDong = hopDong.MaHopDong,
                    MaThietBi = item.Device.MaThietBi,
                    GiaChotThu = item.Price
                };
                _context.ChiTietHopDongs.Add(chiTiet);

                // Khóa máy: chuyển sang 3 (Giữ chỗ / Chờ duyệt)
                item.Device.TrangThai = 3;
            }

            // 7. Tạo Kỳ Hạn Thanh Toán (KyHanThanhToans)
            int soKy = hopDong.SoKyHan > 0 ? hopDong.SoKyHan : 1;
            decimal tienConLai = hopDong.TongTien - hopDong.TienDaCoc;
            if (tienConLai < 0) tienConLai = 0;
            decimal tienMoiKy = soKy > 0 ? Math.Round(tienConLai / soKy, 0) : tienConLai;
            double daysPerKy = days / soKy;

            for (int i = 1; i <= soKy; i++)
            {
                var kyHan = new KyHanThanhToan
                {
                    MaHopDong = hopDong.MaHopDong,
                    SoKyHan = i,
                    NgayDenHan = hopDong.NgayBatDau.AddDays(Math.Max(1, Math.Round(i * daysPerKy))),
                    SoTienPhai = (i == soKy) ? (tienConLai - (tienMoiKy * (soKy - 1))) : tienMoiKy,
                    SoTienDaTra = 0,
                    TrangThai = 0, // Chưa thanh toán
                    GhiChu = $"Kỳ hạn {i}/{soKy}"
                };
                _context.KyHanThanhToans.Add(kyHan);
            }

            await _context.SaveChangesAsync();

            return Ok(new
            {
                success = true,
                message = "Tạo hợp đồng thuê thiết bị thành công trong SQL Server!",
                contractId = hopDong.MaHopDong.ToString(),
                contractCode = $"HD-{hopDong.MaHopDong:D4}",
                customerId = hopDong.MaKhachHang.ToString(),
                customerName = khachHang.HoTen,
                totalAmount = (double)hopDong.TongTien,
                depositAmount = (double)hopDong.TienDaCoc,
                installmentsCount = hopDong.SoKyHan,
                status = "Chờ duyệt",
                statusCode = hopDong.TrangThai,
                deviceCount = allocatedDevices.Count
            });
        }

        // PUT: api/contracts/{id}/cancel
        [HttpPut("{id}/cancel")]
        public async Task<IActionResult> CancelContract(int id)
        {
            var hopDong = await _context.HopDongs.FindAsync(id);
            if (hopDong == null)
            {
                return NotFound(new { message = $"Không tìm thấy hợp đồng #{id}" });
            }

            if (hopDong.TrangThai == 1)
            {
                return BadRequest(new { message = "Hợp đồng đang có hiệu lực không thể hủy trực tiếp." });
            }

            hopDong.TrangThai = 3; // 3: Đã hủy

            // Giải phóng thiết bị về kho (0: Sẵn sàng)
            var chiTiets = await _context.ChiTietHopDongs.Where(c => c.MaHopDong == id).ToListAsync();
            foreach (var ct in chiTiets)
            {
                var tb = await _context.ThietBis.FindAsync(ct.MaThietBi);
                if (tb != null && tb.TrangThai == 3)
                {
                    tb.TrangThai = 0;
                }
            }

            await _context.SaveChangesAsync();
            return Ok(new { success = true, message = "Đã hủy hợp đồng thành công." });
        }

        // POST: api/contracts/{id}/renew
        [HttpPost("{id}/renew")]
        public async Task<IActionResult> RenewContract(int id, [FromBody] RenewContractApiRequest request)
        {
            var hopDong = await _context.HopDongs.FindAsync(id);
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
        [JsonPropertyName("customerId")]
        public string? CustomerId { get; set; }

        [JsonPropertyName("maKhachHang")]
        public int? MaKhachHang { get; set; }

        [JsonPropertyName("customerName")]
        public string? CustomerName { get; set; }

        [JsonPropertyName("customerPhone")]
        public string? CustomerPhone { get; set; }

        [JsonPropertyName("customerEmail")]
        public string? CustomerEmail { get; set; }

        [JsonPropertyName("deviceId")]
        public string? DeviceId { get; set; }

        [JsonPropertyName("maSanPham")]
        public int? MaSanPham { get; set; }

        [JsonPropertyName("quantity")]
        public int Quantity { get; set; } = 1;

        [JsonPropertyName("rentalType")]
        public string? RentalType { get; set; }

        [JsonPropertyName("startDate")]
        public DateTime? StartDate { get; set; }

        [JsonPropertyName("endDate")]
        public DateTime? EndDate { get; set; }

        [JsonPropertyName("depositAmount")]
        public decimal? DepositAmount { get; set; }

        [JsonPropertyName("estimatedAmount")]
        public decimal? EstimatedAmount { get; set; }

        [JsonPropertyName("rentalPrice")]
        public decimal? RentalPrice { get; set; }

        [JsonPropertyName("installmentCount")]
        public int? InstallmentCount { get; set; }

        [JsonPropertyName("soKyHan")]
        public int? SoKyHan { get; set; }

        [JsonPropertyName("deliveryAddress")]
        public string? DeliveryAddress { get; set; }

        [JsonPropertyName("note")]
        public string? Note { get; set; }

        [JsonPropertyName("items")]
        public List<ContractItemRequest>? Items { get; set; }
    }

    public class ContractItemRequest
    {
        [JsonPropertyName("deviceId")]
        public string? DeviceId { get; set; }

        [JsonPropertyName("maSanPham")]
        public int? MaSanPham { get; set; }

        [JsonPropertyName("deviceName")]
        public string? DeviceName { get; set; }

        [JsonPropertyName("quantity")]
        public int Quantity { get; set; } = 1;

        [JsonPropertyName("rentalPrice")]
        public decimal? RentalPrice { get; set; }

        [JsonPropertyName("subtotal")]
        public decimal? Subtotal { get; set; }
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
