import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../services/field_work_service.dart';
import '../../widgets/authenticated_image.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';
import '../../widgets/photo_field.dart';
import '../../widgets/signature_pad.dart';

class HandoverScreen extends StatefulWidget {
  final String contractId;
  const HandoverScreen({super.key, required this.contractId});
  @override
  State<HandoverScreen> createState() => _HandoverScreenState();
}

class _HandoverScreenState extends State<HandoverScreen> {
  final _accessories = TextEditingController(), _condition = TextEditingController(), _notes = TextEditingController();
  final _signature = GlobalKey<SignaturePadState>();
  final List<PickedPhoto> _photos = [];
  late Future<Map<String, dynamic>> _data;
  int _kind = 0;
  bool _busy = false;
  String? _error;
  @override
  void initState() { super.initState(); _data = FieldWorkService.handovers(widget.contractId); }
  @override
  void dispose() { _accessories.dispose(); _condition.dispose(); _notes.dispose(); super.dispose(); }
  Future<void> _save() async {
    if (_busy) return;
    if (_condition.text.trim().isEmpty) { setState(() => _error = 'Nhập tình trạng thiết bị sau kiểm tra.'); return; }
    setState(() { _busy = true; _error = null; });
    try {
      final signature = _signature.currentState;
      await FieldWorkService.handover(widget.contractId, _kind, _accessories.text.trim(), _condition.text.trim(),
        _notes.text.trim(), _photos, signature == null || signature.isEmpty ? null : await signature.exportPng());
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Đã lưu biên bản.')));
        Navigator.pop(context, true);
      }
    } catch (error) { if (mounted) setState(() => _error = error.toString().replaceFirst('Exception: ', '')); }
    finally { if (mounted) setState(() => _busy = false); }
  }
  @override
  Widget build(BuildContext context) => Scaffold(appBar: const CustomAppBar(title: 'Biên bản giao nhận'),
    body: FutureBuilder<Map<String, dynamic>>(future: _data, builder: (_, snapshot) {
      if (snapshot.hasError) { return Center(child: TextButton(onPressed: () => setState(() { _data = FieldWorkService.handovers(widget.contractId); }),
        child: const Text('Không tải được biên bản. Thử lại'))); }
      if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
      final info = snapshot.data!;
      final records = info['records'] as List;
      final allowed = <int>[if (info['canDeliver'] == true) 0, if (info['canReturn'] == true) 1];
      final kind = allowed.contains(_kind) ? _kind : allowed.firstOrNull;
      return ListView(padding: EdgeInsets.fromLTRB(24, 24, 24, 64 + MediaQuery.paddingOf(context).bottom), children: [
        Text('Hợp đồng #${widget.contractId}', style: Theme.of(context).textTheme.titleLarge),
        ...records.map((r) => Card(child: ExpansionTile(title: Text('${r['kind'] == 0 ? "Bàn giao" : "Thu hồi"} #${r['id']}'),
          subtitle: Text(DateFormat('dd/MM/yyyy HH:mm').format(DateTime.parse(r['at']))),
          children: [Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            Text('Phụ kiện: ${r['accessories'] ?? ""}'), Text('Tình trạng: ${r['condition'] ?? ""}'), Text('${r['notes'] ?? ""}'),
            for (final path in (r['photos'] as List).whereType<String>()) AuthenticatedImage(path: path),
            if (r['signature'] != null) AuthenticatedImage(path: r['signature']),
          ]))]))),
        if (kind != null) ...[
          const Divider(height: 32),
          DropdownButtonFormField<int>(initialValue: kind, decoration: const InputDecoration(labelText: 'Loại biên bản'),
            items: allowed.map((v) => DropdownMenuItem(value: v, child: Text(v == 0 ? 'Bàn giao xuất kho' : 'Thu hồi nhập kho'))).toList(),
            onChanged: _busy ? null : (v) => setState(() => _kind = v!)),
          const SizedBox(height: 16),
          TextField(controller: _accessories, enabled: !_busy, maxLength: 2000, decoration: const InputDecoration(labelText: 'Phụ kiện kèm theo')),
          TextField(controller: _condition, enabled: !_busy, maxLines: 3, maxLength: 4000, decoration: const InputDecoration(labelText: 'Tình trạng sau kiểm tra')),
          TextField(controller: _notes, enabled: !_busy, maxLines: 2, maxLength: 4000, decoration: const InputDecoration(labelText: 'Ghi chú')),
          for (int i = 0; i < _photos.length; i++) ListTile(title: Text(_photos[i].name), trailing: IconButton(
            onPressed: _busy ? null : () => setState(() => _photos.removeAt(i)), icon: const Icon(Icons.close))),
          if (_photos.length < 4) PhotoField(label: 'Ảnh thiết bị (${_photos.length}/4)', enabled: !_busy,
            onChanged: (p) => setState(() => _photos.add(p))),
          const SizedBox(height: 16),
          SignaturePad(key: _signature, enabled: !_busy),
          const Text('Khách hàng ký xác nhận giao nhận nếu có.'),
          if (_error != null) Padding(padding: const EdgeInsets.symmetric(vertical: 12), child: Text(_error!, style: const TextStyle(color: Colors.red))),
          CustomButton(text: 'Lưu biên bản', isLoading: _busy, onPressed: _busy ? null : () { _kind = kind; _save(); }),
        ],
      ]);
    }));
}
