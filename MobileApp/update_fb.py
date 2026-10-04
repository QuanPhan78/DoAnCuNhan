import os

code_list = """import 'package:flutter/material.dart';
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
"""

with open("lib/screens/feedbacks/feedback_list_screen.dart", "w", encoding="utf-8") as f:
    f.write(code_list)

code_detail = """import 'package:flutter/material.dart';
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
                      borderRadius: AppRadius.fullRadius,
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
"""

with open("lib/screens/feedbacks/feedback_detail_screen.dart", "w", encoding="utf-8") as f:
    f.write(code_detail)

print("Feedback screens updated.")