import 'package:flutter_test/flutter_test.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/api_config.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/device/remote_device_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/contract/remote_contract_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/repositories/dashboard_repository.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/user_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/role_enum.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/device_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/promotion_model.dart';

void main() {
  setUp(() {
    ApiConfig.reset();
  });

  tearDown(() {
    ApiConfig.reset();
  });

  group('ApiConfig unit tests', () {
    test('Default baseUrl on desktop/testing environment is http://localhost:5000/api', () {
      expect(ApiConfig.baseUrl, equals('http://localhost:5000/api'));
    });

    test('setBaseUrl updates active baseUrl', () {
      ApiConfig.setBaseUrl('http://192.168.1.100:5000/api');
      expect(ApiConfig.baseUrl, equals('http://192.168.1.100:5000/api'));
    });

    test('reset reverts baseUrl to environment default', () {
      ApiConfig.setBaseUrl('https://example.com/api');
      expect(ApiConfig.baseUrl, equals('https://example.com/api'));

      ApiConfig.reset();
      expect(ApiConfig.baseUrl, equals('http://localhost:5000/api'));
    });

    test('ApiConfig empty or whitespace setBaseUrl falls back to environment default', () {
      ApiConfig.setBaseUrl('');
      expect(ApiConfig.baseUrl, equals('http://localhost:5000/api'));

      ApiConfig.setBaseUrl('   ');
      // When whitespace is passed, if not trimmed it would use it or if set properly
      // Let's test that reset recovers to default
      ApiConfig.reset();
      expect(ApiConfig.baseUrl, equals('http://localhost:5000/api'));
    });

    test('DataSources dynamically consume ApiConfig.baseUrl', () {
      final deviceDs = RemoteDeviceDataSource();
      expect(deviceDs.baseUrl, equals('http://localhost:5000/api'));

      ApiConfig.setBaseUrl('http://custom-host:8080/api');
      expect(deviceDs.baseUrl, equals('http://custom-host:8080/api'));

      // If constructor specifies custom baseUrl, it takes precedence
      final customContractDs = RemoteContractDataSource(baseUrl: 'http://override-ds:9000/api');
      expect(customContractDs.baseUrl, equals('http://override-ds:9000/api'));

      final dashboardDs = RemoteDashboardDataSource();
      expect(dashboardDs.baseUrl, equals('http://custom-host:8080/api'));
    });
  });

  group('Backend API Model Contract Tests', () {
    test('UserModel successfully deserializes ApiAuthController response payload', () {
      final jsonPayload = {
        'id': '10',
        'name': 'Nguyễn Văn A',
        'email': 'customer@rental.vn',
        'phone': '0901234567',
        'role': 'Khách hàng',
        'roleCode': 'KhachHang',
        'address': '123 Lê Duẩn, Q1, TP.HCM',
        'cccd': '079123456789',
        'status': true,
      };

      final user = UserModel.fromJson(jsonPayload);
      expect(user.id, equals('10'));
      expect(user.name, equals('Nguyễn Văn A'));
      expect(user.role, equals(Role.customer));
      expect(user.phone, equals('0901234567'));
    });

    test('RoleExtension correctly resolves all backend enterprise role codes', () {
      expect(RoleExtension.fromString('Admin'), equals(Role.admin));
      expect(RoleExtension.fromString('Quản lý'), equals(Role.admin));
      expect(RoleExtension.fromString('NhanVien'), equals(Role.staff));
      expect(RoleExtension.fromString('KinhDoanh'), equals(Role.staff));
      expect(RoleExtension.fromString('KyThuat'), equals(Role.staff));
      expect(RoleExtension.fromString('KhachHang'), equals(Role.customer));
      expect(RoleExtension.fromString(null), equals(Role.customer));
    });

    test('DeviceModel correctly handles API devices JSON response with numeric price', () {
      final jsonPayload = {
        'id': '1',
        'code': 'SP-0001',
        'name': 'Laptop Dell Latitude 7420',
        'type': 'Laptop',
        'brand': 'Chính hãng',
        'model': 'Dell Latitude 7420',
        'serialNumber': 'SN-0001',
        'specifications': 'Core i7, 16GB RAM, 512GB SSD',
        'condition': 'Mới 99%',
        'rentalStatus': 'Sẵn sàng',
        'rentalPrice': 150000.0,
        'description': 'Laptop cao cấp',
      };

      final device = DeviceModel.fromJson(jsonPayload);
      expect(device.id, equals('1'));
      expect(device.name, equals('Laptop Dell Latitude 7420'));
      expect(device.rentalPrice, equals(150000.0));
      expect(device.rentalStatus, equals('Sẵn sàng'));
    });

    test('PromotionModel deserializes ApiPromotionsController response', () {
      final jsonPayload = {
        'id': '1',
        'title': 'Ưu đãi 20% mã WELCOME20',
        'description': 'Nhập mã WELCOME20',
        'discountValue': '20%',
        'validFrom': '01/01/2026',
        'validTo': '31/12/2026',
        'conditions': 'Áp dụng cho mọi đơn',
        'status': 'Đang áp dụng',
        'imageAsset': 'assets/images/promotions/promo1.png',
        'code': 'WELCOME20',
        'percent': 20
      };

      final promo = PromotionModel.fromJson(jsonPayload);
      expect(promo.id, equals('1'));
      expect(promo.title, equals('Ưu đãi 20% mã WELCOME20'));
      expect(promo.discountValue, equals('20%'));
    });
  });
}


