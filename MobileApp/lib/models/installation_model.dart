
class InstallationModel {
  final String contractId;
  String status;
  final String? expectedDate;
  String? actualDate;
  final String? assignedStaffName;
  final String? notes;

  InstallationModel({
    required this.contractId,
    required this.status,
    this.expectedDate,
    this.actualDate,
    this.assignedStaffName,
    this.notes,
  });

  factory InstallationModel.fromJson(Map<String, dynamic> json) {
    return InstallationModel(
      contractId: json['contractId'],
      status: json['status'],
      expectedDate: json['expectedDate'],
      actualDate: json['actualDate'],
      assignedStaffName: json['assignedStaffName'],
      notes: json['notes'],
    );
  }

  InstallationModel copyWith({
    String? status,
    String? actualDate,
  }) {
    return InstallationModel(
      contractId: contractId,
      status: status ?? this.status,
      expectedDate: expectedDate,
      actualDate: actualDate ?? this.actualDate,
      assignedStaffName: assignedStaffName,
      notes: notes,
    );
  }
}