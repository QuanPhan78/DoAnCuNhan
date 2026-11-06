import 'dart:convert';
import 'package:flutter/services.dart';
import '../../models/report_model.dart';
import 'report_datasource.dart';

class LocalReportDataSource implements ReportDataSource {
  @override
  Future<ReportModel> getReports(String timeFilter) async {
    await Future.delayed(const Duration(milliseconds: 600)); // Mock network
    final String response = await rootBundle.loadString('assets/mock/reports.json');
    final data = json.decode(response);
    
    // Simulate filtering by time
    if (timeFilter == 'Tháng này') {
      // Return data as is
      return ReportModel.fromJson(data);
    } else if (timeFilter == 'Năm nay') {
      // Modify data slightly to mock year filter
      data['revenue'] = (data['revenue'] as num?) == null ? null : (data['revenue'] as num) * 5;
      data['deviceStats']['rented'] = 80;
      return ReportModel.fromJson(data);
    }
    
    return ReportModel.fromJson(data);
  }
}