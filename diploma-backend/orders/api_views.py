import json
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Prefetch
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from cart.models import Cart
from catalog.models import Product
from .models import Order, OrderItem
from .services import calculate_delivery, fake_payment_service


def _product_image_url(product):
    """
    Возвращает URL картинки товара.
    Если картинки нет — возвращает путь к заглушке.
    Это критически важно, чтобы фронтенд не падал на product.images
    """
    if product and product.image:
        return product.image.url
    return "/static/frontend/assets/img/logo.png"


def _extract_data(request):
    data = request.data
    if isinstance(data, dict):
        return data
    if isinstance(data, str):
        try:
            parsed = json.loads(data)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
    return {}


def _extract_basket_entries(request, data):
    entries = []
    if isinstance(data, list):
        entries = [d for d in data if isinstance(d, dict)]
    elif isinstance(data, dict):
        for key in ("products", "items", "basket"):
            if isinstance(data.get(key), list):
                entries = [d for d in data[key] if isinstance(d, dict)]
                break
    return entries


def _collect_order_items(request, data):
    counts = {}

    for entry in _extract_basket_entries(request, data):
        pid = entry.get("id") or entry.get("productId")
        try:
            pid = int(pid)
        except (TypeError, ValueError):
            continue
        try:
            cnt = int(entry.get("count") or entry.get("quantity") or 1)
        except (TypeError, ValueError):
            cnt = 1
        if cnt < 1:
            cnt = 1
        counts[pid] = counts.get(pid, 0) + cnt

    result = []
    if counts:
        products = Product.objects.active().filter(id__in=counts.keys())
        result = [(p, counts[p.id]) for p in products]

    if not result:
        try:
            cart = request.user.cart
        except Cart.DoesNotExist:
            return []
        result = [
            (item.product, item.quantity)
            for item in cart.items.select_related("product")
        ]

    return result


def serialize_order_item(item):
    """
    Сериализует позицию заказа.
    ВАЖНО: Здесь мы добавляем поле 'images', которое ждет фронтенд.
    """
    product = item.product if hasattr(item, 'product') else None

    image_url = _product_image_url(product)

    return {
        "id": item.id,
        "productId": item.product_id,
        "title": item.product_name,
        "name": item.product_name,
        "price": str(item.price),
        "count": item.quantity,
        "quantity": item.quantity,
        "total": str(item.total),
        "images": [
            {"src": image_url, "alt": item.product_name or "Товар"}
        ],
    }


def serialize_order(order):
    """
    Сериализует весь заказ.
    """
    return {
        "id": order.id,
        "orderId": order.id,
        "createdAt": order.created_at.isoformat(),
        "fullName": order.full_name,
        "phone": order.phone,
        "email": order.email,
        "deliveryType": order.delivery_type,
        "city": order.city,
        "address": order.address,
        "paymentType": order.payment_type,
        "status": order.payment_status,
        "paymentStatus": order.payment_status,
        "paymentError": order.payment_error or "",
        "totalCost": str(order.total),
        "productsTotal": str(order.products_total),
        "deliveryTotal": str(order.delivery_total),
        # Товары теперь приходят с готовыми картинками
        "products": [
            serialize_order_item(item) for item in order.items.all()
        ],
    }


@api_view(["GET", "POST"])
def create_order_api_view(request: Request) -> Response:
    """
    GET  — история заказов текущего пользователя.
    POST — создание заказа.
    """
    if not request.user.is_authenticated:
        return Response({"error": "Требуется авторизация"}, status=401)

    if request.method == "GET":
        orders = (
            request.user.orders
            .filter(is_deleted=False)
            .prefetch_related("items__product")
        )
        return Response([serialize_order(o) for o in orders])

    data = _extract_data(request)

    items = _collect_order_items(request, data)
    if not items:
        return Response({"error": "Корзина пуста"}, status=400)

    user = request.user

    full_name = (
            data.get("fullName")
            or data.get("full_name")
            or user.full_name
            or f"{user.first_name} {user.last_name}".strip()
            or user.username
    )

    email = data.get("email") or user.email
    if not email:
        return Response({"error": "Укажите email"}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return Response({"error": "Некорректный email"}, status=400)

    phone = data.get("phone") or data.get("tel") or user.phone or ""
    city = data.get("city") or data.get("cityName") or ""
    address = (
            data.get("address")
            or data.get("street")
            or data.get("deliveryAddress")
            or ""
    )

    delivery_type = (
            data.get("deliveryType")
            or data.get("delivery_type")
            or Order.DeliveryType.STANDARD
    )
    payment_type = (
            data.get("paymentType")
            or data.get("payment_type")
            or Order.PaymentType.CARD
    )

    products_total = sum(
        (product.price * quantity for product, quantity in items),
        Decimal("0.00"),
    )

    try:
        delivery_total = calculate_delivery(products_total, delivery_type)
    except Exception:
        delivery_total = Decimal("0.00")

    total = products_total + delivery_total

    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            full_name=full_name,
            email=email,
            phone=phone,
            city=city,
            address=address,
            delivery_type=delivery_type,
            payment_type=payment_type,
            products_total=products_total,
            delivery_total=delivery_total,
            total=total,
            payment_status=Order.PaymentStatus.WAITING,
        )

        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=product,
                product_name=product.name,
                price=product.price,
                quantity=quantity,
            )
            for product, quantity in items
        ])

        try:
            user.cart.items.all().delete()
        except Cart.DoesNotExist:
            pass

    return Response({"orderId": order.id})


@api_view(["GET", "POST"])
def order_detail_api_view(request: Request, order_id: int) -> Response:
    """
    GET  — детали заказа.
    POST — подтверждение заказа.
    """
    if not request.user.is_authenticated:
        return Response({"error": "Требуется авторизация"}, status=401)

    try:
        order = (
            request.user.orders
            .filter(is_deleted=False)
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=OrderItem.objects.select_related("product"),
                )
            )
            .get(pk=order_id)
        )
    except Order.DoesNotExist:
        return Response({"error": "Заказ не найден"}, status=404)

    if request.method == "POST":
        return Response({"orderId": order.id})

    return Response(serialize_order(order))


@api_view(["POST"])
def payment_api_view(request: Request, order_id: int) -> Response:
    if not request.user.is_authenticated:
        return Response({"error": "Требуется авторизация"}, status=401)

    try:
        order = request.user.orders.get(pk=order_id, is_deleted=False)
    except Order.DoesNotExist:
        return Response({"error": "Заказ не найден"}, status=404)

    data = _extract_data(request)

    number = (
            data.get("number1")
            or data.get("number")
            or data.get("card")
            or data.get("account")
            or ""
    )

    if not number:
        return Response({"error": "Введите номер карты"}, status=400)

    number = str(number).replace(" ", "").replace("-", "")

    if not number.isdigit():
        return Response(
            {"error": "Номер должен содержать только цифры"},
            status=400,
        )

    if len(number) > 8:
        number = number[-8:]

    order.payment_status = Order.PaymentStatus.PROCESSING
    order.payment_error = ""
    order.payment_number = number
    order.save(update_fields=[
        "payment_status", "payment_error",
        "payment_number", "updated_at",
    ])

    success, error = fake_payment_service(number)
    if success:
        order.payment_status = Order.PaymentStatus.PAID
        order.payment_error = ""
    else:
        order.payment_status = Order.PaymentStatus.ERROR
        order.payment_error = error
    order.save(update_fields=[
        "payment_status", "payment_error", "updated_at",
    ])

    return Response({
        "success": True,
        "orderId": order.id,
        "status": order.payment_status,
    })
