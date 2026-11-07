using System;
using System.ComponentModel.DataAnnotations.Schema;
using System.Reflection;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using RentalSystem.Common;
using RentalSystem.Models;

namespace AliasChallenger
{
    internal class Program
    {
        private static int passed = 0;
        private static int failed = 0;

        private static void Assert(bool condition, string testName, string details = "")
        {
            if (condition)
            {
                passed++;
                Console.ForegroundColor = ConsoleColor.Green;
                Console.Write("[PASS] ");
                Console.ResetColor();
                Console.WriteLine(testName + (string.IsNullOrEmpty(details) ? "" : $" ({details})"));
            }
            else
            {
                failed++;
                Console.ForegroundColor = ConsoleColor.Red;
                Console.Write("[FAIL] ");
                Console.ResetColor();
                Console.WriteLine(testName + (string.IsNullOrEmpty(details) ? "" : $" -> {details}"));
            }
        }

        static int Main(string[] args)
        {
            Console.WriteLine("================================================================================");
            Console.WriteLine("EMPIRICAL CHALLENGER: ADVERSARIAL STRESS TEST HARNESS");
            Console.WriteLine("Target: KyHanThanhToan (PhiPhatTreHan => TienPhat) Entity Alias & Edge Cases");
            Console.WriteLine("================================================================================\n");

            TestGroup1_TwoWayPropertyMutation();
            TestGroup2_ReflectionVerification();
            TestGroup3_AttributesAndMapping();
            TestGroup4_EfCoreModelMetadata();
            TestGroup5_JsonSerializationDeserialization();
            TestGroup6_EdgeCasesAndBoundaryStress();
            TestGroup7_DebtCalculationHelperOracles();

            Console.WriteLine("\n================================================================================");
            Console.WriteLine($"CHALLENGER ADVERSARIAL TEST RESULTS: {passed} PASSED, {failed} FAILED");
            Console.WriteLine("================================================================================");

            return failed == 0 ? 0 : 1;
        }

        private static void TestGroup1_TwoWayPropertyMutation()
        {
            Console.WriteLine("--- [GROUP 1] Two-Way Property Mutation & Bidirectional Sync ---");

            // 1.1 Direct mutation of TienPhat updates PhiPhatTreHan
            var k1 = new KyHanThanhToan();
            k1.TienPhat = 500m;
            Assert(k1.PhiPhatTreHan == 500m, "G1.1: Setting TienPhat=500 updates PhiPhatTreHan to 500", $"PhiPhatTreHan={k1.PhiPhatTreHan}");

            // 1.2 Direct mutation of PhiPhatTreHan updates TienPhat
            k1.PhiPhatTreHan = 700m;
            Assert(k1.TienPhat == 700m, "G1.2: Setting PhiPhatTreHan=700 updates TienPhat to 700", $"TienPhat={k1.TienPhat}");

            // 1.3 Sequential alternating mutations
            k1.TienPhat = 150_000m;
            Assert(k1.PhiPhatTreHan == 150_000m, "G1.3a: Alternating step 1: TienPhat=150k -> PhiPhatTreHan=150k");
            k1.PhiPhatTreHan = 320_000m;
            Assert(k1.TienPhat == 320_000m, "G1.3b: Alternating step 2: PhiPhatTreHan=320k -> TienPhat=320k");
            k1.TienPhat = 0m;
            Assert(k1.PhiPhatTreHan == 0m, "G1.3c: Alternating step 3: TienPhat=0 -> PhiPhatTreHan=0");
            k1.PhiPhatTreHan = 999m;
            Assert(k1.TienPhat == 999m, "G1.3d: Alternating step 4: PhiPhatTreHan=999 -> TienPhat=999");

            // 1.4 Multi-instance isolation stress test (1,000 instances)
            bool isolationPassed = true;
            for (int i = 0; i < 1000; i++)
            {
                var a = new KyHanThanhToan { TienPhat = i * 10m };
                var b = new KyHanThanhToan { PhiPhatTreHan = i * 20m };
                if (a.PhiPhatTreHan != i * 10m || b.TienPhat != i * 20m)
                {
                    isolationPassed = false;
                    break;
                }
                a.PhiPhatTreHan += 5m;
                if (a.TienPhat != (i * 10m) + 5m || b.TienPhat != i * 20m)
                {
                    isolationPassed = false;
                    break;
                }
            }
            Assert(isolationPassed, "G1.4: 1,000 distinct instances maintain independent state without leakage");
        }

