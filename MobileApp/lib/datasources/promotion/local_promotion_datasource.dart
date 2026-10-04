import 'dart:convert';
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