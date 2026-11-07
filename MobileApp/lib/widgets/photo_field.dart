import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'dart:ui' as ui;
import 'package:image_picker/image_picker.dart';
import '../services/image_upload.dart';

class PickedPhoto {
  final String name;
  final Uint8List bytes;
  const PickedPhoto(this.name, this.bytes);
  String get uploadName => ImageUpload.fileName(name, bytes);
}

class PhotoField extends StatefulWidget {
  final String label;
  final PickedPhoto? value;
  final ValueChanged<PickedPhoto> onChanged;
  final bool enabled;
  const PhotoField({super.key, required this.label, this.value, required this.onChanged, this.enabled = true});

  @override
  State<PhotoField> createState() => _PhotoFieldState();
}

class _PhotoFieldState extends State<PhotoField> {
  bool _picking = false;
  Future<void> _pick(ImageSource source) async {
    setState(() => _picking = true);
    try {
      final image = await ImagePicker().pickImage(source: source, maxWidth: 2000, maxHeight: 2000, imageQuality: 90,
        requestFullMetadata: false);
      if (image == null) return;
      final bytes = await image.readAsBytes();
      if (bytes.length > 5 * 1024 * 1024) throw Exception('Ảnh không được vượt quá 5 MB.');
      final codec = await ui.instantiateImageCodec(bytes);
      codec.dispose();
      if (mounted) widget.onChanged(PickedPhoto(image.name, bytes));
    } catch (error) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error.toString().replaceFirst('Exception: ', ''))));
    } finally { if (mounted) setState(() => _picking = false); }
  }

  @override
  Widget build(BuildContext context) {
    final camera = !kIsWeb && (defaultTargetPlatform == TargetPlatform.android || defaultTargetPlatform == TargetPlatform.iOS);
    final enabled = widget.enabled && !_picking;
    return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
      Text(widget.label, style: Theme.of(context).textTheme.titleMedium),
      if (widget.value != null) Padding(padding: const EdgeInsets.symmetric(vertical: 8),
        child: Image.memory(widget.value!.bytes, height: 140, fit: BoxFit.contain,
          errorBuilder: (_, error, stack) => const Text('Ảnh không đọc được. Vui lòng chọn lại.'))),
      Wrap(spacing: 8, children: [
        if (camera) OutlinedButton.icon(onPressed: enabled ? () => _pick(ImageSource.camera) : null,
          icon: const Icon(Icons.camera_alt_outlined), label: const Text('Chụp ảnh')),
        OutlinedButton.icon(onPressed: enabled ? () => _pick(ImageSource.gallery) : null,
          icon: const Icon(Icons.photo_library_outlined), label: Text(_picking ? 'Đang chọn...' : 'Chọn ảnh')),
      ]),
    ]);
  }
}