        private static void TestGroup2_ReflectionVerification()
        {
            Console.WriteLine("\n--- [GROUP 2] Reflection & Dynamic Inspection Oracles ---");

            Type type = typeof(KyHanThanhToan);

            // 2.1 Check property existences
            PropertyInfo? propPhiPhat = type.GetProperty("PhiPhatTreHan");
            PropertyInfo? propTienPhat = type.GetProperty("TienPhat");

            Assert(propPhiPhat != null, "G2.1: Property 'PhiPhatTreHan' discoverable via Reflection");
            Assert(propTienPhat != null, "G2.2: Property 'TienPhat' discoverable via Reflection");

            if (propPhiPhat != null && propTienPhat != null)
            {
                // 2.2 Property Types
                Assert(propPhiPhat.PropertyType == typeof(decimal), "G2.3: PhiPhatTreHan PropertyType is System.Decimal", propPhiPhat.PropertyType.FullName ?? "");
                Assert(propTienPhat.PropertyType == typeof(decimal), "G2.4: TienPhat PropertyType is System.Decimal", propTienPhat.PropertyType.FullName ?? "");

                // 2.3 Read/Write capabilities
                Assert(propPhiPhat.CanRead && propPhiPhat.CanWrite, "G2.5: PhiPhatTreHan supports both read and write");
                Assert(propTienPhat.CanRead && propTienPhat.CanWrite, "G2.6: TienPhat supports both read and write");

                // 2.4 Accessors visibility
                MethodInfo? getPhi = propPhiPhat.GetGetMethod();
                MethodInfo? setPhi = propPhiPhat.GetSetMethod();
                MethodInfo? getTien = propTienPhat.GetGetMethod();
                MethodInfo? setTien = propTienPhat.GetSetMethod();

                Assert(getPhi != null && getPhi.IsPublic, "G2.7: PhiPhatTreHan getter is public");
                Assert(setPhi != null && setPhi.IsPublic, "G2.8: PhiPhatTreHan setter is public");
                Assert(getTien != null && getTien.IsPublic, "G2.9: TienPhat getter is public");
                Assert(setTien != null && setTien.IsPublic, "G2.10: TienPhat setter is public");

                // 2.5 Reflection GetValue & SetValue Cross-Mutation
                var k = new KyHanThanhToan();
                propTienPhat.SetValue(k, 123456m);
                decimal valFromPhi = (decimal)propPhiPhat.GetValue(k)!;
                Assert(valFromPhi == 123456m, "G2.11: Reflection SetValue(TienPhat, 123456) readable via GetValue(PhiPhatTreHan)", $"Got {valFromPhi}");

                propPhiPhat.SetValue(k, 654321m);
                decimal valFromTien = (decimal)propTienPhat.GetValue(k)!;
                Assert(valFromTien == 654321m, "G2.12: Reflection SetValue(PhiPhatTreHan, 654321) readable via GetValue(TienPhat)", $"Got {valFromTien}");
            }
        }

