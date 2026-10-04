import '../../models/promotion_model.dart';
import 'promotion_datasource.dart';

class RemotePromotionDataSource implements PromotionDataSource {
  @override
  Future<List<PromotionModel>> getPromotions() async {
    throw UnimplementedError('API chưa có sẵn');
  }
}