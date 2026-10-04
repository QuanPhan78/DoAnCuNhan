import os

os.makedirs("lib/screens/reports", exist_ok=True)
report_ui = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../providers/auth_provider.dart';
import '../../providers/report_provider.dart';
import '../../models/permission_enum.dart';
import '../../utils/permission_manager.dart';

class ReportsScreen extends StatefulWidget {
  const ReportsScreen({super.key});

  @override
  State<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends State<ReportsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ReportProvider>().fetchReports();
    });
  }

  @override
  Widget build(BuildContext context) {
    final userRole = context.watch<AuthProvider>().currentUser?.role;
    // Basic check for permission
    final canView = userRole != null && PermissionManager.hasPermission(userRole, AppPermission.viewReports);

    if (!canView) {
      return Scaffold(
        appBar: AppBar(title: const Text('Báo cáo & Thống kê')),
        body: const Center(child: Text('Bạn không có quyền xem báo cáo.')),
      );
    }

    final provider = context.watch<ReportProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Báo cáo & Thống kê'),
        actions: [
          DropdownButton<String>(
            value: provider.currentTimeFilter,
            icon: const Icon(Icons.filter_list, color: Colors.white),
            dropdownColor: Colors.blue,
            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
            underline: const SizedBox(),
            items: ['Tuần này', 'Tháng này', 'Năm nay'].map((String value) {
              return DropdownMenuItem<String>(
                value: value,
                child: Text(value),
              );
            }).toList(),
            onChanged: (val) {
              if (val != null) provider.fetchReports(timeFilter: val);
            },
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: provider.isLoading && provider.reportData == null
          ? const Center(child: CircularProgressIndicator())
          : provider.errorMessage != null
              ? Center(child: Text('Lỗi: ${provider.errorMessage}'))
              : provider.reportData == null
                  ? const Center(child: Text('Không có dữ liệu.'))
                  : RefreshIndicator(
                      onRefresh: () => provider.fetchReports(),
                      child: ListView(
                        padding: const EdgeInsets.all(16),
                        children: [
                          _buildMockWarning(),
                          const SizedBox(height: 16),
                          _buildRevenueSection(provider),
                          const SizedBox(height: 24),
                          _buildOverviewCards(provider),
                          const SizedBox(height: 24),
                          const Text('Cơ cấu Thiết bị', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 16),
                          SizedBox(
                            height: 250,
                            child: _buildDevicePieChart(provider),
                          ),
                          const SizedBox(height: 24),
                          const Text('Biểu đồ Doanh thu (VND)', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 16),
                          SizedBox(
                            height: 250,
                            child: _buildRevenueBarChart(provider),
                          ),
                          const SizedBox(height: 32), // padding bottom
                        ],
                      ),
                    ),
    );
  }

  Widget _buildMockWarning() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: Colors.orange.shade50, borderRadius: BorderRadius.circular(8), border: Border.all(color: Colors.orange)),
      child: const Row(
        children: [
          Icon(Icons.warning, color: Colors.orange),
          SizedBox(width: 8),
          Expanded(child: Text('Chú ý: Đây là Dữ liệu mô phỏng (Mock Data) dùng để kiểm tra giao diện, không phải số liệu thật.', style: TextStyle(color: Colors.orange, fontWeight: FontWeight.bold))),
        ],
      ),
    );
  }

  Widget _buildRevenueSection(ReportProvider provider) {
    final revenue = provider.reportData?.revenue;
    final formatter = NumberFormat.currency(locale: 'vi_VN', symbol: 'đ');
    
    return Card(
      color: Colors.blue.shade50,
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: Colors.blue.shade200)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const Text('TỔNG DOANH THU', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.blue)),
            const SizedBox(height: 8),
            Text(
              revenue == null ? 'Chưa có dữ liệu' : formatter.format(revenue),
              style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: revenue == null ? Colors.grey : Colors.blue.shade800),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOverviewCards(ReportProvider provider) {
    final data = provider.reportData!;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Tổng quan', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(child: _StatCard('Tổng Thiết bị', data.totalDevices.toString(), Colors.indigo)),
            const SizedBox(width: 12),
            Expanded(child: _StatCard('Tổng Hợp đồng', data.totalContracts.toString(), Colors.purple)),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(child: _StatCard('HĐ Đang thuê', data.activeContracts.toString(), Colors.blue)),
            const SizedBox(width: 12),
            Expanded(child: _StatCard('HĐ Hoàn thành', data.completedContracts.toString(), Colors.green)),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(child: _StatCard('Yêu cầu Bảo trì', data.totalMaintenances.toString(), Colors.orange)),
            const SizedBox(width: 12),
            Expanded(child: _StatCard('Đang xử lý', data.processingMaintenances.toString(), Colors.deepOrange)),
          ],
        ),
      ],
    );
  }

  Widget _buildDevicePieChart(ReportProvider provider) {
    final data = provider.reportData!;
    if (data.totalDevices == 0) return const Center(child: Text('Chưa có dữ liệu thiết bị'));

    return PieChart(
      PieChartData(
        sectionsSpace: 2,
        centerSpaceRadius: 40,
        sections: [
          PieChartSectionData(color: Colors.green, value: data.availableDevices.toDouble(), title: 'Sẵn sàng\\n${data.availableDevices}', radius: 50, titleStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white)),
          PieChartSectionData(color: Colors.blue, value: data.rentedDevices.toDouble(), title: 'Đang thuê\\n${data.rentedDevices}', radius: 50, titleStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white)),
          PieChartSectionData(color: Colors.orange, value: data.maintenanceDevices.toDouble(), title: 'Bảo trì\\n${data.maintenanceDevices}', radius: 50, titleStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white)),
          PieChartSectionData(color: Colors.red, value: data.brokenDevices.toDouble(), title: 'Hỏng\\n${data.brokenDevices}', radius: 50, titleStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white)),
        ],
      ),
    );
  }

  Widget _buildRevenueBarChart(ReportProvider provider) {
    final chartData = provider.reportData?.revenueChart ?? [];
    if (chartData.isEmpty || provider.reportData?.revenue == null) {
      return const Center(child: Text('Chưa có dữ liệu biểu đồ'));
    }

    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.spaceAround,
        maxY: _getMaxY(chartData),
        barTouchData: BarTouchData(enabled: false),
        titlesData: FlTitlesData(
          show: true,
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (double value, TitleMeta meta) {
                if (value.toInt() >= 0 && value.toInt() < chartData.length) {
                  return Padding(padding: const EdgeInsets.only(top: 8), child: Text(chartData[value.toInt()].label, style: const TextStyle(fontSize: 10)));
                }
                return const SizedBox();
              },
            ),
          ),
          leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        gridData: const FlGridData(show: false),
        borderData: FlBorderData(show: false),
        barGroups: chartData.asMap().entries.map((e) {
          return BarChartGroupData(
            x: e.key,
            barRods: [
              BarChartRodData(
                toY: e.value.value,
                color: Colors.blue,
                width: 16,
                borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
              )
            ],
          );
        }).toList(),
      ),
    );
  }

  double _getMaxY(List chartData) {
    if (chartData.isEmpty) return 100;
    double max = 0;
    for (var d in chartData) {
      if (d.value > max) max = d.value;
    }
    return max * 1.2; // 20% padding top
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final Color color;

  const _StatCard(this.title, this.value, this.color);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TextStyle(fontSize: 12, color: color, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text(value, style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: color)),
        ],
      ),
    );
  }
}
"""
with open("lib/screens/reports/reports_screen.dart", "w", encoding="utf-8") as f: f.write(report_ui.replace(r'${', '${'))

print("Reports UI Created")