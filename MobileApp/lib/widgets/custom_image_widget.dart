import 'package:flutter/material.dart';
import '../theme/app_colors.dart';


class CustomImageWidget extends StatelessWidget {
  final String imageUrl;
  final double? width;
  final double? height;
  final BoxFit fit;
  final double? borderRadius;

  const CustomImageWidget({
    super.key,
    required this.imageUrl,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
    this.borderRadius,
  });

  @override
  Widget build(BuildContext context) {
    Widget imageWidget;
    
    String cleanUrl = imageUrl.trim();
    if (cleanUrl.startsWith('/')) {
      cleanUrl = cleanUrl.substring(1);
    }

    if (cleanUrl.startsWith('http://') || cleanUrl.startsWith('https://')) {
      imageWidget = Image.network(
        cleanUrl,
        width: width,
        height: height,
        fit: fit,
        loadingBuilder: (context, child, loadingProgress) {
          if (loadingProgress == null) return child;
          return _buildPlaceholder();
        },
        errorBuilder: (context, error, stackTrace) => _buildError(),
      );
    } else {
      imageWidget = Image.asset(
        cleanUrl,
        width: width,
        height: height,
        fit: fit,
        errorBuilder: (context, error, stackTrace) {
          // Thử tìm trong assets nếu đường dẫn chưa có tiền tố assets/
          if (!cleanUrl.startsWith('assets/')) {
            return Image.asset(
              'assets/$cleanUrl',
              width: width,
              height: height,
              fit: fit,
              errorBuilder: (context, error, stackTrace) => _buildError(),
            );
          }
          return _buildError();
        },
      );
    }

    if (borderRadius != null) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(borderRadius!),
        child: imageWidget,
      );
    }
    
    return imageWidget;
  }

  Widget _buildPlaceholder() {
    return Container(
      width: width,
      height: height,
      color: AppColors.divider.withValues(alpha: 0.5),
      child: const Center(
        child: SizedBox(
          width: 24, height: 24,
          child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary),
        ),
      ),
    );
  }

  Widget _buildError() {
    return Container(
      width: width,
      height: height,
      color: AppColors.divider.withValues(alpha: 0.3),
      child: const Center(
        child: Icon(Icons.image_not_supported_outlined, color: AppColors.textSecondary),
      ),
    );
  }
}
