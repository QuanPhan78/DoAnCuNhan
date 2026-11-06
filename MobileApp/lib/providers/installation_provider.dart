import 'package:flutter/material.dart';
import '../models/installation_model.dart';
import '../repositories/installation_repository.dart';

class InstallationProvider with ChangeNotifier {
  final InstallationRepository _repository;

  InstallationProvider(this._repository);

  InstallationModel? _currentInstallation;
  bool _isLoading = false;

  InstallationModel? get currentInstallation => _currentInstallation;
  bool get isLoading => _isLoading;

  Future<void> fetchInstallation(String contractId) async {
    _isLoading = true;
    notifyListeners();

    _currentInstallation = await _repository.getInstallationByContractId(contractId);
    
    _isLoading = false;
    notifyListeners();
  }

  Future<bool> confirmInstallation(String contractId) async {
    final success = await _repository.confirmInstallation(contractId);
    if (success) {
      await fetchInstallation(contractId);
    }
    return success;
  }

  Future<bool> completeInstallation(String contractId) async {
    final success = await _repository.completeInstallation(contractId);
    if (success) {
      await fetchInstallation(contractId);
    }
    return success;
  }

  Future<bool> completeContract(String contractId) async {
    return await _repository.completeContract(contractId);
  }
}