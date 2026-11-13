import 'package:flutter/material.dart';

import '../../core/api_client.dart';
import '../../core/api_exception.dart';

class OrdersPage extends StatefulWidget {
  final ApiClient api;

  const OrdersPage({super.key, required this.api});

  @override
  State<OrdersPage> createState() => _OrdersPageState();
}

class _OrdersPageState extends State<OrdersPage> {
  late Future<List<Map<String, dynamic>>> _orders;

  @override
  void initState() {
    super.initState();
    _orders = _loadOrders();
  }

  Future<List<Map<String, dynamic>>> _loadOrders() async {
    final response = await widget.api.orders();
    return (response['results'] as List?)?.whereType<Map<String, dynamic>>().toList() ??
        <Map<String, dynamic>>[];
  }

  void _reload() {
    setState(() {
      _orders = _loadOrders();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Orders'),
        actions: [
          IconButton(onPressed: _reload, icon: const Icon(Icons.refresh)),
        ],
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _orders,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Text(
                snapshot.error is ApiException
                    ? (snapshot.error as ApiException).message
                    : 'Could not load orders.',
              ),
            );
          }
          final orders = snapshot.data ?? const [];
          if (orders.isEmpty) {
            return const Center(child: Text('No orders yet.'));
          }
          return ListView.separated(
            itemCount: orders.length,
            separatorBuilder: (_, __) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final order = orders[index];
              return ListTile(
                title: Text('Order ${order['id']}'),
                subtitle: Text('${order['status']} • \$${order['grand_total'] ?? '0.00'}'),
              );
            },
          );
        },
      ),
    );
  }
}