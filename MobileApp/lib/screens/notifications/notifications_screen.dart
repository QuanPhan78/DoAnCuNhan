import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../services/api_config.dart';
import '../../services/api_session.dart';
import '../../widgets/core/state_widgets.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key, this.isActive = true});

  final bool isActive;

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  List<_Notification> _items = [];
  bool _loading = true;
  bool _saving = false;
  String? _error;
  int _request = 0;

  @override
  void initState() {
    super.initState();
    if (widget.isActive) _load();
  }

  @override
  void didUpdateWidget(covariant NotificationsScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isActive && !oldWidget.isActive) _load();
  }

  Uri _url([String suffix = '']) => Uri.parse('${ApiConfig.baseUrl}/notifications$suffix');

  Future<void> _load() async {
    final request = ++_request;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final response = await ApiSession.get(_url());
      if (response.statusCode != 200) throw Exception('Không tải được thông báo (${response.statusCode}).');
      final rows = jsonDecode(utf8.decode(response.bodyBytes)) as List;
      if (mounted && request == _request) {
        setState(() => _items = rows.map((row) => _Notification.fromJson(row)).toList());
      }
    } catch (error) {
      if (mounted && request == _request) {
        setState(() => _error = error.toString().replaceFirst('Exception: ', ''));
      }
    } finally {
      if (mounted && request == _request) setState(() => _loading = false);
    }
  }

  Future<void> _read({int? id}) async {
    if (_saving) return;
    setState(() => _saving = true);
    try {
      final response = await ApiSession.put(_url(id == null ? '/read-all' : '/$id/read'));
      if (response.statusCode != 204) throw Exception('Không cập nhật được thông báo (${response.statusCode}).');
      if (!mounted) return;
      await _load();
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text(error.toString().replaceFirst('Exception: ', '')),
        ));
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading && _items.isEmpty) return const LoadingState(message: 'Đang tải thông báo...');
    if (_error != null) return ErrorState(message: _error!, onRetry: _load);

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        children: [
          if (_items.isEmpty)
            const EmptyState(message: 'Chưa có thông báo.', icon: Icons.notifications_none_rounded),
          if (_items.any((item) => !item.isRead))
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: _saving ? null : () => _read(),
                child: const Text('Đánh dấu tất cả đã đọc'),
              ),
            ),
          for (final item in _items)
            Card(
              child: ListTile(
                leading: Icon(item.isRead ? Icons.notifications_none : Icons.notifications_active_outlined),
                title: Text(item.title, style: TextStyle(
                  fontWeight: item.isRead ? FontWeight.normal : FontWeight.bold,
                )),
                subtitle: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(item.content),
                  Text(DateFormat('dd/MM/yyyy HH:mm').format(item.createdAt)),
                  if (item.type == 'PhanCong')
                    TextButton(
                      onPressed: _saving ? null : () async {
                        if (!item.isRead) await _read(id: item.id);
                        if (context.mounted) Navigator.pushNamed(context, '/tasks');
                      },
                      child: const Text('Mở công việc'),
                    ),
                ]),
                trailing: item.isRead ? null : IconButton(
                  tooltip: 'Đánh dấu đã đọc',
                  onPressed: _saving ? null : () => _read(id: item.id),
                  icon: const Icon(Icons.done),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _Notification {
  final int id;
  final String title;
  final String content;
  final String? type;
  final DateTime createdAt;
  final bool isRead;

  _Notification.fromJson(Map<String, dynamic> json)
    : id = json['id'],
      title = json['title'],
      content = json['content'],
      type = json['type'],
      createdAt = DateTime.parse(json['createdAt']),
      isRead = json['isRead'] == true;
}
