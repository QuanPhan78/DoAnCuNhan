import os

code = """import 'package:flutter/material.dart';
import '../../models/incident_model.dart';
import '../../widgets/custom_image_widget.dart';
import '../../widgets/dashboard_widgets.dart'; // StatusBadge, BadgeStatus
import '../../widgets/core/custom_app_bar.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';

class IncidentDetailScreen extends StatelessWidget {
  final IncidentModel incident;

  const IncidentDetailScreen({super.key, required this.incident});

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
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Chi tiết Yêu cầu Hỗ trợ'),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    incident.code, 
                    style: AppTextStyles.h1.copyWith(fontSize: 24),
                  ),
                ),
                StatusBadge(
                  text: incident.status,
                  status: _getBadgeStatus(incident.status),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Thông tin chung
            _buildSectionCard(
              title: 'Thông tin chung',
              icon: Icons.info_outline_rounded,
              content: Column(
                children: [
                  _buildInfoRow('Thiết bị', incident.deviceId, isHighlight: true),
                  _buildDivider(),
                  _buildInfoRow('Loại sự cố', incident.issueType),
                  _buildDivider(),
                  _buildInfoRow(
                    'Mức độ', 
                    incident.severity, 
                    isError: incident.severity.toLowerCase() == 'nghiêm trọng',
                    isWarning: incident.severity.toLowerCase() == 'trung bình',
                  ),
                  _buildDivider(),
                  _buildInfoRow('Hợp đồng', incident.contractId),
                  _buildDivider(),
                  _buildInfoRow('Thời gian', incident.occurrenceTime),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Người phụ trách
            if (incident.assignedStaff != null && incident.assignedStaff!.isNotEmpty) ...[
              _buildSectionCard(
                title: 'Người phụ trách',
                icon: Icons.person_outline_rounded,
                content: _buildInfoRow('Nhân viên', incident.assignedStaff!),
              ),
              const SizedBox(height: 16),
            ],

            // Mô tả
            _buildSectionCard(
              title: 'Mô tả chi tiết',
              icon: Icons.description_outlined,
              content: Text(
                incident.description, 
                style: AppTextStyles.body.copyWith(height: 1.5),
              ),
            ),
            
            // Hình ảnh đính kèm
            if (incident.attachments.isNotEmpty) ...[
              const SizedBox(height: 16),
              _buildSectionCard(
                title: 'Hình ảnh đính kèm',
                icon: Icons.image_outlined,
                content: Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: incident.attachments.map((att) {
                    return Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        border: Border.all(color: AppColors.divider),
                        borderRadius: AppRadius.mdRadius,
                      ),
                      child: ClipRRect(
                        borderRadius: AppRadius.mdRadius,
                        child: CustomImageWidget(
                          imageUrl: att.url ?? att.localPath ?? '',
                          fit: BoxFit.cover,
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ],
            
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  // REUSABLE UI
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

  Widget _buildInfoRow(String label, String value, {bool isHighlight = false, bool isError = false, bool isWarning = false}) {
    Color valColor = AppColors.textPrimary;
    if (isHighlight) valColor = AppColors.primary;
    if (isError) valColor = AppColors.error;
    if (isWarning) valColor = AppColors.warning;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(label, style: AppTextStyles.bodySecondary),
          ),
          Expanded(
            child: Text(
              value,
              style: AppTextStyles.body.copyWith(
                fontWeight: (isHighlight || isError || isWarning) ? FontWeight.bold : FontWeight.w500,
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
"""

with open("lib/screens/incidents/incident_detail_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)

print("IncidentDetailScreen Updated.")