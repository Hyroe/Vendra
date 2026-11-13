import 'package:flutter/material.dart';

import '../../core/api_client.dart';
import '../../core/api_exception.dart';

class ProductDetailPage extends StatefulWidget {
  final ApiClient api;
  final String productId;

  const ProductDetailPage({super.key, required this.api, required this.productId});

  @override
  State<ProductDetailPage> createState() => _ProductDetailPageState();
}

class _ProductDetailPageState extends State<ProductDetailPage> {
  late Future<Map<String, dynamic>> _product;
  int _quantity = 1;
  bool _adding = false;
  String? _message;

  @override
  void initState() {
    super.initState();
    _product = _loadProduct();
  }

  Future<Map<String, dynamic>> _loadProduct() async {
    final response = await widget.api.get('/products/${widget.productId}');
    return response;
  }

  Future<void> _addToCart() async {
    setState(() {
      _adding = true;
      _message = null;
    });
    try {
      await widget.api.addCartItem(productId: widget.productId, quantity: _quantity);
      if (!mounted) return;
      setState(() => _message = 'Added to cart.');
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() => _message = e.message);
    } finally {
      if (mounted) setState(() => _adding = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Product')),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _product,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Text(
                snapshot.error is ApiException
                    ? (snapshot.error as ApiException).message
                    : 'Could not load product.',
              ),
            );
          }
          final product = snapshot.data!;
          final inventory = product['inventory'] as Map<String, dynamic>?;
          final available = inventory == null
              ? 0
              : (inventory['on_hand'] as num).toInt() - (inventory['reserved'] as num).toInt();
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text(
                product['name']?.toString() ?? 'Product',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              Text('\$${product['unit_price']}'),
              const SizedBox(height: 8),
              Text('SKU: ${product['sku']}'),
              const SizedBox(height: 8),
              Text('Available: $available'),
              const SizedBox(height: 16),
              Text(product['description']?.toString() ?? ''),
              const SizedBox(height: 24),
              Row(
                children: [
                  const Text('Quantity'),
                  const SizedBox(width: 12),
                  IconButton(
                    onPressed: _quantity > 1 ? () => setState(() => _quantity--) : null,
                    icon: const Icon(Icons.remove),
                  ),
                  Text('$_quantity'),
                  IconButton(
                    onPressed: () => setState(() => _quantity++),
                    icon: const Icon(Icons.add),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              if (_message != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Text(_message!),
                ),
              FilledButton(
                onPressed: _adding || available <= 0 ? null : _addToCart,
                child: _adding
                    ? const SizedBox(
                        height: 18,
                        width: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Add to cart'),
              ),
            ],
          );
        },
      ),
    );
  }
}