import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:localhub/core/api_client.dart';
import 'package:localhub/features/auth/login_page.dart';

void main() {
  testWidgets('login page renders', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: LoginPage(api: ApiClient(baseUrl: 'http://localhost:8000/api/v1')),
      ),
    );
    await tester.pump();
    expect(find.widgetWithText(AppBar, 'LocalHub'), findsOneWidget);
    expect(find.widgetWithText(TextFormField, 'Email'), findsOneWidget);
  });
}