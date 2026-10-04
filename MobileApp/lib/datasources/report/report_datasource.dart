import '../../models/report_model.dart';

abstract class ReportDataSource {
  Future<ReportModel> getReports(String timeFilter);
}