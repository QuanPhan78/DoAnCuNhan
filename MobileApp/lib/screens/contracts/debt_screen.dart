import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../services/customer_contract_service.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';
import '../../widgets/photo_field.dart';

class DebtScreen extends StatefulWidget {
  final String? contractId;
  const DebtScreen({super.key, this.contractId});
  @override
  State<DebtScreen> createState() => _DebtScreenState();
}

class _DebtScreenState extends State<DebtScreen> with WidgetsBindingObserver {
  late Future<List<Map<String, dynamic>>> _rows;
  int? _paying;
  @override
  void initState() { super.initState(); WidgetsBinding.instance.addObserver(this); _rows = CustomerContractService.debts(); }
  @override
  void dispose() { WidgetsBinding.instance.removeObserver(this); super.dispose(); }
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) { if (state == AppLifecycleState.resumed) _reload(); }
  void _reload() { if (mounted) setState(() { _rows = CustomerContractService.debts(); }); }
  String _money(dynamic v) => '${NumberFormat('#,##0', 'vi_VN').format(v ?? 0)} đ';
  void _message(Object e) { if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString().replaceFirst('Exception: ', '')))); }

  Future<void> _vnPay(int id) async {
    if (_paying != null) return;
    setState(() => _paying = id);
    try {
      final uri = await CustomerContractService.vnPay(id);
      bool launched = false;
      try {
        launched = await launchUrl(uri, mode: LaunchMode.inAppBrowserView);
      } catch (_) {
        launched = false;
      }
      if (!launched) {
        launched = await launchUrl(uri, mode: LaunchMode.externalApplication);
      }
      if (!launched) throw Exception('Không mở được trang VNPay.');
    } catch (error) { _message(error); }
    finally { if (mounted) setState(() => _paying = null); }
  }

  Future<void> _transfer(Map<String, dynamic> row) async {
    final changed = await Navigator.push<bool>(context, MaterialPageRoute(builder: (_) => _TransferScreen(row: row)));
    if (changed == true) { _message('Đã gửi biên lai. Vui lòng chờ đối soát.'); _reload(); }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: CustomAppBar(title: 'Sổ công nợ', actions: [IconButton(onPressed: _reload,
      tooltip: 'Tải lại công nợ', icon: const Icon(Icons.refresh))]),
    body: FutureBuilder<List<Map<String, dynamic>>>(future: _rows, builder: (context, snapshot) {
      if (snapshot.hasError) { return Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
        Text(snapshot.error.toString().replaceFirst('Exception: ', '')), TextButton(onPressed: _reload, child: const Text('Thử lại'))])); }
      if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
      final rows = snapshot.data!.where((r) => widget.contractId == null || '${r['contractId']}' == widget.contractId).toList();
      if (rows.isEmpty) return const Center(child: Text('Chưa có kỳ hạn thanh toán.'));
      final total = rows.fold<num>(0, (sum, r) => sum + (r['canPay'] == true ? r['balance'] as num : 0));
      return RefreshIndicator(onRefresh: () async { _reload(); await _rows; }, child: ListView(
        physics: const AlwaysScrollableScrollPhysics(), padding: const EdgeInsets.all(16), children: [
        Padding(padding: const EdgeInsets.all(12), child: Text('Cần thanh toán: ${_money(total)}', style: Theme.of(context).textTheme.titleLarge)),
        ...rows.map((r) {
          final id = (r['id'] as num).toInt();
          final confirmed = r['confirmationStatus'] == 1;
          return Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            Text('HD-${r['contractId']} · Kỳ ${r['period']}', style: Theme.of(context).textTheme.titleMedium),
            Text('Đến hạn: ${DateFormat('dd/MM/yyyy').format(DateTime.parse(r['dueDate']))}'),
            Text('${r['agingLabel']} · Còn ${_money(r['balance'])}'),
            if (r['isFirstPayment'] == true) const Text('Khoản đầu gồm cọc bảo đảm và tiền thuê kỳ đầu.'),
            if (confirmed) const Padding(padding: EdgeInsets.symmetric(vertical: 8), child: Text('Biên lai đang chờ đối soát.')),
            if (r['canPay'] == true) ...[
              const SizedBox(height: 8),
              OutlinedButton.icon(onPressed: () => _transfer(r), icon: const Icon(Icons.qr_code), label: const Text('VietQR / Biên lai')),
              if (r['canVnPay'] == true) CustomButton(text: 'Thanh toán VNPay', isLoading: _paying == id,
                onPressed: _paying == null ? () => _vnPay(id) : null),
            ],
            if (r['canPay'] != true && (r['balance'] as num) > 0) const Text('Chưa đến bước thanh toán. Vui lòng kiểm tra hợp đồng.'),
          ])));
        }),
      ]));
    }),
  );
}

