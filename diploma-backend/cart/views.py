import json
from decimal import Decimal

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Product

from .models import Cart, CartItem


MAX_QUANTITY = 999


def get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(
            user=request.user,
        )

        return cart

    if not request.session.session_key:
        request.session.create()

    cart, _ = Cart.objects.get_or_create(
        session_key=request.session.session_key,
    )

    return cart


def active_products():
    return Product.objects.filter(
        is_active=True,
        is_deleted=False,
    )


def serialize_cart(cart):
    items = cart.items.select_related(
        "product",
    )

    return [
        {
            "id": item.product.id,
            "product_id": item.product.id,
            "name": item.product.name,
            "title": item.product.name,
            "image": (
                item.product.image.url
                if item.product.image
                else ""
            ),
            "price": float(item.product.price),
            "count": item.quantity,
            "quantity": item.quantity,
            "total": float(item.total),
        }
        for item in items
    ]


def parse_request_data(request):
    content_type = request.content_type or ""

    if content_type.startswith(
        "application/json",
    ):
        try:
            payload = json.loads(
                request.body.decode("utf-8"),
            )
        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
        ):
            return None

        if not isinstance(payload, dict):
            return None

        return payload

    return request.POST


def parse_integer(value):
    try:
        return int(value)
    except (
        TypeError,
        ValueError,
    ):
        return None


def basket_api_view(request):
    cart = get_cart(request)

    if request.method == "GET":
        return JsonResponse(
            serialize_cart(cart),
            safe=False,
        )

    if request.method not in (
        "POST",
        "DELETE",
    ):
        return JsonResponse(
            {
                "detail": "Метод не поддерживается.",
            },
            status=405,
        )

    payload = parse_request_data(request)

    if payload is None:
        return JsonResponse(
            {
                "detail": "Некорректный JSON.",
            },
            status=400,
        )

    product_id = parse_integer(
        payload.get("id"),
    )

    count = parse_integer(
        payload.get("count", 1),
    )

    if product_id is None or count is None:
        return JsonResponse(
            {
                "detail": (
                    "id товара и количество "
                    "должны быть числами."
                ),
            },
            status=400,
        )

    if count <= 0:
        return JsonResponse(
            {
                "detail": (
                    "Количество должно быть "
                    "больше нуля."
                ),
            },
            status=400,
        )

    product = get_object_or_404(
        active_products(),
        pk=product_id,
    )

    if request.method == "POST":
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
        )

        if created:
            item.quantity = count
        else:
            item.quantity += count

        item.quantity = min(
            item.quantity,
            MAX_QUANTITY,
        )

        item.save(
            update_fields=[
                "quantity",
            ],
        )

    else:
        try:
            item = CartItem.objects.get(
                cart=cart,
                product=product,
            )
        except CartItem.DoesNotExist:
            return JsonResponse(
                serialize_cart(cart),
                safe=False,
            )

        item.quantity -= count

        if item.quantity <= 0:
            item.delete()
        else:
            item.save(
                update_fields=[
                    "quantity",
                ],
            )

    return JsonResponse(
        serialize_cart(cart),
        safe=False,
    )


def cart_detail_view(request):
    cart = get_cart(request)

    items = cart.items.select_related(
        "product",
    )

    total = sum(
        (
            item.total
            for item in items
        ),
        Decimal("0.00"),
    )

    return render(
        request,
        "frontend/cart.html",
        {
            "cart": cart,
            "items": items,
            "total": total,
        },
    )


def cart_add_view(
    request,
    product_id,
):
    if request.method != "POST":
        return JsonResponse(
            {
                "detail": "Метод не поддерживается.",
            },
            status=405,
        )

    product = get_object_or_404(
        active_products(),
        pk=product_id,
    )

    cart = get_cart(request)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
    )

    if created:
        item.quantity = 1
    else:
        item.quantity += 1

    item.quantity = min(
        item.quantity,
        MAX_QUANTITY,
    )

    item.save(
        update_fields=[
            "quantity",
        ],
    )

    return JsonResponse(
        serialize_cart(cart),
        safe=False,
    )


def cart_update_view(
    request,
    item_id,
):
    if request.method != "POST":
        return JsonResponse(
            {
                "detail": "Метод не поддерживается.",
            },
            status=405,
        )

    cart = get_cart(request)

    item = get_object_or_404(
        CartItem,
        pk=item_id,
        cart=cart,
    )

    quantity = parse_integer(
        request.POST.get("quantity"),
    )

    if quantity is None:
        quantity = 1

    if quantity <= 0:
        item.delete()
    else:
        item.quantity = min(
            quantity,
            MAX_QUANTITY,
        )

        item.save(
            update_fields=[
                "quantity",
            ],
        )

    return redirect("cart:detail")


def cart_remove_view(
    request,
    item_id,
):
    if request.method != "POST":
        return JsonResponse(
            {
                "detail": "Метод не поддерживается.",
            },
            status=405,
        )

    cart = get_cart(request)

    item = get_object_or_404(
        CartItem,
        pk=item_id,
        cart=cart,
    )

    item.delete()

    return redirect("cart:detail")


def basket_api_add_view(
    request,
    product_id,
):
    return cart_add_view(
        request,
        product_id,
    )


def basket_api_update_view(
    request,
    item_id,
):
    return cart_update_view(
        request,
        item_id,
    )


def basket_api_remove_view(
    request,
    item_id,
):
    return cart_remove_view(
        request,
        item_id,
    )