        private static void TestGroup3_AttributesAndMapping()
        {
            Console.WriteLine("\n--- [GROUP 3] Data Annotations & Schema Attributes Verification ---");

            Type type = typeof(KyHanThanhToan);
            PropertyInfo propPhiPhat = type.GetProperty("PhiPhatTreHan")!;
            PropertyInfo propTienPhat = type.GetProperty("TienPhat")!;

            // 3.1 PhiPhatTreHan MUST have [NotMapped]
            var notMappedAttr = propPhiPhat.GetCustomAttribute<NotMappedAttribute>();
            Assert(notMappedAttr != null, "G3.1: PhiPhatTreHan is decorated with [NotMapped]");

            // 3.2 PhiPhatTreHan MUST NOT have [Column]
            var columnAttrOnPhi = propPhiPhat.GetCustomAttribute<ColumnAttribute>();
            Assert(columnAttrOnPhi == null, "G3.2: PhiPhatTreHan does NOT have [Column] attribute (prevents EF dual column mapping)");

            // 3.3 TienPhat MUST have [Column(TypeName = "decimal(18,2)")]
            var columnAttrOnTien = propTienPhat.GetCustomAttribute<ColumnAttribute>();
            Assert(columnAttrOnTien != null, "G3.3: TienPhat is decorated with [Column]");
            Assert(columnAttrOnTien?.TypeName == "decimal(18,2)", "G3.4: TienPhat Column TypeName is 'decimal(18,2)'", columnAttrOnTien?.TypeName ?? "");

            // 3.4 TienPhat MUST NOT have [NotMapped]
            var notMappedAttrOnTien = propTienPhat.GetCustomAttribute<NotMappedAttribute>();
            Assert(notMappedAttrOnTien == null, "G3.5: TienPhat does NOT have [NotMapped] attribute (physical persistent column)");
        }

        private static void TestGroup4_EfCoreModelMetadata()
        {
            Console.WriteLine("\n--- [GROUP 4] EF Core Model Metadata & Relational Schema Mapping ---");

            var options = new DbContextOptionsBuilder<ApplicationDbContext>()
                .UseSqlServer("Server=localhost;Database=Dummy;Trusted_Connection=True;TrustServerCertificate=True;")
                .Options;

            using var db = new ApplicationDbContext(options);
            var entityType = db.Model.FindEntityType(typeof(KyHanThanhToan));

            Assert(entityType != null, "G4.1: EF Core model contains KyHanThanhToan entity metadata");

            if (entityType != null)
            {
                // 4.2 Physical property TienPhat is tracked by EF Core
                var propTienPhat = entityType.FindProperty("TienPhat");
                Assert(propTienPhat != null, "G4.2: TienPhat is mapped in EF Core relational model properties");

                // 4.3 Unmapped property PhiPhatTreHan is completely excluded from EF Core relational model
                var propPhiPhat = entityType.FindProperty("PhiPhatTreHan");
                Assert(propPhiPhat == null, "G4.3: PhiPhatTreHan is NOT present in EF Core relational model properties (ignored due to [NotMapped])");

                // 4.4 Verify database column type annotation in model
                string? columnType = propTienPhat?.GetColumnType();
                Assert(columnType == "decimal(18,2)", "G4.4: EF Core property TienPhat column type resolved to 'decimal(18,2)'", columnType ?? "");
            }
        }

