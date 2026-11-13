from django.db.models import Q

from .models import Product


def public_products():
    return Product.objects.filter(is_published=True, store__status="ACTIVE").select_related(
        "store", "inventory"
    )


def public_product_detail(*, product_id):
    return public_products().filter(pk=product_id).first()


def search_products(*, store_id=None, search=None):
    queryset = public_products()
    if store_id is not None:
        queryset = queryset.filter(store_id=store_id)
    if search:
        queryset = queryset.filter(Q(name__icontains=search) | Q(sku__icontains=search))
    return queryset.order_by("name")
