import 'package:flutter/material.dart';
import '../../models/feedback_model.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';

class FeedbackDetailScreen extends StatelessWidget {
  final FeedbackModel feedback;

  const FeedbackDetailScreen({super.key, required this.feedback});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Chi tiết Phản hồi'),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    feedback.feedbackCode ?? 'N/A', 
                    style: AppTextStyles.h1.copyWith(fontSize: 24),
                  ),
                ),
                if (feedback.rating != null)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: AppColors.warning.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(100),
                    ),
                    child: Row(
                      children: [
                        Text(
                          '${feedback.rating}', 
                          style: AppTextStyles.h2.copyWith(color: AppColors.warning),
                        ),
                        const SizedBox(width: 4),
                        const Icon(Icons.star_rounded, color: AppColors.warning, size: 18),
                      ],
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 8),
            Text(feedback.createdAt ?? '', style: AppTextStyles.bodySecondary),
            const SizedBox(height: 24),

            if ((feedback.contractId != null && feedback.contractId!.isNotEmpty) || (feedback.maintenanceId != null && feedback.maintenanceId!.isNotEmpty)) ...[
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: AppRadius.lgRadius,
                  boxShadow: AppShadows.cardShadow,
                  border: Border.all(color: AppColors.divider),
                ),
                child: Column(
                  children: [
                    if (feedback.contractId != null && feedback.contractId!.isNotEmpty)
                      _buildRow('Mã Hợp đồng', feedback.contractId!),
                    if (feedback.contractId != null && feedback.contractId!.isNotEmpty && feedback.maintenanceId != null && feedback.maintenanceId!.isNotEmpty)
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 8.0),
                        child: Divider(color: AppColors.divider, height: 1),
                      ),
                    if (feedback.maintenanceId != null && feedback.maintenanceId!.isNotEmpty)
                      _buildRow('Mã Bảo trì', feedback.maintenanceId!),
                  ],
                ),
              ),
              const SizedBox(height: 24),
            ],

            Text('Nội dung phản hồi', style: AppTextStyles.h2.copyWith(fontSize: 16)),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: AppRadius.lgRadius,
                boxShadow: AppShadows.cardShadow,
                border: Border.all(color: AppColors.divider),
              ),
              child: Text(
                feedback.content,
                style: AppTextStyles.body.copyWith(height: 1.5),
              ),
            ),
            
            if (feedback.response != null && feedback.response!.isNotEmpty) ...[
              const SizedBox(height: 24),
              Row(
                children: [
                  const Icon(Icons.forum_rounded, color: AppColors.primary, size: 20),
                  const SizedBox(width: 8),
                  Text('Phản hồi từ doanh nghiệp', style: AppTextStyles.h2.copyWith(fontSize: 16, color: AppColors.primary)),
                ],
              ),
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.05),
                  borderRadius: AppRadius.lgRadius,
                  border: Border.all(color: AppColors.primary.withValues(alpha: 0.2)),
                ),
                child: Text(
                  feedback.response!,
                  style: AppTextStyles.body.copyWith(height: 1.5, color: AppColors.textPrimary),
                ),
              )
            ]
          ],
        ),
      ),
    );
  }

  Widget _buildRow(String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(width: 100, child: Text(label, style: AppTextStyles.bodySecondary)),
        Expanded(child: Text(value, style: AppTextStyles.body.copyWith(fontWeight: FontWeight.w600))),
      ],
    );
  }
}
