import '../../models/installation_model.dart';

abstract class InstallationDataSource {
  Future<InstallationModel?> getInstallationByContractId(String contractId);
}
