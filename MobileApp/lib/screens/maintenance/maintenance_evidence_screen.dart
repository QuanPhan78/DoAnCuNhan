import 'package:flutter/material.dart';
import '../../services/field_work_service.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';
import '../../widgets/photo_field.dart';

class MaintenanceEvidenceScreen extends StatefulWidget {
  final String ticketId;
  const MaintenanceEvidenceScreen({super.key, required this.ticketId});
  @override
  State<MaintenanceEvidenceScreen> createState() => _MaintenanceEvidenceScreenState();
}
class _MaintenanceEvidenceScreenState extends State<MaintenanceEvidenceScreen> {
  final _notes = TextEditingController();
  PickedPhoto? _photo;
  bool _busy = false;
  String? _error;
  @override
  void dispose() { _notes.dispose(); super.dispose(); }
  Future<void> _save() async {
    if (_busy || _photo == null) return;
    setState(() { _busy = true; _error = null; });
    try {
      await FieldWorkService.evidence(widget.ticketId, _photo!, _notes.text.trim());
      if (mounted) Navigator.pop(context, true);
    } catch (error) { if (mounted) setState(() => _error = error.toString().replaceFirst('Exception: ', '')); }
    finally { if (mounted) setState(() => _busy = false); }
  }
  @override
  Widget build(BuildContext context) => Scaffold(appBar: const CustomAppBar(title: 'Ảnh hiện trường'),
    body: ListView(padding: const EdgeInsets.all(24), children: [
      PhotoField(label: 'Ảnh kiểm tra / sửa chữa', value: _photo, enabled: !_busy, onChanged: (p) => setState(() => _photo = p)),
      TextField(controller: _notes, enabled: !_busy, maxLines: 3, maxLength: 2000, decoration: const InputDecoration(labelText: 'Ghi chú kỹ thuật')),
      if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
      const SizedBox(height: 16),
      CustomButton(text: 'Lưu ảnh minh chứng', isLoading: _busy, onPressed: _busy || _photo == null ? null : _save),
    ]));
}
