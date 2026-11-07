import 'dart:convert';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';

class SignaturePad extends StatefulWidget {
  final bool enabled;
  const SignaturePad({super.key, this.enabled = true});
  @override
  State<SignaturePad> createState() => SignaturePadState();
}

class SignaturePadState extends State<SignaturePad> {
  final _boundary = GlobalKey();
  final List<List<Offset>> _strokes = [];
  bool get isEmpty => !_strokes.any((stroke) => stroke.length > 2);

  Future<String> exportPng() async {
    if (isEmpty) throw Exception('Vui lòng ký tên vào khung.');
    final boundary = _boundary.currentContext!.findRenderObject() as RenderRepaintBoundary;
    final image = await boundary.toImage(pixelRatio: 2);
    try {
      final data = await image.toByteData(format: ui.ImageByteFormat.png);
      return 'data:image/png;base64,${base64Encode(data!.buffer.asUint8List())}';
    } finally { image.dispose(); }
  }

  @override
  Widget build(BuildContext context) => Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
    const Text('Chữ ký khách hàng'),
    const SizedBox(height: 8),
    RepaintBoundary(key: _boundary, child: GestureDetector(
      key: const ValueKey('signature-canvas'),
      onPanStart: !widget.enabled ? null : (d) => setState(() => _strokes.add([d.localPosition])),
      onPanUpdate: !widget.enabled ? null : (d) => setState(() => _strokes.last.add(d.localPosition)),
      child: Container(height: 180, clipBehavior: Clip.hardEdge,
        decoration: BoxDecoration(color: Colors.white, border: Border.all(color: Colors.blueGrey)),
        child: CustomPaint(painter: _SignaturePainter(_strokes), size: Size.infinite)),
    )),
    Align(alignment: Alignment.centerRight, child: TextButton(
      onPressed: widget.enabled ? () => setState(_strokes.clear) : null, child: const Text('Ký lại'))),
  ]);
}

class _SignaturePainter extends CustomPainter {
  final List<List<Offset>> strokes;
  _SignaturePainter(this.strokes);
  @override
  void paint(Canvas canvas, Size size) {
    final pen = Paint()..color = const Color(0xff0f2b5c)..strokeWidth = 2.5..strokeCap = StrokeCap.round;
    for (final stroke in strokes) {
      for (int i = 1; i < stroke.length; i++) { canvas.drawLine(stroke[i - 1], stroke[i], pen); }
    }
  }
  @override
  bool shouldRepaint(covariant _SignaturePainter oldDelegate) => true;
}
