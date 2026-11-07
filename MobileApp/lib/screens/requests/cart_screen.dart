import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../../models/rental_request_model.dart';
import '../../models/rental_status.dart';
import '../../providers/auth_provider.dart';
import '../../providers/cart_provider.dart';
import '../../providers/rental_provider.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';

class CartScreen extends StatefulWidget {
  const CartScreen({super.key});
  @override
  State<CartScreen> createState() => _CartScreenState();
}

class _CartScreenState extends State<CartScreen> {
  final _form = GlobalKey<FormState>();
  final _address = TextEditingController(), _note = TextEditingController(), _promo = TextEditingController();
  DateTime _start = DateUtils.dateOnly(DateTime.now());
  DateTime _end = DateUtils.addDaysToDate(DateTime.now(), 1);
  bool _busy = false;
  @override
  void initState() { super.initState(); _address.text = context.read<AuthProvider>().currentUser?.address ?? ''; }
  @override
  void dispose() { _address.dispose(); _note.dispose(); _promo.dispose(); super.dispose(); }
  Future<void> _date(bool start) async {
    final picked = await showDatePicker(context: context, initialDate: start ? _start : _end,
      firstDate: start ? DateUtils.dateOnly(DateTime.now()) : _start, lastDate: DateTime(DateTime.now().year + 5));
    if (picked != null && mounted) { setState(() {
      if (start) { _start = picked; if (_end.isBefore(_start)) _end = _start.add(const Duration(days: 1)); }
      else { _end = picked; }
    }); }
  }
  Future<void> _quote() async {
    if (_busy || !_form.currentState!.validate()) return;
    final user = context.read<AuthProvider>().currentUser;
    final lines = context.read<CartProvider>().lines;
    if (user == null || lines.isEmpty) return;
    setState(() => _busy = true);
    try {
      final request = RentalRequestModel(id: '', customerId: user.id, items: lines, rentalType: 'Theo ngày',
        startDate: _start, endDate: _end, deliveryAddress: _address.text.trim(), note: _note.text.trim(),
        promoCode: _promo.text.trim().isEmpty ? null : _promo.text.trim(), estimatedAmount: 0,
        status: RentalStatus.pending, createdAt: DateTime.now());
      final quoted = await context.read<RentalProvider>().quoteRental(request);
      if (mounted) Navigator.pushNamed(context, '/rental_confirm', arguments: quoted);
    } catch (error) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error.toString().replaceFirst('Exception: ', ''))));
    } finally { if (mounted) setState(() => _busy = false); }
  }
  @override
  Widget build(BuildContext context) {
    final cart = context.watch<CartProvider>();
    if (cart.lines.isEmpty) return Scaffold(appBar: const CustomAppBar(title: 'Giỏ hàng'), body: const Center(child: Text('Giỏ hàng đang trống.')));
    return Scaffold(appBar: const CustomAppBar(title: 'Giỏ hàng'), body: Form(key: _form, child: ListView(
      padding: const EdgeInsets.all(24), children: [
      ...cart.lines.map((line) => Card(child: Padding(padding: const EdgeInsets.all(12), child: Column(
        crossAxisAlignment: CrossAxisAlignment.start, children: [Text(line.deviceName, style: Theme.of(context).textTheme.titleMedium),
        Row(children: [IconButton(onPressed: _busy ? null : () => cart.change(line.deviceId, line.quantity - 1),
          tooltip: 'Giảm số lượng', icon: const Icon(Icons.remove_circle_outline)), Text('${line.quantity}'),
          IconButton(onPressed: _busy ? null : () => cart.change(line.deviceId, line.quantity + 1),
            tooltip: 'Tăng số lượng', icon: const Icon(Icons.add_circle_outline)), const Spacer(),
          IconButton(onPressed: _busy ? null : () => cart.change(line.deviceId, 0), tooltip: 'Bỏ khỏi giỏ', icon: const Icon(Icons.delete_outline))]),
      ])))),
      const SizedBox(height: 16),
      OutlinedButton(onPressed: _busy ? null : () => _date(true), child: Text('Nhận: ${DateFormat('dd/MM/yyyy').format(_start)}')),
      OutlinedButton(onPressed: _busy ? null : () => _date(false), child: Text('Trả: ${DateFormat('dd/MM/yyyy').format(_end)}')),
      const SizedBox(height: 16),
      TextFormField(controller: _address, enabled: !_busy, decoration: const InputDecoration(labelText: 'Địa chỉ giao thiết bị'),
        validator: (v) => v == null || v.trim().isEmpty ? 'Vui lòng nhập địa chỉ.' : null),
      const SizedBox(height: 16),
      TextField(controller: _promo, enabled: !_busy, decoration: const InputDecoration(labelText: 'Mã khuyến mãi'), textCapitalization: TextCapitalization.characters),
      const SizedBox(height: 16),
      TextField(controller: _note, enabled: !_busy, maxLines: 3, decoration: const InputDecoration(labelText: 'Ghi chú')),
      const SizedBox(height: 24),
      CustomButton(text: 'Xem báo giá', isLoading: _busy, onPressed: _busy ? null : _quote),
    ])));
  }
}
