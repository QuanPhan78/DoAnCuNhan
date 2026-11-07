import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../services/api_config.dart';
import '../services/api_session.dart';

Future<Uint8List> loadContractImage(String path) async {
  final base = Uri.parse(ApiConfig.baseUrl);
  final uri = base.resolve(path);
  if (uri.origin != base.origin || !uri.path.startsWith('/uploads/')) throw Exception('Địa chỉ ảnh không hợp lệ.');
  final response = await ApiSession.get(uri);
  if (response.statusCode != 200) throw Exception('Không tải được ảnh (${response.statusCode}).');
  return response.bodyBytes;
}

class AuthenticatedImage extends StatefulWidget {
  final String path;
  final double height;
  const AuthenticatedImage({super.key, required this.path, this.height = 140});
  @override
  State<AuthenticatedImage> createState() => _AuthenticatedImageState();
}
class _AuthenticatedImageState extends State<AuthenticatedImage> {
  late Future<Uint8List> _image;
  @override
  void initState() { super.initState(); _image = loadContractImage(widget.path); }
  @override
  void didUpdateWidget(AuthenticatedImage oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.path != widget.path) _image = loadContractImage(widget.path);
  }
  @override
  Widget build(BuildContext context) => FutureBuilder<Uint8List>(future: _image, builder: (_, snapshot) {
    if (snapshot.hasError) return const Text('Không thể xem ảnh.');
    if (!snapshot.hasData) return SizedBox(height: widget.height, child: const Center(child: CircularProgressIndicator()));
    return Image.memory(snapshot.data!, height: widget.height, fit: BoxFit.contain);
  });
}
