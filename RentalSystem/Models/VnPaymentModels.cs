using System;

namespace RentalSystem.Models
{
    public class VnPaymentRequestModel
    {
        public int ContractId { get; set; }
        public int? InstallmentId { get; set; }
        public string FullName { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public decimal Amount { get; set; }
        public DateTime CreatedDate { get; set; } = DateTime.Now;
    }

    public class VnPaymentResponseModel
    {
        public bool Success { get; set; }
        public bool IsValidSignature { get; set; }
        public string PaymentMethod { get; set; } = "VnPay";
        public string OrderDescription { get; set; } = string.Empty;
        public string OrderId { get; set; } = string.Empty; // vnp_TxnRef
        public string PaymentId { get; set; } = string.Empty;
        public string TransactionId { get; set; } = string.Empty; // vnp_TransactionNo
        public string Token { get; set; } = string.Empty; // vnp_SecureHash
        public string VnPayResponseCode { get; set; } = string.Empty; // vnp_ResponseCode
        public string BankCode { get; set; } = string.Empty; // vnp_BankCode
        public decimal Amount { get; set; } // Quy đổi về VND chuẩn (vnp_Amount / 100)
        public int ContractId { get; set; }
        public int? InstallmentId { get; set; }
    }
}
