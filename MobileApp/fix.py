import os

home_code = r'''import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/dashboard_provider.dart';
import '../../models/role_enum.dart';
import '../../models/dashboard_model.dart';
import '../../widgets/dashboard_widgets.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  Future<void> _loadData() async {
    final role = context.read<AuthProvider>().currentUser?.role;
    if (role != null) {
      await context.read<DashboardProvider>().loadDashboard(role);
    }
  }

  @override
  Widget build(BuildContext context) {
    final role = context.watch<AuthProvider>().currentUser?.role;
    final dashboardProvider = context.watch<DashboardProvider>();

    return RefreshIndicator(
      onRefresh: _loadData,
      child: _buildContent(role, dashboardProvider),
    );
  }

  Widget _buildContent(Role? role, DashboardProvider provider) {
    if (provider.isLoading && provider.data == null) {
      return const Center(child: CircularProgressIndicator());
    }
    
    if (provider.errorMessage != null) {
      return ListView(
        children: [
          SizedBox(height: MediaQuery.of(context).size.height * 0.3),
          Center(
            child: Column(
              children: [
                const Icon(Icons.error_outline, size: 60, color: Colors.red),
                const SizedBox(height: 16),
                Text('Lỗi: ${provider.errorMessage}'),
                const SizedBox(height: 16),
                ElevatedButton(onPressed: _loadData, child: const Text('Thử lại')),
              ],
            ),
          ),
        ],
      );
    }

    if (provider.isEmpty || provider.data == null) {
      return ListView(
        children: [
          SizedBox(height: MediaQuery.of(context).size.height * 0.3),
          const Center(child: Text('Không có dữ liệu')),
        ],
      );
    }

    switch (role) {
      case Role.customer:
        return _buildCustomerDashboard(provider.data!.customerStats!);
      case Role.staff:
        return _buildStaffDashboard(provider.data!.staffStats!);
      case Role.admin:
        return _buildAdminDashboard(provider.data!.adminStats!);
      default:
        return const Center(child: Text('Vai trò không hợp lệ'));
    }
  }

  Widget _buildCustomerDashboard(CustomerStats stats) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const SectionTitle(title: 'Tổng quan'),
        Row(
          children: [
            Expanded(child: SummaryCard(title: 'Đang thuê', value: stats.activeContracts.toString(), icon: Icons.description, color: Colors.blue)),
            const SizedBox(width: 16),
            Expanded(child: SummaryCard(title: 'Sắp hết hạn', value: stats.expiringContracts.toString(), icon: Icons.timer, color: Colors.orange)),
          ],
        ),
        const SizedBox(height: 16),
        SummaryCard(title: 'Yêu cầu bảo trì đang xử lý', value: stats.processingMaintenance.toString(), icon: Icons.build, color: Colors.green),
        
        const SectionTitle(title: 'Thao tác nhanh'),
        Wrap(
          spacing: 16,
          runSpacing: 16,
          alignment: WrapAlignment.start,
          children: [
            QuickActionCard(title: 'Thiết bị', icon: Icons.devices, onTap: () {}),
            QuickActionCard(title: 'Hợp đồng', icon: Icons.description, onTap: () {}),
            QuickActionCard(title: 'Báo sự cố', icon: Icons.warning, onTap: () {}),
            QuickActionCard(title: 'Bảo trì', icon: Icons.build, onTap: () {}),
            QuickActionCard(title: 'Lịch sử', icon: Icons.history, onTap: () {}),
          ],
        ),

        const SectionTitle(title: 'Khuyến mãi & Thông báo'),
        if (stats.promotions.isEmpty) const Text('Chưa có thông báo nào.'),
        ...stats.promotions.map((p) => Card(
          child: ListTile(
            leading: const Icon(Icons.local_offer, color: Colors.red),
            title: Text(p),
            trailing: const StatusBadge(text: 'MỚI', color: Colors.red),
          ),
        )),
      ],
    );
  }

  Widget _buildStaffDashboard(StaffStats stats) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const SectionTitle(title: 'Công việc của tôi'),
        Row(
          children: [
            Expanded(child: SummaryCard(title: 'Được giao', value: stats.assignedTasks.toString(), icon: Icons.assignment, color: Colors.blue)),
            const SizedBox(width: 16),
            Expanded(child: SummaryCard(title: 'Đang chờ', value: stats.pendingRequests.toString(), icon: Icons.pending_actions, color: Colors.orange)),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(child: SummaryCard(title: 'Đang xử lý', value: stats.processingRequests.toString(), icon: Icons.sync, color: Colors.purple)),
            const SizedBox(width: 16),
            Expanded(child: SummaryCard(title: 'Hoàn thành', value: stats.completedRequests.toString(), icon: Icons.check_circle, color: Colors.green)),
          ],
        ),
      ],
    );
  }

  Widget _buildAdminDashboard(AdminStats stats) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const SectionTitle(title: 'Thống kê tổng quan'),
        Row(
          children: [
            Expanded(child: SummaryCard(title: 'Tổng thiết bị', value: stats.totalDevices.toString(), icon: Icons.devices, color: Colors.blue)),
            const SizedBox(width: 16),
            Expanded(child: SummaryCard(title: 'Đang cho thuê', value: stats.rentedDevices.toString(), icon: Icons.outbox, color: Colors.orange)),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(child: SummaryCard(title: 'Tổng hợp đồng', value: stats.totalContracts.toString(), icon: Icons.description, color: Colors.purple)),
            const SizedBox(width: 16),
            Expanded(child: SummaryCard(title: 'Yêu cầu bảo trì', value: stats.maintenanceRequests.toString(), icon: Icons.build, color: Colors.red)),
          ],
        ),
        const SizedBox(height: 16),
        SummaryCard(title: 'Công việc đang xử lý', value: stats.processingTasks.toString(), icon: Icons.sync, color: Colors.green),
      ],
    );
  }
}
'''

