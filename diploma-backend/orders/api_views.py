import json

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from cart.models import Cart
from .models import Order, OrderItem
from .services import calculate_delivery, fake_payment_service

User = get_user_model()


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


@api_view(["POST"])
def create_order_api_view(request: Request) -> Response:
    if not request.user.is_authenticated:
        return Response({"error": "Требуется авторизация"}, status=401)

    try:
        cart = request.user.cart
    except Cart.DoesNotExist:
        return Response({"error": "Корзина пуста"}, status=400)

    items = cart.items.select_related("product")
    if not items.exists():
        return Response({"error": "Корзина пуста"}, status=400)

    data = _extract_data(request)

    full_name = (
        data.get("fullName")
        or data.get("full_name")
        or data.get("name")
        or request.user.full_name
        or f"{request.user.first_name} {request.user.last_name}".strip()
        or request.user.username
    )

    email = data.get("email") or request.user.email
    if not email:
        return Response({"error": "Укажите email"}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return Response({"error": "Некорректный email"}, status=400)

    phone = (
        data.get("phone")
        or data.get("tel")
        or request.user.phone
        or ""
    )

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
        (item.total for item in items), Decimal("0.00")
    )

    try:
        delivery_total = calculate_delivery(products_total, delivery_type)
    except Exception:
        delivery_total = Decimal("0.00")

    total = products_total + delivery_total

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
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
                product=item.product,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
            )
            for item in items
        ])

        cart.items.all().delete()

    return Response({"orderId": order.id})


@api_view(["GET"])
def order_detail_api_view(request: Request, order_id: int) -> Response:
    if not request.user.is_authenticated:
        return Response({"error": "Требуется авторизация"}, status=401)

    try:
        order = request.user.orders.prefetch_related("items").get(
            pk=order_id, is_deleted=False
        )
    except Order.DoesNotExist:
        return Response({"error": "Заказ не найден"}, status=404)

    return Response({
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
        "products": [
            {
                "id": item.id,
                "productId": item.product_id,
                "title": item.product_name,
                "name": item.product_name,
                "price": str(item.price),
                "quantity": item.quantity,
                "total": str(item.total),
            }
            for item in order.items.all()
        ],
    })


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
