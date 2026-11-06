import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';

class ApiConfig {
  static String? _baseUrl;
  static const String _compiledBaseUrl = String.fromEnvironment('API_BASE_URL');

  /// Returns the active base API URL.
  /// Defaults to:
  /// - `http://10.0.2.2:5000/api` on Android emulator
  /// - `http://localhost:5000/api` on Web, Windows, macOS, Linux
  static String get baseUrl {
    if (_baseUrl != null && _baseUrl!.isNotEmpty) {
      return _baseUrl!;
    }

    if (_compiledBaseUrl.trim().isNotEmpty) {
      return _compiledBaseUrl.trim().replaceFirst(RegExp(r'/+$'), '');
    }

    if (kIsWeb) {
      return 'http://localhost:5000/api';
    }

    try {
      if (Platform.isAndroid) {
        return 'http://10.0.2.2:5000/api';
      }
      if (Platform.isWindows || Platform.isMacOS || Platform.isLinux) {
        return 'http://localhost:5000/api';
      }
    } catch (_) {
      // Fallback if dart:io Platform is unsupported
    }

    return 'http://localhost:5000/api';
  }

  /// Override the base URL at runtime.
  static void setBaseUrl(String url) {
    _baseUrl = url.trim().replaceFirst(RegExp(r'/+$'), '');
  }

  /// Clear the runtime override, retaining API_BASE_URL when supplied at build time.
  static void reset() {
    _baseUrl = null;
  }
}
