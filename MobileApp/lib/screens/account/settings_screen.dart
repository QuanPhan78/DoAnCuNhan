import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/app_config_provider.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';
import '../../widgets/core/custom_app_bar.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _pushNotifications = true;
  bool _emailNotifications = true;
  bool _soundEnabled = true;

  @override
  Widget build(BuildContext context) {
    final config = context.watch<AppConfigProvider>();
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: isDark ? AppColors.darkBackground : AppColors.background,
      appBar: CustomAppBar(title: config.tr('Cài đặt hệ thống')),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          // Mục 1: Thông báo
          _buildSectionHeader(config.tr('Thông báo')),
          _buildCardContainer([
            SwitchListTile(
              title: Text(config.tr('Thông báo đẩy'), style: AppTextStyles.body.copyWith(color: isDark ? AppColors.darkTextPrimary : AppColors.textPrimary)),
              subtitle: Text(config.tr('Nhận tin báo hợp đồng và thiết bị'), style: AppTextStyles.caption.copyWith(color: isDark ? AppColors.darkTextSecondary : AppColors.textSecondary)),
              secondary: const Icon(Icons.notifications_active_outlined, color: AppColors.primary),
              value: _pushNotifications,
              activeTrackColor: AppColors.primary,
              onChanged: (val) => setState(() => _pushNotifications = val),
            ),
            Divider(height: 1, color: isDark ? AppColors.darkDivider : AppColors.divider),
            SwitchListTile(
              title: Text(config.tr('Thông báo qua Email'), style: AppTextStyles.body.copyWith(color: isDark ? AppColors.darkTextPrimary : AppColors.textPrimary)),
              subtitle: Text(config.tr('Nhận bản sao hợp đồng và hóa đơn'), style: AppTextStyles.caption.copyWith(color: isDark ? AppColors.darkTextSecondary : AppColors.textSecondary)),
              secondary: const Icon(Icons.mark_email_unread_outlined, color: AppColors.primary),
              value: _emailNotifications,
              activeTrackColor: AppColors.primary,
              onChanged: (val) => setState(() => _emailNotifications = val),
            ),
            Divider(height: 1, color: isDark ? AppColors.darkDivider : AppColors.divider),
            SwitchListTile(
              title: Text(config.tr('Âm thanh thông báo'), style: AppTextStyles.body.copyWith(color: isDark ? AppColors.darkTextPrimary : AppColors.textPrimary)),
              secondary: const Icon(Icons.volume_up_outlined, color: AppColors.primary),
              value: _soundEnabled,
              activeTrackColor: AppColors.primary,
              onChanged: (val) => setState(() => _soundEnabled = val),
            ),
          ], isDark),
          const SizedBox(height: 24),

          // Mục 2: Ngôn ngữ & Giao diện
          _buildSectionHeader(config.tr('Giao diện & Ngôn ngữ')),
          _buildCardContainer([
            ListTile(
              leading: const Icon(Icons.language_rounded, color: AppColors.primary),
              title: Text(config.tr('Ngôn ngữ'), style: AppTextStyles.body.copyWith(color: isDark ? AppColors.darkTextPrimary : AppColors.textPrimary)),
              subtitle: Text('${config.languageName} (${config.tr("Đang chọn")})', style: AppTextStyles.caption.copyWith(color: isDark ? AppColors.darkTextSecondary : AppColors.textSecondary)),
              trailing: Icon(Icons.chevron_right_rounded, color: isDark ? AppColors.darkTextSecondary : AppColors.textSecondary),
              onTap: () => _showLanguageDialog(config, isDark),
            ),
            Divider(height: 1, color: isDark ? AppColors.darkDivider : AppColors.divider),
            ListTile(
              leading: const Icon(Icons.dark_mode_outlined, color: AppColors.primary),
              title: Text(config.tr('Chế độ hiển thị'), style: AppTextStyles.body.copyWith(color: isDark ? AppColors.darkTextPrimary : AppColors.textPrimary)),
              subtitle: Text('${config.themeName} (${config.tr("Đang chọn")})', style: AppTextStyles.caption.copyWith(color: isDark ? AppColors.darkTextSecondary : AppColors.textSecondary)),
              trailing: Icon(Icons.chevron_right_rounded, color: isDark ? AppColors.darkTextSecondary : AppColors.textSecondary),
              onTap: () => _showThemeDialog(config, isDark),
            ),
          ], isDark),
          const SizedBox(height: 24),

          // Mục 3: Dữ liệu & Ứng dụng
          _buildSectionHeader(config.tr('Dữ liệu & Ứng dụng')),
          _buildCardContainer([
            ListTile(
              leading: const Icon(Icons.info_outline_rounded, color: AppColors.primary),
              title: Text(config.tr('Phiên bản ứng dụng'), style: AppTextStyles.body.copyWith(color: isDark ? AppColors.darkTextPrimary : AppColors.textPrimary)),
              subtitle: Text('v1.0.0 (Build 2026)', style: TextStyle(color: isDark ? AppColors.darkTextSecondary : const Color(0xFF64748B), fontSize: 12)),
              trailing: Text(
                config.tr('Mới nhất'),
                style: const TextStyle(color: AppColors.success, fontWeight: FontWeight.bold, fontSize: 13),
              ),
            ),
          ], isDark),
        ],
      ),
    );
  }

  void _showLanguageDialog(AppConfigProvider config, bool isDark) {
    showDialog(
      context: context,
      builder: (ctx) {
        return AlertDialog(
          backgroundColor: isDark ? AppColors.darkSurface : AppColors.surface,
          title: Text(config.tr('Chọn ngôn ngữ'), style: TextStyle(color: isDark ? AppColors.darkTextPrimary : AppColors.textPrimary)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.flag_rounded, color: AppColors.primary),
                title: Text('Tiếng Việt', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: isDark ? AppColors.darkTextPrimary : AppColors.textPrimary)),
                subtitle: Text(config.tr('Mặc định'), style: TextStyle(fontSize: 12, color: isDark ? AppColors.darkTextSecondary : AppColors.textSecondary)),
                trailing: config.language == 'vi'
                    ? const Icon(Icons.check_circle_rounded, color: AppColors.primary)
                    : null,
                onTap: () {
                  config.setLanguage('vi');
                  Navigator.pop(ctx);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(config.isEnglish ? 'Language selected: Vietnamese' : 'Đã chọn ngôn ngữ: Tiếng Việt'),
                      backgroundColor: AppColors.success,
                    ),
                  );
                },
              ),
              Divider(height: 1, color: isDark ? AppColors.darkDivider : AppColors.divider),
              ListTile(
                leading: const Icon(Icons.language_rounded, color: AppColors.primary),
                title: Text('English', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: isDark ? AppColors.darkTextPrimary : AppColors.textPrimary)),
                subtitle: Text('Tiếng Anh', style: TextStyle(fontSize: 12, color: isDark ? AppColors.darkTextSecondary : AppColors.textSecondary)),
                trailing: config.language == 'en'
                    ? const Icon(Icons.check_circle_rounded, color: AppColors.primary)
                    : null,
                onTap: () {
                  config.setLanguage('en');
                  Navigator.pop(ctx);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Language switched to: English'),
                      backgroundColor: AppColors.success,
                    ),
                  );
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: Text(config.tr('Đóng')),
            ),
          ],
        );
      },
    );
  }

  void _showThemeDialog(AppConfigProvider config, bool isDark) {
    showDialog(
      context: context,
      builder: (ctx) {
        return AlertDialog(
          backgroundColor: isDark ? AppColors.darkSurface : AppColors.surface,
          title: Text(config.tr('Chọn chế độ hiển thị'), style: TextStyle(color: isDark ? AppColors.darkTextPrimary : AppColors.textPrimary)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.light_mode_outlined, color: AppColors.primary),
                title: Text(config.tr('Giao diện Sáng'), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: isDark ? AppColors.darkTextPrimary : AppColors.textPrimary)),
                subtitle: Text(config.tr('Mặc định'), style: TextStyle(fontSize: 12, color: isDark ? AppColors.darkTextSecondary : AppColors.textSecondary)),
                trailing: config.themeMode == ThemeMode.light
                    ? const Icon(Icons.check_circle_rounded, color: AppColors.primary)
                    : null,
                onTap: () {
                  config.setThemeMode(ThemeMode.light);
                  Navigator.pop(ctx);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(config.isEnglish ? 'Switched to Light Mode' : 'Đã chuyển sang: Giao diện Sáng'),
                      backgroundColor: AppColors.success,
                    ),
                  );
                },
              ),
              Divider(height: 1, color: isDark ? AppColors.darkDivider : AppColors.divider),
              ListTile(
                leading: const Icon(Icons.dark_mode_outlined, color: AppColors.primary),
                title: Text(config.tr('Giao diện Tối'), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: isDark ? AppColors.darkTextPrimary : AppColors.textPrimary)),
                subtitle: Text('Dark Mode', style: TextStyle(fontSize: 12, color: isDark ? AppColors.darkTextSecondary : AppColors.textSecondary)),
                trailing: config.themeMode == ThemeMode.dark
                    ? const Icon(Icons.check_circle_rounded, color: AppColors.primary)
                    : null,
                onTap: () {
                  config.setThemeMode(ThemeMode.dark);
                  Navigator.pop(ctx);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(config.isEnglish ? 'Switched to Dark Mode' : 'Đã chuyển sang: Giao diện Tối'),
                      backgroundColor: AppColors.success,
                    ),
                  );
                },
              ),
              Divider(height: 1, color: isDark ? AppColors.darkDivider : AppColors.divider),
              ListTile(
                leading: const Icon(Icons.settings_brightness_outlined, color: AppColors.primary),
                title: Text(config.tr('Theo hệ thống'), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: isDark ? AppColors.darkTextPrimary : AppColors.textPrimary)),
                subtitle: Text('Auto', style: TextStyle(fontSize: 12, color: isDark ? AppColors.darkTextSecondary : AppColors.textSecondary)),
                trailing: config.themeMode == ThemeMode.system
                    ? const Icon(Icons.check_circle_rounded, color: AppColors.primary)
                    : null,
                onTap: () {
                  config.setThemeMode(ThemeMode.system);
                  Navigator.pop(ctx);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(config.isEnglish ? 'Set to System Default' : 'Đã chọn: Theo hệ thống'),
                      backgroundColor: AppColors.success,
                    ),
                  );
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: Text(config.tr('Đóng')),
            ),
          ],
        );
      },
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 4, bottom: 8),
      child: Text(
        title,
        style: AppTextStyles.h2.copyWith(fontSize: 16, color: AppColors.primary),
      ),
    );
  }

  Widget _buildCardContainer(List<Widget> children, bool isDark) {
    return Container(
      decoration: BoxDecoration(
        color: isDark ? AppColors.darkSurface : AppColors.surface,
        borderRadius: AppRadius.lgRadius,
        boxShadow: isDark ? [] : AppShadows.cardShadow,
        border: Border.all(color: isDark ? AppColors.darkDivider : AppColors.divider),
      ),
      child: Material(
        color: Colors.transparent,
        child: Column(children: children),
      ),
    );
  }
}
