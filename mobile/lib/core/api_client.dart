import 'dart:convert';

import 'package:http/http.dart' as http;

import 'api_exception.dart';

class ApiClient {
  final http.Client _client;
  final String baseUrl;
  String? csrfToken;

  ApiClient({http.Client? client, required this.baseUrl}) : _client = client ?? http.Client();

  Future<Map<String, dynamic>> _send(
    String method,
    String path, {
    Map<String, String>? headers,
    Object? body,
  }) async {
    final uri = Uri.parse('$baseUrl$path');
    final request = http.Request(method, uri);
    request.headers['Content-Type'] = 'application/json';
    request.headers['Accept'] = 'application/json';
    if (headers != null) {
      request.headers.addAll(headers);
    }
    if (csrfToken != null && method != 'GET' && method != 'HEAD') {
      request.headers['X-CSRFToken'] = csrfToken!;
    }
    if (body != null) {
      request.body = jsonEncode(body);
    }

    final streamed = await _client.send(request);
    final response = await http.Response.fromStream(streamed);

    final setCookie = response.headers['set-cookie'];
    if (setCookie != null) {
      for (final part in setCookie.split(',')) {
        final match = RegExp(r'csrftoken=([^;]+)').firstMatch(part);
        if (match != null) {
          csrfToken = match.group(1);
        }
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

    throw ApiException(code: code, message: message, statusCode: response.statusCode);
  }

  Future<Map<String, dynamic>> get(String path) => _send('GET', path);

  Future<Map<String, dynamic>> post(String path, {Object? body, Map<String, String>? headers}) =>
      _send('POST', path, body: body, headers: headers);

  Future<Map<String, dynamic>> put(String path, {Object? body, Map<String, String>? headers}) =>
      _send('PUT', path, body: body, headers: headers);

  Future<Map<String, dynamic>> delete(String path, {Map<String, String>? headers}) =>
      _send('DELETE', path, headers: headers);

  Future<Map<String, dynamic>> register({required String email, required String password}) {
    return post('/auth/register', body: {'email': email, 'password': password});
  }

  Future<Map<String, dynamic>> login({required String email, required String password}) {
    return post('/auth/login', body: {'email': email, 'password': password});
  }

  Future<void> logout() => post('/auth/logout');

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
    final query = params.isEmpty ? '' : '?${Uri(queryParameters: params).query}';
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
      headers: {'Idempotency-Key': idempotencyKey},
      body: {
        'cart_id': cartId,
        'delivery_address': address ?? <String, dynamic>{},
        'shipping_option_id': shippingOptionId,
      },
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
      body: {'outcome': outcome, if (eventId != null) 'event_id': eventId},
    );
  }
}