import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/app_config_provider.dart';
import '../../providers/dashboard_provider.dart';
import '../../models/role_enum.dart';
import '../../models/dashboard_model.dart';
import '../../models/user_model.dart';
import '../../widgets/dashboard_widgets.dart';
import '../../widgets/core/state_widgets.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../providers/contract_provider.dart';

class HomeScreen extends StatefulWidget {
  final void Function(int tabIndex, [int? subFilter])? onSelectTab;
  const HomeScreen({super.key, this.onSelectTab});

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
    final user = context.read<AuthProvider>().currentUser;
    if (user != null) {
      await context.read<DashboardProvider>().loadDashboard(user.role, userId: user.id);
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = context.watch<AuthProvider>().currentUser;
    final dashboardProvider = context.watch<DashboardProvider>();
    final config = context.watch<AppConfigProvider>();

    return Scaffold(
      body: RefreshIndicator(
        color: AppColors.primary,
        onRefresh: _loadData,
        child: _buildContent(user, dashboardProvider, config),
      ),
    );
  }

  Widget _buildContent(UserModel? user, DashboardProvider provider, AppConfigProvider config) {
    if (user == null) return const SizedBox.shrink();

    if (provider.isLoading && provider.data == null) {
      return LoadingState(message: config.tr('Đang tải dữ liệu tổng quan...'));
    }
    
    if (provider.errorMessage != null) {
      return ErrorState(
        message: '${config.tr("Không thể tải dữ liệu")}: ${provider.errorMessage}',
        onRetry: _loadData,
      );
    }

    if (provider.isEmpty || provider.data == null) {
      return EmptyState(
        message: config.tr('Chưa có dữ liệu thống kê.'),
        icon: Icons.analytics_outlined,
      );
    }

    // Pass safe non-null data
    switch (user.role) {
      case Role.customer:
        return _buildCustomerDashboard(user, provider.data!.customerStats!, config);
      case Role.staff:
        return _buildStaffDashboard(user, provider.data!.staffStats!, config);
      case Role.admin:
        return _buildAdminDashboard(user, provider.data!.adminStats!, config);
    }
  }

