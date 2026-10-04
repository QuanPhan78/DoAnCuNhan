import 'attachment_model.dart';

class IncidentModel {
  final String id;
  final String code;
  final String contractId;
  final String deviceId;
  final String issueType;
  final String description;
  final String severity;
  final String occurrenceTime;
  final String status; // Chờ xử lý, Đang xử lý, Đã hoàn thành
  final String? assignedStaff;
  final String createdAt;
  final List<AttachmentModel> attachments;

  IncidentModel({
    required this.id,
    required this.code,
    required this.contractId,
    required this.deviceId,
    required this.issueType,
    required this.description,
    required this.severity,
    required this.occurrenceTime,
    required this.status,
    this.assignedStaff,
    required this.createdAt,
    this.attachments = const [],
  });

  factory IncidentModel.fromJson(Map<String, dynamic> json) {
    return IncidentModel(
      id: json['id'],
      code: json['code'],
      contractId: json['contractId'],
      deviceId: json['deviceId'],
      issueType: json['issueType'],
      description: json['description'],
      severity: json['severity'],
      occurrenceTime: json['occurrenceTime'],
      status: json['status'],
      assignedStaff: json['assignedStaff'],
      createdAt: json['createdAt'],
      attachments: (json['attachments'] as List?)
              ?.map((e) => AttachmentModel.fromJson(e))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'code': code,
      'contractId': contractId,
      'deviceId': deviceId,
      'issueType': issueType,
      'description': description,
      'severity': severity,
      'occurrenceTime': occurrenceTime,
      'status': status,
      'assignedStaff': assignedStaff,
      'createdAt': createdAt,
      'attachments': attachments.map((e) => e.toJson()).toList(),
    };
  }
}