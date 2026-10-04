import os

code = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/maintenance_model.dart';
import '../../providers/auth_provider.dart';
import '../../providers/maintenance_provider.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';

class MaintenanceUpdateScreen extends StatefulWidget {
  final MaintenanceModel maintenance;
  const MaintenanceUpdateScreen({super.key, required this.maintenance});

  @override
  State<MaintenanceUpdateScreen> createState() => _MaintenanceUpdateScreenState();
}

class _MaintenanceUpdateScreenState extends State<MaintenanceUpdateScreen> {
  final _formKey = GlobalKey<FormState>();
  late String _status;
  final _noteCtrl = TextEditingController();
  final _resultCtrl = TextEditingController();

  final List<String> _statuses = ['Đã gửi', 'Tiếp nhận', 'Phân công', 'Đang xử lý', 'Hoàn thành'];

  @override
  void initState() {
    super.initState();
    _status = widget.maintenance.status ?? 'Đã gửi';
    if (!_statuses.contains(_status)) {
      _statuses.insert(0, _status);
    }
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final user = context.read<AuthProvider>().currentUser;
    if (user == null) return;

    final updated = MaintenanceModel(
      id: widget.maintenance.id,
      requestCode: widget.maintenance.requestCode,
      contractId: widget.maintenance.contractId,
      deviceId: widget.maintenance.deviceId,
      customer: widget.maintenance.customer,
      description: widget.maintenance.description,
      status: _status,
      assignedEmployee: user.name,
      createdAt: widget.maintenance.createdAt,
      completedAt: _status == 'Hoàn thành' ? DateTime.now().toString().substring(0, 16) : widget.maintenance.completedAt,
      result: _status == 'Hoàn thành' ? _resultCtrl.text : widget.maintenance.result,
      notes: List.from(widget.maintenance.notes),
    );

    if (_noteCtrl.text.isNotEmpty || _status == 'Hoàn thành') {
      updated.notes.add(MaintenanceNote(
        time: DateTime.now().toString().substring(0, 16),
        content: _noteCtrl.text.isNotEmpty ? _noteCtrl.text : 'Đã cập nhật trạng thái bảo trì',
        author: user.name,
      ));
    }

    final success = await context.read<MaintenanceProvider>().updateMaintenance(updated);
    if (!mounted) return;
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Cập nhật thành công'), backgroundColor: AppColors.success));
      Navigator.pop(context);
      Navigator.pop(context); 
    } else {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Lỗi cập nhật'), backgroundColor: AppColors.error));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Cập nhật Bảo trì'),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.all(24),
            children: [
              Text('Trạng thái mới', style: AppTextStyles.h2.copyWith(fontSize: 16)),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: _status,
                items: _statuses.map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
                onChanged: (v) => setState(() => _status = v!),
                icon: const Icon(Icons.keyboard_arrow_down_rounded, color: AppColors.textSecondary),
                decoration: _buildInputDecoration('Chọn trạng thái'),
              ),
              const SizedBox(height: 24),
              Text('Ghi chú / Tiến độ', style: AppTextStyles.h2.copyWith(fontSize: 16)),
              const SizedBox(height: 8),
              TextFormField(
                controller: _noteCtrl,
                maxLines: 4,
                decoration: _buildInputDecoration('Nhập thông tin cập nhật...'),
              ),
              if (_status == 'Hoàn thành') ...[
                const SizedBox(height: 24),
                Text('Kết quả xử lý', style: AppTextStyles.h2.copyWith(fontSize: 16)),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _resultCtrl,
                  maxLines: 3,
                  decoration: _buildInputDecoration('Nhập kết quả bảo trì (bắt buộc)...'),
                  validator: (v) => v == null || v.isEmpty ? 'Vui lòng nhập kết quả' : null,
                ),
              ],
              const SizedBox(height: 40),
              CustomButton(
                text: 'Lưu cập nhật',
                onPressed: _submit,
                isFullWidth: true,
                type: ButtonType.primary,
              )
            ],
          ),
        ),
      ),
    );
  }

  InputDecoration _buildInputDecoration(String hint) {
    return InputDecoration(
      hintText: hint,
      hintStyle: AppTextStyles.bodySecondary,
      filled: true,
      fillColor: AppColors.surface,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      border: OutlineInputBorder(
        borderRadius: AppRadius.mdRadius,
        borderSide: const BorderSide(color: AppColors.divider),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: AppRadius.mdRadius,
        borderSide: const BorderSide(color: AppColors.divider),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: AppRadius.mdRadius,
        borderSide: const BorderSide(color: AppColors.primary, width: 2),
      ),
    );
  }
}
"""

with open("lib/screens/maintenance/maintenance_update_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("MaintenanceUpdateScreen Updated.")