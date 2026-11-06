import '../models/installation_model.dart';
import '../datasources/installation/installation_datasource.dart';

class InstallationRepository {
  final InstallationDataSource _dataSource;
  InstallationRepository(this._dataSource);

  Future<InstallationModel?> getInstallationByContractId(String contractId) {
    return _dataSource.getInstallationByContractId(contractId);
  }
}
