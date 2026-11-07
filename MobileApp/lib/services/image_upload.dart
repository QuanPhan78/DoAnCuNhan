import 'dart:typed_data';

/// Android's picker can re-encode a PNG as JPEG while retaining its old name.
/// Keep the bytes and align the multipart filename with their actual format.
class ImageUpload {
  static String fileName(String original, Uint8List bytes) {
    bool startsWith(List<int> header) {
      if (bytes.length < header.length) return false;
      for (var i = 0; i < header.length; i++) {
        if (bytes[i] != header[i]) return false;
      }
      return true;
    }

    final String extension;
    if (startsWith([137, 80, 78, 71, 13, 10, 26, 10])) {
      extension = 'png';
    } else if (startsWith([255, 216, 255])) {
      extension = 'jpg';
    } else if (startsWith([82, 73, 70, 70]) && bytes.length >= 12 &&
        bytes[8] == 87 && bytes[9] == 69 && bytes[10] == 66 && bytes[11] == 80) {
      extension = 'webp';
    } else {
      throw Exception('Ảnh phải có nội dung PNG, JPG hoặc WEBP hợp lệ.');
    }
    final base = original.replaceAll('\\', '/').split('/').last;
    final dot = base.lastIndexOf('.');
    final stem = (dot > 0 ? base.substring(0, dot) : base)
        .replaceAll(RegExp(r'[\x00-\x1f"]'), '_');
    return '${stem.isEmpty ? 'photo' : stem}.$extension';
  }
}
