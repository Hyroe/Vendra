import 'package:flutter/material.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

import 'app.dart';
import 'core/api_config.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  const dsn = String.fromEnvironment('SENTRY_DSN', defaultValue: '');
  if (dsn.isNotEmpty) {
    await SentryFlutter.init(
      (options) {
        options.dsn = dsn;
        options.tracesSampleRate = 0.1;
        options.sendDefaultPii = false;
      },
    );
  }
  runApp(const LocalHubApp(apiBaseUrl: kDefaultApiBaseUrl));
}