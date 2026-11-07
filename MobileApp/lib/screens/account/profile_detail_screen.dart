import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';
import '../../widgets/dashboard_widgets.dart';

class ProfileDetailScreen extends StatefulWidget {
  const ProfileDetailScreen({super.key});

  @override
  State<ProfileDetailScreen> createState() => _ProfileDetailScreenState();
}

class _ProfileDetailScreenState extends State<ProfileDetailScreen> {
  @override
  Widget build(BuildContext context) {
    final user = context.watch<AuthProvider>().currentUser;
    if (user == null) {
      return const Scaffold(
        appBar: CustomAppBar(title: 'Thông tin cá nhân'),
        body: Center(child: Text('Không tìm thấy thông tin người dùng.')),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Thông tin cá nhân'),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            // Avatar Header
            Center(
              child: Stack(
                children: [
                  Container(
                    width: 104,
                    height: 104,
                    decoration: BoxDecoration(
                      color: AppColors.primary.withValues(alpha: 0.1),
                      shape: BoxShape.circle,
                      border: Border.all(color: AppColors.primary.withValues(alpha: 0.3), width: 3),
                    ),
                    child: const Icon(Icons.person_rounded, size: 54, color: AppColors.primary),
                  ),
                  Positioned(
                    bottom: 0,
                    right: 0,
                    child: Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: AppColors.primary,
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 2),
                      ),
                      child: const Icon(Icons.camera_alt_rounded, size: 16, color: Colors.white),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Text(user.name, style: AppTextStyles.h1.copyWith(fontSize: 22)),
            const SizedBox(height: 4),
            StatusBadge(
              text: 'VAI TRÒ: ${user.role.name.toUpperCase()}',
              status: BadgeStatus.processing,
            ),
            const SizedBox(height: 28),

            // Card chi tiết thông tin
            Container(
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: AppRadius.lgRadius,
                boxShadow: AppShadows.cardShadow,
                border: Border.all(color: AppColors.divider),
              ),
              child: Column(
                children: [
                  _buildDetailRow(
                    icon: Icons.badge_outlined,
                    label: 'Mã người dùng',
                    value: '#USR-${user.id.padLeft(4, '0')}',
                  ),
                  const Divider(height: 1, color: AppColors.divider),
                  _buildDetailRow(
                    icon: Icons.person_outline_rounded,
                    label: 'Họ và tên',
                    value: user.name,
                  ),
                  const Divider(height: 1, color: AppColors.divider),
                  _buildDetailRow(
                    icon: Icons.email_outlined,
                    label: 'Email',
                    value: user.email,
                  ),
                  const Divider(height: 1, color: AppColors.divider),
                  _buildDetailRow(
                    icon: Icons.phone_outlined,
                    label: 'Số điện thoại',
                    value: user.phone?.isNotEmpty == true ? user.phone! : 'Chưa cập nhật',
                  ),
                  const Divider(height: 1, color: AppColors.divider),
                  _buildDetailRow(
                    icon: Icons.location_on_outlined,
                    label: 'Địa chỉ',
                    value: user.address?.isNotEmpty == true ? user.address! : 'Chưa cập nhật',
                  ),
                  const Divider(height: 1, color: AppColors.divider),
                  _buildDetailRow(
                    icon: Icons.credit_card_outlined,
                    label: 'Số CCCD',
                    value: user.cccd?.isNotEmpty == true ? user.cccd! : 'Chưa cập nhật',
                  ),
                  const Divider(height: 1, color: AppColors.divider),
                  _buildDetailRow(
                    icon: Icons.work_outline_rounded,
                    label: 'Vai trò tài khoản',
                    value: user.role.name.toUpperCase(),
                  ),
                  const Divider(height: 1, color: AppColors.divider),
                  _buildDetailRow(
                    icon: Icons.check_circle_outline_rounded,
                    label: 'Trạng thái hoạt động',
                    value: 'Đang hoạt động',
                    valueColor: AppColors.success,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 28),

            // Nút hành động
            CustomButton(
              text: 'Chỉnh sửa thông tin',
              icon: Icons.edit_outlined,
              type: ButtonType.primary,
              isFullWidth: true,
              onPressed: () {
                _showEditDialog(context, user);
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow({
    required IconData icon,
    required String label,
    required String value,
    Color? valueColor,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      child: Row(
        children: [
          Icon(icon, size: 22, color: AppColors.textSecondary),
          const SizedBox(width: 14),
          Text(label, style: AppTextStyles.bodySecondary),
          const Spacer(),
          Text(
            value,
            style: AppTextStyles.body.copyWith(
              fontWeight: FontWeight.w600,
              color: valueColor ?? AppColors.textPrimary,
            ),
          ),
        ],
      ),
    );
  }

  void _showEditDialog(BuildContext context, dynamic user) {
    final nameController = TextEditingController(text: user.name);
    final phoneController = TextEditingController(text: user.phone ?? '');
    final addressController = TextEditingController(text: user.address ?? '');
    final cccdController = TextEditingController(text: user.cccd ?? '');
    bool isSaving = false;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Sửa hồ sơ'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(
                    labelText: 'Họ và tên',
                    prefixIcon: Icon(Icons.person_outline),
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: phoneController,
                  keyboardType: TextInputType.phone,
                  decoration: const InputDecoration(
                    labelText: 'Số điện thoại',
                    prefixIcon: Icon(Icons.phone_outlined),
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: addressController,
                  decoration: const InputDecoration(
                    labelText: 'Địa chỉ',
                    prefixIcon: Icon(Icons.location_on_outlined),
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: cccdController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Số CCCD',
                    prefixIcon: Icon(Icons.credit_card_outlined),
                    border: OutlineInputBorder(),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: isSaving ? null : () => Navigator.pop(ctx),
              child: const Text('Hủy'),
            ),
            ElevatedButton(
              onPressed: isSaving
                  ? null
                  : () async {
                      setDialogState(() => isSaving = true);
                      final success = await context.read<AuthProvider>().updateProfile(
                            name: nameController.text.trim(),
                            phone: phoneController.text.trim(),
                            address: addressController.text.trim(),
                            cccd: cccdController.text.trim(),
                          );
                      if (ctx.mounted) {
                        Navigator.pop(ctx);
                      }
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(
                              success
                                  ? 'Cập nhật thông tin thành công!'
                                  : 'Cập nhật thất bại. Vui lòng thử lại.',
                            ),
                            backgroundColor: success ? AppColors.success : AppColors.error,
                          ),
                        );
                      }
                    },
              child: isSaving
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Lưu'),
            ),
          ],
        ),
      ),
    );
  }
}
