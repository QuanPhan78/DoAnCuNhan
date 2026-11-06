import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../models/device_model.dart';
import '../../models/rental_request_model.dart';
import '../../models/rental_status.dart';
import '../../providers/rental_provider.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';
import '../../widgets/custom_image_widget.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import 'package:intl/intl.dart';

class RentalFormScreen extends StatefulWidget {
  final DeviceModel device;

  const RentalFormScreen({super.key, required this.device});

  @override
  State<RentalFormScreen> createState() => _RentalFormScreenState();
}

class _RentalFormScreenState extends State<RentalFormScreen> {
  final _formKey = GlobalKey<FormState>();

  int _quantity = 1;
  bool _quoting = false;

  DateTime _startDate = DateUtils.dateOnly(DateTime.now());
  DateTime _endDate = DateUtils.addDaysToDate(DateTime.now(), 1);

  final _addressCtrl = TextEditingController();
  final _noteCtrl = TextEditingController();
  final _promoCtrl = TextEditingController();

  @override
  void dispose() {
    _addressCtrl.dispose();
    _noteCtrl.dispose();
    _promoCtrl.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final user = context.read<AuthProvider>().currentUser;
      if (user != null && user.address != null && user.address!.isNotEmpty) {
        if (_addressCtrl.text.isEmpty) {
          setState(() {
            _addressCtrl.text = user.address!;
          });
        }
      }
    });
  }

  void _selectDate(bool isStart) async {
    final initialDate = isStart ? _startDate : _endDate;
    final firstDate = isStart ? DateUtils.dateOnly(DateTime.now()) : _startDate;
    final picked = await showDatePicker(
      context: context,
      initialDate: initialDate,
      firstDate: firstDate,
      lastDate: DateTime(DateTime.now().year + 5, 12, 31),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: AppColors.primary,
              onPrimary: Colors.white,
              onSurface: AppColors.textPrimary,
            ),
          ),
          child: child!,
        );
      },
    );

    if (picked != null && mounted) {
      setState(() {
        if (isStart) {
          _startDate = picked;
          if (_endDate.isBefore(_startDate)) {
            _endDate = DateUtils.addDaysToDate(_startDate, 1);
          }
        } else {
          _endDate = picked;
        }
      });
    }
  }

  Future<void> _onConfirm() async {
    if (_quoting || !_formKey.currentState!.validate()) return;
    final user = context.read<AuthProvider>().currentUser;
    if (user == null) return;

    FocusScope.of(context).unfocus();
    final now = DateTime.now();
    final promo = _promoCtrl.text.trim();
    final request = RentalRequestModel(
      id: 'REQ-${now.millisecondsSinceEpoch}',
      customerId: user.id,
      items: [
        RentalRequestItem(
          deviceId: widget.device.id,
          deviceName: widget.device.name,
          imageUrl: widget.device.imageUrl,
          quantity: _quantity,
          rentalPrice: widget.device.rentalPrice ?? 0,
          subtotal: 0,
        ),
      ],
      rentalType: 'Theo ngày',
      startDate: _startDate,
      endDate: _endDate,
      deliveryAddress: _addressCtrl.text.trim(),
      note: _noteCtrl.text.trim(),
      promoCode: promo.isEmpty ? null : promo,
      estimatedAmount: 0,
      status: RentalStatus.pending,
      createdAt: now,
    );

    setState(() => _quoting = true);
    try {
      final quoted = await context.read<RentalProvider>().quoteRental(request);
      if (!mounted) return;
      Navigator.pushNamed(context, '/rental_confirm', arguments: quoted);
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(error.toString().replaceFirst('Exception: ', '')),
        backgroundColor: AppColors.error,
      ));
    } finally {
      if (mounted) setState(() => _quoting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Thông tin thuê thiết bị'),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Thông tin thiết bị tóm tắt
                Row(
                  children: [
                    Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        color: AppColors.surface,
                        borderRadius: AppRadius.mdRadius,
                        border: Border.all(color: AppColors.divider),
                      ),
                      child: ClipRRect(
                        borderRadius: AppRadius.mdRadius,
                        child: CustomImageWidget(
                          imageUrl: (widget.device.imageUrl != null && widget.device.imageUrl!.isNotEmpty)
                              ? widget.device.imageUrl!
                              : (widget.device.imageAsset ?? ''),
                          width: 80,
                          height: 80,
                          fit: BoxFit.cover,
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(widget.device.name, style: AppTextStyles.h2, maxLines: 2, overflow: TextOverflow.ellipsis),
                          const SizedBox(height: 8),
                          Text(
                            '${NumberFormat('#,###').format(widget.device.rentalPrice ?? 0)} VNĐ / ngày', 
                            style: AppTextStyles.body.copyWith(color: AppColors.error, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 32),
                
                _buildLabel('Số lượng'),
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.remove_circle_outline, color: AppColors.primary),
                      onPressed: () {
                        if (_quantity > 1) setState(() => _quantity--);
                      },
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
                      decoration: BoxDecoration(
                        color: AppColors.surface,
                        borderRadius: AppRadius.smRadius,
                        border: Border.all(color: AppColors.divider),
                      ),
                      child: Text('$_quantity', style: AppTextStyles.h2),
                    ),
                    IconButton(
                      icon: const Icon(Icons.add_circle_outline, color: AppColors.primary),
                      onPressed: () => setState(() => _quantity++),
                    ),
                  ],
                ),

                const SizedBox(height: 24),
                _buildLabel('Thời gian thuê'),
                Row(
                  children: [
                    Expanded(
                      child: InkWell(
                        onTap: () => _selectDate(true),
                        child: _buildDateBox('Bắt đầu', _startDate),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: InkWell(
                        onTap: () => _selectDate(false),
                        child: _buildDateBox('Kết thúc', _endDate),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 24),
                _buildLabel('Địa chỉ giao thiết bị'),
                TextFormField(
                  controller: _addressCtrl,
                  decoration: _inputDecoration('Nhập địa chỉ chi tiết...'),
                  validator: (v) => v == null || v.trim().isEmpty ? 'Vui lòng nhập địa chỉ' : null,
                ),

                const SizedBox(height: 24),
                _buildLabel('Ghi chú'),
                TextFormField(
                  controller: _noteCtrl,
                  maxLines: 3,
                  decoration: _inputDecoration('Nhập yêu cầu đặc biệt (không bắt buộc)...'),
                ),

                const SizedBox(height: 24),
                _buildLabel('Mã khuyến mãi'),
                TextFormField(
                  controller: _promoCtrl,
                  textCapitalization: TextCapitalization.characters,
                  decoration: _inputDecoration('Không bắt buộc'),
                ),

                const SizedBox(height: 40),
                CustomButton(
                  text: 'TIẾP TỤC',
                  onPressed: _quoting ? null : _onConfirm,
                  isLoading: _quoting,
                  isFullWidth: true,
                  type: ButtonType.primary,
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLabel(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Text(text, style: AppTextStyles.h2.copyWith(fontSize: 16)),
    );
  }

  Widget _buildDateBox(String label, DateTime date) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: AppRadius.mdRadius,
        border: Border.all(color: AppColors.divider),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: AppTextStyles.bodySecondary.copyWith(fontSize: 12)),
          const SizedBox(height: 4),
          Row(
            children: [
              const Icon(Icons.calendar_today, size: 16, color: AppColors.primary),
              const SizedBox(width: 8),
              Text('${date.day}/${date.month}/${date.year}', style: AppTextStyles.body.copyWith(fontWeight: FontWeight.w500)),
            ],
          ),
        ],
      ),
    );
  }

  InputDecoration _inputDecoration(String hint) {
    return InputDecoration(
      hintText: hint,
      hintStyle: AppTextStyles.bodySecondary,
      filled: true,
      fillColor: AppColors.surface,
      contentPadding: const EdgeInsets.all(16),
      border: OutlineInputBorder(borderRadius: AppRadius.mdRadius, borderSide: const BorderSide(color: AppColors.divider)),
      enabledBorder: OutlineInputBorder(borderRadius: AppRadius.mdRadius, borderSide: const BorderSide(color: AppColors.divider)),
      focusedBorder: OutlineInputBorder(borderRadius: AppRadius.mdRadius, borderSide: const BorderSide(color: AppColors.primary, width: 2)),
    );
  }

}
