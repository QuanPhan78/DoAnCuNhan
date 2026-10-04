import '../../models/search/search_result_model.dart';
import '../../models/role_enum.dart';
import 'search_datasource.dart';

class RemoteSearchDataSource implements SearchDataSource {
  @override
  Future<List<SearchResultModel>> search(String query, {String filterType = 'all', String? userId, Role? role}) async {
    throw UnimplementedError('API chưa có sẵn');
  }
}