using Microsoft.EntityFrameworkCore;
using RentalSystem.Models;

namespace RentalSystem.Services;

internal sealed record RevenuePeriod(string Key, DateTime? Start, DateTime? End)
{
    internal static RevenuePeriod Resolve(string? filter, DateTime today)
    {
        today = today.Date;
        var monday = today.AddDays(-((int)today.DayOfWeek + 6) % 7);
        var month = new DateTime(today.Year, today.Month, 1);
        var year = new DateTime(today.Year, 1, 1);
        return filter?.Trim().ToLowerInvariant() switch
        {
            "week" or "tuần này" or "tuannay" => new("week", monday, monday.AddDays(7)),
            "month" or "tháng này" or "thangnay" => new("month", month, month.AddMonths(1)),
            "year" or "năm nay" or "namnay" => new("year", year, year.AddYears(1)),
            _ => new("all", null, null)
        };
    }
}

internal sealed record RevenuePoint(string Label, decimal Value);
internal sealed record RevenueReport(decimal Total, IReadOnlyList<RevenuePoint> Chart)
{
    internal static async Task<RevenueReport> LoadAsync(ApplicationDbContext db, RevenuePeriod period, DateTime today)
    {
        var month = new DateTime(today.Year, today.Month, 1);
        var start = period.Start ?? month.AddMonths(-5);
        var end = period.End ?? month.AddMonths(1);
        var completed = db.HopDongs.Where(h => h.TrangThai == 2);
        var dailyTotals = await completed.Where(h => h.NgayBatDau >= start && h.NgayBatDau < end)
            .GroupBy(h => h.NgayBatDau.Date)
            .Select(group => new { Date = group.Key, Total = group.Sum(h => h.TongTien) })
            .ToListAsync();
        var chart = new List<RevenuePoint>();
        for (var from = start; from < end;)
        {
            var until = period.Key switch
            {
                "week" => from.AddDays(1),
                "month" => from.AddDays(7),
                _ => from.AddMonths(1)
            };
            if (until > end) until = end;
            var label = period.Key switch
            {
                "week" => from.ToString("dd/MM"),
                "month" => $"{from:dd}–{until.AddDays(-1):dd}",
                _ => from.ToString("MM/yy")
            };
            chart.Add(new(label, dailyTotals.Where(d => d.Date >= from && d.Date < until).Sum(d => d.Total)));
            from = until;
        }
        var total = period.Key == "all"
            ? await completed.SumAsync(h => (decimal?)h.TongTien) ?? 0
            : dailyTotals.Sum(day => day.Total);
        return new(total, chart);
    }
}
