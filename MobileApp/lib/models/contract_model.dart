class ContractModel {
  final String id;
  final String? contractCode;
  final String? customerId;
  final String? customerName;
  final List<String>? deviceIds;
  final String? rentalStart;
  final String? rentalEnd;
  final String? rentalType;
  final String? status;
  final double? totalAmount;
  final String? installationDetails;
  final String? extensionDetails;

  ContractModel({
    required this.id,
    this.contractCode,
    this.customerId,
    this.customerName,
    this.deviceIds,
    this.rentalStart,
    this.rentalEnd,
    this.rentalType,
    this.status,
    this.totalAmount,
    this.installationDetails,
    this.extensionDetails,
  });

  factory ContractModel.fromJson(Map<String, dynamic> json) {
    return ContractModel(
      id: json['id'],
      contractCode: json['contractCode'],
      customerId: json['customerId'],
      customerName: json['customerName'],
      deviceIds: json['deviceIds'] != null ? List<String>.from(json['deviceIds']) : [],
      rentalStart: json['rentalStart'],
      rentalEnd: json['rentalEnd'],
      rentalType: json['rentalType'],
      status: json['status'],
      totalAmount: (json['totalAmount'] as num?)?.toDouble(),
      installationDetails: json['installationDetails'],
      extensionDetails: json['extensionDetails'],
    );
  }
}
