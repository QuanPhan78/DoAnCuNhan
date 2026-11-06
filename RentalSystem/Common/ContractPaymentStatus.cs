namespace RentalSystem.Common;

public static class ContractPaymentStatus
{
    public const int Unpaid = 0;
    public const int DepositPaid = 1;
    public const int Outstanding = 2;
    public const int Settled = 3;

    public static string Label(int code) => code switch
    {
        Unpaid => "Chưa thanh toán",
        DepositPaid => "Đã đặt cọc",
        Outstanding => "Còn nợ",
        Settled => "Đã tất toán",
        _ => "Chưa xác định"
    };

    public static string BadgeTone(int code) => code switch
    {
        DepositPaid => "navy",
        Outstanding => "warning",
        Settled => "success",
        _ => "neutral"
    };
}
