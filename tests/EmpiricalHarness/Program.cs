using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.RegularExpressions;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using RentalSystem.Areas.Admin.Controllers;
using RentalSystem.Models;

namespace EmpiricalHarness
{
    class Program
    {
        private static int _passCount = 0;
        private static int _failCount = 0;

        static void Assert(bool condition, string testId, string description)
        {
            if (condition)
            {
                Console.ForegroundColor = ConsoleColor.Green;
                Console.Write("[PASS] ");
                Console.ResetColor();
                Console.WriteLine($"{testId}: {description}");
                _passCount++;
            }
            else
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.Write("[FAIL] ");
                Console.ResetColor();
                Console.WriteLine($"{testId}: {description}");
                _failCount++;
            }
        }

        static void Main(string[] args)
        {
            Console.WriteLine("================================================================================");
            Console.WriteLine("EMPIRICAL CHALLENGER 1: PHASE 2 CRITERIA 1 & 2 VERIFICATION SUITE");
            Console.WriteLine("================================================================================");

            string rootDir = @"d:\DoAnCuNhan";
            string adminViewsDir = Path.Combine(rootDir, @"RentalSystem\Areas\Admin\Views");
            string adminCtrlDir = Path.Combine(rootDir, @"RentalSystem\Areas\Admin\Controllers");

            // ========================================================================
            // CRITERIA 1: KYTHUAT ROLE VERIFICATION
            // ========================================================================
            Console.WriteLine("\n--- [CRITERIA 1] KyThuat Role Permissions & Workflows ---");

            // 1. ThietBiController Class Authorization
            var tbType = typeof(ThietBiController);
            var tbClassAuth = tbType.GetCustomAttribute<AuthorizeAttribute>();
            var tbRoles = tbClassAuth?.Roles?.Split(',').Select(r => r.Trim()).ToList() ?? new();
            Assert(tbRoles.Contains("KyThuat"), "CHAL-01.01", "ThietBiController class authorizes 'KyThuat'");
            Assert(tbRoles.Contains("Admin"), "CHAL-01.02", "ThietBiController class authorizes 'Admin'");
            Assert(tbRoles.Contains("KinhDoanh"), "CHAL-01.03", "ThietBiController class authorizes 'KinhDoanh'");

            // 2. ThietBiController.Index and Details
            var mTbIndex = tbType.GetMethod("Index", new[] { typeof(int?), typeof(string) });
            Assert(mTbIndex != null, "CHAL-01.04", "ThietBiController.Index(int? status, string? search) exists");
            var tbIndexAuth = mTbIndex?.GetCustomAttribute<AuthorizeAttribute>();
            bool tbIndexAccessibleToKyThuat = tbIndexAuth == null || (tbIndexAuth.Roles?.Contains("KyThuat") ?? false);
            Assert(tbIndexAccessibleToKyThuat, "CHAL-01.05", "ThietBiController.Index is accessible to KyThuat");

            var mTbDetails = tbType.GetMethod("Details", new[] { typeof(int) });
            Assert(mTbDetails != null, "CHAL-01.06", "ThietBiController.Details(int id) exists");
            var tbDetailsAuth = mTbDetails?.GetCustomAttribute<AuthorizeAttribute>();
            bool tbDetailsAccessibleToKyThuat = tbDetailsAuth == null || (tbDetailsAuth.Roles?.Contains("KyThuat") ?? false);
            Assert(tbDetailsAccessibleToKyThuat, "CHAL-01.07", "ThietBiController.Details is accessible to KyThuat");

            // 3. ThietBiController.Edit and Status Mutation
            var mTbEditGet = tbType.GetMethods().FirstOrDefault(m => m.Name == "Edit" && m.GetParameters().Length == 1 && m.GetParameters()[0].ParameterType == typeof(int) && m.GetCustomAttribute<HttpPostAttribute>() == null);
            Assert(mTbEditGet != null, "CHAL-01.08", "ThietBiController.Edit(int id) GET exists");
            var mTbEditPost = tbType.GetMethods().FirstOrDefault(m => m.Name == "Edit" && m.GetCustomAttribute<HttpPostAttribute>() != null);
            Assert(mTbEditPost != null, "CHAL-01.09", "ThietBiController.Edit POST exists");

            // 4. ThietBiController Delete Lock to Admin Only
            var mTbDelGet = tbType.GetMethods().FirstOrDefault(m => m.Name == "Delete" && m.GetParameters().Length == 1 && m.GetCustomAttribute<HttpPostAttribute>() == null);
            Assert(mTbDelGet != null, "CHAL-01.10", "ThietBiController.Delete(int id) GET exists");
            var delGetAuth = mTbDelGet?.GetCustomAttribute<AuthorizeAttribute>();
            Assert(delGetAuth != null && delGetAuth.Roles == "Admin", "CHAL-01.11", $"ThietBi Delete GET strictly locks to [Authorize(Roles = 'Admin')] (Actual: '{delGetAuth?.Roles}')");

            var mTbDelPost = tbType.GetMethods().FirstOrDefault(m => m.Name == "DeleteConfirmed" || (m.Name == "Delete" && m.GetCustomAttribute<HttpPostAttribute>() != null));
            Assert(mTbDelPost != null, "CHAL-01.12", "ThietBiController.DeleteConfirmed POST exists");
            var delPostAuth = mTbDelPost?.GetCustomAttribute<AuthorizeAttribute>();
            Assert(delPostAuth != null && delPostAuth.Roles == "Admin", "CHAL-01.13", $"ThietBi DeleteConfirmed POST strictly locks to [Authorize(Roles = 'Admin')] (Actual: '{delPostAuth?.Roles}')");
            Assert(!delGetAuth?.Roles?.Contains("KyThuat") == true && !delPostAuth?.Roles?.Contains("KyThuat") == true, "CHAL-01.14", "KyThuat role is completely barred from ThietBi Delete");

            // 5. ThietBi Source Logic: Lifecycle Logging & Option 4
            string tbCtrlSrc = File.ReadAllText(Path.Combine(adminCtrlDir, "ThietBiController.cs"));
            Assert(tbCtrlSrc.Contains("oldTb.TrangThai != tb.TrangThai") && tbCtrlSrc.Contains("LichSuThietBis.Add"), "CHAL-01.15", "ThietBiController records state transitions in LichSuThietBi on Edit");
            Assert(tbCtrlSrc.Contains("4 => \"Hỏng thanh lý\""), "CHAL-01.16", "ThietBiController supports status 4 (Hỏng thanh lý)");

            string tbEditSrc = File.ReadAllText(Path.Combine(adminViewsDir, @"ThietBi\Edit.cshtml"));
            Assert(tbEditSrc.Contains("value=\"4\"") && tbEditSrc.Contains("Hỏng thanh lý"), "CHAL-01.17", "ThietBi/Edit.cshtml dropdown includes option 4: Hỏng thanh lý");

            string tbDetailsPath = Path.Combine(adminViewsDir, @"ThietBi\Details.cshtml");
            Assert(File.Exists(tbDetailsPath), "CHAL-01.18", "ThietBi/Details.cshtml view file exists on disk");
            string tbDetailsSrc = File.Exists(tbDetailsPath) ? File.ReadAllText(tbDetailsPath) : "";
            Assert(tbDetailsSrc.Contains("@model RentalSystem.Models.ThietBi"), "CHAL-01.19", "ThietBi/Details.cshtml strongly binds @model RentalSystem.Models.ThietBi");
            Assert(tbDetailsSrc.Contains("LichSuThietBis") && tbDetailsSrc.Contains("PhieuBaoTris"), "CHAL-01.20", "ThietBi/Details.cshtml renders lifecycle log and maintenance history");

            // 6. SanPhamController Class Authorization
            var spType = typeof(SanPhamController);
            var spClassAuth = spType.GetCustomAttribute<AuthorizeAttribute>();
            var spRoles = spClassAuth?.Roles?.Split(',').Select(r => r.Trim()).ToList() ?? new();
            Assert(spRoles.Contains("KyThuat"), "CHAL-01.21", "SanPhamController class authorizes 'KyThuat' for reading");

            var mSpIndex = spType.GetMethod("Index", Type.EmptyTypes);
            Assert(mSpIndex != null, "CHAL-01.22", "SanPhamController.Index() exists");
            var spIndexAuth = mSpIndex?.GetCustomAttribute<AuthorizeAttribute>();
            bool spIndexAccessibleToKyThuat = spIndexAuth == null || (spIndexAuth.Roles?.Contains("KyThuat") ?? false);
            Assert(spIndexAccessibleToKyThuat, "CHAL-01.23", "SanPhamController.Index is accessible to KyThuat");

            var mSpDetails = spType.GetMethod("Details", new[] { typeof(int) });
            Assert(mSpDetails != null, "CHAL-01.24", "SanPhamController.Details(int id) exists");
            var spDetailsAuth = mSpDetails?.GetCustomAttribute<AuthorizeAttribute>();
            bool spDetailsAccessibleToKyThuat = spDetailsAuth == null || (spDetailsAuth.Roles?.Contains("KyThuat") ?? false);
            Assert(spDetailsAccessibleToKyThuat, "CHAL-01.25", "SanPhamController.Details is accessible to KyThuat");

            // 7. SanPham Create/Edit/Delete Barred from KyThuat
            var mSpCreateGet = spType.GetMethods().FirstOrDefault(m => m.Name == "Create" && m.GetParameters().Length == 0 && m.GetCustomAttribute<HttpPostAttribute>() == null);
            var spCreateAuth = mSpCreateGet?.GetCustomAttribute<AuthorizeAttribute>();
            var spCreateRoles = spCreateAuth?.Roles?.Split(',').Select(r => r.Trim()).ToList() ?? new();
            Assert(!spCreateRoles.Contains("KyThuat") && spCreateRoles.Contains("Admin") && spCreateRoles.Contains("KinhDoanh"), "CHAL-01.26", $"SanPham Create GET barred from KyThuat (Roles: '{spCreateAuth?.Roles}')");

            var mSpCreatePost = spType.GetMethods().FirstOrDefault(m => m.Name == "Create" && m.GetCustomAttribute<HttpPostAttribute>() != null);
            var spCreatePostAuth = mSpCreatePost?.GetCustomAttribute<AuthorizeAttribute>();
            var spCreatePostRoles = spCreatePostAuth?.Roles?.Split(',').Select(r => r.Trim()).ToList() ?? new();
            Assert(!spCreatePostRoles.Contains("KyThuat"), "CHAL-01.27", $"SanPham Create POST barred from KyThuat (Roles: '{spCreatePostAuth?.Roles}')");

            var mSpEditGet = spType.GetMethods().FirstOrDefault(m => m.Name == "Edit" && m.GetParameters().Length == 1 && m.GetCustomAttribute<HttpPostAttribute>() == null);
            var spEditAuth = mSpEditGet?.GetCustomAttribute<AuthorizeAttribute>();
            var spEditRoles = spEditAuth?.Roles?.Split(',').Select(r => r.Trim()).ToList() ?? new();
            Assert(!spEditRoles.Contains("KyThuat"), "CHAL-01.28", $"SanPham Edit GET barred from KyThuat (Roles: '{spEditAuth?.Roles}')");

            var mSpDelGet = spType.GetMethods().FirstOrDefault(m => m.Name == "Delete" && m.GetCustomAttribute<HttpPostAttribute>() == null);
            var spDelAuth = mSpDelGet?.GetCustomAttribute<AuthorizeAttribute>();
            var spDelRoles = spDelAuth?.Roles?.Split(',').Select(r => r.Trim()).ToList() ?? new();
            Assert(!spDelRoles.Contains("KyThuat"), "CHAL-01.29", $"SanPham Delete GET barred from KyThuat (Roles: '{spDelAuth?.Roles}')");

            string spDetailsPath = Path.Combine(adminViewsDir, @"SanPham\Details.cshtml");
            Assert(File.Exists(spDetailsPath), "CHAL-01.30", "SanPham/Details.cshtml view file exists on disk");
            string spDetailsSrc = File.Exists(spDetailsPath) ? File.ReadAllText(spDetailsPath) : "";
            Assert(spDetailsSrc.Contains("@model RentalSystem.Models.SanPham"), "CHAL-01.31", "SanPham/Details.cshtml strongly binds @model RentalSystem.Models.SanPham");
            Assert(spDetailsSrc.Contains("ViewBag.Devices"), "CHAL-01.32", "SanPham/Details.cshtml lists warehouse devices from ViewBag.Devices");

            // 8. Sidebar Admin Menu Alignment (_AdminLayout.cshtml)
            string adminLayoutSrc = File.ReadAllText(Path.Combine(adminViewsDir, @"Shared\_AdminLayout.cshtml"));
            bool rendersSanPhamForKyThuat = Regex.IsMatch(adminLayoutSrc, @"User\.IsInRole\(""KyThuat""\)[^}]*\/Admin\/SanPham", RegexOptions.Singleline);
            bool rendersThietBiForKyThuat = Regex.IsMatch(adminLayoutSrc, @"User\.IsInRole\(""KyThuat""\)[^}]*\/Admin\/ThietBi", RegexOptions.Singleline);
            Assert(rendersSanPhamForKyThuat, "CHAL-01.33", "Sidebar renders 'Dòng sản phẩm' (/Admin/SanPham) for KyThuat");
            Assert(rendersThietBiForKyThuat, "CHAL-01.34", "Sidebar renders 'Serial Máy' (/Admin/ThietBi) for KyThuat");

            // Check no neon classes in sidebar
            var neonRegex = new Regex(@"class=""[^""]*\b(text-info|text-success|text-warning|text-primary|text-secondary|text-danger)\b[^""]*""");
            int sidebarStart = adminLayoutSrc.IndexOf("class=\"sidebar-menu\"");
            int sidebarEnd = adminLayoutSrc.IndexOf("</div>", sidebarStart + 20);
            string sidebarSub = sidebarStart >= 0 ? adminLayoutSrc.Substring(sidebarStart, Math.Min(3000, adminLayoutSrc.Length - sidebarStart)) : "";
            Assert(!neonRegex.IsMatch(sidebarSub), "CHAL-01.35", "Sidebar menu uses monochrome slate icons without scattered neon colors");

            // 9. BaoTri Controller SLA & Index View
            var btType = typeof(BaoTriController);
            var btClassAuth = btType.GetCustomAttribute<AuthorizeAttribute>();
            var btRoles = btClassAuth?.Roles?.Split(',').Select(r => r.Trim()).ToList() ?? new();
            Assert(btRoles.Contains("KyThuat"), "CHAL-01.36", "BaoTriController authorizes KyThuat");

            string btCtrlSrc = File.ReadAllText(Path.Combine(adminCtrlDir, "BaoTriController.cs"));
            Assert(btCtrlSrc.Contains("p.TrangThai < 3 && p.HanHoanThanh.HasValue && p.HanHoanThanh.Value < now"), "CHAL-01.37", "BaoTri overdue_sla oracle strictly preserved for EDGE-04.11");
            Assert(btCtrlSrc.Contains("filter == \"near_sla\"") && btCtrlSrc.Contains("AddHours(12)"), "CHAL-01.38", "BaoTri near_sla filter implemented (< 12h deadline)");

            string btIndexSrc = File.ReadAllText(Path.Combine(adminViewsDir, @"BaoTri\Index.cshtml"));
            int btStatCardCount = Regex.Matches(btIndexSrc, @"class=""stat-card""").Count;
            Assert(btStatCardCount == 4, "CHAL-01.39", $"BaoTri/Index.cshtml renders exactly 4 KPI stat cards (Found: {btStatCardCount})");
            Assert(btIndexSrc.Contains("asp-route-filter=\"overdue_sla\""), "CHAL-01.40", "BaoTri/Index.cshtml renders Trễ hạn SLA filter tab");
            Assert(btIndexSrc.Contains("asp-route-filter=\"near_sla\""), "CHAL-01.41", "BaoTri/Index.cshtml renders Sắp đến hạn (< 12h) filter tab");
            Assert(btIndexSrc.Contains("badge-soft-danger") && btIndexSrc.Contains("Quá hạn SLA"), "CHAL-01.42", "BaoTri/Index.cshtml renders badge-soft-danger for overdue SLA");
            Assert(btIndexSrc.Contains("badge-soft-warning") && btIndexSrc.Contains("Sắp hết"), "CHAL-01.43", "BaoTri/Index.cshtml renders badge-soft-warning for near deadline");
            Assert(btIndexSrc.Contains("badge-soft-success") && btIndexSrc.Contains("Đúng hạn"), "CHAL-01.44", "BaoTri/Index.cshtml renders badge-soft-success for on-time SLA");
            Assert(btIndexSrc.Contains("table-danger") && btIndexSrc.Contains("table-warning"), "CHAL-01.45", "BaoTri/Index.cshtml highlights table rows based on SLA risk tier");

            // ========================================================================
            // CRITERIA 2: KINHDOANH ROLE VERIFICATION
            // ========================================================================
            Console.WriteLine("\n--- [CRITERIA 2] KinhDoanh Role Permissions & Workflows ---");

            // 1. HopDongController Create Permissions
            var hdType = typeof(HopDongController);
            var mHdCreateGet = hdType.GetMethods().FirstOrDefault(m => m.Name == "Create" && m.GetParameters().Length == 0 && m.GetCustomAttribute<HttpPostAttribute>() == null);
            Assert(mHdCreateGet != null, "CHAL-02.01", "HopDongController.Create() GET exists");
            var hdCreateGetAuth = mHdCreateGet?.GetCustomAttribute<AuthorizeAttribute>();
            var hdCreateGetRoles = hdCreateGetAuth?.Roles?.Split(',').Select(r => r.Trim()).ToList() ?? new();
            Assert(hdCreateGetRoles.Contains("KinhDoanh"), "CHAL-02.02", "HopDongController.Create GET authorizes 'KinhDoanh'");

            var mHdCreatePost = hdType.GetMethods().FirstOrDefault(m => m.Name == "Create" && m.GetCustomAttribute<HttpPostAttribute>() != null);
            Assert(mHdCreatePost != null, "CHAL-02.03", "HopDongController.Create POST exists");
            var hdCreatePostAuth = mHdCreatePost?.GetCustomAttribute<AuthorizeAttribute>();
            var hdCreatePostRoles = hdCreatePostAuth?.Roles?.Split(',').Select(r => r.Trim()).ToList() ?? new();
            Assert(hdCreatePostRoles.Contains("KinhDoanh"), "CHAL-02.04", "HopDongController.Create POST authorizes 'KinhDoanh'");
            Assert(mHdCreatePost.GetParameters().Length == 12, "CHAL-02.05", $"HopDongController.Create POST preserves exact 12-parameter signature invariant (Actual: {mHdCreatePost.GetParameters().Length})");

            // 2. Fast Device Lookup (TrangThai == 0)
            string tbIndexSrc = File.ReadAllText(Path.Combine(adminViewsDir, @"ThietBi\Index.cshtml"));
            Assert(tbIndexSrc.Contains("asp-route-status=\"0\"") && tbIndexSrc.Contains("Sẵn sàng"), "CHAL-02.06", "ThietBi/Index.cshtml provides fast filter tab for ready devices (status=0)");
            Assert(tbIndexSrc.Contains("name=\"search\""), "CHAL-02.07", "ThietBi/Index.cshtml provides search bar for quick serial/product lookup");

            string hdCtrlSrc = File.ReadAllText(Path.Combine(adminCtrlDir, "HopDongController.cs"));
            Assert(hdCtrlSrc.Contains("t.TrangThai == 0") && hdCtrlSrc.Contains("ViewBag.AvailableDevices"), "CHAL-02.08", "HopDongController.Create GET populates ViewBag.AvailableDevices where TrangThai == 0");

            string hdCreateSrc = File.ReadAllText(Path.Combine(adminViewsDir, @"HopDong\Create.cshtml"));
            Assert(hdCreateSrc.Contains("id=\"modalTraCuuKho\""), "CHAL-02.09", "HopDong/Create.cshtml renders quick lookup modal (#modalTraCuuKho)");
            Assert(hdCreateSrc.Contains("id=\"txtSearchModal\""), "CHAL-02.10", "HopDong/Create.cshtml modal provides real-time client-side search input (#txtSearchModal)");
            Assert(hdCreateSrc.Contains("btn-chon-may") && hdCreateSrc.Contains("Chọn máy"), "CHAL-02.11", "HopDong/Create.cshtml modal includes 'Chọn máy' button to select stock into contract");
            Assert(hdCreateSrc.Contains("id=\"cboChonKhachHang\"") && hdCreateSrc.Contains("data-hoten"), "CHAL-02.12", "HopDong/Create.cshtml includes customer autofill dropdown (#cboChonKhachHang)");

            // 3. Deposit Recording & Advance Rent Flow (PhieuThu Loai 1 & Loai 0)
            Assert(hdCtrlSrc.Contains("LoaiPhieu = 1") && hdCtrlSrc.Contains("hd.TienCocBaoDamMay"), "CHAL-02.13", "HopDong Create POST generates PhieuThu Loai 1 (tiền cọc bảo đảm)");
            Assert(hdCtrlSrc.Contains("LoaiPhieu = 0") && hdCtrlSrc.Contains("hd.TienThueTraTruoc"), "CHAL-02.14", "HopDong Create POST generates PhieuThu Loai 0 (tiền thuê trả trước)");

            var mThemTienCoc = hdType.GetMethod("ThemTienCoc");
            Assert(mThemTienCoc != null, "CHAL-02.15", "HopDongController.ThemTienCoc exists");
            var themCocAuth = mThemTienCoc?.GetCustomAttribute<AuthorizeAttribute>();
            var themCocRoles = themCocAuth?.Roles?.Split(',').Select(r => r.Trim()).ToList() ?? new();
            Assert(themCocRoles.Contains("KinhDoanh"), "CHAL-02.16", "HopDongController.ThemTienCoc authorizes 'KinhDoanh'");
            Assert(hdCtrlSrc.Contains("LoaiPhieu = 0") && hdCtrlSrc.Contains("soTienCoc") && hdCtrlSrc.Contains("ThemTienCoc"), "CHAL-02.17", "HopDongController.ThemTienCoc generates PhieuThu Loai 0 for installment debt deduction");

            Assert(hdCreateSrc.Contains("name=\"TienCocBaoDamMay\""), "CHAL-02.18", "HopDong/Create.cshtml contains TienCocBaoDamMay input field");
            Assert(hdCreateSrc.Contains("name=\"TienThueTraTruoc\""), "CHAL-02.19", "HopDong/Create.cshtml contains TienThueTraTruoc input field");
            Assert(hdCreateSrc.Contains("name=\"TienDaCoc\""), "CHAL-02.20", "HopDong/Create.cshtml contains TienDaCoc readonly summary input");

            // ========================================================================
            // UI DESIGN SYSTEM & SUBTITLE SANITIZATION
            // ========================================================================
            Console.WriteLine("\n--- [UI DESIGN SYSTEM] Executive Navy & Clean Title Verification ---");

            var viewsToCheck = new[]
            {
                @"ThietBi\Index.cshtml",
                @"ThietBi\Details.cshtml",
                @"SanPham\Index.cshtml",
                @"SanPham\Details.cshtml",
                @"BaoTri\Index.cshtml",
                @"HopDong\Create.cshtml"
            };

            int viewIdx = 1;
            foreach (var relPath in viewsToCheck)
            {
                string fullPath = Path.Combine(adminViewsDir, relPath);
                Assert(File.Exists(fullPath), $"CHAL-03.{viewIdx:D2}a", $"{relPath} exists on disk");
                string content = File.ReadAllText(fullPath);

                Assert(content.Contains("class=\"page-header") && content.Contains("class=\"page-title"), $"CHAL-03.{viewIdx:D2}b", $"{relPath} uses .page-header and .page-title semantic classes");

                // Check no redundant explanatory subtitles in page-header
                int phStart = content.IndexOf("class=\"page-header");
                int phEnd = phStart >= 0 ? content.IndexOf("</div>", phStart) : -1;
                string headerSnippet = (phStart >= 0 && phEnd > phStart) ? content.Substring(phStart, phEnd - phStart + 6) : "";
                bool hasRedundantSubtitle = Regex.IsMatch(headerSnippet, @"<p\b[^>]*>.*?(cấu hình|theo dõi|điều phối|quản lý hệ thống|tại đây).*?<\/p>", RegexOptions.IgnoreCase);
                Assert(!hasRedundantSubtitle, $"CHAL-03.{viewIdx:D2}c", $"{relPath} has zero redundant explanatory subtitles in page-header");

                viewIdx++;
            }

            // ========================================================================
            // SUMMARY
            // ========================================================================
            Console.WriteLine("\n================================================================================");
            Console.WriteLine($"EMPIRICAL HARNESS SUMMARY: {_passCount} PASSED, {_failCount} FAILED (TOTAL: {_passCount + _failCount})");
            Console.WriteLine("================================================================================");

            Environment.Exit(_failCount > 0 ? 1 : 0);
        }
    }
}
