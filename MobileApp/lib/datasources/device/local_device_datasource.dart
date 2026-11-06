import 'dart:convert';
import 'package:flutter/services.dart';
import '../../models/device_model.dart';
import 'device_datasource.dart';

class LocalDeviceDataSource implements DeviceDataSource {
  @override
  Future<List<DeviceModel>> getDevices() async {
    await Future.delayed(const Duration(seconds: 1)); // Mô phỏng delay
    final String response = await rootBundle.loadString('assets/mock/devices.json');
    final List<dynamic> data = json.decode(response);
    return data.map((json) => DeviceModel.fromJson(json)).toList();
  }

  @override
  Future<DeviceModel> getDeviceById(String id) async {
    final devices = await getDevices();
    return devices.firstWhere((device) => device.id == id, orElse: () => throw Exception('Không tìm thấy thiết bị'));
  }
}
