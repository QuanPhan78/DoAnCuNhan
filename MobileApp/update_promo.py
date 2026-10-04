import os

p_list = "lib/screens/promotions/promotion_list_screen.dart"
code_list = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/promotion_provider.dart';
import '../../widgets/custom_image_widget.dart';
import '../../widgets/core/state_widgets.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';

class PromotionListScreen extends StatefulWidget {
  const PromotionListScreen({super.key});

  @override
  State<PromotionListScreen> createState() => _PromotionListScreenState();
}

class _PromotionListScreenState extends State<PromotionListScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PromotionProvider>().fetchPromotions();
    });
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<PromotionProvider>();

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Khuyến Mãi'),
      body: _buildContent(provider),
    );
  }

  Widget _buildContent(PromotionProvider provider) {
    if (provider.isLoading && provider.promotions.isEmpty) {
      return const LoadingState(message: 'Đang tải khuyến mãi...');
    }
    if (provider.errorMessage != null) {
      return ErrorState(
        message: 'Lỗi: ${provider.errorMessage}',
        onRetry: () => context.read<PromotionProvider>().fetchPromotions(),
      );
    }
    if (provider.promotions.isEmpty) {
      return const EmptyState(message: 'Hiện chưa có chương trình khuyến mãi nào.', icon: Icons.local_offer_outlined);
    }

    return RefreshIndicator(
      color: AppColors.primary,
      onRefresh: () => context.read<PromotionProvider>().fetchPromotions(),
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        itemCount: provider.promotions.length,
        itemBuilder: (context, index) {
          final promo = provider.promotions[index];
          return Container(
            margin: const EdgeInsets.only(bottom: 20),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: AppRadius.lgRadius,
              boxShadow: AppShadows.cardShadow,
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                borderRadius: AppRadius.lgRadius,
                onTap: () {
                  Navigator.pushNamed(context, '/promotion_detail', arguments: promo);
                },
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    AspectRatio(
                      aspectRatio: 16 / 9,
                      child: ClipRRect(
                        borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                        child: CustomImageWidget(
                          imageUrl: promo.imageUrl ?? promo.imageAsset ?? '',
                          fit: BoxFit.cover,
                        ),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Expanded(
                                child: Text(
                                  promo.title,
                                  style: AppTextStyles.h2.copyWith(fontSize: 18),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              if (promo.status != null) ...[
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: AppColors.error.withValues(alpha: 0.1),
                                    borderRadius: AppRadius.smRadius,
                                  ),
                                  child: Text(
                                    promo.status!,
                                    style: AppTextStyles.body.copyWith(
                                      color: AppColors.error,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                              ]
                            ],
                          ),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              const Icon(Icons.calendar_today_rounded, size: 14, color: AppColors.textSecondary),
                              const SizedBox(width: 6),
                              Expanded(
                                child: Text(
                                  'Từ ${promo.validFrom} đến ${promo.validTo}',
                                  style: AppTextStyles.bodySecondary.copyWith(fontSize: 13),
                                ),
                              ),
                            ],
                          ),
                          if (promo.discountValue != null) ...[
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                const Icon(Icons.local_offer_rounded, size: 14, color: AppColors.success),
                                const SizedBox(width: 6),
                                Expanded(
                                  child: Text(
                                    promo.discountValue!,
                                    style: AppTextStyles.body.copyWith(color: AppColors.success, fontWeight: FontWeight.bold),
                                  ),
                                ),
                              ],
                            ),
                          ]
                        ],
                      ),
                    )
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
"""

with open(p_list, "w", encoding="utf-8") as f:
    f.write(code_list)

p_detail = "lib/screens/promotions/promotion_detail_screen.dart"
code_detail = """import 'package:flutter/material.dart';
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
"""

with open(p_detail, "w", encoding="utf-8") as f:
    f.write(code_detail)

print("Promotion screens updated.")