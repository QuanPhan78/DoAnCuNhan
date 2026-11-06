class AttachmentModel {
  final String id;
  final String? localPath;
  final String? url;
  final String type; // 'image', 'document', etc.

  AttachmentModel({
    required this.id,
    this.localPath,
    this.url,
    this.type = 'image',
  });

  factory AttachmentModel.fromJson(Map<String, dynamic> json) {
    return AttachmentModel(
      id: json['id'],
      localPath: json['localPath'],
      url: json['url'],
      type: json['type'] ?? 'image',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'localPath': localPath,
      'url': url,
      'type': type,
    };
  }
}