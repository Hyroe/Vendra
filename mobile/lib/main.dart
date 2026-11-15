import 'package:material_ui/material_ui.dart';

import 'app.dart';
import 'core/api_config.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const LocalHubApp(apiBaseUrl: kDefaultApiBaseUrl));
}
