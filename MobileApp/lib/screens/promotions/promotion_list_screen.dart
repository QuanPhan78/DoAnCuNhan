import 'package:flutter/material.dart';
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
