class RenewalModel {
  final String id;
  final String contractId;
  final String customerId;
  final String duration;
  final String notes;
  final String status; // Chờ xử lý, Đã duyệt, Từ chối, Hoàn tất
  final String requestedAt;

  RenewalModel({
    required this.id,
    required this.contractId,
    required this.customerId,
    required this.duration,
    required this.notes,
    required this.status,
    required this.requestedAt,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'contractId': contractId,
      'customerId': customerId,
      'duration': duration,
      'notes': notes,
      'status': status,
      'requestedAt': requestedAt,
    };
  }

  factory RenewalModel.fromJson(Map<String, dynamic> json) {
    return RenewalModel(
      id: json['id'],
      contractId: json['contractId'],
      customerId: json['customerId'],
      duration: json['duration'],
      notes: json['notes'],
      status: json['status'],
      requestedAt: json['requestedAt'],
    );
  }
}