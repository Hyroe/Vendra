import 'package:flutter/material.dart';

import 'app.dart';
import 'core/api_config.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const LocalHubApp(apiBaseUrl: kDefaultApiBaseUrl));
}