        private static void TestGroup5_JsonSerializationDeserialization()
        {
            Console.WriteLine("\n--- [GROUP 5] JSON Serialization & Deserialization Oracles ---");

            // 5.1 System.Text.Json Serialization
            var k = new KyHanThanhToan
            {
                MaKyHan = 10,
                MaHopDong = 2,
                SoTienPhai = 2_000_000m,
                TienPhat = 350_000m
            };

            string json = JsonSerializer.Serialize(k);
            Assert(json.Contains("\"TienPhat\":350000") || json.Contains("\"TienPhat\": 350000"), "G5.1: JSON serialization includes TienPhat", json);
            Assert(json.Contains("\"PhiPhatTreHan\":350000") || json.Contains("\"PhiPhatTreHan\": 350000"), "G5.2: JSON serialization includes PhiPhatTreHan alias", json);

            // 5.2 Deserialization with only 'TienPhat' in payload
            string jsonOnlyTienPhat = "{\"MaKyHan\":1,\"TienPhat\":450000}";
            var deser1 = JsonSerializer.Deserialize<KyHanThanhToan>(jsonOnlyTienPhat);
            Assert(deser1 != null && deser1.TienPhat == 450000m && deser1.PhiPhatTreHan == 450000m,
                "G5.3: Deserializing payload with only 'TienPhat' populates both TienPhat and PhiPhatTreHan",
                $"TienPhat={deser1?.TienPhat}, PhiPhatTreHan={deser1?.PhiPhatTreHan}");

            // 5.3 Deserialization with legacy payload containing only 'PhiPhatTreHan'
            string jsonOnlyPhiPhat = "{\"MaKyHan\":2,\"PhiPhatTreHan\":850000}";
            var deser2 = JsonSerializer.Deserialize<KyHanThanhToan>(jsonOnlyPhiPhat);
            Assert(deser2 != null && deser2.PhiPhatTreHan == 850000m && deser2.TienPhat == 850000m,
                "G5.4: Deserializing legacy payload with only 'PhiPhatTreHan' populates physical TienPhat",
                $"TienPhat={deser2?.TienPhat}, PhiPhatTreHan={deser2?.PhiPhatTreHan}");

            // 5.4 Deserialization order stress: payload containing both keys
            // Case A: TienPhat first, PhiPhatTreHan second (last-in wins)
            string jsonBothA = "{\"TienPhat\":100000,\"PhiPhatTreHan\":200000}";
            var deserA = JsonSerializer.Deserialize<KyHanThanhToan>(jsonBothA);
            Assert(deserA != null && deserA.TienPhat == deserA.PhiPhatTreHan,
                "G5.5a: Deserializing payload with both properties produces synchronized value (last property wins)",
                $"Final synchronized value: {deserA?.TienPhat}");

            // Case B: PhiPhatTreHan first, TienPhat second
            string jsonBothB = "{\"PhiPhatTreHan\":200000,\"TienPhat\":100000}";
            var deserB = JsonSerializer.Deserialize<KyHanThanhToan>(jsonBothB);
            Assert(deserB != null && deserB.TienPhat == 100000m && deserB.PhiPhatTreHan == 100000m,
                "G5.5b: Deserializing payload with PhiPhatTreHan then TienPhat correctly adopts TienPhat=100000",
                $"TienPhat={deserB?.TienPhat}");
        }

