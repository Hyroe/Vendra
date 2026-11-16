import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/api_client.dart';
import 'core/providers.dart';
import 'features/auth/login_page.dart';
import 'features/catalog/catalog_page.dart';

class LocalHubApp extends ConsumerWidget {
  const LocalHubApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final api = ref.watch(apiClientProvider);
    return MaterialApp(
      title: 'LocalHub',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1B5E20)),
        useMaterial3: true,
      ),
      home: _Bootstrap(api: api),
      routes: {
        '/catalog': (context) => CatalogPage(api: api),
        '/login': (context) => LoginPage(api: api),
      },
    );
  }
}

class _Bootstrap extends StatefulWidget {
  final ApiClient api;

  const _Bootstrap({required this.api});

  @override
  State<_Bootstrap> createState() => _BootstrapState();
}

class _BootstrapState extends State<_Bootstrap> {
  bool _checking = true;
  Widget? _next;

  @override
  void initState() {
    super.initState();
    _checkSession();
  }

  Future<void> _checkSession() async {
    try {
      await widget.api.me();
      _next = CatalogPage(api: widget.api);
    } catch (_) {
      _next = LoginPage(api: widget.api);
    }
    if (mounted) {
      setState(() => _checking = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_checking) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    return _next ?? const SizedBox.shrink();
  }
}