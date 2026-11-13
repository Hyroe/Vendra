import 'package:flutter/material.dart';

import 'core/api_client.dart';
import 'features/auth/login_page.dart';
import 'features/catalog/catalog_page.dart';

class LocalHubApp extends StatelessWidget {
  final String apiBaseUrl;

  const LocalHubApp({super.key, required this.apiBaseUrl});

  @override
  Widget build(BuildContext context) {
    final api = ApiClient(baseUrl: apiBaseUrl);
    return MaterialApp(
      title: 'LocalHub',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1B5E20)),
        useMaterial3: true,
      ),
      home: LoginPage(api: api),
      routes: {
        '/catalog': (context) => CatalogPage(api: api),
      },
    );
  }
}