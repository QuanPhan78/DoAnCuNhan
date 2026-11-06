class FeedbackModel {
  final String id;
  final String? feedbackCode;
  final String? contractId;
  final String? maintenanceId;
  final String content;
  final int? rating;
  final String? status;
  final String? createdAt;
  final String? response;

  FeedbackModel({
    required this.id,
    this.feedbackCode,
    this.contractId,
    this.maintenanceId,
    required this.content,
    this.rating,
    this.status,
    this.createdAt,
    this.response,
  });

  factory FeedbackModel.fromJson(Map<String, dynamic> json) {
    return FeedbackModel(
      id: json['id'],
      feedbackCode: json['feedbackCode'],
      contractId: json['contractId'],
      maintenanceId: json['maintenanceId'],
      content: json['content'] ?? '',
      rating: json['rating'],
      status: json['status'],
      createdAt: json['createdAt'],
      response: json['response'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'feedbackCode': feedbackCode,
      'contractId': contractId,
      'maintenanceId': maintenanceId,
      'content': content,
      'rating': rating,
      'status': status,
      'createdAt': createdAt,
      'response': response,
    };
  }
}