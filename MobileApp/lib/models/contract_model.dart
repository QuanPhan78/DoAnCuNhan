class ContractModel {
  final String id;
  final String? contractCode;
  final String? customerId;
  final String? customerName;
  final String? customerPhone;
  final List<String>? deviceIds;
  final String? rentalStart;
  final String? rentalEnd;
  final String? rentalType;
  final String? status;
  final double? totalAmount;
  final double? depositAmount;
  final String? paymentStatus;
  final String? installationDetails;
  final String? extensionDetails;
  final String? note;
  final int? installmentsCount;

  ContractModel({
    required this.id,
    this.contractCode,
    this.customerId,
    this.customerName,
    this.customerPhone,
    this.deviceIds,
    this.rentalStart,
    this.rentalEnd,
    this.rentalType,
    this.status,
    this.totalAmount,
    this.depositAmount,
    this.paymentStatus,
    this.installationDetails,
    this.extensionDetails,
    this.note,
    this.installmentsCount,
  });

  factory ContractModel.fromJson(Map<String, dynamic> json) {
    return ContractModel(
      id: json['id']?.toString() ?? '',
      contractCode: json['contractCode'] ?? (json['id'] != null ? 'HD-${json['id'].toString().padLeft(4, '0')}' : null),
      customerId: json['customerId']?.toString(),
      customerName: json['customerName'],
      customerPhone: json['customerPhone'],
      deviceIds: json['deviceIds'] != null ? List<String>.from(json['deviceIds']) : [],
      rentalStart: json['rentalStart'],
      rentalEnd: json['rentalEnd'],
      rentalType: json['rentalType'] ?? 'Theo ngày',
      status: json['status'],
      totalAmount: (json['totalAmount'] as num?)?.toDouble(),
      depositAmount: (json['depositAmount'] as num?)?.toDouble(),
      paymentStatus: json['paymentStatus'],
      installationDetails: json['installationDetails'],
      extensionDetails: json['extensionDetails'],
      note: json['note'],
      installmentsCount: json['installmentsCount'] != null ? (json['installmentsCount'] as num).toInt() : null,
    );
  }
}
