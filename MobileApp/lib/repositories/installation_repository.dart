import '../models/installation_model.dart';
import '../datasources/installation/installation_datasource.dart';

class InstallationRepository {
  final InstallationDataSource _dataSource;
  InstallationRepository(this._dataSource);

  Future<InstallationModel?> getInstallationByContractId(String contractId) {
    return _dataSource.getInstallationByContractId(contractId);
  }

  Future<bool> confirmInstallation(String contractId) {
    return _dataSource.updateInstallationStatus(contractId, 'Đang thực hiện');
  }

  Future<bool> completeInstallation(String contractId) {
    return _dataSource.updateInstallationStatus(contractId, 'Đã hoàn thành');
  }

  Future<bool> completeContract(String contractId) {
    return _dataSource.completeContract(contractId);
  }
}