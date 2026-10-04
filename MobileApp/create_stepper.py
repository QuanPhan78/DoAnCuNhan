import os

code = """import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

class MaintenanceStepper extends StatelessWidget {
  final String currentStatus;
  const MaintenanceStepper({super.key, required this.currentStatus});

  final List<String> _steps = const ['Đã gửi', 'Tiếp nhận', 'Phân công', 'Đang xử lý', 'Hoàn thành'];

  int _getCurrentIndex() {
    final status = currentStatus.toLowerCase();
    if (status.contains('hoàn thành')) return 4;
    if (status.contains('đang xử lý')) return 3;
    if (status.contains('phân công')) return 2;
    if (status.contains('tiếp nhận')) return 1;
    return 0; // Đã gửi or unknown
  }

  @override
  Widget build(BuildContext context) {
    final currentIndex = _getCurrentIndex();
    
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Column(
        children: [
          Row(
            children: List.generate(_steps.length * 2 - 1, (index) {
              if (index % 2 != 0) {
                // Line
                final stepIndex = index ~/ 2;
                final isPassed = stepIndex < currentIndex;
                return Expanded(
                  child: Container(
                    height: 2,
                    color: isPassed ? AppColors.primary : AppColors.divider,
                  ),
                );
              }
              // Circle
              final stepIndex = index ~/ 2;
              final isPassed = stepIndex < currentIndex;
              final isCurrent = stepIndex == currentIndex;
              
              return Container(
                width: 24,
                height: 24,
                decoration: BoxDecoration(
                  color: isPassed || isCurrent ? AppColors.primary : AppColors.surface,
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: isPassed || isCurrent ? AppColors.primary : AppColors.divider,
                    width: 2,
                  ),
                ),
                child: isPassed 
                  ? const Icon(Icons.check, size: 14, color: Colors.white)
                  : isCurrent 
                    ? Center(child: Container(width: 8, height: 8, decoration: const BoxDecoration(color: Colors.white, shape: BoxShape.circle)))
                    : null,
              );
            }),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: _steps.asMap().entries.map((entry) {
              final isCurrent = entry.key == currentIndex;
              final isPassed = entry.key < currentIndex;
              return Expanded(
                child: Text(
                  entry.value,
                  textAlign: TextAlign.center,
                  style: AppTextStyles.bodySecondary.copyWith(
                    fontSize: 10,
                    fontWeight: isCurrent || isPassed ? FontWeight.bold : FontWeight.normal,
                    color: isCurrent || isPassed ? AppColors.textPrimary : AppColors.textSecondary,
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}
"""
with open("lib/widgets/maintenance_stepper.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("MaintenanceStepper created.")