import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../models/device_model.dart';
import '../../models/rental_request_model.dart';
import '../../models/rental_status.dart';
import '../../services/rental_service.dart';
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

  String _rentalType = 'Theo ngày';
  final List<String> _rentalTypes = ['Theo ngày', 'Theo tuần', 'Theo tháng', 'Dài hạn'];
  
  int _quantity = 1;
  
  DateTime _startDate = DateTime.now();
  DateTime _endDate = DateTime.now().add(const Duration(days: 1));
  
  final _addressCtrl = TextEditingController();
  final _noteCtrl = TextEditingController();

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
    final firstDate = isStart ? DateTime.now() : _startDate;
    final picked = await showDatePicker(
      context: context,
      initialDate: initialDate,
      firstDate: firstDate,
      lastDate: DateTime(2030),
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

    if (picked != null) {
      setState(() {
        if (isStart) {
          _startDate = picked;
          if (_endDate.isBefore(_startDate)) {
            _endDate = _startDate.add(const Duration(days: 1));
          }
        } else {
          _endDate = picked;
        }
      });
    }
  }

  void _onConfirm() {
    if (!_formKey.currentState!.validate()) return;
    
    if (_endDate.isBefore(_startDate)) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Ngày kết thúc không được trước ngày bắt đầu'),
        backgroundColor: AppColors.error,
      ));
      return;
    }

    final estimatedCost = RentalService.calculateEstimatedCost(
      devicePrice: widget.device.rentalPrice ?? 0,
      rentalType: _rentalType,
      quantity: _quantity,
      startDate: _startDate,
      endDate: _endDate,
    );

    final authProvider = context.read<AuthProvider>();
    final currentUserId = authProvider.currentUser?.id ?? '1';

    final request = RentalRequestModel(
      id: 'REQ-${DateTime.now().millisecondsSinceEpoch}',
      customerId: currentUserId,
      items: [
        RentalRequestItem(
          deviceId: widget.device.id,
          deviceName: widget.device.name,
          imageUrl: widget.device.imageUrl,
          quantity: _quantity,
          rentalPrice: widget.device.rentalPrice ?? 0,
          subtotal: estimatedCost,
        ),
      ],
      rentalType: _rentalType,
      startDate: _startDate,
      endDate: _endDate,
      deliveryAddress: _addressCtrl.text,
      note: _noteCtrl.text,
      estimatedAmount: estimatedCost,
      status: RentalStatus.pending,
      createdAt: DateTime.now(),
    );

    Navigator.pushNamed(context, '/rental_confirm', arguments: request);
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
                
                _buildLabel('1. Hình thức thuê'),
                _buildDropdown(
                  value: _rentalType,
                  items: _rentalTypes.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
                  onChanged: (v) => setState(() => _rentalType = v!),
                ),
                
                const SizedBox(height: 24),
                _buildLabel('2. Số lượng'),
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
                _buildLabel('3. Thời gian thuê'),
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
                _buildLabel('4. Địa chỉ giao/lắp đặt'),
                TextFormField(
                  controller: _addressCtrl,
                  decoration: _inputDecoration('Nhập địa chỉ chi tiết...'),
                  validator: (v) => v == null || v.isEmpty ? 'Vui lòng nhập địa chỉ' : null,
                ),

                const SizedBox(height: 24),
                _buildLabel('5. Ghi chú thêm'),
                TextFormField(
                  controller: _noteCtrl,
                  maxLines: 3,
                  decoration: _inputDecoration('Nhập yêu cầu đặc biệt (không bắt buộc)...'),
                ),

                const SizedBox(height: 40),
                CustomButton(
                  text: 'TIẾP TỤC',
                  onPressed: _onConfirm,
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

  Widget _buildDropdown({
    required String value,
    required List<DropdownMenuItem<String>> items,
    required void Function(String?) onChanged,
  }) {
    final bool hasValue = items.any((item) => item.value == value);
    return DropdownButtonFormField<String>(
      initialValue: hasValue ? value : (items.isNotEmpty ? items.first.value : null),
      items: items,
      onChanged: onChanged,
      icon: const Icon(Icons.keyboard_arrow_down_rounded, color: AppColors.textSecondary),
      decoration: _inputDecoration(''),
    );
  }
}
