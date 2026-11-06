import 'package:flutter/material.dart';
import 'app_colors.dart';

class AppTextStyles {
  static const TextStyle h1 = TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.textPrimary, letterSpacing: -0.5);
  static const TextStyle h2 = TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.textPrimary, letterSpacing: -0.5);
  static const TextStyle h3 = TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: AppColors.textPrimary);
  
  static const TextStyle subtitle = TextStyle(fontSize: 16, fontWeight: FontWeight.w500, color: AppColors.textSecondary);
  
  static const TextStyle body = TextStyle(fontSize: 14, fontWeight: FontWeight.normal, color: AppColors.textPrimary);
  static const TextStyle bodySecondary = TextStyle(fontSize: 14, fontWeight: FontWeight.normal, color: AppColors.textSecondary);
  
  static const TextStyle caption = TextStyle(fontSize: 12, fontWeight: FontWeight.normal, color: AppColors.textSecondary);
  
  static const TextStyle button = TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.white, letterSpacing: 0.5);
}
