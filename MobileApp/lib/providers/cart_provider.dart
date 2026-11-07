import 'package:flutter/foundation.dart';
import '../models/device_model.dart';
import '../models/rental_request_model.dart';

class CartProvider extends ChangeNotifier {
  String? _owner;
  final Map<String, (DeviceModel, int)> _items = {};
  void setOwner(String? id) { if (_owner != id) { _owner = id; _items.clear(); } }
  int get count => _items.values.fold(0, (sum, item) => sum + item.$2);
  List<RentalRequestItem> get lines => _items.values.map((item) => RentalRequestItem(
    deviceId: item.$1.id, deviceName: item.$1.name, imageUrl: item.$1.imageUrl,
    quantity: item.$2, rentalPrice: item.$1.rentalPrice ?? 0, subtotal: 0)).toList();
  void add(DeviceModel device) { _items[device.id] = (device, (_items[device.id]?.$2 ?? 0) + 1); notifyListeners(); }
  void change(String id, int quantity) {
    final item = _items[id]; if (item == null) return;
    if (quantity <= 0) { _items.remove(id); } else { _items[id] = (item.$1, quantity); }
    notifyListeners();
  }
  void clear() { _items.clear(); notifyListeners(); }
}
