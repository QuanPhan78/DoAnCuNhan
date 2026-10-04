import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';
import '../../widgets/core/custom_button.dart';
import '../../widgets/dashboard_widgets.dart';

class AccountScreen extends StatelessWidget {
  const AccountScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final user = context.watch<AuthProvider>().currentUser;
    if (user == null) return const SizedBox();

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            const SizedBox(height: 24),
            // Avatar
            Center(
              child: Container(
                width: 100, height: 100,
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                  border: Border.all(color: AppColors.primary.withValues(alpha: 0.2), width: 2),
                ),
                child: const Icon(Icons.person_rounded, size: 48, color: AppColors.primary),
              ),
            ),
            const SizedBox(height: 16),
            Text(user.name, style: AppTextStyles.h1.copyWith(fontSize: 24)),
            const SizedBox(height: 4),
            Text(user.email, style: AppTextStyles.bodySecondary),
            const SizedBox(height: 12),
            StatusBadge(
              text: 'Vai trò: ${user.role.name.toUpperCase()}', 
              status: BadgeStatus.processing,
            ),
            const SizedBox(height: 32),

            // Info Card
            Container(
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: AppRadius.lgRadius,
                boxShadow: AppShadows.cardShadow,
                border: Border.all(color: AppColors.divider),
              ),
              child: Column(
                children: [
                  _buildListTile(Icons.info_outline_rounded, 'Thông tin cá nhân', () {}),
                  const Divider(color: AppColors.divider, height: 1),
                  _buildListTile(Icons.settings_outlined, 'Cài đặt hệ thống', () {}),
                  const Divider(color: AppColors.divider, height: 1),
                  _buildListTile(Icons.security_outlined, 'Bảo mật & Phân quyền', () {}),
                ],
              ),
            ),
            
            const SizedBox(height: 24),
            
            // System Testing
            if (user.role.name == 'admin')
              CustomButton(
                text: 'Test truy cập Báo Cáo',
                icon: Icons.analytics_outlined,
                type: ButtonType.secondary,
                isFullWidth: true,
                onPressed: () {
                  Navigator.of(context).pushNamed('/admin/reports');
                },
              ),
              
            const SizedBox(height: 24),

            // Logout
            CustomButton(
              text: 'Đăng xuất',
              icon: Icons.logout_rounded,
              type: ButtonType.destructive,
              isFullWidth: true,
              onPressed: () async {
                await context.read<AuthProvider>().logout();
                if (context.mounted) {
                  Navigator.of(context).pushNamedAndRemoveUntil('/login', (route) => false);
                }
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildListTile(IconData icon, String title, VoidCallback onTap) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(color: AppColors.primary.withValues(alpha: 0.1), borderRadius: AppRadius.smRadius),
        child: Icon(icon, color: AppColors.primary, size: 20),
      ),
      title: Text(title, style: AppTextStyles.body.copyWith(fontWeight: FontWeight.w600)),
      trailing: const Icon(Icons.chevron_right_rounded, color: AppColors.textSecondary),
      onTap: onTap,
    );
  }
}
