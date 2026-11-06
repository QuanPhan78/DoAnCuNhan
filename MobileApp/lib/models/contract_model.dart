class ContractDevice {
  final String id;
  final String name;
  final String serial;

  const ContractDevice(this.id, this.name, this.serial);

  String get label => serial.isEmpty ? name : '$name ($serial)';
}

class ContractModel {
  final String id;
  final String? contractCode;
  final String? customerId;
  final String? customerName;
  final String? customerPhone;
  final List<String>? deviceIds;
  final List<ContractDevice> devices;
  final String? rentalStart;
  final String? rentalEnd;
  final String? rentalType;
  final String? status;
  final int? statusCode;
  final bool cancellationRequested;
  final String? cancellationReason;
  final double? totalAmount;
  final double? depositAmount;
  final String? paymentStatus;
  final bool? customerSigned;
  final bool? staffSigned;
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
    this.devices = const [],
    this.rentalStart,
    this.rentalEnd,
    this.rentalType,
    this.status,
    this.statusCode,
    this.cancellationRequested = false,
    this.cancellationReason,
    this.totalAmount,
    this.depositAmount,
    this.paymentStatus,
    this.customerSigned,
    this.staffSigned,
    this.installationDetails,
    this.extensionDetails,
    this.note,
    this.installmentsCount,
  });

  factory ContractModel.fromJson(Map<String, dynamic> json) {
    final paymentCode = json['paymentStatusCode'];
    final paymentLabel = json['paymentStatus'];
    final hasPaymentStatus = const [0, 1, 2, 3].contains(paymentCode) &&
        paymentLabel is String &&
        paymentLabel.trim().isNotEmpty;
    return ContractModel(
      id: json['id']?.toString() ?? '',
      contractCode: json['contractCode'] ?? (json['id'] != null ? 'HD-${json['id'].toString().padLeft(4, '0')}' : null),
      customerId: json['customerId']?.toString(),
      customerName: json['customerName'],
      customerPhone: json['customerPhone'],
      deviceIds: json['deviceIds'] != null ? List<String>.from(json['deviceIds']) : [],
      devices: (json['devices'] as List? ?? []).map((device) => ContractDevice(
        device['deviceId'].toString(),
        device['productName'] as String? ?? 'Thiết bị',
        device['serialNumber'] as String? ?? '',
      )).toList(),
      rentalStart: json['rentalStart'],
      rentalEnd: json['rentalEnd'],
      rentalType: json['rentalType'] ?? 'Theo ngày',
      status: json['status'],
      statusCode: (json['statusCode'] as num?)?.toInt(),
      cancellationRequested: json['cancellationRequested'] == true,
      cancellationReason: json['cancellationReason'],
      totalAmount: (json['totalAmount'] as num?)?.toDouble(),
      depositAmount: (json['depositAmount'] as num?)?.toDouble(),
      paymentStatus: hasPaymentStatus ? paymentLabel : 'Chưa xác định',
      customerSigned: json['customerSigned'] is bool ? json['customerSigned'] : null,
      staffSigned: json['staffSigned'] is bool ? json['staffSigned'] : null,
      installationDetails: json['installationDetails'],
      extensionDetails: json['extensionDetails'],
      note: json['note'],
      installmentsCount: json['installmentsCount'] != null ? (json['installmentsCount'] as num).toInt() : null,
    );
  }
}
