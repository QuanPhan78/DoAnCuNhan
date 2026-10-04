import os

code = """import 'package:flutter/material.dart';
import '../models/contract_model.dart';
import 'dashboard_widgets.dart'; // For StatusBadge, BadgeStatus
import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';
import '../theme/app_radius.dart';
import '../theme/app_shadows.dart';
import 'package:intl/intl.dart';

class ContractCard extends StatelessWidget {
  final ContractModel contract;
  final VoidCallback onTap;

  const ContractCard({super.key, required this.contract, required this.onTap});

  BadgeStatus _getBadgeStatus(String? status) {
    if (status == null) return BadgeStatus.neutral;
    switch (status.toLowerCase()) {
      case 'đang hiệu lực':
        return BadgeStatus.success;
      case 'chờ duyệt':
        return BadgeStatus.warning;
      case 'đã thanh lý':
      case 'hoàn thành':
        return BadgeStatus.processing; // or neutral
      default:
        return BadgeStatus.neutral;
    }
  }

  String _formatCurrency(double? amount) {
    if (amount == null) return '0 đ';
    final formatter = NumberFormat('#,###', 'vi_VN');
    return '${formatter.format(amount)} đ';
  }

  @override
  Widget build(BuildContext context) {
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
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header: Code & Status
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      contract.contractCode ?? 'N/A', 
                      style: AppTextStyles.subtitle.copyWith(fontSize: 16),
                    ),
                    StatusBadge(
                      text: contract.status ?? 'Không rõ',
                      status: _getBadgeStatus(contract.status),
                    ),
                  ],
                ),
                
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 12),
                  child: Divider(color: AppColors.divider, height: 1),
                ),
                
                // Content: Device, Customer, Dates
                _buildRow(Icons.person_outline_rounded, contract.customerName ?? 'Khách hàng không rõ'),
                const SizedBox(height: 8),
                
                _buildRow(
                  Icons.devices_rounded, 
                  'Số lượng: ${contract.deviceIds?.length ?? 0} thiết bị'
                ),
                const SizedBox(height: 8),
                
                _buildRow(
                  Icons.calendar_today_rounded, 
                  '${contract.rentalStart ?? "N/A"} - ${contract.rentalEnd ?? "N/A"}'
                ),
                const SizedBox(height: 12),
                
                // Footer: Price
                Row(
                  children: [
                    const Icon(Icons.payments_outlined, size: 18, color: AppColors.textSecondary),
                    const SizedBox(width: 8),
                    Text(
                      'Tổng giá trị: ', 
                      style: AppTextStyles.bodySecondary,
                    ),
                    Text(
                      _formatCurrency(contract.totalAmount),
                      style: AppTextStyles.body.copyWith(
                        color: AppColors.error,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRow(IconData icon, String text) {
    return Row(
      children: [
        Icon(icon, size: 18, color: AppColors.textSecondary),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            text, 
            style: AppTextStyles.body,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}
"""

with open("lib/widgets/contract_card.dart", "w", encoding="utf-8") as f:
    f.write(code)

print("ContractCard Updated.")