        private static void TestGroup6_EdgeCasesAndBoundaryStress()
        {
            Console.WriteLine("\n--- [GROUP 6] Financial Edge Cases & Stress Scenarios ---");

            // 6.1 Default initialization value
            var kDefault = new KyHanThanhToan();
            Assert(kDefault.TienPhat == 0m && kDefault.PhiPhatTreHan == 0m,
                "G6.1: Default initialized KyHanThanhToan has TienPhat == 0 and PhiPhatTreHan == 0");

            // 6.2 Zero penalty calculation
            var kZero = new KyHanThanhToan { SoTienPhai = 5_000_000m, SoTienDaTra = 3_000_000m, TienPhat = 0m };
            decimal balanceZero = DebtCalculationHelper.GetInstallmentBalance(kZero);
            Assert(balanceZero == 2_000_000m, "G6.2: Zero penalty balance calculation: 5M - 3M + 0 = 2M", $"Balance={balanceZero}");

            // 6.3 Negative penalty stress testing
            var kNegative = new KyHanThanhToan { SoTienPhai = 1_000_000m, SoTienDaTra = 1_000_000m };
            kNegative.PhiPhatTreHan = -500_000m;
            Assert(kNegative.TienPhat == -500_000m, "G6.3a: Negative value assignment propagates across alias: TienPhat=-500,000");

            // Verify GetInstallmentBalance non-negative guard Math.Max(0, ...)
            decimal balanceNeg = DebtCalculationHelper.GetInstallmentBalance(kNegative);
            Assert(balanceNeg == 0m, "G6.3b: GetInstallmentBalance clamps negative balance to 0m via Math.Max(0m, ...)", $"Balance={balanceNeg}");

            // Partially paid with negative penalty
            kNegative.SoTienDaTra = 0m;
            decimal balanceNegPartial = DebtCalculationHelper.GetInstallmentBalance(kNegative);
            Assert(balanceNegPartial == 500_000m, "G6.3c: Partial with negative penalty: 1M - 0 - 500k = 500,000m", $"Balance={balanceNegPartial}");

            // 6.4 Very large financial value (Extreme upper bound)
            var kLarge = new KyHanThanhToan();
            decimal largeVal = 999_999_999_999.99m;
            kLarge.TienPhat = largeVal;
            Assert(kLarge.PhiPhatTreHan == largeVal, "G6.4a: High-magnitude assignment (999,999,999,999.99) preserves precision across alias");

            kLarge.SoTienPhai = 1_000_000_000m;
            kLarge.SoTienDaTra = 0m;
            decimal balanceLarge = DebtCalculationHelper.GetInstallmentBalance(kLarge);
            Assert(balanceLarge == 1_000_000_000m + largeVal, "G6.4b: GetInstallmentBalance handles high-magnitude numbers without overflow", $"Balance={balanceLarge:N2}");

            // 6.5 Fractional and rounding decimals
            var kFraction = new KyHanThanhToan();
            kFraction.PhiPhatTreHan = 12345.6789m;
            Assert(kFraction.TienPhat == 12345.6789m, "G6.5: Fractional decimal assignment (12345.6789m) preserves 4 decimal places in memory");

            // 6.6 Overpayment edge case
            var kOverpaid = new KyHanThanhToan
            {
                SoTienPhai = 2_000_000m,
                SoTienDaTra = 2_500_000m, // Overpaid 500k
                TienPhat = 200_000m       // Penalty 200k -> Net -300k
            };
            decimal balanceOverpaid = DebtCalculationHelper.GetInstallmentBalance(kOverpaid);
            Assert(balanceOverpaid == 0m, "G6.6a: Overpaid installment (2M - 2.5M + 200k = -300k) correctly clamped to 0m", $"Balance={balanceOverpaid}");

            kOverpaid.TienPhat = 800_000m; // Net: 2M - 2.5M + 800k = 300k
            decimal balanceOverpaidWithHighPenalty = DebtCalculationHelper.GetInstallmentBalance(kOverpaid);
            Assert(balanceOverpaidWithHighPenalty == 300_000m, "G6.6b: Overpaid installment with penalty exceeding overpayment yields exact net balance (300,000m)", $"Balance={balanceOverpaidWithHighPenalty}");
        }

