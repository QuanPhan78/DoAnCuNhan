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
    return TokenModel(
      accessToken: json['access_token'],
      refreshToken: json['refresh_token'],
      expiresIn: DateTime.parse(json['expires_in']),
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