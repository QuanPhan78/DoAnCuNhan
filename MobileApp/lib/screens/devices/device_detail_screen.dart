import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/device_provider.dart';
import '../../models/device_model.dart';
import '../../widgets/custom_image_widget.dart';
import '../../widgets/dashboard_widgets.dart'; // StatusBadge, BadgeStatus
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';
import 'package:intl/intl.dart';

class DeviceDetailScreen extends StatelessWidget {
  final DeviceModel device;

  const DeviceDetailScreen({super.key, required this.device});

  DeviceModel _resolveDevice(BuildContext context) {
    final cached = context.watch<DeviceProvider>().getDeviceById(device.id);
    if (cached != null && (device.code == null || device.imageUrl == null || device.brand == null || device.serialNumber == null)) {
      return cached;
    }
    return device;
  }

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
    final d = _resolveDevice(context);
    final canChooseDates = d.rentableQuantity != null
        ? d.rentableQuantity! > 0
        : d.rentalStatus?.toLowerCase() == 'sẵn sàng';

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Chi tiết thiết bị'),
      body: SingleChildScrollView(
        padding: const EdgeInsets.only(bottom: 40),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // PHẦN 1: Ảnh thiết bị lớn
            _buildDeviceImage(d),
            
            // Container bọc toàn bộ nội dung phía dưới để tạo cảm giác chìm nhẹ
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // PHẦN 2: Tên, Mã, Trạng thái, Loại
                  _buildHeaderSection(d),
                  
                  const SizedBox(height: 24),
                  
                  // PHẦN 3: Thông tin thiết bị
                  _buildSectionCard(
                    title: 'Thông tin thiết bị',
                    icon: Icons.info_outline_rounded,
                    content: Column(
                      children: [
                        _buildInfoRow('Hãng sản xuất', d.brand),
                        _buildDivider(),
                        _buildInfoRow('Model', d.model),
                        if (d.serialNumber != null && d.serialNumber!.isNotEmpty) ...[
                          _buildDivider(),
                          _buildInfoRow('Serial Number', d.serialNumber),
                        ],
                        if (d.condition != null && d.condition!.isNotEmpty) ...[
                          _buildDivider(),
                          _buildInfoRow('Tình trạng', d.condition),
                        ],
                      ],
                    ),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // PHẦN 4: Thông số kỹ thuật
                  if (d.specifications != null && d.specifications!.isNotEmpty)
                    _buildSectionCard(
                      title: 'Thông số kỹ thuật',
                      icon: Icons.memory_rounded,
                      content: Text(
                        d.specifications!, 
                        style: AppTextStyles.body.copyWith(height: 1.5),
                      ),
                    ),
                  
                  const SizedBox(height: 16),
                  
                  // PHẦN 5: Thông tin thuê
                  if (d.rentalPrice != null)
                    _buildSectionCard(
                      title: 'Thông tin thuê',
                      icon: Icons.payments_outlined,
                      content: Row(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          const Text('Đơn giá:', style: AppTextStyles.bodySecondary),
                          const Spacer(),
                          Text(
                            '${NumberFormat('#,###').format(d.rentalPrice)} VNĐ / ngày',
                            style: AppTextStyles.h2.copyWith(color: AppColors.error),
                          ),
                        ],
                      ),
                    ),

                  const SizedBox(height: 16),
                  
                  // PHẦN 6: Mô tả
                  if (d.description != null && d.description!.isNotEmpty)
                    _buildSectionCard(
                      title: 'Mô tả',
                      icon: Icons.description_outlined,
                      content: Text(
                        d.description!, 
                        style: AppTextStyles.body.copyWith(height: 1.5),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          decoration: BoxDecoration(
            color: AppColors.surface,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.05),
                blurRadius: 10,
                offset: const Offset(0, -4),
              ),
            ],
            border: const Border(top: BorderSide(color: AppColors.divider)),
          ),
          child: CustomButton(
            text: canChooseDates ? 'Chọn ngày thuê' : 'Không khả dụng',
            type: ButtonType.primary,
            isFullWidth: true,
            onPressed: canChooseDates
                ? () {
                    Navigator.pushNamed(context, '/rental_form', arguments: d);
                  }
                : null,
            icon: Icons.shopping_cart_checkout,
          ),
        ),
      ),
    );
  }

  Widget _buildDeviceImage(DeviceModel dev) {
    final hasImage = (dev.imageUrl != null && dev.imageUrl!.isNotEmpty) || 
                     (dev.imageAsset != null && dev.imageAsset!.isNotEmpty);
                     
    final imagePath = (dev.imageUrl != null && dev.imageUrl!.isNotEmpty) 
        ? dev.imageUrl! 
        : (dev.imageAsset ?? '');

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

  Widget _buildHeaderSection(DeviceModel dev) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Text(
                dev.name,
                style: AppTextStyles.h1.copyWith(fontSize: 24, height: 1.3),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          'Mã: ${dev.code ?? "---"}',
          style: AppTextStyles.bodySecondary.copyWith(fontSize: 16),
        ),
        const SizedBox(height: 16),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            StatusBadge(text: dev.type, color: AppColors.primary),
            if (dev.rentalStatus != null)
              StatusBadge(
                text: dev.rentalStatus!,
                status: _getBadgeStatus(dev.rentalStatus!),
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
