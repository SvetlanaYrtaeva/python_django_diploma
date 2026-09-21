from decimal import Decimal

from .models import Category

try:
    from cart.models import Cart
except ImportError:
    Cart = None


def global_context(request):
    categories = (
        Category.objects.active()
        .filter(is_active=True, parent__isnull=True)
        .prefetch_related("children")
    )

    basket_count = 0
    basket_price = Decimal("0.00")

    if Cart is not None:
        cart = None
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        elif request.session.session_key:
            cart = Cart.objects.filter(
                session_key=request.session.session_key
            ).first()

        if cart:
            for item in cart.items.select_related("product"):
                basket_count += item.quantity
                basket_price += item.total

    return {
        "menu_categories": categories,
        "basketCount": {
            "count": basket_count,
            "price": str(basket_price),
        },
    }
