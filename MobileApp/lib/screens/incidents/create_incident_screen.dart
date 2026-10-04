import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/incident_model.dart';
import '../../models/attachment_model.dart';
import '../../models/contract_model.dart';
import '../../providers/auth_provider.dart';
import '../../providers/contract_provider.dart';
import '../../providers/incident_provider.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';

class CreateIncidentScreen extends StatefulWidget {
  const CreateIncidentScreen({super.key});

  @override
  State<CreateIncidentScreen> createState() => _CreateIncidentScreenState();
}

class _CreateIncidentScreenState extends State<CreateIncidentScreen> {
  final _formKey = GlobalKey<FormState>();
  
  String? _selectedContractId;
  String? _selectedDeviceId;
  String _selectedIssueType = 'Không lên nguồn';
  String _selectedSeverity = 'Trung bình';
  final _descCtrl = TextEditingController();
  
  final List<String> _issueTypes = [
    'Không lên nguồn', 'Lỗi màn hình', 'Lỗi bàn phím', 'Chuột lỗi', 'Mất kết nối', 'Lỗi phần mềm', 'Khác'
  ];
  final List<String> _severities = ['Nhẹ', 'Trung bình', 'Nghiêm trọng'];
  final List<AttachmentModel> _mockAttachments = [];

  List<ContractModel> _myContracts = [];
  List<String> _contractDevices = [];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final userId = context.read<AuthProvider>().currentUser?.id;
      final allContracts = context.read<ContractProvider>().contracts;
      setState(() {
        _myContracts = allContracts.where((c) => c.customerId == userId && c.status != 'Đã thanh lý').toList();
      });
    });
  }

  void _onContractChanged(String? val) {
    setState(() {
      _selectedContractId = val;
      _selectedDeviceId = null;
      if (val != null) {
        final c = _myContracts.firstWhere((c) => c.id == val);
        _contractDevices = c.deviceIds ?? [];
      } else {
        _contractDevices = [];
      }
    });
  }

  void _addMockImage() {
    setState(() {
      _mockAttachments.add(AttachmentModel(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        localPath: 'assets/images/placeholder.png',
        type: 'image'
      ));
    });
  }

  void _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedContractId == null || _selectedDeviceId == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Vui lòng chọn Hợp đồng và Thiết bị'),
        backgroundColor: AppColors.error,
      ));
      return;
    }

    final inc = IncidentModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      code: 'INC-2026-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}',
      contractId: _selectedContractId!,
      deviceId: _selectedDeviceId!,
      issueType: _selectedIssueType,
      description: _descCtrl.text,
      severity: _selectedSeverity,
      occurrenceTime: DateTime.now().toString().substring(0, 16),
      status: 'Chờ xử lý',
      createdAt: DateTime.now().toString().substring(0, 16),
      attachments: _mockAttachments,
    );

    final success = await context.read<IncidentProvider>().createIncident(inc);
    if (!mounted) return;
    
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Đã gửi yêu cầu hỗ trợ'), 
        backgroundColor: AppColors.success
      ));
      Navigator.pop(context, true);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Lỗi khi gửi yêu cầu'), 
        backgroundColor: AppColors.error
      ));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Báo sự cố mới'),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildLabel('1. Chọn hợp đồng'),
                _buildDropdown(
                  value: _selectedContractId,
                  hint: 'Chọn hợp đồng của bạn',
                  items: _myContracts.map((c) => DropdownMenuItem(value: c.id, child: Text(c.contractCode ?? c.id))).toList(),
                  onChanged: _onContractChanged,
                  validator: (v) => v == null ? 'Vui lòng chọn hợp đồng' : null,
                ),
                
                const SizedBox(height: 24),
                _buildLabel('2. Chọn thiết bị'),
                _buildDropdown(
                  value: _selectedDeviceId,
                  hint: 'Chọn thiết bị gặp sự cố',
                  items: _contractDevices.map((d) => DropdownMenuItem(value: d, child: Text('Mã TB: $d'))).toList(),
                  onChanged: (v) => setState(() => _selectedDeviceId = v),
                  validator: (v) => v == null ? 'Vui lòng chọn thiết bị' : null,
                ),

                const SizedBox(height: 24),
                _buildLabel('3. Loại sự cố'),
                _buildDropdown(
                  value: _selectedIssueType,
                  hint: 'Chọn loại sự cố',
                  items: _issueTypes.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
                  onChanged: (v) => setState(() => _selectedIssueType = v!),
                ),

                const SizedBox(height: 24),
                _buildLabel('4. Mô tả chi tiết'),
                TextFormField(
                  controller: _descCtrl,
                  maxLines: 4,
                  decoration: InputDecoration(
                    hintText: 'Nhập mô tả tình trạng thiết bị...',
                    hintStyle: AppTextStyles.bodySecondary,
                    filled: true,
                    fillColor: AppColors.surface,
                    contentPadding: const EdgeInsets.all(16),
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
                  ),
                  validator: (v) => v == null || v.isEmpty ? 'Vui lòng nhập mô tả' : null,
                ),

                const SizedBox(height: 24),
                _buildLabel('5. Mức độ'),
                _buildDropdown(
                  value: _selectedSeverity,
                  hint: 'Chọn mức độ',
                  items: _severities.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
                  onChanged: (v) => setState(() => _selectedSeverity = v!),
                ),

                const SizedBox(height: 24),
                _buildLabel('6. Hình ảnh đính kèm'),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    ..._mockAttachments.map((a) => Container(
                      width: 80, height: 80,
                      decoration: BoxDecoration(
                        color: AppColors.surface,
                        borderRadius: AppRadius.mdRadius,
                        border: Border.all(color: AppColors.divider),
                      ),
                      child: ClipRRect(
                        borderRadius: AppRadius.mdRadius,
                        child: Icon(Icons.image_outlined, size: 32, color: AppColors.textSecondary),
                      ),
                    )),
                    InkWell(
                      onTap: _addMockImage,
                      borderRadius: AppRadius.mdRadius,
                      child: Container(
                        width: 80, height: 80,
                        decoration: BoxDecoration(
                          color: AppColors.primary.withValues(alpha: 0.1),
                          borderRadius: AppRadius.mdRadius,
                          border: Border.all(color: AppColors.primary, width: 1, style: BorderStyle.solid),
                        ),
                        child: const Icon(Icons.add_a_photo_rounded, color: AppColors.primary),
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 40),
                CustomButton(
                  text: 'Gửi yêu cầu',
                  onPressed: _submit,
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

  Widget _buildDropdown({
    required String? value,
    required String hint,
    required List<DropdownMenuItem<String>> items,
    required void Function(String?) onChanged,
    String? Function(String?)? validator,
  }) {
    return DropdownButtonFormField<String>(
      initialValue: value,
      hint: Text(hint, style: AppTextStyles.bodySecondary),
      items: items,
      onChanged: onChanged,
      validator: validator,
      icon: const Icon(Icons.keyboard_arrow_down_rounded, color: AppColors.textSecondary),
      decoration: InputDecoration(
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
      ),
    );
  }
}
