class MaintenanceNote {
  final String time;
  final String content;
  final String author;

  MaintenanceNote({required this.time, required this.content, required this.author});

  factory MaintenanceNote.fromJson(Map<String, dynamic> json) {
    return MaintenanceNote(
      time: json['time'] ?? '',
      content: json['content'] ?? '',
      author: json['author'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {'time': time, 'content': content, 'author': author};
  }
}

class MaintenanceModel {
  final String id;
  final String? requestCode;
  final String? contractId;
  final String? deviceId;
  final String? customer;
  final String? description;
  String? status;
  String? assignedEmployee;
  final String? assignedStaffId;
  final int? statusCode;
  final String? updateNote;
  bool get isClosed => statusCode == 4 || statusCode == 5;
  final String? createdAt;
  String? completedAt;
  String? result;
  List<MaintenanceNote> notes;
  final List<String> imageUrls;

  MaintenanceModel({
    required this.id,
    this.requestCode,
    this.contractId,
    this.deviceId,
    this.customer,
    this.description,
    this.status,
    this.assignedEmployee,
    this.assignedStaffId,
    this.statusCode,
    this.updateNote,
    this.createdAt,
    this.completedAt,
    this.result,
    this.notes = const [],
    this.imageUrls = const [],
  });

  factory MaintenanceModel.fromJson(Map<String, dynamic> json) {
    return MaintenanceModel(
      id: json['id'],
      requestCode: json['requestCode'],
      contractId: json['contractId'],
      deviceId: json['deviceId'],
      customer: json['customer'],
      description: json['description'],
      status: json['status'],
      assignedEmployee: json['assignedEmployee'],
      assignedStaffId: json['assignedStaffId']?.toString(),
      statusCode: (json['statusCode'] as num?)?.toInt(),
      createdAt: json['createdAt'],
      completedAt: json['completedAt'],
      result: json['result'],
      notes: (json['notes'] as List?)?.map((n) => MaintenanceNote.fromJson(n)).toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'requestCode': requestCode,
      'contractId': contractId,
      'deviceId': deviceId,
      'customer': customer,
      'description': description,
      'status': status,
      'assignedEmployee': assignedEmployee,
      'assignedStaffId': assignedStaffId,
      'statusCode': statusCode,
      'createdAt': createdAt,
      'completedAt': completedAt,
      'result': result,
      'notes': notes.map((n) => n.toJson()).toList(),
    };
  }
}
