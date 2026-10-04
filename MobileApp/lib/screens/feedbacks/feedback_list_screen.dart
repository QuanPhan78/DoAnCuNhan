import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/feedback_provider.dart';
import '../../widgets/core/state_widgets.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/dashboard_widgets.dart'; // StatusBadge, BadgeStatus
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';

class FeedbackListScreen extends StatefulWidget {
  const FeedbackListScreen({super.key});

  @override
  State<FeedbackListScreen> createState() => _FeedbackListScreenState();
}

class _FeedbackListScreenState extends State<FeedbackListScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<FeedbackProvider>().fetchFeedbacks();
    });
  }

  BadgeStatus _getBadgeStatus(String status) {
    if (status.toLowerCase().contains('phản hồi')) return BadgeStatus.success;
    if (status.toLowerCase().contains('ghi nhận')) return BadgeStatus.processing;
    return BadgeStatus.neutral;
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<FeedbackProvider>();

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: CustomAppBar(
        title: 'Phản hồi của tôi',
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: IconButton(
              icon: const Icon(Icons.add_rounded, size: 28),
              color: AppColors.primary,
              onPressed: () async {
                final result = await Navigator.pushNamed(context, '/create_feedback');
                if (result == true && context.mounted) {
                  context.read<FeedbackProvider>().fetchFeedbacks();
                }
              },
            ),
          )
        ],
      ),
      body: _buildContent(provider),
    );
  }

  Widget _buildContent(FeedbackProvider provider) {
    if (provider.isLoading && provider.feedbacks.isEmpty) {
      return const LoadingState(message: 'Đang tải danh sách phản hồi...');
    }
    if (provider.errorMessage != null) {
      return ErrorState(message: 'Lỗi: ${provider.errorMessage}', onRetry: () => context.read<FeedbackProvider>().fetchFeedbacks());
    }
    if (provider.feedbacks.isEmpty) {
      return const EmptyState(message: 'Chưa có phản hồi nào.', icon: Icons.feedback_outlined);
    }
    return RefreshIndicator(
      color: AppColors.primary,
      onRefresh: () => context.read<FeedbackProvider>().fetchFeedbacks(),
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        itemCount: provider.feedbacks.length,
        itemBuilder: (context, index) {
          final fb = provider.feedbacks[index];
          return Container(
            margin: const EdgeInsets.only(bottom: 16),
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
                  Navigator.pushNamed(context, '/feedback_detail', arguments: fb);
                },
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
                              fb.feedbackCode ?? 'N/A', 
                              style: AppTextStyles.h2.copyWith(fontSize: 16),
                              maxLines: 1, overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          StatusBadge(
                            text: fb.status ?? 'Mới tạo', 
                            status: _getBadgeStatus(fb.status ?? ''),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text(
                        fb.content,
                        style: AppTextStyles.body,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(fb.createdAt ?? '', style: AppTextStyles.bodySecondary.copyWith(fontSize: 12)),
                          if (fb.rating != null)
                            Row(
                              children: [
                                Text('${fb.rating}', style: AppTextStyles.body.copyWith(fontWeight: FontWeight.bold, color: AppColors.warning)),
                                const Icon(Icons.star_rounded, size: 16, color: AppColors.warning),
                              ],
                            )
                        ],
                      )
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
