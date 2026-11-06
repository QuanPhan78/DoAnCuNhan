import 'attachment_model.dart';

typedef IncidentReview = ({String status, int statusCode, int? rating, String? feedback});

class IncidentModel {
  final String id;
  final String code;
  final String contractId;
  final String deviceId;
  final String issueType;
  final String description;
  final String severity;
  final String occurrenceTime;
  final String status;
  final int? statusCode;
  final int? rating;
  final String? feedback;
  final String? deviceName;
  final String? result;
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
    this.statusCode,
    this.rating,
    this.feedback,
    this.deviceName,
    this.result,
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
      statusCode: json['statusCode'],
      rating: json['rating'],
      feedback: json['feedback'],
      deviceName: json['deviceName'],
      result: json['result'],
      assignedStaff: json['assignedStaff'],
      createdAt: json['createdAt'],
      attachments: (json['attachments'] as List?)
              ?.map((e) => AttachmentModel.fromJson(e))
              .toList() ??
          [],
    );
  }

  IncidentModel withReview(IncidentReview review) => IncidentModel(
    id: id, code: code, contractId: contractId, deviceId: deviceId,
    deviceName: deviceName, issueType: issueType, description: description, result: result,
    severity: severity, occurrenceTime: occurrenceTime, status: review.status,
    statusCode: review.statusCode, rating: review.rating, feedback: review.feedback,
    assignedStaff: assignedStaff, createdAt: createdAt, attachments: attachments,
  );

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
      'statusCode': statusCode,
      'rating': rating,
      'feedback': feedback,
      'deviceName': deviceName,
      'result': result,
      'assignedStaff': assignedStaff,
      'createdAt': createdAt,
      'attachments': attachments.map((e) => e.toJson()).toList(),
    };
  }
}
