import 'dart:convert';

import 'package:http/http.dart' as http;

import 'api_exception.dart';
import 'token_storage.dart';

class ApiClient {
  final http.Client _client;
  final String baseUrl;
  final TokenStorage storage;

  String? _accessToken;
  String? _refreshToken;
  bool _refreshing = false;

  ApiClient({http.Client? client, required this.baseUrl, TokenStorage? storage})
    : _client = client ?? http.Client(),
      storage = storage ?? const TokenStorage();

  Future<void> loadTokens() async {
    _accessToken = await storage.readAccessToken();
    _refreshToken = await storage.readRefreshToken();
  }

  Future<void> saveTokens(Map<String, dynamic> tokens) async {
    _accessToken = tokens['access']?.toString();
    _refreshToken = tokens['refresh']?.toString();
    if (_accessToken != null && _refreshToken != null) {
      await storage.writeTokens(
        accessToken: _accessToken!,
        refreshToken: _refreshToken!,
      );
    }
  }

  Future<void> clearTokens() async {
    _accessToken = null;
    _refreshToken = null;
    await storage.clear();
  }

  Future<bool> _refreshAccessToken() async {
    if (_refreshing || _refreshToken == null) return false;
    _refreshing = true;
    try {
      final response = await _send(
        'POST',
        '/auth/token/refresh',
        body: {'refresh_token': _refreshToken},
        retry: false,
      );
      await saveTokens(response);
      return true;
    } catch (_) {
      await clearTokens();
      return false;
    } finally {
      _refreshing = false;
    }
  }

  Future<Map<String, dynamic>> _send(
    String method,
    String path, {
    Map<String, String>? headers,
    Object? body,
    bool retry = true,
  }) async {
    final uri = Uri.parse('$baseUrl$path');
    final request = http.Request(method, uri);
    request.headers['Content-Type'] = 'application/json';
    request.headers['Accept'] = 'application/json';
    if (headers != null) {
      request.headers.addAll(headers);
    }
    if (_accessToken != null) {
      request.headers['Authorization'] = 'Bearer $_accessToken';
    }
    if (body != null) {
      request.body = jsonEncode(body);
    }

    final streamed = await _client.send(request);
    final response = await http.Response.fromStream(streamed);

    if (response.statusCode == 401 && retry && _refreshToken != null) {
      final refreshed = await _refreshAccessToken();
      if (refreshed) {
        return _send(method, path, headers: headers, body: body, retry: false);
      }
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) return <String, dynamic>{};
      final decoded = jsonDecode(response.body);
      return decoded is Map<String, dynamic> ? decoded : <String, dynamic>{};
    }

    String code = 'HTTP_${response.statusCode}';
    String message = 'Request failed with status ${response.statusCode}.';
    if (response.body.isNotEmpty) {
      try {
        final decoded = jsonDecode(response.body);
        if (decoded is Map<String, dynamic> && decoded['error'] is Map) {
          final error = decoded['error'] as Map;
          code = error['code']?.toString() ?? code;
          message = error['message']?.toString() ?? message;
        }
      } catch (_) {
        // keep defaults
      }
    }

    throw ApiException(
      code: code,
      message: message,
      statusCode: response.statusCode,
    );
  }

  Future<Map<String, dynamic>> get(String path) => _send('GET', path);

  Future<Map<String, dynamic>> post(
    String path, {
    Object? body,
    Map<String, String>? headers,
  }) => _send('POST', path, body: body, headers: headers);

  Future<Map<String, dynamic>> put(
    String path, {
    Object? body,
    Map<String, String>? headers,
  }) => _send('PUT', path, body: body, headers: headers);

  Future<Map<String, dynamic>> delete(
    String path, {
    Map<String, String>? headers,
  }) => _send('DELETE', path, headers: headers);

  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
  }) {
    return post('/auth/register', body: {'email': email, 'password': password});
  }

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final response = await post(
      '/auth/token',
      body: {'email': email, 'password': password},
    );
    await saveTokens(response);
    return response;
  }

  Future<void> logout() async {
    if (_refreshToken != null) {
      try {
        await post(
          '/auth/token/revoke',
          body: {'refresh_token': _refreshToken},
        );
      } catch (_) {
        // ignore revocation failures and clear local state
      }
    }
    await clearTokens();
  }

  Future<Map<String, dynamic>> me() => get('/me');

  Future<Map<String, dynamic>> cart() => get('/cart');

  Future<Map<String, dynamic>> addCartItem({
    required String productId,
    required int quantity,
  }) {
    return put('/cart/items/$productId', body: {'quantity': quantity});
  }

  Future<Map<String, dynamic>> removeCartItem({required String productId}) {
    return delete('/cart/items/$productId');
  }

  Future<Map<String, dynamic>> products({String? storeId, String? search}) {
    final params = <String, String>{};
    if (storeId != null) params['store_id'] = storeId;
    if (search != null && search.isNotEmpty) params['search'] = search;
    final query = params.isEmpty
        ? ''
        : '?${Uri(queryParameters: params).query}';
    return get('/products$query');
  }

  Future<Map<String, dynamic>> checkout({
    required String cartId,
    required String idempotencyKey,
    Map<String, dynamic>? address,
    String shippingOptionId = 'standard',
  }) {
    return post(
      '/orders',
      body: {
        'cart_id': cartId,
        'delivery_address': address ?? <String, dynamic>{},
        'shipping_option_id': shippingOptionId,
      },
      headers: {'Idempotency-Key': idempotencyKey},
    );
  }

  Future<Map<String, dynamic>> orders() => get('/orders');

  Future<Map<String, dynamic>> order(String orderId) => get('/orders/$orderId');

  Future<Map<String, dynamic>> simulatePayment({
    required String attemptId,
    required String outcome,
    String? eventId,
  }) {
    return post(
      '/dev/payments/$attemptId/simulate',
      body: {'outcome': outcome, 'event_id': ?eventId},
    );
  }
}
