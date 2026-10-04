import os

code = """import 'package:flutter/material.dart';
import '../models/maintenance_model.dart';
import 'dashboard_widgets.dart'; // For StatusBadge, BadgeStatus
import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';
import '../theme/app_radius.dart';
import '../theme/app_shadows.dart';

class MaintenanceCard extends StatelessWidget {
  final MaintenanceModel maintenance;
  final VoidCallback onTap;

  const MaintenanceCard({super.key, required this.maintenance, required this.onTap});

  BadgeStatus _getBadgeStatus(String status) {
    status = status.toLowerCase();
    if (status.contains('hoàn thành')) return BadgeStatus.success;
    if (status.contains('đang xử lý')) return BadgeStatus.processing;
    if (status.contains('tiếp nhận') || status.contains('phân công')) return BadgeStatus.info;
    return BadgeStatus.warning;
  }

  @override
  Widget build(BuildContext context) {
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
          onTap: onTap,
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
                        'Mã: ${maintenance.requestCode ?? 'N/A'}',
                        style: AppTextStyles.h2.copyWith(fontSize: 16),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    StatusBadge(
                      text: maintenance.status ?? 'N/A',
                      status: _getBadgeStatus(maintenance.status ?? ''),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                _buildInfoRow(Icons.devices_rounded, 'Thiết bị', maintenance.deviceId ?? 'N/A'),
                const SizedBox(height: 4),
                _buildInfoRow(Icons.error_outline_rounded, 'Nội dung', maintenance.description ?? 'N/A'),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Row(
                        children: [
                          const Icon(Icons.person_outline_rounded, size: 16, color: AppColors.textSecondary),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              'Phụ trách: ${maintenance.assignedEmployee?.isEmpty ?? true ? 'Chưa có' : maintenance.assignedEmployee}',
                              style: AppTextStyles.bodySecondary.copyWith(fontSize: 13),
                              maxLines: 1, overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: AppColors.textSecondary),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 16, color: AppColors.textSecondary),
        const SizedBox(width: 8),
        Expanded(
          child: RichText(
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            text: TextSpan(
              style: AppTextStyles.body.copyWith(fontSize: 14),
              children: [
                TextSpan(text: '$label: ', style: const TextStyle(color: AppColors.textSecondary)),
                TextSpan(text: value, style: const TextStyle(fontWeight: FontWeight.w500)),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
"""

with open("lib/widgets/maintenance_card.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("MaintenanceCard Updated.")