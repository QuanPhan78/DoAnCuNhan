import os

card_code = """import 'package:flutter/material.dart';
import '../models/device_model.dart';
import 'custom_image_widget.dart';
import 'dashboard_widgets.dart'; // For StatusBadge and BadgeStatus
import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';
import '../theme/app_radius.dart';
import '../theme/app_shadows.dart';

class DeviceCard extends StatelessWidget {
  final DeviceModel device;
  final VoidCallback onTap;

  const DeviceCard({super.key, required this.device, required this.onTap});

  BadgeStatus _getBadgeStatus(String? status) {
    if (status == null) return BadgeStatus.neutral;
    switch (status.toLowerCase()) {
      case 'sẵn sàng':
        return BadgeStatus.success;
      case 'đang cho thuê':
        return BadgeStatus.processing;
      case 'bảo trì':
      case 'hỏng':
        return BadgeStatus.error;
      default:
        return BadgeStatus.neutral;
    }
  }

  @override
  Widget build(BuildContext context) {
    final hasImage = (device.imageUrl != null && device.imageUrl!.isNotEmpty) || 
                     (device.imageAsset != null && device.imageAsset!.isNotEmpty);
                     
    final imagePath = (device.imageUrl != null && device.imageUrl!.isNotEmpty) 
        ? device.imageUrl! 
        : (device.imageAsset ?? '');

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
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
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Image
                ClipRRect(
                  borderRadius: AppRadius.mdRadius,
                  child: hasImage 
                      ? CustomImageWidget(
                          imageUrl: imagePath, 
                          width: 88, 
                          height: 88, 
                          fit: BoxFit.cover,
                        )
                      : Container(
                          width: 88, 
                          height: 88, 
                          color: AppColors.divider.withValues(alpha: 0.3), 
                          child: const Icon(Icons.devices_rounded, color: AppColors.textSecondary, size: 32),
                        ),
                ),
                const SizedBox(width: 16),
                
                // Content
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Name & Code
                      Text(
                        device.name, 
                        style: AppTextStyles.subtitle.copyWith(fontSize: 16, height: 1.3),
                        maxLines: 2, 
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Mã: ${device.code ?? "---"}', 
                        style: AppTextStyles.bodySecondary.copyWith(fontSize: 13),
                      ),
                      const SizedBox(height: 8),
                      
                      // Tags (Type & Status)
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: [
                          StatusBadge(text: device.type, color: AppColors.primary),
                          if (device.rentalStatus != null)
                            StatusBadge(
                              text: device.rentalStatus!, 
                              status: _getBadgeStatus(device.rentalStatus!),
                            ),
                        ],
                      ),
                      
                      const SizedBox(height: 12),
                      
                      // Price
                      Row(
                        children: [
                          Icon(Icons.payments_outlined, size: 16, color: AppColors.textSecondary),
                          const SizedBox(width: 4),
                          Text(
                            device.rentalPrice != null ? '${device.rentalPrice} đ/ngày' : 'Liên hệ để báo giá',
                            style: AppTextStyles.body.copyWith(
                              color: device.rentalPrice != null ? AppColors.error : AppColors.textSecondary,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
"""

with open("lib/widgets/device_card.dart", "w", encoding="utf-8") as f:
    f.write(card_code)

print("DeviceCard Updated.")