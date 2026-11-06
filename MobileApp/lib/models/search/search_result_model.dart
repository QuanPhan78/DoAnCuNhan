class SearchResultModel {
  final String id;
  final String type; // 'device', 'contract', 'incident', 'maintenance'
  final String title;
  final String subtitle;
  final String? status;
  final dynamic originalData; // The actual Model object

  SearchResultModel({
    required this.id,
    required this.type,
    required this.title,
    required this.subtitle,
    this.status,
    required this.originalData,
  });
}