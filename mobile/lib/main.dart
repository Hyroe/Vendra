import 'package:material_ui/material_ui.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

import 'app.dart';
import 'core/api_client.dart';
import 'core/api_config.dart';
import 'core/providers.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  const dsn = String.fromEnvironment('SENTRY_DSN', defaultValue: '');
  if (dsn.isNotEmpty) {
    await SentryFlutter.init((options) {
      options.dsn = dsn;
      options.tracesSampleRate = 0.1;
      options.sendDefaultPii = false;
    });
  }

  final api = ApiClient(baseUrl: kDefaultApiBaseUrl);
  await api.loadTokens();
  runApp(
    ProviderScope(
      overrides: [apiClientProvider.overrideWithValue(api)],
      child: const LocalHubApp(),
    ),
  );
}
