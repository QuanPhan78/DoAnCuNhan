import os
import json
from base64 import b64decode

# 1. Update pubspec.yaml
pubspec_path = "pubspec.yaml"
with open(pubspec_path, "r", encoding="utf-8") as f:
    pubspec = f.read()

if "assets/images/promotions/" not in pubspec:
    pubspec = pubspec.replace("    - assets/images/devices/", "    - assets/images/devices/\n    - assets/images/promotions/")
    with open(pubspec_path, "w", encoding="utf-8") as f:
        f.write(pubspec)

# 2. Create images directory and dummy images
os.makedirs("assets/images/promotions", exist_ok=True)
png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
dummy_png = b64decode(png_base64)
with open("assets/images/promotions/promo1.png", "wb") as f: f.write(dummy_png)
with open("assets/images/promotions/promo2.png", "wb") as f: f.write(dummy_png)

# 3. Create mock promotions JSON
os.makedirs("assets/mock", exist_ok=True)
mock_promos = [
    {
        "id": "P001",
        "title": "Giảm 20% Laptop cho Sinh viên",
        "description": "Ưu đãi đặc biệt mùa Back to School. Áp dụng cho tất cả các dòng Laptop từ 6 tháng trở lên.",
        "discountValue": "20%",
        "validFrom": "01/09/2026",
        "validTo": "30/10/2026",
        "conditions": "Cung cấp thẻ sinh viên hợp lệ. Thời hạn thuê tối thiểu 6 tháng.",
        "status": "Đang diễn ra",
        "imageAsset": "assets/images/promotions/promo1.png"
    },
    {
        "id": "P002",
        "title": "Thuê 1 tặng 1 - Thiết bị mạng",
        "description": "Thuê Router tặng kèm Access Point miễn phí.",
        "discountValue": "Tặng Access Point",
        "validFrom": "15/09/2026",
        "validTo": "15/12/2026",
        "conditions": "Áp dụng cho hợp đồng doanh nghiệp.",
        "status": "Sắp diễn ra",
        "imageAsset": "assets/images/promotions/promo2.png"
    }
]
with open("assets/mock/promotions.json", "w", encoding="utf-8") as f:
    json.dump(mock_promos, f, ensure_ascii=False, indent=2)

# 4. Promotion Model
os.makedirs("lib/models", exist_ok=True)
model_code = """
class PromotionModel {
  final String id;
  final String title;
  final String? description;
  final String? discountValue;
  final String? validFrom;
  final String? validTo;
  final String? conditions;
  final String? status;
  final String? imageAsset;
  final String? imageUrl;

  PromotionModel({
    required this.id,
    required this.title,
    this.description,
    this.discountValue,
    this.validFrom,
    this.validTo,
    this.conditions,
    this.status,
    this.imageAsset,
    this.imageUrl,
  });

  factory PromotionModel.fromJson(Map<String, dynamic> json) {
    return PromotionModel(
      id: json['id'],
      title: json['title'] ?? 'Khuyến mãi',
      description: json['description'],
      discountValue: json['discountValue'],
      validFrom: json['validFrom'],
      validTo: json['validTo'],
      conditions: json['conditions'],
      status: json['status'],
      imageAsset: json['imageAsset'],
      imageUrl: json['imageUrl'],
    );
  }
}
"""
with open("lib/models/promotion_model.dart", "w", encoding="utf-8") as f: f.write(model_code.strip())

# 5. Promotion DataSource and Repository
os.makedirs("lib/datasources/promotion", exist_ok=True)
ds_abs = """import '../../models/promotion_model.dart';

abstract class PromotionDataSource {
  Future<List<PromotionModel>> getPromotions();
}
"""
with open("lib/datasources/promotion/promotion_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_abs.strip())

ds_loc = """import 'dart:convert';
import 'package:flutter/services.dart';
import '../../models/promotion_model.dart';
import 'promotion_datasource.dart';

class LocalPromotionDataSource implements PromotionDataSource {
  @override
  Future<List<PromotionModel>> getPromotions() async {
    await Future.delayed(const Duration(milliseconds: 500));
    final String response = await rootBundle.loadString('assets/mock/promotions.json');
    final List<dynamic> data = json.decode(response);
    return data.map((j) => PromotionModel.fromJson(j)).toList();
  }
}
"""
with open("lib/datasources/promotion/local_promotion_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_loc.strip())

ds_rem = """import '../../models/promotion_model.dart';
import 'promotion_datasource.dart';

class RemotePromotionDataSource implements PromotionDataSource {
  @override
  Future<List<PromotionModel>> getPromotions() async {
    throw UnimplementedError('API chưa có sẵn');
  }
}
"""
with open("lib/datasources/promotion/remote_promotion_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_rem.strip())

os.makedirs("lib/repositories", exist_ok=True)
repo = """import '../models/promotion_model.dart';
import '../datasources/promotion/promotion_datasource.dart';

class PromotionRepository {
  final PromotionDataSource _dataSource;
  PromotionRepository(this._dataSource);

  Future<List<PromotionModel>> getPromotions() {
    return _dataSource.getPromotions();
  }
}
"""
with open("lib/repositories/promotion_repository.dart", "w", encoding="utf-8") as f: f.write(repo.strip())

# 6. Promotion Provider
os.makedirs("lib/providers", exist_ok=True)
prov = """import 'package:flutter/material.dart';
import '../models/promotion_model.dart';
import '../repositories/promotion_repository.dart';

class PromotionProvider with ChangeNotifier {
  final PromotionRepository _repository;
  PromotionProvider(this._repository);

  List<PromotionModel> _promotions = [];
  bool _isLoading = false;
  String? _errorMessage;

  List<PromotionModel> get promotions => _promotions;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<void> fetchPromotions() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _promotions = await _repository.getPromotions();
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
"""
with open("lib/providers/promotion_provider.dart", "w", encoding="utf-8") as f: f.write(prov.strip())

print("Promotion layer set up.")