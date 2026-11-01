class TokenModel {
  final String accessToken;
  final String refreshToken;
  final DateTime expiresIn;

  TokenModel({
    required this.accessToken,
    required this.refreshToken,
    required this.expiresIn,
  });

  // Mock token cho nay. Sau nay xai JWT that.
  factory TokenModel.fromJson(Map<String, dynamic> json) {
    final token = json['access_token'] ?? json['accessToken'] ?? '';
    final refresh = json['refresh_token'] ?? json['refreshToken'] ?? '';
    final expires = json['expires_in'] ?? json['expiresIn'];
    DateTime expiresDate;
    if (expires != null) {
      expiresDate = DateTime.tryParse(expires.toString()) ?? DateTime.now().add(const Duration(days: 7));
    } else {
      expiresDate = DateTime.now().add(const Duration(days: 7));
    }

    return TokenModel(
      accessToken: token.toString(),
      refreshToken: refresh.toString(),
      expiresIn: expiresDate,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'refresh_token': refreshToken,
      'expires_in': expiresIn.toIso8601String(),
    };
  }
}