from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from catalog.models import Product
from .models import Cart, CartItem

MAX_QUANTITY = 999


def get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    if not request.session.session_key:
        request.session.create()

    request.session.modified = True

    cart, _ = Cart.objects.get_or_create(
        session_key=request.session.session_key,
    )
    return cart


def active_products():
    return Product.objects.filter(is_active=True, is_deleted=False)


def _img_or_placeholder(product):
    if product.image:
        return product.image.url
    return "/static/frontend/assets/img/logo.png"


def serialize_cart(cart):
    items = cart.items.select_related("product")
    return [
        {
            "id": item.product.id,
            "product_id": item.product.id,
            "name": item.product.name,
            "title": item.product.name,
            "image": _img_or_placeholder(item.product),
            "images": [
                {
                    "src": _img_or_placeholder(item.product),
                    "alt": item.product.name,
                }
            ],
            "price": str(item.product.price),
            "count": item.quantity,
            "quantity": item.quantity,
            "total": str(item.total),
        }
        for item in items
    ]


@api_view(["GET", "POST", "DELETE"])
def basket_api_view(request):
    cart = get_cart(request)

    if request.method == "GET":
        return Response(serialize_cart(cart))

    data = request.data

    product_id = data.get("id") or data.get("productId") or data.get("product_id")
    count = data.get("count") or data.get("quantity") or 1

    try:
        count = int(count)
    except (TypeError, ValueError):
        count = 1
    if count <= 0:
        count = 1

    if not product_id:
        return Response(
            {"detail": "Требуется поле id"},
            status=400,
        )

    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        return Response(
            {"detail": "id должен быть числом"},
            status=400,
        )

    product = get_object_or_404(active_products(), pk=product_id)

    if request.method == "POST":
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product
        )
        if created:
            item.quantity = count
        else:
            item.quantity += count
        item.quantity = min(item.quantity, MAX_QUANTITY)
        item.save(update_fields=["quantity"])

    elif request.method == "DELETE":
        try:
            item = CartItem.objects.get(cart=cart, product=product)
        except CartItem.DoesNotExist:
            return Response(serialize_cart(cart))

        item.quantity -= count
        if item.quantity <= 0:
            item.delete()
        else:
            item.save(update_fields=["quantity"])

    return Response(serialize_cart(cart))


def cart_detail_view(request):
    from django.shortcuts import render

    cart = get_cart(request)
    items = cart.items.select_related("product")
    total = sum((item.total for item in items), Decimal("0.00"))
    return render(
        request,
        "frontend/cart.html",
        {"cart": cart, "items": items, "total": total},
    )


def cart_add_view(request, product_id):
    if request.method != "POST":
        return Response(
            {"detail": "Метод не поддерживается."},
            status=405,
        )

    product = get_object_or_404(active_products(), pk=product_id)
    cart = get_cart(request)

    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product
    )
    if created:
        item.quantity = 1
    else:
        item.quantity += 1
    item.quantity = min(item.quantity, MAX_QUANTITY)
    item.save(update_fields=["quantity"])

    return Response(serialize_cart(cart))


def cart_update_view(request, item_id):
    from django.http import JsonResponse
    from django.shortcuts import redirect

    if request.method != "POST":
        return JsonResponse(
            {"detail": "Метод не поддерживается."}, status=405
        )

    cart = get_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    quantity = 1
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        pass

    if quantity <= 0:
        item.delete()
    else:
        item.quantity = min(quantity, MAX_QUANTITY)
        item.save(update_fields=["quantity"])

    return redirect("cart:detail")


def cart_remove_view(request, item_id):
    from django.http import JsonResponse
    from django.shortcuts import redirect

    if request.method != "POST":
        return JsonResponse(
            {"detail": "Метод не поддерживается."}, status=405
        )

    cart = get_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()

    return redirect("cart:detail")
