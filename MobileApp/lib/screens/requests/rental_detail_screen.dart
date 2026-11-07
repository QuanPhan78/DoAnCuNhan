import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/rental_request_model.dart';
import '../../models/rental_status.dart';
import '../../providers/rental_provider.dart';
import '../../providers/contract_provider.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';
import '../../widgets/cancellation_reason_dialog.dart';
import '../../providers/auth_provider.dart';
import 'package:intl/intl.dart';

class RentalDetailScreen extends StatelessWidget {
  final RentalRequestModel initialRequest;

  const RentalDetailScreen({super.key, required this.initialRequest});

  Future<void> _cancelRequest(BuildContext context, RentalProvider provider, RentalRequestModel request) async {
    final reason = await showCancellationReasonDialog(context);
    if (reason == null || !context.mounted || provider.isLoading) return;
    try {
      await provider.requestCancellation(request.id, reason);
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Đã gửi yêu cầu hủy. Vui lòng chờ duyệt.')),
      );
    } catch (error) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _viewContract(BuildContext context, String contractId) async {
    final user = context.read<AuthProvider>().currentUser;
    if (user == null) return;
    try {
      final contract = await context.read<ContractProvider>().getContract(contractId, user.id, user.role);
      if (context.mounted) Navigator.pushNamed(context, '/contract_detail', arguments: contract);
    } catch (error) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<RentalProvider>(
      builder: (context, provider, child) {
        // Find latest data from provider
        final request = provider.rentals.firstWhere(
          (r) => r.id == initialRequest.id,
          orElse: () => initialRequest,
        );
        final device = request.items.first;

        return Scaffold(
          backgroundColor: AppColors.background,
          appBar: CustomAppBar(title: 'Chi tiết đơn ${request.id}'),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Timeline
                _buildTimeline(request.status),
                if (request.cancellationReason?.isNotEmpty == true)
                  _buildInfoRow('Lý do hủy', request.cancellationReason!),
                const SizedBox(height: 24),
                
                // Device info
                _buildSectionCard(
                  title: 'Thông tin thiết bị',
                  icon: Icons.devices_rounded,
                  content: Column(
                    children: [
                      _buildInfoRow('Thiết bị', device.deviceName),
                      _buildDivider(),
                      _buildInfoRow('Số lượng', '${device.quantity}'),
                      _buildDivider(),
                      _buildInfoRow('Hình thức', request.rentalType),
                    ],
                  ),
                ),
                
                const SizedBox(height: 16),
                
                // Time & Address
                _buildSectionCard(
                  title: 'Thời gian & Địa chỉ',
                  icon: Icons.calendar_today_rounded,
                  content: Column(
                    children: [
                      _buildInfoRow('Bắt đầu', '${request.startDate.day}/${request.startDate.month}/${request.startDate.year}'),
                      _buildDivider(),
                      _buildInfoRow('Kết thúc', '${request.endDate.day}/${request.endDate.month}/${request.endDate.year}'),
                      _buildDivider(),
                      _buildInfoRow('Địa chỉ', request.deliveryAddress),
                      if (request.note.isNotEmpty) ...[
                        _buildDivider(),
                        _buildInfoRow('Ghi chú', request.note),
                      ],
                    ],
                  ),
                ),

                const SizedBox(height: 16),
                
                // Cost
                _buildSectionCard(
                  title: 'Chi phí dự kiến',
                  icon: Icons.payments_outlined,
                  content: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Tổng tiền:', style: AppTextStyles.h2),
                      Text(
                        '${NumberFormat('#,###').format(request.estimatedAmount)} VNĐ', 
                        style: AppTextStyles.h2.copyWith(color: AppColors.error),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 32),
                
                if (request.status == RentalStatus.pending)
                  CustomButton(
                    text: 'Yêu cầu hủy',
                    onPressed: provider.isLoading ? null : () => _cancelRequest(context, provider, request),
                    type: ButtonType.destructive,
                    isFullWidth: true,
                  ),

                if (request.contractId != null && request.contractId!.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  CustomButton(
                    text: 'XEM HỢP ĐỒNG',
                    onPressed: () => _viewContract(context, request.id),
                    type: ButtonType.primary,
                    isFullWidth: true,
                  ),
                ]
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildTimeline(RentalStatus currentStatus) {
    const steps = [
      RentalStatus.pending,
      RentalStatus.renting,
      RentalStatus.returnedPendingSettlement,
      RentalStatus.completed,
    ];
    final current = steps.indexOf(currentStatus);
    if (current < 0) {
      return _buildSectionCard(
        title: currentStatus.displayName,
        icon: Icons.info_outline,
        content: const SizedBox.shrink(),
      );
    }
    return Column(
      children: [
        for (var index = 0; index < steps.length; index++)
          ListTile(
            contentPadding: EdgeInsets.zero,
            leading: Icon(index <= current ? Icons.check_circle : Icons.circle_outlined),
            title: Text(steps[index].displayName),
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
