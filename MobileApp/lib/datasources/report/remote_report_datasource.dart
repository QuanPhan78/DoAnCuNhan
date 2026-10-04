import '../../models/report_model.dart';
import 'report_datasource.dart';

class RemoteReportDataSource implements ReportDataSource {
  @override
  Future<ReportModel> getReports(String timeFilter) async {
    throw UnimplementedError('API chưa có sẵn');
  }
}