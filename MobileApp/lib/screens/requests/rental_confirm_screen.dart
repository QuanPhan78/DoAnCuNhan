import '../../providers/cart_provider.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/rental_request_model.dart';
import '../../providers/rental_provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/contract_provider.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';
import 'package:intl/intl.dart';

class RentalConfirmScreen extends StatelessWidget {
  final RentalRequestModel requestData;

  const RentalConfirmScreen({super.key, required this.requestData});

  void _onConfirm(BuildContext context) async {
    final provider = context.read<RentalProvider>();
    if (provider.isLoading) return;

    try {
      // Lưu đơn thuê và tạo hợp đồng thật trong CSDL SQL Server
      final createdRental = await provider.createRental(requestData);

      // Cập nhật lại danh sách hợp đồng cho người dùng
      if (context.mounted) {
        context.read<CartProvider>().clear();
        final auth = context.read<AuthProvider>();
        if (auth.currentUser != null) {
          context.read<ContractProvider>().fetchContracts(
                auth.currentUser!.role,
                auth.currentUser!.id,
              );
        }
      }

      if (context.mounted) {
        final contractCode = createdRental.contractId ?? 'Hợp đồng mới';

        // Hiển thị thông báo thành công
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (ctx) => AlertDialog(
            shape: RoundedRectangleBorder(borderRadius: AppRadius.lgRadius),
            title: const Icon(Icons.check_circle, color: AppColors.success, size: 60),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('Đã gửi yêu cầu thuê', style: AppTextStyles.h2, textAlign: TextAlign.center),
                const SizedBox(height: 12),
                Text(
                  '$contractCode · Chờ duyệt\nTổng tiền: ${_money(createdRental.estimatedAmount)}\nMở hợp đồng để ký và thanh toán.',
                  style: AppTextStyles.bodySecondary, 
                  textAlign: TextAlign.center,
                ),
              ],
            ),
            actions: [
              CustomButton(
                text: 'Xem hợp đồng',
                onPressed: () {
                  Navigator.pop(ctx); // Đóng dialog
                  Navigator.of(context).pushReplacementNamed('/contracts');
                },
                isFullWidth: true,
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Lỗi tạo hợp đồng: ${e.toString().replaceAll("Exception: ", "")}'),
          backgroundColor: AppColors.error,
        ));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final submitting = context.watch<RentalProvider>().isLoading;
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Xác nhận thông tin thuê'),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildSectionCard(
                title: 'Thông tin thiết bị',
                icon: Icons.devices_rounded,
                content: Column(
                  children: [
                    _buildInfoRow('Thiết bị', requestData.items.first.deviceName),
                    _buildDivider(),
                    _buildInfoRow('Số lượng', '${requestData.items.first.quantity}'),
                  ],
                ),
              ),
              
              const SizedBox(height: 16),
              
              _buildSectionCard(
                title: 'Chi tiết thuê',
                icon: Icons.calendar_today_rounded,
                content: Column(
                  children: [
                    _buildInfoRow('Số ngày thuê', '${requestData.rentalDays ?? '—'}'),
                    _buildDivider(),
                    _buildInfoRow('Bắt đầu', '${requestData.startDate.day}/${requestData.startDate.month}/${requestData.startDate.year}'),
                    _buildDivider(),
                    _buildInfoRow('Kết thúc', '${requestData.endDate.day}/${requestData.endDate.month}/${requestData.endDate.year}'),
                  ],
                ),
              ),
              
              const SizedBox(height: 16),
              
              _buildSectionCard(
                title: 'Giao hàng',
                icon: Icons.local_shipping_outlined,
                content: Column(
                  children: [
                    _buildInfoRow('Địa chỉ', requestData.deliveryAddress),
                    if (requestData.note.isNotEmpty) ...[
                      _buildDivider(),
                      _buildInfoRow('Ghi chú', requestData.note),
                    ],
                  ],
                ),
              ),

              const SizedBox(height: 16),
              
              _buildSectionCard(
                title: 'Chi phí dự kiến',
                icon: Icons.payments_outlined,
                content: Column(
                  children: [
                    _buildInfoRow('Tiền thuê', _money(requestData.items.fold<double>(0, (sum, item) => sum + item.subtotal))),
                    if (requestData.promoCode != null) ...[
                      _buildDivider(),
                      _buildInfoRow('Giảm giá (${requestData.promoCode})', '-${_money(requestData.discountAmount)}'),
                    ],
                    _buildDivider(),
                    _buildInfoRow('Tổng tiền thuê', _money(requestData.estimatedAmount)),
                      _buildDivider(),
                      _buildInfoRow('Cọc bảo đảm thiết bị', _money(requestData.depositRequired)),
                  ],
                ),
              ),

              const SizedBox(height: 40),
              
              Row(
                children: [
                  Expanded(
                    child: CustomButton(
                      text: 'QUAY LẠI',
                      onPressed: submitting ? null : () => Navigator.pop(context),
                      type: ButtonType.outline,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: CustomButton(
                      text: 'XÁC NHẬN THUÊ',
                      onPressed: submitting ? null : () => _onConfirm(context),
                      isLoading: submitting,
                      type: ButtonType.primary,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  String _money(double value) => '${NumberFormat('#,##0.##', 'vi_VN').format(value)} đ';

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

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(label, style: AppTextStyles.bodySecondary),
          ),
          Expanded(
            child: Text(
              value, 
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
