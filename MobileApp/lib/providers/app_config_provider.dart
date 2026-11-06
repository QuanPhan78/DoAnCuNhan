import 'package:flutter/material.dart';
import '../utils/app_translations.dart';

class AppConfigProvider with ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.light;
  String _language = 'vi'; // 'vi' hoặc 'en'

  ThemeMode get themeMode => _themeMode;
  String get language => _language;
  bool get isDarkMode => _themeMode == ThemeMode.dark;
  bool get isEnglish => _language == 'en';

  String get themeName {
    if (_themeMode == ThemeMode.dark) return isEnglish ? 'Dark Mode' : 'Giao diện Tối';
    if (_themeMode == ThemeMode.system) return isEnglish ? 'System Default' : 'Theo hệ thống';
    return isEnglish ? 'Light Mode' : 'Giao diện Sáng';
  }

  String get languageName => _language == 'en' ? 'English' : 'Tiếng Việt';

  void setThemeMode(ThemeMode mode) {
    _themeMode = mode;
    notifyListeners();
  }

  void setLanguage(String lang) {
    _language = lang;
    notifyListeners();
  }

  String tr(String key) {
    return AppTranslations.tr(key, _language);
  }
}
