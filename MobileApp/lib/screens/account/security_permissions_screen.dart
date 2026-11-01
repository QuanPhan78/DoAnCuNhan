import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../models/permission_enum.dart';
import '../../utils/permission_manager.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/dashboard_widgets.dart';

class SecurityPermissionsScreen extends StatefulWidget {
  const SecurityPermissionsScreen({super.key});

  @override
  State<SecurityPermissionsScreen> createState() => _SecurityPermissionsScreenState();
}

class _SecurityPermissionsScreenState extends State<SecurityPermissionsScreen> {
  String _getPermissionTitle(AppPermission permission) {
    switch (permission) {
      case AppPermission.viewDevices:
        return 'Xem danh sách thiết bị cho thuê';
      case AppPermission.viewOwnContracts:
        return 'Xem danh sách hợp đồng của tôi';
      case AppPermission.viewRentalHistory:
        return 'Xem lịch sử thuê thiết bị';
      case AppPermission.requestExtension:
        return 'Yêu cầu gia hạn hợp đồng';
      case AppPermission.reportIssue:
        return 'Gửi báo cáo sự cố & hư hỏng';
      case AppPermission.trackMaintenance:
        return 'Theo dõi tiến độ bảo trì';
      case AppPermission.submitFeedback:
        return 'Gửi đánh giá và phản hồi';
      case AppPermission.viewPromotions:
        return 'Xem các chương trình ưu đãi';
      case AppPermission.viewAssignedTasks:
        return 'Xem công việc được phân công';
      case AppPermission.viewAssignedMaintenance:
        return 'Xem danh sách bảo trì được giao';
      case AppPermission.updateTaskStatus:
        return 'Cập nhật tiến độ lắp đặt & bảo trì';
      case AppPermission.manageDevices:
        return 'Quản lý toàn bộ thiết bị';
      case AppPermission.manageContracts:
        return 'Quản trị danh sách hợp đồng';
      case AppPermission.manageMaintenance:
        return 'Quản lý và điều phối bảo trì';
      case AppPermission.viewReports:
        return 'Xem báo cáo thống kê doanh thu';
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = context.watch<AuthProvider>().currentUser;
    if (user == null) {
      return const Scaffold(
        appBar: CustomAppBar(title: 'Bảo mật & Phân quyền'),
        body: Center(child: Text('Không tìm thấy thông tin tài khoản.')),
      );
    }

    final permissions = PermissionManager.getPermissionsForRole(user.role);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Bảo mật & Phân quyền'),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          // Mục 1: Bảo mật tài khoản
          _buildSectionHeader('Bảo mật tài khoản'),
          Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: AppRadius.lgRadius,
              boxShadow: AppShadows.cardShadow,
              border: Border.all(color: AppColors.divider),
            ),
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.lock_reset_rounded, color: AppColors.primary),
                  title: const Text('Đổi mật khẩu', style: AppTextStyles.body),
                  subtitle: const Text('Cập nhật mật khẩu định kỳ để bảo vệ tài khoản', style: AppTextStyles.caption),
                  trailing: const Icon(Icons.chevron_right_rounded, color: AppColors.textSecondary),
                  onTap: () => _showChangePasswordDialog(context),
                ),
                const Divider(height: 1, color: AppColors.divider),
                ListTile(
                  leading: const Icon(Icons.verified_user_outlined, color: AppColors.primary),
                  title: const Text('Xác thực 2 yếu tố (2FA)', style: AppTextStyles.body),
                  subtitle: const Text('Chưa kích hoạt', style: AppTextStyles.caption),
                  trailing: TextButton(
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Tính năng 2FA đang trong quá trình phát triển.')),
                      );
                    },
                    child: const Text('Kích hoạt'),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 28),

          // Mục 2: Phân quyền vai trò
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildSectionHeader('Quyền hạn của bạn'),
              StatusBadge(
                text: user.role.name.toUpperCase(),
                status: BadgeStatus.processing,
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Hệ thống cấp các quyền sau đây dựa trên vai trò của tài khoản:',
            style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
          ),
          const SizedBox(height: 12),

          Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: AppRadius.lgRadius,
              boxShadow: AppShadows.cardShadow,
              border: Border.all(color: AppColors.divider),
            ),
            child: Column(
              children: permissions.asMap().entries.map((entry) {
                final idx = entry.key;
                final perm = entry.value;
                return Column(
                  children: [
                    if (idx > 0) const Divider(height: 1, color: AppColors.divider),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                      child: Row(
                        children: [
                          const Icon(Icons.check_circle_rounded, color: AppColors.success, size: 20),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              _getPermissionTitle(perm),
                              style: AppTextStyles.body.copyWith(fontSize: 14),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Text(
      title,
      style: AppTextStyles.h2.copyWith(fontSize: 16, color: AppColors.primary),
    );
  }

  void _showChangePasswordDialog(BuildContext context) {
    final oldPassController = TextEditingController();
    final newPassController = TextEditingController();
    final confirmPassController = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Đổi mật khẩu'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: oldPassController,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Mật khẩu hiện tại',
                  prefixIcon: Icon(Icons.lock_outline),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: newPassController,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Mật khẩu mới',
                  prefixIcon: Icon(Icons.lock_reset),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: confirmPassController,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Xác nhận mật khẩu mới',
                  prefixIcon: Icon(Icons.check_circle_outline),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Hủy'),
          ),
          ElevatedButton(
            onPressed: () {
              if (newPassController.text.isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Vui lòng nhập mật khẩu mới!')),
                );
                return;
              }
              if (newPassController.text != confirmPassController.text) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Mật khẩu xác nhận không khớp!')),
                );
                return;
              }
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: const Text('Đổi mật khẩu thành công!'),
                  backgroundColor: AppColors.success,
                ),
              );
            },
            child: const Text('Cập nhật'),
          ),
        ],
      ),
    );
  }
}
