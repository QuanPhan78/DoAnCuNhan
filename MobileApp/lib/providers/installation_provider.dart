import 'package:flutter/material.dart';
import '../models/installation_model.dart';
import '../repositories/installation_repository.dart';
import '../services/staff_task_service.dart';

class InstallationProvider with ChangeNotifier {
  final InstallationRepository _repository;

  InstallationProvider(this._repository);

  InstallationModel? currentInstallation;
  bool isLoading = false;
  String? errorMessage;
  int _request = 0;

  Future<void> fetchInstallation(String contractId) async {
    final request = ++_request;
    isLoading = true;
    errorMessage = null;
    currentInstallation = null;
    notifyListeners();

    try {
      final installation = await _repository.getInstallationByContractId(contractId);
      if (request == _request) currentInstallation = installation;
    } catch (error) {
      if (request == _request) errorMessage = error.toString().replaceFirst('Exception: ', '');
    } finally {
      if (request == _request) {
        isLoading = false;
        notifyListeners();
      }
    }
  }

  Future<void> updateInstallation(InstallationModel task, int status) async {
    await StaffTaskService.update(task.taskId!, status);
    if (currentInstallation?.taskId == task.taskId) await fetchInstallation(task.contractId);
  }
}
