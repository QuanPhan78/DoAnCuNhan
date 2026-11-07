import 'dart:convert';
import 'package:http/http.dart' as http;
import '../widgets/photo_field.dart';
import 'api_config.dart';
import 'api_session.dart';

class CustomerContractService {
  static Uri url(String path) => Uri.parse('${ApiConfig.baseUrl}$path');

  static dynamic decode(http.Response response) {
    dynamic data;
    try { data = jsonDecode(utf8.decode(response.bodyBytes)); } on FormatException { data = null; }
    if (response.statusCode < 200 || response.statusCode >= 300) {
      final message = data is Map ? data['message'] ?? data['title'] : null;
      throw Exception(message ?? 'Không thực hiện được yêu cầu (${response.statusCode}).');
    }
    return data;
  }

  static Future<Map<String, dynamic>> signInfo(String id) async =>
      Map<String, dynamic>.from(decode(await ApiSession.get(url('/contracts/$id/sign'))));

  static Future<List<Map<String, dynamic>>> debts() async =>
      (decode(await ApiSession.get(url('/debts'))) as List)
          .map((e) => Map<String, dynamic>.from(e)).toList();

  static Future<List<Map<String, dynamic>>> renewals(String id) async =>
      (decode(await ApiSession.get(url('/contracts/$id/renewals'))) as List)
          .map((e) => Map<String, dynamic>.from(e)).toList();

  static Future<void> sign(String id, int periods, String signature, PickedPhoto front, PickedPhoto back) async {
    final request = http.MultipartRequest('POST', url('/contracts/$id/sign'))
      ..fields.addAll({'installments': '$periods', 'signatureData': signature})
      ..files.addAll([http.MultipartFile.fromBytes('front', front.bytes, filename: front.uploadName),
        http.MultipartFile.fromBytes('back', back.bytes, filename: back.uploadName)]);
    decode(await ApiSession.send(request));
  }

  static Future<void> sendReceipt(int id, String reference, PickedPhoto photo) async {
    final request = http.MultipartRequest('POST', url('/debts/$id/receipt'))
      ..fields['reference'] = reference
      ..files.add(http.MultipartFile.fromBytes('image', photo.bytes, filename: photo.uploadName));
    decode(await ApiSession.send(request));
  }

  static Future<Uri> vnPay(int id) async {
    final data = decode(await ApiSession.post(url('/debts/$id/vnpay')));
    final uri = Uri.parse(data['url'] as String);
    if (uri.scheme != 'https' || !uri.host.endsWith('.vnpayment.vn')) {
      throw Exception('Địa chỉ thanh toán không hợp lệ.');
    }
    return uri;
  }
}
