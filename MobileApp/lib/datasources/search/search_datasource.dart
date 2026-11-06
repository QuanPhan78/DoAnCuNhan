import '../../models/search/search_result_model.dart';
import '../../models/role_enum.dart';

abstract class SearchDataSource {
  Future<List<SearchResultModel>> search(String query, {String filterType = 'all', String? userId, Role? role});
}