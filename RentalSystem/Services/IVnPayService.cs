using Microsoft.AspNetCore.Http;
using RentalSystem.Models;

namespace RentalSystem.Services
{
    public interface IVnPayService
    {
        string CreatePaymentUrl(HttpContext context, VnPaymentRequestModel request);
        VnPaymentResponseModel PaymentExecute(IQueryCollection collections);
    }
}
