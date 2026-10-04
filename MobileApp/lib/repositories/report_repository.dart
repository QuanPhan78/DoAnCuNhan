import '../models/report_model.dart';
import '../datasources/report/report_datasource.dart';

class ReportRepository {
  final ReportDataSource _dataSource;
  ReportRepository(this._dataSource);

  Future<ReportModel> getReports(String timeFilter) {
    return _dataSource.getReports(timeFilter);
  }
}