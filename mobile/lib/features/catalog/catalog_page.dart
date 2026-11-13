import 'package:flutter/material.dart';

import '../../core/api_client.dart';
import '../../core/api_exception.dart';
import '../cart/cart_page.dart';
import 'product_detail_page.dart';

class CatalogPage extends StatefulWidget {
  final ApiClient api;

  const CatalogPage({super.key, required this.api});

  @override
  State<CatalogPage> createState() => _CatalogPageState();
}

class _CatalogPageState extends State<CatalogPage> {
  late Future<List<Map<String, dynamic>>> _products;
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _products = _loadProducts();
  }

  Future<List<Map<String, dynamic>>> _loadProducts({String? search}) async {
    final response = await widget.api.products(search: search);
    final results = response['results'];
    if (results is List) {
      return results.whereType<Map<String, dynamic>>().toList();
    }
    return const [];
  }

  void _reload({String? search}) {
    setState(() {
      _products = _loadProducts(search: search);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Catalog'),
        actions: [
          IconButton(
            tooltip: 'Cart',
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => CartPage(api: widget.api)),
              );
            },
            icon: const Icon(Icons.shopping_cart),
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search products',
                suffixIcon: IconButton(
                  icon: const Icon(Icons.search),
                  onPressed: () => _reload(search: _searchController.text),
                ),
              ),
              onSubmitted: (value) => _reload(search: value),
            ),
          ),
          Expanded(
            child: FutureBuilder<List<Map<String, dynamic>>>(
              future: _products,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError) {
                  final message = snapshot.error is ApiException
                      ? (snapshot.error as ApiException).message
                      : 'Could not load catalog.';
                  return _ErrorView(
                    message: message,
                    onRetry: () => _reload(search: _searchController.text),
                  );
                }
                final products = snapshot.data ?? const [];
                if (products.isEmpty) {
                  return const Center(child: Text('No products found.'));
                }
                return ListView.separated(
                  itemCount: products.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final product = products[index];
                    return ListTile(
                      title: Text(product['name']?.toString() ?? 'Product'),
                      subtitle: Text(
                        '${product['sku'] ?? ''} • \$${product['unit_price'] ?? '0.00'}',
                      ),
                      onTap: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => ProductDetailPage(
                              api: widget.api,
                              productId: product['id'].toString(),
                            ),
                          ),
                        );
                      },
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const _ErrorView({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(message),
          const SizedBox(height: 12),
          OutlinedButton(onPressed: onRetry, child: const Text('Retry')),
        ],
      ),
    );
  }
}