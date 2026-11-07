import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/incident/remote_incident_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/attachment_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/incident_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/api_session.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('reports the exact machine with image bytes and sends reviews separately', () async {
    SharedPreferences.setMockInitialValues({
      ApiSession.tokenKey: jsonEncode({
        'accessToken': 'rs1.maintenance-fixture',
        'expiresIn': DateTime.now().add(const Duration(hours: 1)).toIso8601String(),
      }),
    });
    final source = RemoteIncidentDataSource(baseUrl: 'https://test.invalid/api');
    final imageBytes = base64Decode('iVBORw0KGgoAAAANSUhEUgAAACAAAAAUCAIAAABj86gYAAAAIklEQVR4nGO48+wDTRHDqAWjFoxaMGrBqAWjFoxacIcICwB2m71bwEJcewAAAABJRU5ErkJggg==');
    final calls = <String>[];
    await http.runWithClient(() async {
      final ticket = await source.createIncident(IncidentModel(
        id: '', code: '', contractId: '12', deviceId: '23', issueType: 'Mất kết nối',
        description: 'Cáp lỗi', severity: 'Nhẹ', occurrenceTime: '', status: '',
        createdAt: '', attachments: [AttachmentModel(
          id: 'photo', fileName: 'photo.png', bytes: imageBytes,
        )],
      ));
      expect(ticket.id, '42');
      expect(ticket.attachments.single.url, 'https://test.invalid/uploads/baotri/photo.png');
      expect((await source.rateIncident(ticket.id, 4, 'Phản hồi')).statusCode, 3);
      expect((await source.acceptIncident(ticket.id, false, 'Còn lỗi')).statusCode, 2);
      expect((await source.acceptIncident(ticket.id, true, '')).statusCode, 5);
      expect(calls, ['/api/maintenance', '/api/maintenance/42/rating',
        '/api/maintenance/42/acceptance', '/api/maintenance/42/acceptance']);
    }, () => MockClient((request) async {
      calls.add(request.url.path);
      expect(request.headers['authorization'], 'Bearer rs1.maintenance-fixture');
      if (request.method == 'POST') {
        expect(request.headers['content-type'], startsWith('multipart/form-data; boundary='));
        final body = latin1.decode(request.bodyBytes);
        expect(body, contains('name="contractId"\r\n\r\n12'));
        expect(body, contains('name="deviceId"\r\n\r\n23'));
        expect(body, contains('name="images"; filename="photo.png"'));
        expect(body, contains(latin1.decode(imageBytes)));
        return http.Response('{"id":"42","imagePaths":["/uploads/baotri/photo.png"]}', 200);
      }
      final payload = jsonDecode(utf8.decode(request.bodyBytes));
      if (request.url.path.endsWith('/rating')) {
        expect(payload, {'rating': 4, 'feedback': 'Phản hồi'});
        return http.Response.bytes(utf8.encode('{"status":"Chờ nghiệm thu","statusCode":3,"rating":4}'), 200);
      }
      final accepted = payload['accepted'] as bool;
      expect(payload['feedback'], accepted ? '' : 'Còn lỗi');
      return http.Response.bytes(utf8.encode(jsonEncode({
        'status': accepted ? 'Đã nghiệm thu' : 'Đang xử lý',
        'statusCode': accepted ? 5 : 2,
        'rating': 4,
      })), 200);
    }));
  });
}
