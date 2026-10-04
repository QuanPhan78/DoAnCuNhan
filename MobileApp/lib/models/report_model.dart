class ChartData {
  final String label;
  final double value;

  ChartData({required this.label, required this.value});

  factory ChartData.fromJson(Map<String, dynamic> json) {
    return ChartData(
      label: json['label'] ?? '',
      value: (json['value'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class ReportModel {
  final int totalDevices;
  final int availableDevices;
  final int rentedDevices;
  final int maintenanceDevices;
  final int brokenDevices;

  final int totalContracts;
  final int activeContracts;
  final int completedContracts;

  final int totalMaintenances;
  final int processingMaintenances;
  final int completedMaintenances;

  final double? revenue;
  final List<ChartData> revenueChart;

  ReportModel({
    required this.totalDevices,
    required this.availableDevices,
    required this.rentedDevices,
    required this.maintenanceDevices,
    required this.brokenDevices,
    required this.totalContracts,
    required this.activeContracts,
    required this.completedContracts,
    required this.totalMaintenances,
    required this.processingMaintenances,
    required this.completedMaintenances,
    this.revenue,
    this.revenueChart = const [],
  });

  factory ReportModel.fromJson(Map<String, dynamic> json) {
    final dev = json['deviceStats'] ?? {};
    final con = json['contractStats'] ?? {};
    final main = json['maintenanceStats'] ?? {};
    
    return ReportModel(
      totalDevices: dev['total'] ?? 0,
      availableDevices: dev['available'] ?? 0,
      rentedDevices: dev['rented'] ?? 0,
      maintenanceDevices: dev['maintenance'] ?? 0,
      brokenDevices: dev['broken'] ?? 0,
      
      totalContracts: con['total'] ?? 0,
      activeContracts: con['active'] ?? 0,
      completedContracts: con['completed'] ?? 0,
      
      totalMaintenances: main['total'] ?? 0,
      processingMaintenances: main['processing'] ?? 0,
      completedMaintenances: main['completed'] ?? 0,
      
      revenue: (json['revenue'] as num?)?.toDouble(),
      revenueChart: (json['revenueChart'] as List?)?.map((e) => ChartData.fromJson(e)).toList() ?? [],
    );
  }
}