        private static void TestGroup7_DebtCalculationHelperOracles()
        {
            Console.WriteLine("\n--- [GROUP 7] DebtCalculationHelper Business Logic Oracles ---");

            // 7.1 CalculateLateFee grace period oracle (3 days grace period)
            DateTime today = new DateTime(2026, 11, 7);
            decimal feeGrace0 = DebtCalculationHelper.CalculateLateFee(10_000_000m, today, today);
            decimal feeGrace3 = DebtCalculationHelper.CalculateLateFee(10_000_000m, today.AddDays(-3), today);
            decimal feePastGrace = DebtCalculationHelper.CalculateLateFee(10_000_000m, today.AddDays(-4), today);

            Assert(feeGrace0 == 0m, "G7.1a: CalculateLateFee within grace (0 days) returns 0m", $"Fee={feeGrace0}");
            Assert(feeGrace3 == 0m, "G7.1b: CalculateLateFee within grace (3 days) returns 0m", $"Fee={feeGrace3}");
            Assert(feePastGrace == 40_000m, "G7.1c: CalculateLateFee at 4 days past due returns 10M * 0.001 * 4 = 40,000m", $"Fee={feePastGrace}");

            // Negative or zero unpaid amount returns 0m
            decimal feeZeroUnpaid = DebtCalculationHelper.CalculateLateFee(0m, today.AddDays(-10), today);
            decimal feeNegativeUnpaid = DebtCalculationHelper.CalculateLateFee(-500_000m, today.AddDays(-10), today);
            Assert(feeZeroUnpaid == 0m, "G7.1d: CalculateLateFee with 0 unpaid returns 0m");
            Assert(feeNegativeUnpaid == 0m, "G7.1e: CalculateLateFee with negative unpaid returns 0m");

            // 7.2 GetAgingBadgeClass oracle (all tiers)
            Assert(DebtCalculationHelper.GetAgingBadgeClass(0) == "badge bg-success", "G7.2a: Aging tier 0 -> 'badge bg-success'");
            Assert(DebtCalculationHelper.GetAgingBadgeClass(1) == "badge bg-info text-dark", "G7.2b: Aging tier 1 -> 'badge bg-info text-dark'");
            Assert(DebtCalculationHelper.GetAgingBadgeClass(2) == "badge bg-warning text-dark", "G7.2c: Aging tier 2 -> 'badge bg-warning text-dark'");
            Assert(DebtCalculationHelper.GetAgingBadgeClass(3) == "badge bg-orange text-white", "G7.2d: Aging tier 3 -> 'badge bg-orange text-white'");
            Assert(DebtCalculationHelper.GetAgingBadgeClass(4) == "badge bg-danger", "G7.2e: Aging tier 4 -> 'badge bg-danger'");
            Assert(DebtCalculationHelper.GetAgingBadgeClass(-1) == "badge bg-secondary", "G7.2f: Aging tier -1 (unknown) -> 'badge bg-secondary'");
            Assert(DebtCalculationHelper.GetAgingBadgeClass(99) == "badge bg-secondary", "G7.2g: Aging tier 99 (unknown) -> 'badge bg-secondary'");

            // 7.3 CalculateAgingTier boundary oracle
            Assert(DebtCalculationHelper.CalculateAgingTier(0) == 0, "G7.3a: CalculateAgingTier(0) -> Tier 0");
            Assert(DebtCalculationHelper.CalculateAgingTier(1) == 1, "G7.3b: CalculateAgingTier(1) -> Tier 1");
            Assert(DebtCalculationHelper.CalculateAgingTier(30) == 1, "G7.3c: CalculateAgingTier(30) -> Tier 1");
            Assert(DebtCalculationHelper.CalculateAgingTier(31) == 2, "G7.3d: CalculateAgingTier(31) -> Tier 2");
            Assert(DebtCalculationHelper.CalculateAgingTier(60) == 2, "G7.3e: CalculateAgingTier(60) -> Tier 2");
            Assert(DebtCalculationHelper.CalculateAgingTier(61) == 3, "G7.3f: CalculateAgingTier(61) -> Tier 3");
            Assert(DebtCalculationHelper.CalculateAgingTier(90) == 3, "G7.3g: CalculateAgingTier(90) -> Tier 3");
            Assert(DebtCalculationHelper.CalculateAgingTier(91) == 4, "G7.3h: CalculateAgingTier(91) -> Tier 4");
            Assert(DebtCalculationHelper.CalculateAgingTier(999) == 4, "G7.3i: CalculateAgingTier(999) -> Tier 4");

            // 7.4 CalculateDepositSettlement integration with KyHanThanhToan.TienPhat
            var hd = new HopDong
            {
                MaHopDong = 99,
                TongTien = 10_000_000m,
                PhieuThus = new List<PhieuThu>
                {
                    new PhieuThu { LoaiPhieu = 1, SoTien = 5_000_000m, DaHuy = false } // Deposit 5M
                },
                KyHanThanhToans = new List<KyHanThanhToan>
                {
                    new KyHanThanhToan { SoTienPhai = 2_000_000m, SoTienDaTra = 1_000_000m, TienPhat = 100_000m, TrangThai = 0 }, // Unpaid 1.1M
                    new KyHanThanhToan { SoTienPhai = 2_000_000m, SoTienDaTra = 2_000_000m, TienPhat = 0m, TrangThai = 1 }        // Paid
                }
            };

            var (refund, remainingDebt) = DebtCalculationHelper.CalculateDepositSettlement(hd);
            // Deposit = 5M, unpaidRent = (2M - 1M + 100k) = 1.1M -> refund = 5M - 1.1M = 3.9M, remainingDebt = 0
            Assert(refund == 3_900_000m && remainingDebt == 0m,
                "G7.4: CalculateDepositSettlement incorporates TienPhat penalty in unpaidRent calculation",
                $"Refund={refund}, Debt={remainingDebt}");
        }
    }
}
