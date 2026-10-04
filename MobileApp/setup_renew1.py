import os
import json

# 1. Renewal Model
os.makedirs("lib/models", exist_ok=True)
model_code = """
class RenewalModel {
  final String id;
  final String contractId;
  final String customerId;
  final String duration;
  final String notes;
  final String status; // Chờ xử lý, Đã duyệt, Từ chối, Hoàn tất
  final String requestedAt;

  RenewalModel({
    required this.id,
    required this.contractId,
    required this.customerId,
    required this.duration,
    required this.notes,
    required this.status,
    required this.requestedAt,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'contractId': contractId,
      'customerId': customerId,
      'duration': duration,
      'notes': notes,
      'status': status,
      'requestedAt': requestedAt,
    };
  }

  factory RenewalModel.fromJson(Map<String, dynamic> json) {
    return RenewalModel(
      id: json['id'],
      contractId: json['contractId'],
      customerId: json['customerId'],
      duration: json['duration'],
      notes: json['notes'],
      status: json['status'],
      requestedAt: json['requestedAt'],
    );
  }
}
"""
with open("lib/models/renewal_model.dart", "w", encoding="utf-8") as f: f.write(model_code.strip())

# 2. DataSource and Repo
os.makedirs("lib/datasources/renewal", exist_ok=True)
ds_abs = """import '../../models/renewal_model.dart';

abstract class RenewalDataSource {
  Future<bool> submitRenewalRequest(RenewalModel request);
}
"""
with open("lib/datasources/renewal/renewal_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_abs.strip())

ds_loc = """import '../../models/renewal_model.dart';
import 'renewal_datasource.dart';

class LocalRenewalDataSource implements RenewalDataSource {
  // Mock in-memory storage cho các yêu cầu gia hạn
  static final List<RenewalModel> _requests = [];

  @override
  Future<bool> submitRenewalRequest(RenewalModel request) async {
    await Future.delayed(const Duration(milliseconds: 500));
    _requests.add(request);
    return true; // Luôn thành công trong mock
  }
}
"""
with open("lib/datasources/renewal/local_renewal_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_loc.strip())

ds_rem = """import '../../models/renewal_model.dart';
import 'renewal_datasource.dart';

class RemoteRenewalDataSource implements RenewalDataSource {
  @override
  Future<bool> submitRenewalRequest(RenewalModel request) async {
    throw UnimplementedError('API chưa có sẵn');
  }
}
"""
with open("lib/datasources/renewal/remote_renewal_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_rem.strip())

repo = """import '../models/renewal_model.dart';
import '../datasources/renewal/renewal_datasource.dart';

class RenewalRepository {
  final RenewalDataSource _dataSource;
  RenewalRepository(this._dataSource);

  Future<bool> submitRenewalRequest(RenewalModel request) {
    return _dataSource.submitRenewalRequest(request);
  }
}
"""
with open("lib/repositories/renewal_repository.dart", "w", encoding="utf-8") as f: f.write(repo.strip())

# 3. Provider
os.makedirs("lib/providers", exist_ok=True)
prov = """import 'package:flutter/material.dart';
import '../models/renewal_model.dart';
import '../repositories/renewal_repository.dart';

class RenewalProvider with ChangeNotifier {
  final RenewalRepository _repository;
  RenewalProvider(this._repository);

  bool _isSubmitting = false;
  bool get isSubmitting => _isSubmitting;

  Future<bool> submitRenewalRequest({
    required String contractId,
    required String customerId,
    required String duration,
    required String notes,
  }) async {
    _isSubmitting = true;
    notifyListeners();

    final request = RenewalModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      contractId: contractId,
      customerId: customerId,
      duration: duration,
      notes: notes,
      status: 'Chờ xử lý',
      requestedAt: DateTime.now().toString(),
    );

    try {
      final success = await _repository.submitRenewalRequest(request);
      return success;
    } catch (e) {
      return false;
    } finally {
      _isSubmitting = false;
      notifyListeners();
    }
  }
}
"""
with open("lib/providers/renewal_provider.dart", "w", encoding="utf-8") as f: f.write(prov.strip())

# Inject Provider
def insert_provider(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "RenewalProvider" not in content:
        import_str = "import 'package:quan_ly_cho_thue_thiet_bi/providers/renewal_provider.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/repositories/renewal_repository.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/datasources/renewal/local_renewal_datasource.dart';\n"
        if "package:quan_ly_cho_thue_thiet_bi" not in content and "main.dart" in file_path:
            import_str = "import 'providers/renewal_provider.dart';\nimport 'repositories/renewal_repository.dart';\nimport 'datasources/renewal/local_renewal_datasource.dart';\n"
        content = import_str + content
        provider_str = """
          ChangeNotifierProvider(
            create: (_) => RenewalProvider(
              RenewalRepository(LocalRenewalDataSource()),
            ),
          ),"""
        content = content.replace("providers: [", "providers: [" + provider_str)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

insert_provider("lib/main.dart")
insert_provider("test/widget_test.dart")

print("Renewal layer setup complete.")