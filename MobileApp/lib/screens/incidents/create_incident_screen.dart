import 'package:image_picker/image_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/incident_model.dart';
import '../../models/attachment_model.dart';
import '../../models/contract_model.dart';
import '../../models/role_enum.dart';
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
  final List<AttachmentModel> _attachments = [];
  bool _loadingContracts = true;
  bool _picking = false;
  bool _submitting = false;
  String? _contractsError;

  List<ContractModel> _myContracts = [];
  List<ContractDevice> _contractDevices = [];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadContracts());
  }

  @override
  void dispose() {
    _descCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadContracts() async {
    if (!mounted) return;
    final user = context.read<AuthProvider>().currentUser;
    if (user == null || user.role != Role.customer) {
      setState(() {
        _loadingContracts = false;
        _contractsError = 'Chỉ khách hàng có thể báo sự cố cho máy đang thuê.';
      });
      return;
    }
    final provider = context.read<ContractProvider>();
    setState(() => _loadingContracts = true);
    await provider.fetchContracts(user.role, user.id);
    if (!mounted) return;
    setState(() {
      _loadingContracts = false;
      _contractsError = provider.errorMessage;
      _myContracts = provider.errorMessage == null
          ? provider.allContracts.where((contract) =>
              contract.customerId == user.id && contract.statusCode == 1 && contract.devices.isNotEmpty).toList()
          : [];
    });
  }

  void _onContractChanged(String? value) {
    setState(() {
      _selectedContractId = value;
      _selectedDeviceId = null;
      _contractDevices = value == null ? [] : _myContracts.firstWhere((contract) => contract.id == value).devices;
    });
  }

  void _message(String message, {bool success = false}) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(message), backgroundColor: success ? AppColors.success : AppColors.error,
    ));
  }

  Future<void> _takePhoto() async {
    if (_picking || _submitting || _attachments.length >= 3) return;
    setState(() => _picking = true);
    try {
      final photo = await ImagePicker().pickImage(source: ImageSource.camera, maxWidth: 2000, maxHeight: 2000, imageQuality: 90,
        requestFullMetadata: false);
      if (photo == null) return;
      final bytes = await photo.readAsBytes();
      if (bytes.length > 10 * 1024 * 1024) throw Exception('Ảnh không được vượt quá 10 MB.');
      if (mounted) setState(() => _attachments.add(AttachmentModel(id: photo.name, fileName: photo.name, bytes: bytes)));
    } catch (error) { if (mounted) _message(error.toString().replaceFirst('Exception: ', '')); }
    finally { if (mounted) setState(() => _picking = false); }
  }

  Future<void> _pickImages() async {
    if (_picking || _submitting || _attachments.length == 3) return;
    setState(() => _picking = true);
    try {
      final selection = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['jpg', 'jpeg', 'png', 'webp'],
        allowMultiple: true,
        withData: true,
      );
      if (selection == null || !mounted) return;
      if (selection.files.length + _attachments.length > 3) {
        _message('Chỉ có thể đính kèm tối đa 3 ảnh.');
        return;
      }
      final picked = <AttachmentModel>[];
      for (final file in selection.files) {
        final bytes = file.bytes;
        if (bytes == null || bytes.isEmpty || bytes.length > 10 * 1024 * 1024) {
          _message('Ảnh phải đọc được và có dung lượng tối đa 10 MB.');
          return;
        }
        picked.add(AttachmentModel(id: file.name, fileName: file.name, bytes: bytes));
      }
      setState(() => _attachments.addAll(picked));
    } catch (_) {
      if (mounted) _message('Không thể mở trình chọn ảnh.');
    } finally {
      if (mounted) setState(() => _picking = false);
    }
  }

  Future<void> _submit() async {
    if (_submitting || _picking || !_formKey.currentState!.validate()) return;
    final incident = IncidentModel(
      id: '',
      code: '',
      contractId: _selectedContractId!,
      deviceId: _selectedDeviceId!,
      deviceName: _contractDevices.firstWhere((device) => device.id == _selectedDeviceId).label,
      issueType: _selectedIssueType,
      description: _descCtrl.text.trim(),
      severity: _selectedSeverity,
      occurrenceTime: DateTime.now().toString().substring(0, 16),
      status: 'Chờ xử lý',
      createdAt: DateTime.now().toString().substring(0, 16),
      attachments: List.of(_attachments),
    );

    setState(() => _submitting = true);
    try {
      await context.read<IncidentProvider>().createIncident(incident);
      if (!mounted) return;
      _message('Đã gửi báo cáo sự cố.', success: true);
      Navigator.pop(context, true);
    } catch (error) {
      if (mounted) _message(error.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _submitting = false);
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
                if (_loadingContracts)
                  const LinearProgressIndicator()
                else if (_contractsError != null)
                  TextButton(onPressed: _loadContracts, child: const Text('Không tải được hợp đồng. Thử lại'))
                else if (_myContracts.isEmpty)
                  const Text('Bạn chưa có thiết bị thuộc hợp đồng đang thuê.'),
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
                  key: ValueKey(_selectedContractId),
                  value: _selectedDeviceId,
                  hint: 'Chọn thiết bị gặp sự cố',
                  items: _contractDevices.map((d) => DropdownMenuItem(value: d.id, child: Text(d.label, overflow: TextOverflow.ellipsis))).toList(),
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
                  validator: (v) => v == null || v.trim().isEmpty ? 'Vui lòng nhập mô tả' : null,
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
                    for (final attachment in _attachments)
                      InputChip(
                        avatar: CircleAvatar(backgroundImage: MemoryImage(attachment.bytes!)),
                        label: Text(attachment.fileName!),
                        onDeleted: _submitting ? null : () => setState(() => _attachments.remove(attachment)),
                      ),
                    if (_attachments.length < 3 && !kIsWeb && defaultTargetPlatform == TargetPlatform.android)
                      OutlinedButton.icon(onPressed: _submitting || _picking ? null : _takePhoto,
                        icon: const Icon(Icons.camera_alt_outlined), label: const Text('Chụp ảnh')),
                    if (_attachments.length < 3)
                      OutlinedButton.icon(
                        onPressed: _submitting || _picking ? null : _pickImages,
                        icon: const Icon(Icons.add_photo_alternate_outlined),
                        label: const Text('Chọn ảnh'),
                      ),
                  ],
                ),

                const SizedBox(height: 40),
                CustomButton(
                  text: 'Gửi yêu cầu',
                  onPressed: _submitting || _picking || _myContracts.isEmpty ? null : _submit,
                  isLoading: _submitting,
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
    Key? key,
    required String? value,
    required String hint,
    required List<DropdownMenuItem<String>> items,
    required void Function(String?) onChanged,
    String? Function(String?)? validator,
  }) {
    final bool hasValue = value != null && items.any((item) => item.value == value);
    return DropdownButtonFormField<String>(
      key: key,
      isExpanded: true,
      initialValue: hasValue ? value : null,
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
