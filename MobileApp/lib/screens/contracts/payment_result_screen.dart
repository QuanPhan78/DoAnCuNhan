import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';

class PaymentResultScreen extends StatelessWidget {
  final String? rawUri;
  const PaymentResultScreen({super.key, this.rawUri});

  @override
  Widget build(BuildContext context) {
    Map<String, String> params = {};
    if (rawUri != null) {
      try {
        final parsed = Uri.parse(rawUri!);
        params = parsed.queryParameters;
      } catch (_) {}
    }

    final isSuccess = params['status'] == 'success';
    final contractId = params['contractId'];
    final txn = params['txn'];
    final message = params['message'];
    num amount = 0;
    if (params['amount'] != null) {
      amount = num.tryParse(params['amount']!) ?? 0;
    }

    String moneyStr = NumberFormat('#,##0', 'vi_VN').format(amount);

    return Scaffold(
      appBar: const CustomAppBar(title: 'Kết quả giao dịch'),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Icon(
                    isSuccess ? Icons.check_circle_rounded : Icons.error_outline_rounded,
                    color: isSuccess ? const Color(0xFF16A34A) : const Color(0xFFDC2626),
                    size: 72,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    isSuccess ? 'Thanh toán thành công' : 'Giao dịch chưa hoàn tất',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: const Color(0xFF0F2B5C),
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    isSuccess
                        ? 'Cổng VNPay đã ghi nhận giao dịch thành công.'
                        : (message ?? 'Giao dịch VNPay không hoàn tất hoặc đã bị hủy.'),
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: isSuccess ? Colors.black87 : const Color(0xFFDC2626),
                      fontSize: 14,
                    ),
                  ),
                  const Divider(height: 32),
                  if (amount > 0) ...[
                    _infoRow('Số tiền thanh toán', '$moneyStr đ'),
                    const SizedBox(height: 8),
                  ],
                  if (contractId != null && contractId.isNotEmpty) ...[
                    _infoRow('Mã hợp đồng', '#$contractId'),
                    const SizedBox(height: 8),
                  ],
                  if (txn != null && txn.isNotEmpty) ...[
                    _infoRow('Mã GD VNPay', txn),
                    const SizedBox(height: 8),
                  ],
                  const SizedBox(height: 24),
                  CustomButton(
                    text: 'Xem sổ công nợ',
                    onPressed: () {
                      Navigator.pushNamedAndRemoveUntil(
                        context,
                        '/debts',
                        (route) => route.settings.name == '/dashboard',
                      );
                    },
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton(
                    onPressed: () {
                      Navigator.pushNamedAndRemoveUntil(context, '/dashboard', (r) => false);
                    },
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFF0F2B5C),
                      side: const BorderSide(color: Color(0xFF0F2B5C)),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                    child: const Text('Về trang chủ'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: Color(0xFF64748B), fontSize: 13)),
        Text(value, style: const TextStyle(fontWeight: FontWeight.w640, fontSize: 13)),
      ],
    );
  }
}
