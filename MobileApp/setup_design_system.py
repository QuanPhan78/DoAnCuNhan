import os
import re

os.makedirs("lib/theme", exist_ok=True)

app_colors = """import 'package:flutter/material.dart';

class AppColors {
  // Brand Colors
  static const Color primary = Color(0xFF1565C0); // Xanh dÆ°Æ¡ng Ä‘áº­m chuyĂªn nghiá»‡p
  static const Color primaryLight = Color(0xFF5E92F3);
  static const Color primaryDark = Color(0xFF003C8F);
  static const Color secondary = Color(0xFF039BE5); // Xanh nhĂ¡nh thá»ƒ hiá»‡n tech/modern

  // Background & Surface
  static const Color background = Color(0xFFF8FAFC); // XĂ¡m nháº¡t tráº¯ng tĂ´n ná» n
  static const Color surface = Colors.white;

  // Text Colors
  static const Color textPrimary = Color(0xFF1E293B); // Slate 800 - XĂ¡m Ä‘áº­m, dá»… Ä‘á» c hÆ¡n Ä‘en thuáº§n
  static const Color textSecondary = Color(0xFF64748B); // Slate 500

  // Border & Divider
  static const Color divider = Color(0xFFE2E8F0); // Slate 200

  // Semantic / Status Colors
  static const Color error = Color(0xFFEF4444);
  static const Color success = Color(0xFF10B981);
  static const Color warning = Color(0xFFF59E0B);
  static const Color info = Color(0xFF3B82F6);
}
"""
with open("lib/theme/app_colors.dart", "w", encoding="utf-8") as f: f.write(app_colors)

app_text_styles = """import 'package:flutter/material.dart';
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
"""
with open("lib/theme/app_text_styles.dart", "w", encoding="utf-8") as f: f.write(app_text_styles)

app_spacing = """class AppSpacing {
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 12.0;
  static const double lg = 16.0;
  static const double xl = 24.0;
  static const double xxl = 32.0;
  static const double xxxl = 48.0;
}
"""
with open("lib/theme/app_spacing.dart", "w", encoding="utf-8") as f: f.write(app_spacing)

app_radius = """import 'package:flutter/material.dart';

class AppRadius {
  static const double sm = 4.0;
  static const double md = 8.0;
  static const double lg = 12.0;
  static const double xl = 16.0;
  static const double round = 999.0;

  static BorderRadius get smRadius => BorderRadius.circular(sm);
  static BorderRadius get mdRadius => BorderRadius.circular(md);
  static BorderRadius get lgRadius => BorderRadius.circular(lg);
  static BorderRadius get xlRadius => BorderRadius.circular(xl);
}
"""
with open("lib/theme/app_radius.dart", "w", encoding="utf-8") as f: f.write(app_radius)

app_shadows = """import 'package:flutter/material.dart';

class AppShadows {
  static List<BoxShadow> get cardShadow => [
    BoxShadow(
      color: Colors.black.withValues(alpha: 0.05),
      blurRadius: 10,
      offset: const Offset(0, 4),
    ),
  ];

  static List<BoxShadow> get dropShadow => [
    BoxShadow(
      color: Colors.black.withValues(alpha: 0.1),
      blurRadius: 15,
      offset: const Offset(0, 8),
    ),
  ];
}
"""
with open("lib/theme/app_shadows.dart", "w", encoding="utf-8") as f: f.write(app_shadows)

app_theme = """import 'package:flutter/material.dart';
import 'app_colors.dart';
import 'app_text_styles.dart';
import 'app_radius.dart';

class AppTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.primary,
        primary: AppColors.primary,
        secondary: AppColors.secondary,
        surface: AppColors.surface,
        error: AppColors.error,
      ).copyWith(surface: AppColors.background), // Scaffold background fallback
      scaffoldBackgroundColor: AppColors.background,
      
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white, letterSpacing: -0.5),
        iconTheme: IconThemeData(color: Colors.white),
      ),
      
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(borderRadius: AppRadius.mdRadius),
          textStyle: AppTextStyles.button,
        ),
      ),
      
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.primary,
          side: const BorderSide(color: AppColors.primary, width: 1.5),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(borderRadius: AppRadius.mdRadius),
          textStyle: AppTextStyles.button.copyWith(color: AppColors.primary),
        ),
      ),
      
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: AppColors.primary,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          textStyle: AppTextStyles.button.copyWith(color: AppColors.primary),
        ),
      ),
      
      cardTheme: CardTheme(
        color: AppColors.surface,
        elevation: 0, // Using custom shadows if needed, or 0 for clean look
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: AppRadius.lgRadius,
          side: const BorderSide(color: AppColors.divider, width: 1), // Tinh táº¿, ko quĂ¡ Ä‘áº­m
        ),
      ),
      
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.surface,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(borderRadius: AppRadius.mdRadius, borderSide: const BorderSide(color: AppColors.divider)),
        enabledBorder: OutlineInputBorder(borderRadius: AppRadius.mdRadius, borderSide: const BorderSide(color: AppColors.divider)),
        focusedBorder: OutlineInputBorder(borderRadius: AppRadius.mdRadius, borderSide: const BorderSide(color: AppColors.primary, width: 1.5)),
        errorBorder: OutlineInputBorder(borderRadius: AppRadius.mdRadius, borderSide: const BorderSide(color: AppColors.error)),
        labelStyle: AppTextStyles.bodySecondary,
        hintStyle: AppTextStyles.bodySecondary,
      ),
      
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: AppColors.surface,
        selectedItemColor: AppColors.primary,
        unselectedItemColor: AppColors.textSecondary,
        selectedLabelStyle: TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
        unselectedLabelStyle: TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),
      
      dividerTheme: const DividerThemeData(
        color: AppColors.divider,
        thickness: 1,
        space: 1,
      ),
      
      snackBarTheme: const SnackBarThemeData(
        backgroundColor: AppColors.textPrimary,
        contentTextStyle: TextStyle(color: Colors.white),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}
"""
with open("lib/theme/app_theme.dart", "w", encoding="utf-8") as f: f.write(app_theme)

# Update main.dart to use AppTheme
main_path = "lib/main.dart"
with open(main_path, "r", encoding="utf-8") as f:
    main_content = f.read()

if "AppTheme.lightTheme" not in main_content:
    main_content = main_content.replace(
        "import 'routes/app_router.dart';",
        "import 'routes/app_router.dart';\nimport 'theme/app_theme.dart';"
    )
    # Search for theme: ThemeData(...) and replace it
    main_content = re.sub(
        r"theme:\s*ThemeData\([^)]*\),",
        "theme: AppTheme.lightTheme,",
        main_content
    )
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(main_content)

print("Design System Created Successfully")