class _TransferScreen extends StatefulWidget {
  final Map<String, dynamic> row;
  const _TransferScreen({required this.row});
  @override
  State<_TransferScreen> createState() => _TransferScreenState();
}

class _TransferScreenState extends State<_TransferScreen> {
  final _reference = TextEditingController();
  PickedPhoto? _image;
  bool _busy = false;
  String? _error;
  @override
  void dispose() { _reference.dispose(); super.dispose(); }
  Future<void> _send() async {
    if (_busy) return;
    if (_image == null || _reference.text.trim().isEmpty) { setState(() => _error = 'Nhập mã giao dịch và chọn ảnh biên lai.'); return; }
    setState(() { _busy = true; _error = null; });
    try {
      await CustomerContractService.sendReceipt((widget.row['id'] as num).toInt(), _reference.text.trim(), _image!);
      if (mounted) Navigator.pop(context, true);
    } catch (error) { if (mounted) setState(() => _error = error.toString().replaceFirst('Exception: ', '')); }
    finally { if (mounted) setState(() => _busy = false); }
  }
  @override
  Widget build(BuildContext context) {
    final r = widget.row;
    final bank = r['bank'] as Map;
    Widget copy(String label, String value) => ListTile(contentPadding: EdgeInsets.zero,
      title: Text(label), subtitle: SelectableText(value), trailing: IconButton(tooltip: 'Sao chép $label',
        icon: const Icon(Icons.copy), onPressed: () => Clipboard.setData(ClipboardData(text: value))));
    return Scaffold(appBar: const CustomAppBar(title: 'Chuyển khoản'), body: ListView(padding: const EdgeInsets.all(24), children: [
      if (r['qrUrl'] != null) Image.network(r['qrUrl'], height: 250, errorBuilder: (_, e, s) =>
        const Padding(padding: EdgeInsets.all(16), child: Text('Không tải được mã QR. Bạn có thể dùng thông tin chuyển khoản bên dưới.'))),
      Text('${bank['bankName']} · ${bank['accountName']}', style: Theme.of(context).textTheme.titleMedium),
      copy('Số tài khoản', '${bank['accountNumber']}'),
      copy('Số tiền', '${NumberFormat('#,##0', 'vi_VN').format(r['balance'])} đ'),
      copy('Nội dung chuyển khoản', '${r['reference']}'),
      if (r['canSendReceipt'] == true) ...[
        const Divider(height: 32),
        TextField(controller: _reference, enabled: !_busy, maxLength: 100, decoration: const InputDecoration(labelText: 'Mã giao dịch ngân hàng')),
        PhotoField(label: 'Ảnh biên lai', value: _image, enabled: !_busy, onChanged: (p) => setState(() => _image = p)),
        if (_error != null) Padding(padding: const EdgeInsets.symmetric(vertical: 12), child: Text(_error!, style: const TextStyle(color: Colors.red))),
        const SizedBox(height: 16),
        CustomButton(text: 'Gửi biên lai để đối soát', onPressed: _busy ? null : _send, isLoading: _busy),
      ] else const Padding(padding: EdgeInsets.all(16), child: Text('Biên lai đã được gửi. Vui lòng chờ nhân viên đối soát.')),
    ]));
  }
}
