import os

code = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../providers/auth_provider.dart';
import '../../providers/report_provider.dart';
import '../../models/permission_enum.dart';
import '../../utils/permission_manager.dart';
import '../../widgets/core/state_widgets.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';

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
    final canView = userRole != null && PermissionManager.hasPermission(userRole, AppPermission.viewReports);

    if (!canView) {
      return const Scaffold(
        backgroundColor: AppColors.background,
        appBar: CustomAppBar(title: 'Báo cáo & Thống kê'),
        body: EmptyState(
          message: 'Bạn không có quyền xem báo cáo.',
          icon: Icons.lock_outline_rounded,
        ),
      );
    }

    final provider = context.watch<ReportProvider>();

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: CustomAppBar(
        title: 'Thống kê & Báo cáo',
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: AppRadius.fullRadius,
              border: Border.all(color: AppColors.divider),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: provider.currentTimeFilter,
                icon: const Icon(Icons.filter_list_rounded, color: AppColors.primary, size: 20),
                style: AppTextStyles.body.copyWith(fontWeight: FontWeight.bold, color: AppColors.primary),
                dropdownColor: AppColors.surface,
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
            ),
          ),
        ],
      ),
      body: _buildContent(provider),
    );
  }

  Widget _buildContent(ReportProvider provider) {
    if (provider.isLoading && provider.reportData == null) {
      return const LoadingState(message: 'Đang tải báo cáo...');
    }
    if (provider.errorMessage != null) {
      return ErrorState(message: 'Lỗi: ${provider.errorMessage}', onRetry: () => provider.fetchReports());
    }
    if (provider.reportData == null) {
      return const EmptyState(message: 'Không có dữ liệu báo cáo.', icon: Icons.analytics_outlined);
    }

    return RefreshIndicator(
      color: AppColors.primary,
      onRefresh: () => provider.fetchReports(),
      child: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          _buildMockWarning(),
          const SizedBox(height: 24),
          _buildRevenueSection(provider),
          const SizedBox(height: 24),
          _buildOverviewCards(provider),
          const SizedBox(height: 32),
          Text('Cơ cấu Thiết bị', style: AppTextStyles.h2.copyWith(fontSize: 18)),
          const SizedBox(height: 16),
          _buildChartContainer(
            height: 280,
            child: _buildDevicePieChart(provider),
          ),
          const SizedBox(height: 32),
          Text('Biểu đồ Doanh thu (VND)', style: AppTextStyles.h2.copyWith(fontSize: 18)),
          const SizedBox(height: 16),
          _buildChartContainer(
            height: 300,
            child: _buildRevenueBarChart(provider),
          ),
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  Widget _buildChartContainer({required double height, required Widget child}) {
    return Container(
      height: height,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: AppRadius.lgRadius,
        boxShadow: AppShadows.cardShadow,
        border: Border.all(color: AppColors.divider),
      ),
      child: child,
    );
  }

  Widget _buildMockWarning() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.warning.withValues(alpha: 0.1),
        borderRadius: AppRadius.mdRadius,
        border: Border.all(color: AppColors.warning.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.info_outline_rounded, color: AppColors.warning),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              'Chú ý: Đây là dữ liệu mô phỏng (Mock Data) dùng để kiểm tra giao diện, không phải số liệu thật.',
              style: AppTextStyles.body.copyWith(color: AppColors.warning),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRevenueSection(ReportProvider provider) {
    final revenue = provider.reportData?.revenue;
    final formatter = NumberFormat.currency(locale: 'vi_VN', symbol: 'đ');
    
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [AppColors.primary, AppColors.primary.withValues(alpha: 0.8)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: AppRadius.lgRadius,
        boxShadow: AppShadows.cardShadow,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.2), shape: BoxShape.circle),
                child: const Icon(Icons.account_balance_wallet_rounded, color: Colors.white, size: 24),
              ),
              const SizedBox(width: 12),
              Text('TỔNG DOANH THU', style: AppTextStyles.bodySecondary.copyWith(color: Colors.white70, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            revenue == null ? 'Chưa có dữ liệu' : formatter.format(revenue),
            style: AppTextStyles.h1.copyWith(fontSize: 32, color: Colors.white),
          ),
        ],
      ),
    );
  }

  Widget _buildOverviewCards(ReportProvider provider) {
    final data = provider.reportData!;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Tổng quan hoạt động', style: AppTextStyles.h2.copyWith(fontSize: 18)),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(child: _StatCard('Tổng Thiết bị', data.totalDevices.toString(), Colors.indigo, Icons.devices_rounded)),
            const SizedBox(width: 16),
            Expanded(child: _StatCard('Tổng Hợp đồng', data.totalContracts.toString(), Colors.purple, Icons.description_rounded)),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(child: _StatCard('HĐ Đang thuê', data.activeContracts.toString(), Colors.blue, Icons.check_circle_rounded)),
            const SizedBox(width: 16),
            Expanded(child: _StatCard('HĐ Hoàn thành', data.completedContracts.toString(), AppColors.success, Icons.task_alt_rounded)),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(child: _StatCard('Y/C Bảo trì', data.totalMaintenances.toString(), AppColors.warning, Icons.build_rounded)),
            const SizedBox(width: 16),
            Expanded(child: _StatCard('Đang xử lý', data.processingMaintenances.toString(), AppColors.error, Icons.sync_rounded)),
          ],
        ),
      ],
    );
  }

  Widget _buildDevicePieChart(ReportProvider provider) {
    final data = provider.reportData!;
    if (data.totalDevices == 0) {
      return const EmptyState(message: 'Chưa có dữ liệu thiết bị', icon: Icons.pie_chart_outline_rounded);
    }

    return Row(
      children: [
        Expanded(
          flex: 3,
          child: PieChart(
            PieChartData(
              sectionsSpace: 4,
              centerSpaceRadius: 40,
              sections: [
                if (data.availableDevices > 0)
                  PieChartSectionData(color: AppColors.success, value: data.availableDevices.toDouble(), title: '', radius: 25),
                if (data.rentedDevices > 0)
                  PieChartSectionData(color: Colors.blue, value: data.rentedDevices.toDouble(), title: '', radius: 25),
                if (data.maintenanceDevices > 0)
                  PieChartSectionData(color: AppColors.warning, value: data.maintenanceDevices.toDouble(), title: '', radius: 25),
                if (data.brokenDevices > 0)
                  PieChartSectionData(color: AppColors.error, value: data.brokenDevices.toDouble(), title: '', radius: 25),
              ],
            ),
          ),
        ),
        Expanded(
          flex: 2,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildLegend('Sẵn sàng', data.availableDevices, AppColors.success),
              _buildLegend('Đang thuê', data.rentedDevices, Colors.blue),
              _buildLegend('Bảo trì', data.maintenanceDevices, AppColors.warning),
              _buildLegend('Hỏng', data.brokenDevices, AppColors.error),
            ],
          ),
        )
      ],
    );
  }

  Widget _buildLegend(String label, int value, Color color) {
    if (value == 0) return const SizedBox();
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Container(width: 12, height: 12, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
          const SizedBox(width: 8),
          Expanded(child: Text(label, style: AppTextStyles.bodySecondary.copyWith(fontSize: 13))),
          Text('$value', style: AppTextStyles.body.copyWith(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildRevenueBarChart(ReportProvider provider) {
    final chartData = provider.reportData?.revenueChart ?? [];
    if (chartData.isEmpty || provider.reportData?.revenue == null) {
      return const EmptyState(message: 'Chưa có dữ liệu biểu đồ', icon: Icons.bar_chart_rounded);
    }

    return Padding(
      padding: const EdgeInsets.only(top: 16.0),
      child: BarChart(
        BarChartData(
          alignment: BarChartAlignment.spaceAround,
          maxY: _getMaxY(chartData),
          barTouchData: BarTouchData(
            enabled: true,
            touchTooltipData: BarTouchTooltipData(
              getTooltipColor: (group) => AppColors.surface,
              tooltipBorder: const BorderSide(color: AppColors.divider),
              getTooltipItem: (group, groupIndex, rod, rodIndex) {
                final formatter = NumberFormat.currency(locale: 'vi_VN', symbol: 'đ');
                return BarTooltipItem(
                  formatter.format(rod.toY),
                  AppTextStyles.body.copyWith(fontWeight: FontWeight.bold, color: AppColors.primary),
                );
              },
            )
          ),
          titlesData: FlTitlesData(
            show: true,
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (double value, TitleMeta meta) {
                  if (value.toInt() >= 0 && value.toInt() < chartData.length) {
                    return Padding(
                      padding: const EdgeInsets.only(top: 12),
                      child: Text(
                        chartData[value.toInt()].label,
                        style: AppTextStyles.bodySecondary.copyWith(fontSize: 11),
                      ),
                    );
                  }
                  return const SizedBox();
                },
              ),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 45,
                getTitlesWidget: (value, meta) {
                  if (value == 0) return const SizedBox();
                  return Text(
                    '${(value / 1000000).toStringAsFixed(0)}M',
                    style: AppTextStyles.bodySecondary.copyWith(fontSize: 10),
                  );
                },
              ),
            ),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            horizontalInterval: _getMaxY(chartData) / 4,
            getDrawingHorizontalLine: (value) => FlLine(color: AppColors.divider, strokeWidth: 1, dashArray: [5, 5]),
          ),
          borderData: FlBorderData(show: false),
          barGroups: chartData.asMap().entries.map((e) {
            return BarChartGroupData(
              x: e.key,
              barRods: [
                BarChartRodData(
                  toY: e.value.value,
                  color: AppColors.primary,
                  width: 20,
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(6)),
                )
              ],
            );
          }).toList(),
        ),
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
  final IconData icon;

  const _StatCard(this.title, this.value, this.color, this.icon);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: AppRadius.lgRadius,
        boxShadow: AppShadows.cardShadow,
        border: Border.all(color: AppColors.divider),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: AppRadius.smRadius),
                child: Icon(icon, color: color, size: 16),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(value, style: AppTextStyles.h1.copyWith(fontSize: 24, color: AppColors.textPrimary)),
          const SizedBox(height: 4),
          Text(title, style: AppTextStyles.bodySecondary.copyWith(fontSize: 12)),
        ],
      ),
    );
  }
}
"""
with open("lib/screens/reports/reports_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("ReportsScreen updated.")