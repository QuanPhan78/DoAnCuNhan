import 'package:flutter/material.dart';
import '../../models/promotion_model.dart';
import '../../widgets/custom_image_widget.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';

class PromotionDetailScreen extends StatelessWidget {
  final PromotionModel promotion;

  const PromotionDetailScreen({super.key, required this.promotion});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Chi tiết Khuyến Mãi'),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            AspectRatio(
              aspectRatio: 16 / 9,
              child: CustomImageWidget(
                imageUrl: promotion.imageUrl ?? promotion.imageAsset ?? '',
                fit: BoxFit.cover,
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(promotion.title, style: AppTextStyles.h1.copyWith(fontSize: 22)),
                  const SizedBox(height: 24),
                  
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
                        if (promotion.discountValue != null) ...[
                          _buildSection('Mức ưu đãi', promotion.discountValue!, Icons.local_offer_rounded, AppColors.success),
                          const Divider(color: AppColors.divider, height: 24),
                        ],
                        _buildSection('Thời gian', '${promotion.validFrom} - ${promotion.validTo}', Icons.date_range_rounded, AppColors.primary),
                        if (promotion.status != null) ...[
                          const Divider(color: AppColors.divider, height: 24),
                          _buildSection('Trạng thái', promotion.status!, Icons.info_outline_rounded, AppColors.error),
                        ],
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),
                  _buildContentCard('Nội dung chương trình', promotion.description ?? 'Đang cập nhật', Icons.description_outlined),
                  const SizedBox(height: 16),
                  _buildContentCard('Điều kiện áp dụng', promotion.conditions ?? 'Không có điều kiện đặc biệt', Icons.rule_rounded),
                  const SizedBox(height: 40),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }

  Widget _buildContentCard(String title, String content, IconData icon) {
    return Container(
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
          Text(content, style: AppTextStyles.body.copyWith(height: 1.6)),
        ],
      ),
    );
  }

  Widget _buildSection(String title, String content, IconData icon, Color iconColor) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: iconColor.withValues(alpha: 0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: iconColor, size: 20),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: AppTextStyles.bodySecondary.copyWith(fontSize: 13)),
              const SizedBox(height: 4),
              Text(content, style: AppTextStyles.body.copyWith(fontWeight: FontWeight.bold, fontSize: 15)),
            ],
          ),
        )
      ],
    );
  }
}
