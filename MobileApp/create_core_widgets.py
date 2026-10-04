import os

os.makedirs("lib/widgets/core", exist_ok=True)

# 1. Custom Button
custom_button = """import 'package:flutter/material.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';

enum ButtonType { primary, secondary, outline, destructive }

class CustomButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final ButtonType type;
  final bool isLoading;
  final IconData? icon;
  final bool isFullWidth;

  const CustomButton({
    super.key,
    required this.text,
    this.onPressed,
    this.type = ButtonType.primary,
    this.isLoading = false,
    this.icon,
    this.isFullWidth = true,
  });

  @override
  Widget build(BuildContext context) {
    Color bgColor;
    Color textColor;
    BorderSide? border;

    switch (type) {
      case ButtonType.primary:
        bgColor = AppColors.primary;
        textColor = Colors.white;
        break;
      case ButtonType.secondary:
        bgColor = AppColors.secondary;
        textColor = Colors.white;
        break;
      case ButtonType.destructive:
        bgColor = AppColors.error;
        textColor = Colors.white;
        break;
      case ButtonType.outline:
        bgColor = Colors.transparent;
        textColor = AppColors.primary;
        border = const BorderSide(color: AppColors.primary, width: 1.5);
        break;
    }

    if (onPressed == null) {
      bgColor = AppColors.divider;
      textColor = AppColors.textSecondary;
      border = null;
    }

    final content = Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (isLoading) ...[
          SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(strokeWidth: 2, color: textColor),
          ),
          const SizedBox(width: 8),
        ] else if (icon != null) ...[
          Icon(icon, size: 18, color: textColor),
          const SizedBox(width: 8),
        ],
        Text(text, style: AppTextStyles.button.copyWith(color: textColor)),
      ],
    );

    final button = ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: bgColor,
        foregroundColor: textColor,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        shape: RoundedRectangleBorder(
          borderRadius: AppRadius.mdRadius,
          side: border ?? BorderSide.none,
        ),
      ),
      onPressed: isLoading ? null : onPressed,
      child: content,
    );

    return isFullWidth ? SizedBox(width: double.infinity, child: button) : button;
  }
}
"""
with open("lib/widgets/core/custom_button.dart", "w", encoding="utf-8") as f: f.write(custom_button)

# 2. Custom Text Field
custom_textfield = """import 'package:flutter/material.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';

class CustomTextField extends StatelessWidget {
  final TextEditingController? controller;
  final String label;
  final String? hint;
  final IconData? prefixIcon;
  final Widget? suffixIcon;
  final bool obscureText;
  final String? Function(String?)? validator;
  final int maxLines;
  final TextInputType keyboardType;
  final void Function(String)? onChanged;

  const CustomTextField({
    super.key,
    required this.label,
    this.controller,
    this.hint,
    this.prefixIcon,
    this.suffixIcon,
    this.obscureText = false,
    this.validator,
    this.maxLines = 1,
    this.keyboardType = TextInputType.text,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: AppTextStyles.subtitle.copyWith(fontSize: 14)),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          obscureText: obscureText,
          validator: validator,
          maxLines: maxLines,
          keyboardType: keyboardType,
          onChanged: onChanged,
          style: AppTextStyles.body,
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon: prefixIcon != null ? Icon(prefixIcon, color: AppColors.textSecondary) : null,
            suffixIcon: suffixIcon,
          ),
        ),
      ],
    );
  }
}
"""
with open("lib/widgets/core/custom_textfield.dart", "w", encoding="utf-8") as f: f.write(custom_textfield)

# 3. State Widgets (Empty, Error, Loading)
state_widgets = """import 'package:flutter/material.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';

class EmptyState extends StatelessWidget {
  final String message;
  final IconData icon;

  const EmptyState({
    super.key,
    required this.message,
    this.icon = Icons.inbox_outlined,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 64, color: AppColors.textSecondary.withValues(alpha: 0.5)),
          const SizedBox(height: 16),
          Text(message, style: AppTextStyles.subtitle, textAlign: TextAlign.center),
        ],
      ),
    );
  }
}

class ErrorState extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const ErrorState({
    super.key,
    required this.message,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 64, color: AppColors.error),
          const SizedBox(height: 16),
          Text(message, style: AppTextStyles.subtitle.copyWith(color: AppColors.error), textAlign: TextAlign.center),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: onRetry,
            icon: const Icon(Icons.refresh),
            label: const Text('Thử lại'),
          )
        ],
      ),
    );
  }
}

class LoadingState extends StatelessWidget {
  final String? message;

  const LoadingState({super.key, this.message});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(color: AppColors.primary),
          if (message != null) ...[
            const SizedBox(height: 16),
            Text(message!, style: AppTextStyles.subtitle),
          ]
        ],
      ),
    );
  }
}
"""
with open("lib/widgets/core/state_widgets.dart", "w", encoding="utf-8") as f: f.write(state_widgets)

# 4. Confirmation Dialog
confirm_dialog = """import 'package:flutter/material.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import 'custom_button.dart';

class ConfirmationDialog {
  static Future<bool?> show({
    required BuildContext context,
    required String title,
    required String content,
    String confirmText = 'Xác nhận',
    String cancelText = 'Hủy',
    bool isDestructive = false,
  }) {
    return showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: AppRadius.lgRadius),
        title: Text(title, style: AppTextStyles.h3),
        content: Text(content, style: AppTextStyles.body),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text(cancelText, style: AppTextStyles.button.copyWith(color: AppColors.textSecondary)),
          ),
          CustomButton(
            text: confirmText,
            isFullWidth: false,
            type: isDestructive ? ButtonType.destructive : ButtonType.primary,
            onPressed: () => Navigator.pop(ctx, true),
          ),
        ],
      ),
    );
  }
}
"""
with open("lib/widgets/core/confirmation_dialog.dart", "w", encoding="utf-8") as f: f.write(confirm_dialog)

# 5. Custom App Bar
app_bar = """import 'package:flutter/material.dart';
import '../../theme/app_colors.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  final bool centerTitle;

  const CustomAppBar({
    super.key,
    required this.title,
    this.actions,
    this.centerTitle = true,
  });

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: Text(title),
      centerTitle: centerTitle,
      actions: actions,
      backgroundColor: AppColors.primary,
      elevation: 0,
      iconTheme: const IconThemeData(color: Colors.white),
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}
"""
with open("lib/widgets/core/custom_app_bar.dart", "w", encoding="utf-8") as f: f.write(app_bar)
print("Core widgets created.")