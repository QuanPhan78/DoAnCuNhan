class DeviceModel {
  final String id;
  final String? code;
  final String name;
  final String type;
  final String? brand;
  final String? model;
  final String? serialNumber;
  final String? specifications;
  final String? condition;
  final String? rentalStatus;
  final double? rentalPrice;
  final String? description;
  final String? imageAsset;
  final String? imageUrl;

  DeviceModel({
    required this.id,
    this.code,
    required this.name,
    required this.type,
    this.brand,
    this.model,
    this.serialNumber,
    this.specifications,
    this.condition,
    this.rentalStatus,
    this.rentalPrice,
    this.description,
    this.imageAsset,
    this.imageUrl,
  });

  factory DeviceModel.fromJson(Map<String, dynamic> json) {
    return DeviceModel(
      id: json['id'],
      code: json['code'],
      name: json['name'],
      type: json['type'],
      brand: json['brand'],
      model: json['model'],
      serialNumber: json['serialNumber'],
      specifications: json['specifications'],
      condition: json['condition'],
      rentalStatus: json['rentalStatus'],
      rentalPrice: (json['rentalPrice'] as num?)?.toDouble(),
      description: json['description'],
      imageAsset: json['imageAsset'],
      imageUrl: json['imageUrl'],
    );
  }
}
