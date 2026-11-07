import 'package:flutter/material.dart';
import '../../models/contract_model.dart';
import '../../services/customer_contract_service.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';
import '../../widgets/photo_field.dart';
import '../../widgets/signature_pad.dart';
import 'contract_pdf_viewer_screen.dart';

class SignContractScreen extends StatefulWidget {
  final ContractModel contract;
  const SignContractScreen({super.key, required this.contract});
  @override
  State<SignContractScreen> createState() => _SignContractScreenState();
}

class _SignContractScreenState extends State<SignContractScreen> {
  final _signature = GlobalKey<SignaturePadState>();
  final _periods = TextEditingController(text: '1');
  PickedPhoto? _front, _back;
  late Future<Map<String, dynamic>> _info;
  bool _accepted = false, _busy = false;
  String? _error;
  @override
  void initState() { super.initState(); _info = CustomerContractService.signInfo(widget.contract.id); }
  @override
  void dispose() { _periods.dispose(); super.dispose(); }

  Future<void> _submit(int max) async {
    final periods = int.tryParse(_periods.text);
    if (_busy) return;
    if (!_accepted || _front == null || _back == null || periods == null || periods < 1 || periods > max) {
      setState(() => _error = 'Chọn đủ hai mặt CCCD, số kỳ hợp lệ và xác nhận điều khoản.'); return;
    }
    setState(() { _busy = true; _error = null; });
    try {
      final signature = await _signature.currentState!.exportPng();
      await CustomerContractService.sign(widget.contract.id, periods, signature, _front!, _back!);
      if (mounted) Navigator.pop(context, true);
    } catch (error) {
      if (mounted) setState(() => _error = error.toString().replaceFirst('Exception: ', ''));
    } finally { if (mounted) setState(() => _busy = false); }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: const CustomAppBar(title: 'Ký hợp đồng'),
    body: FutureBuilder<Map<String, dynamic>>(future: _info, builder: (context, snapshot) {
      if (snapshot.hasError) { return Center(child: TextButton(onPressed: () => setState(() {
        _info = CustomerContractService.signInfo(widget.contract.id);
      }), child: const Text('Không tải được hợp đồng. Thử lại'))); }
      if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
      final info = snapshot.data!;
      if (info['canSign'] != true) return const Center(child: Text('Hợp đồng không còn chờ ký.'));
      final max = (info['maxInstallments'] as num).toInt();
      return ListView(padding: EdgeInsets.fromLTRB(24, 24, 24, 64 + MediaQuery.paddingOf(context).bottom), children: [
        Text(widget.contract.contractCode ?? widget.contract.id, style: Theme.of(context).textTheme.titleLarge),
        OutlinedButton.icon(onPressed: _busy ? null : () => Navigator.push(context, MaterialPageRoute(
          builder: (_) => ContractPdfViewerScreen(contract: widget.contract))),
          icon: const Icon(Icons.description_outlined), label: const Text('Đọc nội dung hợp đồng')),
        const SizedBox(height: 16),
        PhotoField(label: 'CCCD mặt trước', value: _front, enabled: !_busy, onChanged: (p) => setState(() => _front = p)),
        const SizedBox(height: 16),
        PhotoField(label: 'CCCD mặt sau', value: _back, enabled: !_busy, onChanged: (p) => setState(() => _back = p)),
        const SizedBox(height: 16),
        TextField(controller: _periods, enabled: !_busy, keyboardType: TextInputType.number,
          decoration: InputDecoration(labelText: 'Số kỳ thanh toán (1–$max)')),
        const SizedBox(height: 24),
        SignaturePad(key: _signature, enabled: !_busy),
        CheckboxListTile(value: _accepted, controlAffinity: ListTileControlAffinity.leading,
          onChanged: _busy ? null : (v) => setState(() => _accepted = v ?? false),
          title: const Text('Tôi đã đọc và đồng ý nội dung hợp đồng.')),
        if (_error != null) Padding(padding: const EdgeInsets.symmetric(vertical: 12), child: Text(_error!, style: const TextStyle(color: Colors.red))),
        CustomButton(text: 'Ký và lưu hợp đồng', isLoading: _busy, onPressed: _busy ? null : () => _submit(max)),
      ]);
    }),
  );
}
