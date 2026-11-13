import 'package:flutter_test/flutter_test.dart';
import 'package:localhub/app.dart';

void main() {
  testWidgets('app boots', (tester) async {
    await tester.pumpWidget(
      const LocalHubApp(apiBaseUrl: 'http://localhost:8000/api/v1'),
    );
    expect(find.text('LocalHub'), findsOneWidget);
  });
}