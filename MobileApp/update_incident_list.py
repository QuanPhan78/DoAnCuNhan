import os

code = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/contract_provider.dart';
import '../../providers/incident_provider.dart';
import '../../models/permission_enum.dart';
import '../../utils/permission_manager.dart';
import '../../widgets/core/state_widgets.dart';
import '../../widgets/dashboard_widgets.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';

class IncidentListScreen extends StatefulWidget {
  const IncidentListScreen({super.key});

  @override
  State<IncidentListScreen> createState() => _IncidentListScreenState();
}

class _IncidentListScreenState extends State<IncidentListScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  void _loadData() {
    final auth = context.read<AuthProvider>();
    if (auth.currentUser != null) {
      context.read<IncidentProvider>().fetchIncidents(
        auth.currentUser!.id, 
        auth.currentUser!.role, 
        context.read<ContractProvider>()
      );
    }
  }

  BadgeStatus _getBadgeStatus(String status) {
    switch (status.toLowerCase()) {
      case 'đã hoàn thành':
        return BadgeStatus.success;
      case 'đang xử lý':
        return BadgeStatus.processing;
      case 'chờ xử lý':
        return BadgeStatus.warning;
      default:
        return BadgeStatus.neutral;
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<IncidentProvider>();
    final userRole = context.read<AuthProvider>().currentUser?.role;
    final canReport = userRole != null && PermissionManager.hasPermission(userRole, AppPermission.reportIssue);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Yêu cầu & Sự cố'),
        actions: [
          if (canReport)
            Padding(
              padding: const EdgeInsets.only(right: 8.0),
              child: IconButton(
                icon: const Icon(Icons.add_rounded, size: 28),
                color: AppColors.primary,
                onPressed: () async {
                  final result = await Navigator.pushNamed(context, '/create_incident');
                  if (result == true) {
                    _loadData();
                  }
                },
              ),
            )
        ],
      ),
      body: _buildListContent(provider),
    );
  }

  Widget _buildListContent(IncidentProvider provider) {
    if (provider.isLoading && provider.incidents.isEmpty) {
      return const LoadingState(message: 'Đang tải danh sách sự cố...');
    }

    if (provider.errorMessage != null) {
      return ErrorState(
        message: 'Đã xảy ra lỗi: ${provider.errorMessage}',
        onRetry: _loadData,
      );
    }

    if (provider.incidents.isEmpty) {
      return const EmptyState(
        message: 'Chưa có yêu cầu sự cố nào.',
        icon: Icons.report_gmailerrorred_rounded,
      );
    }

    return RefreshIndicator(
      color: AppColors.primary,
      onRefresh: () async => _loadData(),
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        physics: const AlwaysScrollableScrollPhysics(),
        itemCount: provider.incidents.length,
        itemBuilder: (context, index) {
          final inc = provider.incidents[index];
          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: AppRadius.lgRadius,
              boxShadow: AppShadows.cardShadow,
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: () {
                  Navigator.pushNamed(context, '/incident_detail', arguments: inc);
                },
                borderRadius: AppRadius.lgRadius,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Text(
                              '${inc.code} - ${inc.issueType}', 
                              style: AppTextStyles.subtitle.copyWith(fontSize: 16),
                              maxLines: 1, overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          StatusBadge(
                            text: inc.status,
                            status: _getBadgeStatus(inc.status),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          const Icon(Icons.devices_rounded, size: 16, color: AppColors.textSecondary),
                          const SizedBox(width: 8),
                          Text('Thiết bị: ${inc.deviceId}', style: AppTextStyles.body),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          const Icon(Icons.assignment_outlined, size: 16, color: AppColors.textSecondary),
                          const SizedBox(width: 8),
                          Text('Hợp đồng: ${inc.contractId}', style: AppTextStyles.bodySecondary),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text(
                        inc.createdAt, 
                        style: AppTextStyles.bodySecondary.copyWith(fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
"""

with open("lib/screens/incidents/incident_list_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)

print("IncidentListScreen Updated.")