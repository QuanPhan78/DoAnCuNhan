using System;
using System.Collections.Generic;
using System.Globalization;
using System.Net;
using System.Security.Cryptography;
using System.Text;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using RentalSystem.Models;

namespace RentalSystem.Services
{
    public class VnPayService : IVnPayService
    {
        private readonly IConfiguration _configuration;

        public VnPayService(IConfiguration configuration)
        {
            _configuration = configuration;
        }

        public string CreatePaymentUrl(HttpContext context, VnPaymentRequestModel request)
        {
            var tmnCode = _configuration["Vnpay:TmnCode"] ?? string.Empty;
            var hashSecret = _configuration["Vnpay:HashSecret"] ?? string.Empty;
            var baseUrl = _configuration["Vnpay:BaseUrl"] ?? "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html";
            var returnUrl = _configuration["Vnpay:ReturnUrl"] ?? string.Empty;
            var version = _configuration["Vnpay:Version"] ?? "2.1.0";
            var command = _configuration["Vnpay:Command"] ?? "pay";
            var currCode = _configuration["Vnpay:CurrCode"] ?? "VND";
            var locale = _configuration["Vnpay:Locale"] ?? "vn";

            long vnpAmount = (long)(request.Amount * 100);

            string ipAddress = context.Connection.RemoteIpAddress?.ToString() ?? "127.0.0.1";
            if (ipAddress == "::1")
            {
                ipAddress = "127.0.0.1";
            }

            var payParams = new SortedList<string, string>(new VnPayCompare());
            payParams.Add("vnp_Version", version);
            payParams.Add("vnp_Command", command);
            payParams.Add("vnp_TmnCode", tmnCode);
            payParams.Add("vnp_Amount", vnpAmount.ToString());
            payParams.Add("vnp_CreateDate", request.CreatedDate.ToString("yyyyMMddHHmmss"));
            payParams.Add("vnp_CurrCode", currCode);
            payParams.Add("vnp_IpAddr", ipAddress);
            payParams.Add("vnp_Locale", locale);
            payParams.Add("vnp_OrderInfo", string.IsNullOrWhiteSpace(request.Description) ? $"Thanh toan hop dong {request.ContractId}" : request.Description);
            payParams.Add("vnp_OrderType", "other");
            payParams.Add("vnp_ReturnUrl", returnUrl);
            payParams.Add("vnp_TxnRef", $"{request.ContractId}_{request.InstallmentId ?? 0}_{DateTime.Now.Ticks}");

            var hashData = new StringBuilder();
            var query = new StringBuilder();

            foreach (var kv in payParams)
            {
                if (!string.IsNullOrEmpty(kv.Value))
                {
                    string encodedKey = WebUtility.UrlEncode(kv.Key);
                    string encodedValue = WebUtility.UrlEncode(kv.Value);
                    hashData.Append(encodedKey).Append('=').Append(encodedValue).Append('&');
                    query.Append(encodedKey).Append('=').Append(encodedValue).Append('&');
                }
            }

            if (hashData.Length > 0)
            {
                hashData.Remove(hashData.Length - 1, 1);
            }

            string rawHash = hashData.ToString();
            string secureHash = HmacSha512(hashSecret, rawHash);
            query.Append("vnp_SecureHash=").Append(secureHash);

            return $"{baseUrl}?{query}";
        }

        public VnPaymentResponseModel PaymentExecute(IQueryCollection collections)
        {
            var hashSecret = _configuration["Vnpay:HashSecret"] ?? string.Empty;

            var payParams = new SortedList<string, string>(new VnPayCompare());
            string vnpSecureHash = string.Empty;

            foreach (var key in collections.Keys)
            {
                if (!string.IsNullOrEmpty(key) && key.StartsWith("vnp_"))
                {
                    string val = collections[key].ToString();
                    if (key == "vnp_SecureHash")
                    {
                        vnpSecureHash = val;
                    }
                    else if (key != "vnp_SecureHashType")
                    {
                        if (!string.IsNullOrEmpty(val))
                        {
                            payParams.Add(key, val);
                        }
                    }
                }
            }

            var hashData = new StringBuilder();
            foreach (var kv in payParams)
            {
                string encodedKey = WebUtility.UrlEncode(kv.Key);
                string encodedValue = WebUtility.UrlEncode(kv.Value);
                hashData.Append(encodedKey).Append('=').Append(encodedValue).Append('&');
            }

            if (hashData.Length > 0)
            {
                hashData.Remove(hashData.Length - 1, 1);
            }

            string rawHash = hashData.ToString();
            string checkSignature = HmacSha512(hashSecret, rawHash);
            bool isValidSignature = checkSignature.Equals(vnpSecureHash, StringComparison.InvariantCultureIgnoreCase);

            string vnpResponseCode = collections["vnp_ResponseCode"].ToString();
            string vnpTransactionNo = collections["vnp_TransactionNo"].ToString();
            string vnpTxnRef = collections["vnp_TxnRef"].ToString();
            string vnpOrderInfo = collections["vnp_OrderInfo"].ToString();
            string vnpBankCode = collections["vnp_BankCode"].ToString();
            string vnpAmountStr = collections["vnp_Amount"].ToString();

            decimal amount = 0;
            if (long.TryParse(vnpAmountStr, out long parsedAmount))
            {
                amount = parsedAmount / 100m;
            }

            int contractId = 0;
            int? installmentId = null;
            if (!string.IsNullOrEmpty(vnpTxnRef))
            {
                var parts = vnpTxnRef.Split('_');
                if (parts.Length >= 1 && int.TryParse(parts[0], out int cid))
                {
                    contractId = cid;
                }
                if (parts.Length >= 2 && int.TryParse(parts[1], out int iid) && iid > 0)
                {
                    installmentId = iid;
                }
            }

            return new VnPaymentResponseModel
            {
                IsValidSignature = isValidSignature,
                Success = isValidSignature && vnpResponseCode == "00",
                PaymentMethod = "VnPay",
                OrderDescription = vnpOrderInfo,
                OrderId = vnpTxnRef,
                TransactionId = vnpTransactionNo,
                Token = vnpSecureHash,
                VnPayResponseCode = vnpResponseCode,
                BankCode = vnpBankCode,
                Amount = amount,
                ContractId = contractId,
                InstallmentId = installmentId
            };
        }

        public static string HmacSha512(string key, string inputData)
        {
            var hash = new StringBuilder();
            byte[] keyBytes = Encoding.UTF8.GetBytes(key);
            byte[] inputBytes = Encoding.UTF8.GetBytes(inputData);
            using (var hmac = new HMACSHA512(keyBytes))
            {
                byte[] hashValue = hmac.ComputeHash(inputBytes);
                foreach (var b in hashValue)
                {
                    hash.Append(b.ToString("x2"));
                }
            }
            return hash.ToString();
        }
    }

    public class VnPayCompare : IComparer<string>
    {
        public int Compare(string? x, string? y)
        {
            if (x == y) return 0;
            if (x == null) return -1;
            if (y == null) return 1;
            return string.Compare(x, y, StringComparison.Ordinal);
        }
    }
}
