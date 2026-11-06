import '../../models/device_model.dart';

abstract class DeviceDataSource {
  Future<List<DeviceModel>> getDevices();
  Future<DeviceModel> getDeviceById(String id);
}
