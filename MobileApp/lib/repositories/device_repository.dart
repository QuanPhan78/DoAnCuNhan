import '../models/device_model.dart';
import '../datasources/device/device_datasource.dart';

class DeviceRepository {
  final DeviceDataSource _dataSource;
  DeviceRepository(this._dataSource);

  Future<List<DeviceModel>> getAllDevices() {
    return _dataSource.getDevices();
  }

  Future<DeviceModel> getDeviceById(String id) {
    return _dataSource.getDeviceById(id);
  }
}
