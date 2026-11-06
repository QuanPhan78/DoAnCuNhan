import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../models/device_model.dart';
import '../../services/api_config.dart';
import 'device_datasource.dart';

class RemoteDeviceDataSource implements DeviceDataSource {
  final String? _baseUrl;
  String get baseUrl => _baseUrl ?? ApiConfig.baseUrl;

  RemoteDeviceDataSource({String? baseUrl}) : _baseUrl = baseUrl;

  @override
  Future<List<DeviceModel>> getDevices() async {
    final response = await http.get(Uri.parse('$baseUrl/devices'));

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
      return data.map((jsonItem) => DeviceModel(
        id: jsonItem['id']?.toString() ?? '',
        code: jsonItem['code'],
        name: jsonItem['name'] ?? '',
        type: jsonItem['type'] ?? 'Khác',
        brand: jsonItem['brand'],
        model: jsonItem['model'],
        serialNumber: jsonItem['serialNumber'],
        specifications: jsonItem['specifications'],
        condition: jsonItem['condition'],
        rentalStatus: jsonItem['rentalStatus'] ?? 'Sẵn sàng',
        rentalPrice: jsonItem['rentalPrice'] != null ? (jsonItem['rentalPrice'] as num).toDouble() : null,
        description: jsonItem['description'],
        imageUrl: jsonItem['imageUrl'],
      )).toList();
    } else {
      throw Exception('Không thể tải danh sách thiết bị: ${response.statusCode}');
    }
  }

  @override
  Future<DeviceModel> getDeviceById(String id) async {
    final devices = await getDevices();
    return devices.firstWhere(
      (d) => d.id == id,
      orElse: () => throw Exception('Không tìm thấy thiết bị với ID: $id'),
    );
  }
}