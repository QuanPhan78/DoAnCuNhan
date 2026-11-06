import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/core/custom_button.dart';
import '../../widgets/core/custom_textfield.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _cccdController = TextEditingController();
  final _addressController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _cccdController.dispose();
    _addressController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.error_outline, color: Colors.white),
            const SizedBox(width: 8),
            Expanded(child: Text(message)),
          ],
        ),
        backgroundColor: AppColors.error,
        duration: const Duration(seconds: 3),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  Future<void> _handleRegister() async {
    FocusScope.of(context).unfocus();

    final name = _nameController.text.trim();
    final phone = _phoneController.text.trim();
    final email = _emailController.text.trim();
    final cccd = _cccdController.text.trim();
    final address = _addressController.text.trim();
    final password = _passwordController.text;
    final confirmPassword = _confirmPasswordController.text;

    if (name.isEmpty) {
      _showError('Vui lòng nhập họ và tên');
      return;
    }

    if (phone.isEmpty) {
      _showError('Vui lòng nhập số điện thoại');
      return;
    }

    if (phone.length < 9) {
      _showError('Số điện thoại không hợp lệ');
      return;
    }

    if (email.isEmpty || !email.contains('@') || !email.contains('.')) {
      _showError('Email không hợp lệ');
      return;
    }

    if (!RegExp(r'^[0-9]{12}$').hasMatch(cccd)) {
      _showError('Số CCCD phải có đúng 12 chữ số.');
      return;
    }

    if (password.isEmpty || password.length < 6) {
      _showError('Mật khẩu phải từ 6 ký tự trở lên');
      return;
    }

    if (password != confirmPassword) {
      _showError('Mật khẩu xác nhận không khớp');
      return;
    }

    final authProvider = context.read<AuthProvider>();
    final success = await authProvider.register(
      name: name,
      phone: phone,
      email: email,
      password: password,
      address: address.isNotEmpty ? address : null,
      cccd: cccd,
    );

    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Row(
            children: [
              Icon(Icons.check_circle_outline, color: Colors.white),
              SizedBox(width: 8),
              Expanded(child: Text('Đăng ký tài khoản thành công!')),
            ],
          ),
          backgroundColor: AppColors.success,
          duration: Duration(seconds: 2),
          behavior: SnackBarBehavior.floating,
        ),
      );
      Navigator.of(context).pushNamedAndRemoveUntil('/dashboard', (route) => false);
    } else {
      _showError(authProvider.errorMessage ?? 'Đăng ký thất bại');
    }
  }

  @override
  Widget build(BuildContext context) {
    final isLoading = context.watch<AuthProvider>().isLoading;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.textPrimary),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 32.0, vertical: 16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Header
                Center(
                  child: Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withValues(alpha: 0.1),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.person_add_alt_1_rounded, size: 48, color: AppColors.primary),
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  'Đăng ký',
                  style: AppTextStyles.h1.copyWith(fontSize: 26),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 32),

                // Form fields
                CustomTextField(
                  label: 'Họ và tên *',
                  prefixIcon: Icons.badge_outlined,
                  controller: _nameController,
                  enabled: !isLoading,
                  textCapitalization: TextCapitalization.words,
                ),
                const SizedBox(height: 16),

                CustomTextField(
                  label: 'Số điện thoại *',
                  prefixIcon: Icons.phone_outlined,
                  controller: _phoneController,
                  enabled: !isLoading,
                  keyboardType: TextInputType.phone,
                ),
                const SizedBox(height: 16),

                CustomTextField(
                  label: 'Email *',
                  prefixIcon: Icons.email_outlined,
                  controller: _emailController,
                  enabled: !isLoading,
                  keyboardType: TextInputType.emailAddress,
                ),
                const SizedBox(height: 16),

                CustomTextField(
                  label: 'Số CCCD *',
                  hint: '12 chữ số',
                  prefixIcon: Icons.credit_card_outlined,
                  controller: _cccdController,
                  enabled: !isLoading,
                  keyboardType: TextInputType.number,
                ),
                const SizedBox(height: 16),

                CustomTextField(
                  label: 'Địa chỉ',
                  prefixIcon: Icons.location_on_outlined,
                  controller: _addressController,
                  enabled: !isLoading,
                ),
                const SizedBox(height: 16),

                CustomTextField(
                  label: 'Mật khẩu *',
                  hint: 'Tối thiểu 6 ký tự',
                  prefixIcon: Icons.lock_outline_rounded,
                  controller: _passwordController,
                  enabled: !isLoading,
                  obscureText: _obscurePassword,
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                      color: AppColors.textSecondary,
                    ),
                    onPressed: () {
                      setState(() {
                        _obscurePassword = !_obscurePassword;
                      });
                    },
                  ),
                ),
                const SizedBox(height: 16),

                CustomTextField(
                  label: 'Nhập lại mật khẩu *',
                  prefixIcon: Icons.lock_outline_rounded,
                  controller: _confirmPasswordController,
                  enabled: !isLoading,
                  obscureText: _obscureConfirmPassword,
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscureConfirmPassword ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                      color: AppColors.textSecondary,
                    ),
                    onPressed: () {
                      setState(() {
                        _obscureConfirmPassword = !_obscureConfirmPassword;
                      });
                    },
                  ),
                ),
                const SizedBox(height: 32),

                // Register Button
                CustomButton(
                  text: 'Đăng ký ngay',
                  isLoading: isLoading,
                  onPressed: _handleRegister,
                  isFullWidth: true,
                ),
                const SizedBox(height: 24),

                // Already have account
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text('Đã có tài khoản? ', style: AppTextStyles.bodySecondary),
                    TextButton(
                      onPressed: isLoading ? null : () => Navigator.of(context).pop(),
                      style: TextButton.styleFrom(
                        padding: EdgeInsets.zero,
                        minimumSize: Size.zero,
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      child: Text(
                        'Đăng nhập',
                        style: AppTextStyles.button.copyWith(color: AppColors.primary),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
