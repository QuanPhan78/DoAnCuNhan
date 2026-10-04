import os

code = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/feedback_model.dart';
import '../../providers/feedback_provider.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';

class CreateFeedbackScreen extends StatefulWidget {
  const CreateFeedbackScreen({super.key});

  @override
  State<CreateFeedbackScreen> createState() => _CreateFeedbackScreenState();
}

class _CreateFeedbackScreenState extends State<CreateFeedbackScreen> {
  final _formKey = GlobalKey<FormState>();
  String _selectedType = 'Chung';
  final _refCtrl = TextEditingController();
  final _contentCtrl = TextEditingController();
  int _rating = 5;

  final List<String> _types = ['Chung', 'Hợp đồng', 'Thiết bị', 'Lắp đặt', 'Bảo trì', 'Sửa chữa', 'Chất lượng phục vụ'];

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    
    final fb = FeedbackModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      feedbackCode: 'FB-2026-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}',
      contractId: (_selectedType == 'Hợp đồng') ? _refCtrl.text : null,
      maintenanceId: (_selectedType == 'Bảo trì' || _selectedType == 'Sửa chữa') ? _refCtrl.text : null,
      content: _contentCtrl.text,
      rating: _rating,
      status: 'Mới tạo',
      createdAt: DateTime.now().toString().substring(0, 16),
    );

    final success = await context.read<FeedbackProvider>().createFeedback(fb);
    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Đã gửi phản hồi'), backgroundColor: AppColors.success));
      Navigator.pop(context, true);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Lỗi khi gửi phản hồi'), backgroundColor: AppColors.error));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Gửi Phản hồi'),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildLabel('Chủ đề'),
                DropdownButtonFormField<String>(
                  value: _selectedType,
                  items: _types.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
                  onChanged: (v) => setState(() {
                    _selectedType = v!;
                    _refCtrl.clear();
                  }),
                  icon: const Icon(Icons.keyboard_arrow_down_rounded, color: AppColors.textSecondary),
                  decoration: _buildInputDecoration('Chọn chủ đề'),
                ),
                
                if (_selectedType == 'Hợp đồng' || _selectedType == 'Bảo trì' || _selectedType == 'Sửa chữa') ...[
                  const SizedBox(height: 24),
                  _buildLabel('Mã $_selectedType liên quan'),
                  TextFormField(
                    controller: _refCtrl,
                    decoration: _buildInputDecoration('Nhập mã $_selectedType...'),
                  ),
                ],
                
                const SizedBox(height: 24),
                _buildLabel('Nội dung phản hồi'),
                TextFormField(
                  controller: _contentCtrl,
                  maxLines: 5,
                  decoration: _buildInputDecoration('Vui lòng chia sẻ chi tiết trải nghiệm của bạn...'),
                  validator: (v) => v == null || v.isEmpty ? 'Vui lòng nhập nội dung' : null,
                ),
                
                const SizedBox(height: 32),
                Center(
                  child: Column(
                    children: [
                      Text('Bạn đánh giá dịch vụ thế nào?', style: AppTextStyles.h2.copyWith(fontSize: 16)),
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: List.generate(5, (index) {
                          return GestureDetector(
                            onTap: () => setState(() => _rating = index + 1),
                            child: Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 4.0),
                              child: Icon(
                                index < _rating ? Icons.star_rounded : Icons.star_border_rounded,
                                color: AppColors.warning,
                                size: 48,
                              ),
                            ),
                          );
                        }),
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 48),
                CustomButton(
                  text: 'Gửi phản hồi',
                  onPressed: _submit,
                  isFullWidth: true,
                  type: ButtonType.primary,
                )
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

  InputDecoration _buildInputDecoration(String hint) {
    return InputDecoration(
      hintText: hint,
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
    );
  }
}
"""

with open("lib/screens/feedbacks/create_feedback_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)

print("CreateFeedbackScreen updated.")