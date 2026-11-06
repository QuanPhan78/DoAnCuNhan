import 'package:flutter/material.dart';

Future<String?> showCancellationReasonDialog(BuildContext context) {
  final formKey = GlobalKey<FormState>();
  String reason = '';
  return showDialog<String>(
    context: context,
    builder: (dialog) => AlertDialog(
      title: const Text('Yêu cầu hủy'),
      content: Form(
        key: formKey,
        child: TextFormField(
          decoration: const InputDecoration(labelText: 'Lý do hủy'),
          minLines: 2,
          maxLines: 4,
          maxLength: 500,
          onChanged: (value) => reason = value.trim(),
          validator: (value) =>
              value == null || value.trim().isEmpty ? 'Nhập lý do hủy.' : null,
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(dialog), child: const Text('Đóng')),
        FilledButton(
          onPressed: () {
            if (formKey.currentState!.validate()) Navigator.pop(dialog, reason);
          },
          child: const Text('Gửi yêu cầu'),
        ),
      ],
    ),
  );
}
