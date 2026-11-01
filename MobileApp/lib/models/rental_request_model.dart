import 'rental_status.dart';

class RentalRequestItem {
  final String deviceId;
  final String deviceName;
  final String? imageUrl;
  final int quantity;
  final double rentalPrice;
  final double subtotal;

  RentalRequestItem({
    required this.deviceId,
    required this.deviceName,
    this.imageUrl,
    required this.quantity,
    required this.rentalPrice,
    required this.subtotal,
  });
}

class RentalRequestModel {
  final String id;
  final String customerId;
  final List<RentalRequestItem> items;
  final String rentalType;
  final DateTime startDate;
  final DateTime endDate;
  final String deliveryAddress;
  final String? installationAddress;
  final String note;
  final double estimatedAmount;
  final RentalStatus status;
  final String? contractId;
  final DateTime createdAt;

  RentalRequestModel({
    required this.id,
    required this.customerId,
    required this.items,
    required this.rentalType,
    required this.startDate,
    required this.endDate,
    required this.deliveryAddress,
    this.installationAddress,
    required this.note,
    required this.estimatedAmount,
    required this.status,
    this.contractId,
    required this.createdAt,
  });

  RentalRequestModel copyWith({
    String? id,
    String? customerId,
    List<RentalRequestItem>? items,
    String? rentalType,
    DateTime? startDate,
    DateTime? endDate,
    String? deliveryAddress,
    String? installationAddress,
    String? note,
    double? estimatedAmount,
    RentalStatus? status,
    String? contractId,
    DateTime? createdAt,
  }) {
    return RentalRequestModel(
      id: id ?? this.id,
      customerId: customerId ?? this.customerId,
      items: items ?? this.items,
      rentalType: rentalType ?? this.rentalType,
      startDate: startDate ?? this.startDate,
      endDate: endDate ?? this.endDate,
      deliveryAddress: deliveryAddress ?? this.deliveryAddress,
      installationAddress: installationAddress ?? this.installationAddress,
      note: note ?? this.note,
      estimatedAmount: estimatedAmount ?? this.estimatedAmount,
      status: status ?? this.status,
      contractId: contractId ?? this.contractId,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}

