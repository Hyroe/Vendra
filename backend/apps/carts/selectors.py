from .models import Cart


def get_active_cart(*, customer):
    return Cart.objects.filter(customer=customer).order_by("-updated_at").first()
