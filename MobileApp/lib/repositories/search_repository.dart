import '../models/search/search_result_model.dart';
import '../models/role_enum.dart';
import '../datasources/search/search_datasource.dart';

class SearchRepository {
  final SearchDataSource _dataSource;
  SearchRepository(this._dataSource);

  Future<List<SearchResultModel>> search(String query, {String filterType = 'all', String? userId, Role? role}) {
    return _dataSource.search(query, filterType: filterType, userId: userId, role: role);
  }
}