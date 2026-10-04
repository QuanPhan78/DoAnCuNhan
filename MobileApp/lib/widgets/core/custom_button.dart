import 'package:flutter/material.dart';
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
