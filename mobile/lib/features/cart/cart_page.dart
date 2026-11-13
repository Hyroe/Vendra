import 'package:flutter/material.dart';

import '../../core/api_client.dart';
import '../../core/api_exception.dart';
import '../orders/orders_page.dart';

class CartPage extends StatefulWidget {
  final ApiClient api;

  const CartPage({super.key, required this.api});

  @override
  State<CartPage> createState() => _CartPageState();
}

class _CartPageState extends State<CartPage> {
  late Future<Map<String, dynamic>> _cart;
  bool _checkingOut = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cart = widget.api.cart();
  }

  void _reload() {
    setState(() {
      _cart = widget.api.cart();
    });
  }

  Future<void> _updateQuantity(String productId, int quantity) async {
    if (quantity <= 0) {
      await widget.api.removeCartItem(productId: productId);
    } else {
      await widget.api.addCartItem(productId: productId, quantity: quantity);
    }
    _reload();
  }

  Future<void> _checkout() async {
    final current = await _cart;
    final cartId = current['id']?.toString();
    if (cartId == null) return;
    setState(() {
      _checkingOut = true;
      _error = null;
    });
    try {
      await widget.api.checkout(
        cartId: cartId,
        idempotencyKey: 'mobile-${DateTime.now().microsecondsSinceEpoch}',
        address: const {},
        shippingOptionId: 'standard',
      );
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => OrdersPage(api: widget.api)),
      );
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() => _error = e.message);
    } catch (_) {
      if (!mounted) return;
      setState(() => _error = 'Network error. Please retry.');
    } finally {
      if (mounted) setState(() => _checkingOut = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Cart')),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _cart,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Text(
                snapshot.error is ApiException
                    ? (snapshot.error as ApiException).message
                    : 'Could not load cart.',
              ),
            );
          }
          final items = (snapshot.data?['items'] as List?) ?? const [];
          if (items.isEmpty) {
            return const Center(child: Text('Your cart is empty.'));
          }
          return Column(
            children: [
              Expanded(
                child: ListView.separated(
                  itemCount: items.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final item = items[index] as Map<String, dynamic>;
                    final productId = item['product_id'].toString();
                    final quantity = (item['quantity'] as num).toInt();
                    return ListTile(
                      title: Text(item['name']?.toString() ?? 'Item'),
                      subtitle: Text('\$${item['unit_price']} • Qty $quantity'),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          IconButton(
                            icon: const Icon(Icons.remove),
                            onPressed: () => _updateQuantity(productId, quantity - 1),
                          ),
                          IconButton(
                            icon: const Icon(Icons.add),
                            onPressed: () => _updateQuantity(productId, quantity + 1),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text('Subtotal: \$${snapshot.data?['subtotal'] ?? '0.00'}'),
                    const SizedBox(height: 12),
                    if (_error != null)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: Text(
                          _error!,
                          style: TextStyle(color: Theme.of(context).colorScheme.error),
                        ),
                      ),
                    FilledButton(
                      onPressed: _checkingOut ? null : _checkout,
                      child: _checkingOut
                          ? const SizedBox(
                              height: 18,
                              width: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Checkout'),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}