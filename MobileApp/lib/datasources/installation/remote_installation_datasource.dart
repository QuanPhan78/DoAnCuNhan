import '../../models/installation_model.dart';
import 'installation_datasource.dart';

class RemoteInstallationDataSource implements InstallationDataSource {
  @override
  Future<InstallationModel?> getInstallationByContractId(String contractId) async {
    throw UnimplementedError();
  }

  @override
  Future<bool> updateInstallationStatus(String contractId, String status) async {
    throw UnimplementedError();
  }

  @override
  Future<bool> completeContract(String contractId) async {
    throw UnimplementedError();
  }
}