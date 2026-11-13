import 'package:flutter_test/flutter_test.dart';

import 'package:localhub/core/api_exception.dart';

void main() {
  test('ApiException exposes stable code and status', () {
    final exception = ApiException(code: 'ORDER_CONFLICT', message: 'Conflict', statusCode: 409);
    expect(exception.code, 'ORDER_CONFLICT');
    expect(exception.statusCode, 409);
  });
}