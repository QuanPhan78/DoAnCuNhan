import 'role_enum.dart';

class UserModel {
  final String id;
  final String email;
  final String name;
  final Role role;
  final String? phone;
  final String? address;
  final String? cccd;

  UserModel({
    required this.id,
    required this.email,
    required this.name,
    required this.role,
    this.phone,
    this.address,
    this.cccd,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id']?.toString() ?? '',
      email: json['email'] ?? '',
      name: json['name'] ?? '',
      role: RoleExtension.fromString(json['role'] ?? json['roleCode']),
      phone: json['phone'],
      address: json['address'],
      cccd: json['cccd'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'name': name,
      'role': role.name,
      'phone': phone,
      'address': address,
      'cccd': cccd,
    };
  }
}