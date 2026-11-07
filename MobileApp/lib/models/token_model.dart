class TokenModel {
  final String accessToken;
  final String refreshToken;
  final DateTime expiresIn;

  TokenModel({
    required this.accessToken,
    required this.refreshToken,
    required this.expiresIn,
  });

  factory TokenModel.fromJson(Map<String, dynamic> json) {
    final token = json['access_token'] ?? json['accessToken'] ?? '';
    final refresh = json['refresh_token'] ?? json['refreshToken'] ?? '';
    final expires = json['expires_in'] ?? json['expiresIn'];
    final expiresDate = DateTime.tryParse(expires.toString()) ??
        DateTime.fromMillisecondsSinceEpoch(0, isUtc: true);

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