  // CUSTOMER DASHBOARD
  Widget _buildCustomerDashboard(UserModel user, CustomerStats stats, AppConfigProvider config) {
    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
      children: [
        _buildGreeting(user.name, config),
        const SizedBox(height: 24),
        
        SectionTitle(title: config.tr('Tổng quan hợp đồng')),
        Row(
          children: [
            Expanded(
              child: SummaryCard(
                title: config.tr('Đang thuê'),
                value: stats.activeContracts.toString(),
                icon: Icons.description_rounded,
                color: AppColors.primary,
                onTap: () {
                  context.read<ContractProvider>().setStatusFilter('Đang hiệu lực');
                  if (widget.onSelectTab != null) {
                    widget.onSelectTab!(2);
                  } else {
                    Navigator.pushNamed(context, '/contracts');
                  }
                },
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: SummaryCard(
                title: config.tr('Sắp hết hạn'),
                value: stats.expiringContracts.toString(),
                icon: Icons.timer_rounded,
                color: AppColors.warning,
                onTap: () {
                  context.read<ContractProvider>().setStatusFilter(null);
                  if (widget.onSelectTab != null) {
                    widget.onSelectTab!(2);
                  } else {
                    Navigator.pushNamed(context, '/contracts');
                  }
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        SummaryCard(
          title: config.tr('Yêu cầu bảo trì đang xử lý'),
          value: stats.processingMaintenance.toString(),
          icon: Icons.build_circle_rounded,
          color: AppColors.info,
          onTap: () => Navigator.pushNamed(context, '/create_incident'),
        ),
        
        const SizedBox(height: 8),
        SectionTitle(title: config.tr('Thao tác nhanh')),
        Wrap(
          spacing: 16,
          runSpacing: 16,
          alignment: WrapAlignment.start,
          children: [
            QuickActionCard(
              title: config.tr('Thiết bị'), 
              icon: Icons.devices_rounded, 
              onTap: () {
                if (widget.onSelectTab != null) {
                  widget.onSelectTab!(1);
                } else {
                  Navigator.pushNamed(context, '/devices');
                }
              },
            ),
            QuickActionCard(
              title: config.tr('Hợp đồng'), 
              icon: Icons.assignment_rounded, 
              onTap: () {
                context.read<ContractProvider>().setStatusFilter(null);
                if (widget.onSelectTab != null) {
                  widget.onSelectTab!(2);
                } else {
                  Navigator.pushNamed(context, '/contracts');
                }
              },
            ),
            QuickActionCard(title: config.tr('Báo sự cố'), icon: Icons.warning_rounded, onTap: () => Navigator.pushNamed(context, '/create_incident')),
            QuickActionCard(title: config.tr('Phản hồi'), icon: Icons.feedback_rounded, onTap: () => Navigator.pushNamed(context, '/feedbacks')),
            QuickActionCard(title: config.tr('Khuyến mãi'), icon: Icons.local_offer_rounded, onTap: () => Navigator.pushNamed(context, '/promotions')),
            QuickActionCard(title: config.tr('Thông báo'), icon: Icons.notifications_outlined,
              onTap: () => Navigator.pushNamed(context, '/notifications')),
          ],
        ),

        const SizedBox(height: 8),
        SectionTitle(title: config.tr('Khuyến mãi')),
        if (stats.promotions.isEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 16),
            child: Text(config.tr('Chưa có khuyến mãi.'), style: AppTextStyles.bodySecondary),
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
  Widget _buildStaffDashboard(UserModel user, StaffStats stats, AppConfigProvider config) {
    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
      children: [
        _buildGreeting(user.name, config),
        const SizedBox(height: 24),

        SectionTitle(title: config.tr('Công việc của tôi')),
        Row(
          children: [
            Expanded(
              child: SummaryCard(
                title: config.tr('Được giao'),
                value: stats.assignedTasks.toString(),
                icon: Icons.assignment_ind_rounded,
                color: AppColors.primary,
                onTap: () {
                  if (widget.onSelectTab != null) {
                    widget.onSelectTab!(1, 0); // Tab Công việc, filter Tất cả
                  } else {
                    Navigator.pushNamed(context, '/tasks');
                  }
                },
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: SummaryCard(
                title: config.tr('Đang chờ'),
                value: stats.pendingRequests.toString(),
                icon: Icons.pending_actions_rounded,
                color: AppColors.warning,
                onTap: () {
                  if (widget.onSelectTab != null) {
                    widget.onSelectTab!(1, 1); // Tab Công việc, filter Đang chờ
                  } else {
                    Navigator.pushNamed(context, '/tasks');
                  }
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: SummaryCard(
                title: config.tr('Đang xử lý'),
                value: stats.processingRequests.toString(),
                icon: Icons.sync_rounded,
                color: AppColors.info,
                onTap: () {
                  if (widget.onSelectTab != null) {
                    widget.onSelectTab!(1, 2); // Tab Công việc, filter Đang xử lý
                  } else {
                    Navigator.pushNamed(context, '/tasks');
                  }
                },
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: SummaryCard(
                title: config.tr('Hoàn thành'),
                value: stats.completedRequests.toString(),
                icon: Icons.check_circle_rounded,
                color: AppColors.success,
                onTap: () {
                  if (widget.onSelectTab != null) {
                    widget.onSelectTab!(1, 3); // Tab Công việc, filter Hoàn thành
                  } else {
                    Navigator.pushNamed(context, '/tasks');
                  }
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 24),
        SectionTitle(title: config.tr('Nhiệm vụ & Chức năng')),
        Wrap(
          spacing: 16,
          runSpacing: 16,
          alignment: WrapAlignment.start,
          children: [
            QuickActionCard(title: config.tr('Sự cố'), icon: Icons.report_problem_rounded, onTap: () => Navigator.pushNamed(context, '/incidents')),
            QuickActionCard(
              title: config.tr('Bảo trì'), 
              icon: Icons.build_rounded, 
              onTap: () {
                if (widget.onSelectTab != null) {
                  widget.onSelectTab!(2);
                } else {
                  Navigator.pushNamed(context, '/maintenances');
                }
              },
            ),
            QuickActionCard(title: config.tr('Thiết bị'), icon: Icons.devices_rounded, onTap: () => Navigator.pushNamed(context, '/devices')),
            QuickActionCard(title: config.tr('Hợp đồng'), icon: Icons.assignment_rounded, onTap: () => Navigator.pushNamed(context, '/contracts')),
          ],
        ),
      ],
    );
  }

  // ADMIN DASHBOARD
  Widget _buildAdminDashboard(UserModel user, AdminStats stats, AppConfigProvider config) {
    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
      children: [
        _buildGreeting(user.name, config),
        const SizedBox(height: 24),

        SectionTitle(title: config.tr('Tổng quan kinh doanh')),
        Row(
          children: [
            Expanded(
              child: SummaryCard(
                title: config.tr('Thiết bị (Tổng)'),
                value: stats.totalDevices.toString(),
                icon: Icons.devices_rounded,
                color: AppColors.primary,
                onTap: () {
                  if (widget.onSelectTab != null) {
                    widget.onSelectTab!(1);
                  } else {
                    Navigator.pushNamed(context, '/devices');
                  }
                },
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: SummaryCard(
                title: config.tr('Đang cho thuê'),
                value: stats.rentedDevices.toString(),
                icon: Icons.outbox_rounded,
                color: AppColors.success,
                onTap: () {
                  if (widget.onSelectTab != null) {
                    widget.onSelectTab!(1);
                  } else {
                    Navigator.pushNamed(context, '/devices');
                  }
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: SummaryCard(
                title: config.tr('Tổng hợp đồng'),
                value: stats.totalContracts.toString(),
                icon: Icons.description_rounded,
                color: AppColors.secondary,
                onTap: () {
                  if (widget.onSelectTab != null) {
                    widget.onSelectTab!(2);
                  } else {
                    Navigator.pushNamed(context, '/contracts');
                  }
                },
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: SummaryCard(
                title: config.tr('Bảo trì (Tồn đọng)'),
                value: stats.maintenanceRequests.toString(),
                icon: Icons.build_circle_rounded,
                color: AppColors.error,
                onTap: () => Navigator.pushNamed(context, '/maintenances'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        SummaryCard(
          title: config.tr('Công việc đang xử lý'),
          value: stats.processingTasks.toString(),
          icon: Icons.sync_rounded,
          color: AppColors.info,
          onTap: () {
            if (widget.onSelectTab != null) {
              widget.onSelectTab!(2);
            } else {
              Navigator.pushNamed(context, '/contracts');
            }
          },
        ),
        const SizedBox(height: 24),
        SectionTitle(title: config.tr('Quản lý vận hành')),
        Wrap(
          spacing: 16,
          runSpacing: 16,
          alignment: WrapAlignment.start,
          children: [
            QuickActionCard(title: config.tr('Việc của tôi'), icon: Icons.assignment_outlined,
              onTap: () => Navigator.pushNamed(context, '/tasks')),
            QuickActionCard(title: config.tr('Thông báo'), icon: Icons.notifications_outlined,
              onTap: () => Navigator.pushNamed(context, '/notifications')),
            QuickActionCard(title: config.tr('Sự cố'), icon: Icons.report_problem_rounded, onTap: () => Navigator.pushNamed(context, '/incidents')),
            QuickActionCard(title: config.tr('Bảo trì'), icon: Icons.build_rounded, onTap: () => Navigator.pushNamed(context, '/maintenances')),
            QuickActionCard(title: config.tr('Phản hồi'), icon: Icons.feedback_rounded, onTap: () => Navigator.pushNamed(context, '/feedbacks')),
            QuickActionCard(title: config.tr('Khuyến mãi'), icon: Icons.local_offer_rounded, onTap: () => Navigator.pushNamed(context, '/promotions')),
          ],
        ),
      ],
    );
  }

  Widget _buildGreeting(String name, AppConfigProvider config) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(config.tr('Xin chào,'), style: AppTextStyles.bodySecondary.copyWith(fontSize: 16)),
        const SizedBox(height: 4),
        Text(name, style: AppTextStyles.h1.copyWith(fontSize: 26, color: AppColors.primary)),
      ],
    );
  }
}
