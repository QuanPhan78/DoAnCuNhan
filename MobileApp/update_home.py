import os

home_code = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/dashboard_provider.dart';
import '../../models/role_enum.dart';
import '../../models/dashboard_model.dart';
import '../../models/user_model.dart';
import '../../widgets/dashboard_widgets.dart';
import '../../widgets/core/state_widgets.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';

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
    final user = context.watch<AuthProvider>().currentUser;
    final dashboardProvider = context.watch<DashboardProvider>();

    return Scaffold(
      body: RefreshIndicator(
        color: AppColors.primary,
        onRefresh: _loadData,
        child: _buildContent(user, dashboardProvider),
      ),
    );
  }

  Widget _buildContent(UserModel? user, DashboardProvider provider) {
    if (user == null) return const SizedBox.shrink();

    if (provider.isLoading && provider.data == null) {
      return const LoadingState(message: 'Đang tải dữ liệu tổng quan...');
    }
    
    if (provider.errorMessage != null) {
      return ErrorState(
        message: 'Không thể tải dữ liệu: ${provider.errorMessage}',
        onRetry: _loadData,
      );
    }

    if (provider.isEmpty || provider.data == null) {
      return const EmptyState(
        message: 'Chưa có dữ liệu thống kê.',
        icon: Icons.analytics_outlined,
      );
    }

    // Pass safe non-null data
    switch (user.role) {
      case Role.customer:
        return _buildCustomerDashboard(user, provider.data!.customerStats!);
      case Role.staff:
        return _buildStaffDashboard(user, provider.data!.staffStats!);
      case Role.admin:
        return _buildAdminDashboard(user, provider.data!.adminStats!);
      default:
        return const EmptyState(message: 'Vai trò không hợp lệ');
    }
  }

  // CUSTOMER DASHBOARD
  Widget _buildCustomerDashboard(UserModel user, CustomerStats stats) {
    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
      children: [
        _buildGreeting(user.name),
        const SizedBox(height: 24),
        
        const SectionTitle(title: 'Tổng quan hợp đồng'),
        Row(
          children: [
            Expanded(
              child: SummaryCard(
                title: 'Đang thuê',
                value: stats.activeContracts.toString(),
                icon: Icons.description_rounded,
                color: AppColors.primary,
                onTap: () => Navigator.pushNamed(context, '/contracts'),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: SummaryCard(
                title: 'Sắp hết hạn',
                value: stats.expiringContracts.toString(),
                icon: Icons.timer_rounded,
                color: AppColors.warning,
                onTap: () => Navigator.pushNamed(context, '/contracts'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        SummaryCard(
          title: 'Yêu cầu bảo trì đang xử lý',
          value: stats.processingMaintenance.toString(),
          icon: Icons.build_circle_rounded,
          color: AppColors.info,
          onTap: () => Navigator.pushNamed(context, '/create_incident'),
        ),
        
        const SizedBox(height: 8),
        const SectionTitle(title: 'Thao tác nhanh'),
        Wrap(
          spacing: 16,
          runSpacing: 16,
          alignment: WrapAlignment.start,
          children: [
            QuickActionCard(title: 'Thiết bị', icon: Icons.devices_rounded, onTap: () => Navigator.pushNamed(context, '/devices')),
            QuickActionCard(title: 'Hợp đồng', icon: Icons.assignment_rounded, onTap: () => Navigator.pushNamed(context, '/contracts')),
            QuickActionCard(title: 'Báo sự cố', icon: Icons.warning_rounded, onTap: () => Navigator.pushNamed(context, '/create_incident')),
            QuickActionCard(title: 'Phản hồi', icon: Icons.feedback_rounded, onTap: () => Navigator.pushNamed(context, '/feedbacks')),
            QuickActionCard(title: 'Khuyến mãi', icon: Icons.local_offer_rounded, onTap: () => Navigator.pushNamed(context, '/promotions')),
          ],
        ),

        const SizedBox(height: 8),
        const SectionTitle(title: 'Khuyến mãi & Thông báo'),
        if (stats.promotions.isEmpty)
          const Padding(
            padding: EdgeInsets.only(top: 16),
            child: Text('Chưa có thông báo nào mới.', style: AppTextStyles.bodySecondary),
          ),
        ...stats.promotions.map((p) => Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            leading: const Icon(Icons.celebration_rounded, color: AppColors.error),
            title: Text(p, style: AppTextStyles.body),
            trailing: const StatusBadge(text: 'MỚI', status: BadgeStatus.error),
          ),
        )),
      ],
    );
  }

  // STAFF DASHBOARD
  Widget _buildStaffDashboard(UserModel user, StaffStats stats) {
    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
      children: [
        _buildGreeting(user.name),
        const SizedBox(height: 24),

        const SectionTitle(title: 'Công việc của tôi'),
        Row(
          children: [
            Expanded(
              child: SummaryCard(
                title: 'Được giao',
                value: stats.assignedTasks.toString(),
                icon: Icons.assignment_ind_rounded,
                color: AppColors.primary,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: SummaryCard(
                title: 'Đang chờ',
                value: stats.pendingRequests.toString(),
                icon: Icons.pending_actions_rounded,
                color: AppColors.warning,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: SummaryCard(
                title: 'Đang xử lý',
                value: stats.processingRequests.toString(),
                icon: Icons.sync_rounded,
                color: AppColors.info,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: SummaryCard(
                title: 'Hoàn thành',
                value: stats.completedRequests.toString(),
                icon: Icons.check_circle_rounded,
                color: AppColors.success,
              ),
            ),
          ],
        ),
      ],
    );
  }

  // ADMIN DASHBOARD
  Widget _buildAdminDashboard(UserModel user, AdminStats stats) {
    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
      children: [
        _buildGreeting(user.name),
        const SizedBox(height: 24),

        const SectionTitle(title: 'Tổng quan kinh doanh'),
        Row(
          children: [
            Expanded(
              child: SummaryCard(
                title: 'Thiết bị (Tổng)',
                value: stats.totalDevices.toString(),
                icon: Icons.devices_rounded,
                color: AppColors.primary,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: SummaryCard(
                title: 'Đang cho thuê',
                value: stats.rentedDevices.toString(),
                icon: Icons.outbox_rounded,
                color: AppColors.success,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: SummaryCard(
                title: 'Tổng hợp đồng',
                value: stats.totalContracts.toString(),
                icon: Icons.description_rounded,
                color: AppColors.secondary,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: SummaryCard(
                title: 'Bảo trì (Tồn đọng)',
                value: stats.maintenanceRequests.toString(),
                icon: Icons.build_circle_rounded,
                color: AppColors.error,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        SummaryCard(
          title: 'Công việc đang xử lý',
          value: stats.processingTasks.toString(),
          icon: Icons.sync_rounded,
          color: AppColors.info,
        ),
      ],
    );
  }

  Widget _buildGreeting(String name) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Xin chào,', style: AppTextStyles.bodySecondary.copyWith(fontSize: 16)),
        const SizedBox(height: 4),
        Text('$name 👋', style: AppTextStyles.h1.copyWith(fontSize: 26, color: AppColors.primary)),
      ],
    );
  }
}
"""

with open("lib/screens/home/home_screen.dart", "w", encoding="utf-8") as f:
    f.write(home_code)

print("Home Screen Dashboard Updated.")