widgets_code = r'''import 'package:flutter/material.dart';

class SummaryCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  const SummaryCard({
    super.key,
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: color, size: 32),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: TextStyle(color: Colors.grey[600], fontSize: 14)),
                  const SizedBox(height: 4),
                  Text(value, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class QuickActionCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final VoidCallback onTap;

  const QuickActionCard({
    super.key,
    required this.title,
    required this.icon,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: 80,
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: Colors.blue.withValues(alpha: 0.05),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.blue.withValues(alpha: 0.2)),
        ),
        child: Column(
          children: [
            Icon(icon, color: Colors.blue, size: 28),
            const SizedBox(height: 8),
            Text(
              title,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
            ),
          ],
        ),
      ),
    );
  }
}

class SectionTitle extends StatelessWidget {
  final String title;

  const SectionTitle({super.key, required this.title});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 16.0),
      child: Text(
        title,
        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
      ),
    );
  }
}

class StatusBadge extends StatelessWidget {
  final String text;
  final Color color;

  const StatusBadge({
    super.key,
    required this.text,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color),
      ),
      child: Text(
        text,
        style: TextStyle(color: color, fontWeight: FontWeight.w600, fontSize: 12),
      ),
    );
  }
}
'''

test_code = r'''import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:quan_ly_cho_thue_thiet_bi/main.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/auth_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/repositories/auth_repository.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/local/local_auth_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/dashboard_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/repositories/dashboard_repository.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('App should render splash screen and navigate', (WidgetTester tester) async {
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(
            create: (_) => AuthProvider(AuthRepository(LocalAuthDataSource())),
          ),
          ChangeNotifierProvider(
            create: (_) => DashboardProvider(
              DashboardRepository(LocalDashboardDataSource()),
            ),
          ),
        ],
        child: const MyApp(),
      ),
    );

    expect(find.text('Thiết Bị Điện Tử'), findsOneWidget);
    await tester.pumpAndSettle(const Duration(seconds: 2));
    expect(find.text('Quản lý thiết bị điện tử'), findsWidgets);
  });
}
'''

with open(r'lib\screens\home\home_screen.dart', 'w', encoding='utf-8') as f:
    f.write(home_code)

with open(r'lib\widgets\dashboard_widgets.dart', 'w', encoding='utf-8') as f:
    f.write(widgets_code)

with open(r'test\widget_test.dart', 'w', encoding='utf-8') as f:
    f.write(test_code)