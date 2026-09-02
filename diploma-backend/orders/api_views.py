from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from cart.models import Cart
from .models import Order, OrderItem

User = get_user_model()


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

    products_total = sum(
        (item.total for item in items), Decimal("0.00")
    )

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            full_name=request.user.full_name,
            email=request.user.email,
            phone=request.user.phone or "",
            city="",
            address="",
            delivery_type=Order.DeliveryType.STANDARD,
            payment_type=Order.PaymentType.CARD,
            products_total=products_total,
            delivery_total=Decimal("0.00"),
            total=products_total,
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
        order = request.user.orders.prefetch_related("items").get(pk=order_id, is_deleted=False)
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

    data = dict(request.data) if request.data else {}

    number = (
        data.get("number")
        or data.get("number1")
        or data.get("card")
        or data.get("account")
        or ""
    )

    if not number:
        return Response({"error": "Введите номер"}, status=400)

    number = str(number).strip()

    if not number.isdigit():
        return Response({"error": "Номер должен содержать только цифры"}, status=400)
    if len(number) > 8:
        return Response({"error": "Номер не должен быть длиннее 8 цифр"}, status=400)

    order.payment_status = Order.PaymentStatus.PROCESSING
    order.payment_error = ""
    order.payment_number = number
    order.save(update_fields=["payment_status", "payment_error", "payment_number", "updated_at"])

    try:
        from .tasks import process_payment
        process_payment.delay(order.id, number)
    except Exception:
        from .services import fake_payment_service
        success, error = fake_payment_service(number)
        if success:
            order.payment_status = Order.PaymentStatus.PAID
            order.payment_error = ""
        else:
            order.payment_status = Order.PaymentStatus.ERROR
            order.payment_error = error
        order.save(update_fields=["payment_status", "payment_error", "updated_at"])

    return Response({
        "success": True,
        "orderId": order.id,
        "status": order.payment_status,
    })
