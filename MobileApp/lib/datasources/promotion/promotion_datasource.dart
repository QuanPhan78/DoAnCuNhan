import '../../models/promotion_model.dart';

abstract class PromotionDataSource {
  Future<List<PromotionModel>> getPromotions();
}