import '../models/promotion_model.dart';
import '../datasources/promotion/promotion_datasource.dart';

class PromotionRepository {
  final PromotionDataSource _dataSource;
  PromotionRepository(this._dataSource);

  Future<List<PromotionModel>> getPromotions() {
    return _dataSource.getPromotions();
  }
}