import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/maintenance_model.dart';
import '../../providers/auth_provider.dart';
import '../../models/permission_enum.dart';
import '../../utils/permission_manager.dart';
import '../../widgets/maintenance_timeline.dart';
import '../../widgets/maintenance_stepper.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';

class MaintenanceDetailScreen extends StatelessWidget {
  final MaintenanceModel maintenance;

  const MaintenanceDetailScreen({super.key, required this.maintenance});

  @override
  Widget build(BuildContext context) {
    final userRole = context.read<AuthProvider>().currentUser?.role;
    final canUpdate = userRole != null && PermissionManager.hasPermission(userRole, AppPermission.viewAssignedMaintenance);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Chi tiết Yêu cầu Bảo trì'),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Yêu cầu: ${maintenance.requestCode ?? 'N/A'}', 
              style: AppTextStyles.h1.copyWith(fontSize: 22),
            ),
            const SizedBox(height: 16),
            
            // Stepper Visual
            MaintenanceStepper(currentStatus: maintenance.status ?? 'Đã gửi'),
            const SizedBox(height: 24),

            _buildSectionCard(
              title: 'Thông tin bảo trì',
              icon: Icons.info_outline_rounded,
              content: Column(
                children: [
                  _buildInfoRow('Thiết bị', maintenance.deviceId ?? 'N/A', isHighlight: true),
                  _buildDivider(),
                  _buildInfoRow('Khách hàng', maintenance.customer ?? 'N/A'),
                  _buildDivider(),
                  _buildInfoRow('Hợp đồng', maintenance.contractId ?? 'N/A'),
                  _buildDivider(),
                  _buildInfoRow('Người phụ trách', maintenance.assignedEmployee?.isEmpty ?? true ? 'Chưa phân công' : maintenance.assignedEmployee!),
                  _buildDivider(),
                  _buildInfoRow('Ngày tạo', maintenance.createdAt ?? 'N/A'),
                  if (maintenance.completedAt != null && maintenance.completedAt!.isNotEmpty) ...[
                    _buildDivider(),
                    _buildInfoRow('Hoàn thành', maintenance.completedAt!, isSuccess: true),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 16),

            _buildSectionCard(
              title: 'Mô tả sự cố',
              icon: Icons.error_outline_rounded,
              content: Text(
                maintenance.description ?? 'N/A', 
                style: AppTextStyles.body.copyWith(height: 1.5),
              ),
            ),

            if (maintenance.result != null && maintenance.result!.isNotEmpty) ...[
              const SizedBox(height: 16),
              _buildSectionCard(
                title: 'Kết quả xử lý',
                icon: Icons.check_circle_outline_rounded,
                content: Text(
                  maintenance.result!, 
                  style: AppTextStyles.body.copyWith(height: 1.5, color: AppColors.success),
                ),
              ),
            ],

            const SizedBox(height: 16),
            _buildSectionCard(
              title: 'Tiến trình thực hiện',
              icon: Icons.history_rounded,
              content: MaintenanceTimeline(notes: maintenance.notes),
            ),

            const SizedBox(height: 40),
          ],
        ),
      ),
      bottomNavigationBar: canUpdate && maintenance.status != 'Hoàn thành'
          ? SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: CustomButton(
                  text: 'Cập nhật trạng thái',
                  onPressed: () {
                    Navigator.pushNamed(context, '/maintenance_update', arguments: maintenance);
                  },
                  isFullWidth: true,
                  type: ButtonType.primary,
                ),
              ),
            )
          : null,
    );
  }

  Widget _buildSectionCard({required String title, required IconData icon, required Widget content}) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: AppRadius.lgRadius,
        boxShadow: AppShadows.cardShadow,
        border: Border.all(color: AppColors.divider),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 20, color: AppColors.primary),
              const SizedBox(width: 8),
              Text(title, style: AppTextStyles.h2),
            ],
          ),
          const SizedBox(height: 16),
          content,
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value, {bool isHighlight = false, bool isSuccess = false}) {
    Color valColor = AppColors.textPrimary;
    if (isHighlight) valColor = AppColors.primary;
    if (isSuccess) valColor = AppColors.success;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 110,
            child: Text(label, style: AppTextStyles.bodySecondary),
          ),
          Expanded(
            child: Text(
              value,
              style: AppTextStyles.body.copyWith(
                fontWeight: (isHighlight || isSuccess) ? FontWeight.bold : FontWeight.w500,
                color: valColor,
              ),
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDivider() {
    return const Padding(
      padding: EdgeInsets.symmetric(vertical: 8),
      child: Divider(color: AppColors.divider, height: 1),
    );
  }
}
