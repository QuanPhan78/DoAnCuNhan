import '../../models/role_enum.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/app_config_provider.dart';
import '../../providers/auth_provider.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';
import '../../widgets/core/custom_button.dart';
import '../../widgets/dashboard_widgets.dart';
import 'profile_detail_screen.dart';
import 'settings_screen.dart';
import 'security_permissions_screen.dart';

class AccountScreen extends StatelessWidget {
  const AccountScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final user = context.watch<AuthProvider>().currentUser;
    final config = context.watch<AppConfigProvider>();
    final isDark = Theme.of(context).brightness == Brightness.dark;

    if (user == null) return const SizedBox();

    return Scaffold(
      backgroundColor: isDark ? AppColors.darkBackground : AppColors.background,
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
            Text(
              user.name, 
              style: AppTextStyles.h1.copyWith(
                fontSize: 24,
                color: isDark ? AppColors.darkTextPrimary : AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              user.email, 
              style: AppTextStyles.bodySecondary.copyWith(
                color: isDark ? AppColors.darkTextSecondary : AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 12),
            StatusBadge(
              text: '${config.tr('Vai trò:')} ${user.role.displayName}', 
              status: BadgeStatus.processing,
            ),
            const SizedBox(height: 32),

            // Info Card
            Container(
              decoration: BoxDecoration(
                color: isDark ? AppColors.darkSurface : AppColors.surface,
                borderRadius: AppRadius.lgRadius,
                boxShadow: isDark ? [] : AppShadows.cardShadow,
                border: Border.all(color: isDark ? AppColors.darkDivider : AppColors.divider),
              ),
              child: Material(
                color: Colors.transparent,
                child: Column(
                  children: [
                    _buildListTile(
                      Icons.info_outline_rounded,
                      config.tr('Thông tin cá nhân'),
                      () => Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => const ProfileDetailScreen()),
                      ),
                      isDark,
                    ),
                    Divider(color: isDark ? AppColors.darkDivider : AppColors.divider, height: 1),
                    _buildListTile(
                      Icons.settings_outlined,
                      config.tr('Cài đặt hệ thống'),
                      () => Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => const SettingsScreen()),
                      ),
                      isDark,
                    ),
                    Divider(color: isDark ? AppColors.darkDivider : AppColors.divider, height: 1),
                    _buildListTile(
                      Icons.security_outlined,
                      config.tr('Bảo mật & Phân quyền'),
                      () => Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => const SecurityPermissionsScreen()),
                      ),
                      isDark,
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 24),
            
            // System Testing
            if (user.role.name == 'admin')
              CustomButton(
                text: config.tr('Test truy cập Báo Cáo'),
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
              text: config.tr('Đăng xuất'),
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

  Widget _buildListTile(IconData icon, String title, VoidCallback onTap, bool isDark) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(color: AppColors.primary.withValues(alpha: 0.1), borderRadius: AppRadius.smRadius),
        child: Icon(icon, color: AppColors.primary, size: 20),
      ),
      title: Text(
        title, 
        style: AppTextStyles.body.copyWith(
          fontWeight: FontWeight.w600,
          color: isDark ? AppColors.darkTextPrimary : AppColors.textPrimary,
        ),
      ),
      trailing: Icon(Icons.chevron_right_rounded, color: isDark ? AppColors.darkTextSecondary : AppColors.textSecondary),
      onTap: onTap,
    );
  }
}
