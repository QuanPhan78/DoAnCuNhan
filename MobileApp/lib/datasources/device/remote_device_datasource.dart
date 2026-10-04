import '../../models/device_model.dart';
import 'device_datasource.dart';

class RemoteDeviceDataSource implements DeviceDataSource {
  @override
  Future<List<DeviceModel>> getDevices() async {
    throw UnimplementedError('API chưa có sẵn');
  }

  @override
  Future<DeviceModel> getDeviceById(String id) async {
    throw UnimplementedError('API chưa có sẵn');
  }
}
