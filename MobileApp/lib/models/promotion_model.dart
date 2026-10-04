class PromotionModel {
  final String id;
  final String title;
  final String? description;
  final String? discountValue;
  final String? validFrom;
  final String? validTo;
  final String? conditions;
  final String? status;
  final String? imageAsset;
  final String? imageUrl;

  PromotionModel({
    required this.id,
    required this.title,
    this.description,
    this.discountValue,
    this.validFrom,
    this.validTo,
    this.conditions,
    this.status,
    this.imageAsset,
    this.imageUrl,
  });

  factory PromotionModel.fromJson(Map<String, dynamic> json) {
    return PromotionModel(
      id: json['id'],
      title: json['title'] ?? 'Khuyến mãi',
      description: json['description'],
      discountValue: json['discountValue'],
      validFrom: json['validFrom'],
      validTo: json['validTo'],
      conditions: json['conditions'],
      status: json['status'],
      imageAsset: json['imageAsset'],
      imageUrl: json['imageUrl'],
    );
  }
}