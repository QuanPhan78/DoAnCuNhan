import 'package:flutter/material.dart';
import '../../models/device_model.dart';
import '../../widgets/custom_image_widget.dart';
import '../../widgets/dashboard_widgets.dart'; // StatusBadge, BadgeStatus
import '../../widgets/core/custom_app_bar.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';

class DeviceDetailScreen extends StatelessWidget {
  final DeviceModel device;

  const DeviceDetailScreen({super.key, required this.device});

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
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Chi tiết thiết bị'),
      body: SingleChildScrollView(
        padding: const EdgeInsets.only(bottom: 40),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // PHẦN 1: Ảnh thiết bị lớn
            _buildDeviceImage(),
            
            // Container bọc toàn bộ nội dung phía dưới để tạo cảm giác chìm nhẹ
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // PHẦN 2: Tên, Mã, Trạng thái, Loại
                  _buildHeaderSection(),
                  
                  const SizedBox(height: 24),
                  
                  // PHẦN 3: Thông tin thiết bị
                  _buildSectionCard(
                    title: 'Thông tin thiết bị',
                    icon: Icons.info_outline_rounded,
                    content: Column(
                      children: [
                        _buildInfoRow('Hãng sản xuất', device.brand),
                        _buildDivider(),
                        _buildInfoRow('Model', device.model),
                        if (device.serialNumber != null && device.serialNumber!.isNotEmpty) ...[
                          _buildDivider(),
                          _buildInfoRow('Serial Number', device.serialNumber),
                        ],
                        if (device.condition != null && device.condition!.isNotEmpty) ...[
                          _buildDivider(),
                          _buildInfoRow('Tình trạng', device.condition),
                        ],
                      ],
                    ),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // PHẦN 4: Thông số kỹ thuật
                  if (device.specifications != null && device.specifications!.isNotEmpty)
                    _buildSectionCard(
                      title: 'Thông số kỹ thuật',
                      icon: Icons.memory_rounded,
                      content: Text(
                        device.specifications!, 
                        style: AppTextStyles.body.copyWith(height: 1.5),
                      ),
                    ),
                  
                  const SizedBox(height: 16),
                  
                  // PHẦN 5: Thông tin thuê
                  if (device.rentalPrice != null)
                    _buildSectionCard(
                      title: 'Thông tin thuê',
                      icon: Icons.payments_outlined,
                      content: Row(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          const Text('Đơn giá:', style: AppTextStyles.bodySecondary),
                          const Spacer(),
                          Text(
                            '${device.rentalPrice} đ / ngày',
                            style: AppTextStyles.h2.copyWith(color: AppColors.error),
                          ),
                        ],
                      ),
                    ),

                  const SizedBox(height: 16),
                  
                  // PHẦN 6: Mô tả
                  if (device.description != null && device.description!.isNotEmpty)
                    _buildSectionCard(
                      title: 'Mô tả',
                      icon: Icons.description_outlined,
                      content: Text(
                        device.description!, 
                        style: AppTextStyles.body.copyWith(height: 1.5),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDeviceImage() {
    final hasImage = (device.imageUrl != null && device.imageUrl!.isNotEmpty) || 
                     (device.imageAsset != null && device.imageAsset!.isNotEmpty);
                     
    final imagePath = (device.imageUrl != null && device.imageUrl!.isNotEmpty) 
        ? device.imageUrl! 
        : (device.imageAsset ?? '');

    return Container(
      width: double.infinity,
      height: 300,
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: const Border(bottom: BorderSide(color: AppColors.divider)),
      ),
      child: hasImage
          ? CustomImageWidget(
              imageUrl: imagePath,
              fit: BoxFit.contain,
              width: double.infinity,
              height: 300,
            )
          : const Center(
              child: Icon(Icons.devices_rounded, size: 100, color: AppColors.textSecondary),
            ),
    );
  }

  Widget _buildHeaderSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Text(
                device.name,
                style: AppTextStyles.h1.copyWith(fontSize: 24, height: 1.3),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          'Mã: ${device.code ?? "---"}',
          style: AppTextStyles.bodySecondary.copyWith(fontSize: 16),
        ),
        const SizedBox(height: 16),
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
      ],
    );
  }

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

  Widget _buildInfoRow(String label, String? value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(label, style: AppTextStyles.bodySecondary),
          ),
          Expanded(
            child: Text(
              (value == null || value.isEmpty) ? '---' : value, 
              style: AppTextStyles.body.copyWith(fontWeight: FontWeight.w500),
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
