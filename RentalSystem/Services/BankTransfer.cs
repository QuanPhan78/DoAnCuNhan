using System.Globalization;

namespace RentalSystem.Services;

public sealed record BankTransfer(string BankCode, string BankName, string AccountNumber, string AccountName)
{
    // Existing installation defaults are retained; deployments can override each value in configuration.
    public static BankTransfer From(IConfiguration config) => new(
        config["BankTransfer:BankCode"] ?? "MB",
        config["BankTransfer:BankName"] ?? "MBBank",
        config["BankTransfer:AccountNumber"] ?? "0783406516",
        config["BankTransfer:AccountName"] ?? "PHAN MINH QUAN");

    public string QrUrl(decimal amount, string reference) =>
        $"https://img.vietqr.io/image/{Uri.EscapeDataString(BankCode)}-{Uri.EscapeDataString(AccountNumber)}-compact.png" +
        $"?amount={decimal.Ceiling(amount).ToString(CultureInfo.InvariantCulture)}&addInfo={Uri.EscapeDataString(reference)}&accountName={Uri.EscapeDataString(AccountName)}";
}
