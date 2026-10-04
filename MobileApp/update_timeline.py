import os

code = """import 'package:flutter/material.dart';
import '../models/maintenance_model.dart';
import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';
import '../theme/app_radius.dart';

class MaintenanceTimeline extends StatelessWidget {
  final List<MaintenanceNote> notes;
  const MaintenanceTimeline({super.key, required this.notes});

  @override
  Widget build(BuildContext context) {
    if (notes.isEmpty) {
      return Text('Chưa có lịch sử cập nhật.', style: AppTextStyles.bodySecondary);
    }
    
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: notes.length,
      itemBuilder: (context, index) {
        final note = notes[index];
        final isLast = index == notes.length - 1;
        
        return IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              SizedBox(
                width: 20,
                child: Column(
                  children: [
                    Container(
                      margin: const EdgeInsets.only(top: 4),
                      width: 12, height: 12,
                      decoration: BoxDecoration(
                        color: AppColors.primary,
                        shape: BoxShape.circle,
                        border: Border.all(color: AppColors.primary.withValues(alpha: 0.3), width: 3),
                      ),
                    ),
                    if (!isLast)
                      Expanded(
                        child: Container(
                          width: 2,
                          color: AppColors.primary.withValues(alpha: 0.2),
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 24),
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: AppRadius.mdRadius,
                      border: Border.all(color: AppColors.divider),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(note.time, style: AppTextStyles.bodySecondary.copyWith(fontSize: 12)),
                        const SizedBox(height: 6),
                        Text(note.content, style: AppTextStyles.body.copyWith(fontWeight: FontWeight.w500)),
                        const SizedBox(height: 6),
                        Text('Bởi: ${note.author}', style: AppTextStyles.bodySecondary.copyWith(fontStyle: FontStyle.italic)),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
"""
with open("lib/widgets/maintenance_timeline.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("MaintenanceTimeline updated.")