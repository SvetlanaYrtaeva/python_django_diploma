from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from cart.views import get_cart

from .forms import (
    CustomerDataForm,
    DeliveryForm,
    PaymentForm,
    PaymentMethodForm,
)
from .models import Order, OrderItem
from .services import calculate_delivery, generate_random_account, validate_payment_number
from .tasks import process_payment

User = get_user_model()


def checkout_customer_view(request):
    cart = get_cart(request)

    if not cart.items.exists():
        messages.warning(request, "Корзина пуста.")
        return redirect("cart:detail")

    if request.method == "POST":
        form = CustomerDataForm(request.POST)

        if form.is_valid():
            request.session["checkout_customer"] = form.cleaned_data
            return redirect("orders:delivery")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                "full_name": request.user.full_name,
                "email": request.user.email,
                "phone": request.user.phone or "",
            }
        form = CustomerDataForm(initial=initial)

    return render(
        request,
        "frontend/order.html",
        {"form": form, "step": "customer"},
    )


def checkout_delivery_view(request):
    customer = request.session.get("checkout_customer")
    if not customer:
        return redirect("orders:customer")

    if request.method == "POST":
        form = DeliveryForm(request.POST)

        if form.is_valid():
            request.session["checkout_delivery"] = form.cleaned_data
            return redirect("orders:payment_method")
    else:
        form = DeliveryForm(initial={"delivery_type": "standard"})

    return render(
        request,
        "frontend/order.html",
        {"form": form, "step": "delivery"},
    )


def checkout_payment_method_view(request):
    customer = request.session.get("checkout_customer")
    delivery = request.session.get("checkout_delivery")

    if not customer or not delivery:
        return redirect("orders:customer")

    if request.method == "POST":
        form = PaymentMethodForm(request.POST)

        if form.is_valid():
            request.session["checkout_payment"] = form.cleaned_data
            return redirect("orders:confirm")
    else:
        form = PaymentMethodForm()

    return render(
        request,
        "frontend/order.html",
        {"form": form, "step": "payment_method"},
    )


def checkout_confirm_view(request):
    cart = get_cart(request)

    customer = request.session.get("checkout_customer")
    delivery = request.session.get("checkout_delivery")
    payment = request.session.get("checkout_payment")

    if not customer or not delivery or not payment:
        return redirect("orders:customer")

    items = list(cart.items.select_related("product"))

    if not items:
        messages.warning(request, "Корзина пуста.")
        return redirect("cart:detail")

    products_total = sum(
        (item.total for item in items), Decimal("0.00")
    )

    delivery_total = calculate_delivery(
        products_total, delivery["delivery_type"]
    )
    total = products_total + delivery_total

    if request.method == "POST":
        with transaction.atomic():
            user = request.user if request.user.is_authenticated else None

            if user is None and customer.get("password1"):
                email = customer["email"].lower()

                if User.objects.filter(email=email).exists():
                    messages.error(
                        request,
                        "Пользователь с указанным email уже существует.",
                    )
                    return redirect("orders:customer")

                username = email.split("@")[0]
                base = username
                i = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base}{i}"
                    i += 1

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=customer["password1"],
                    first_name=customer["full_name"],
                    phone=customer["phone"],
                )
                login(request, user)

            order = Order.objects.create(
                user=user,
                full_name=customer["full_name"],
                email=customer["email"],
                phone=customer["phone"],
                city=delivery["city"],
                address=delivery["address"],
                delivery_type=delivery["delivery_type"],
                payment_type=payment["payment_type"],
                products_total=products_total,
                delivery_total=delivery_total,
                total=total,
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

        request.session["checkout_order_id"] = order.id

        return redirect("orders:payment", order_id=order.id)

    return render(
        request,
        "frontend/order.html",
        {
            "items": items,
            "customer": customer,
            "delivery": delivery,
            "payment": payment,
            "products_total": products_total,
            "delivery_total": delivery_total,
            "total": total,
            "step": "confirm",
        },
    )


def payment_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id, is_deleted=False)

    if request.user.is_authenticated:
        if order.user_id != request.user.id:
            return redirect("catalog:index")
    else:
        if request.session.get("checkout_order_id") != order.id:
            return redirect("catalog:index")

    if request.method == "POST":
        form = PaymentForm(request.POST)

        if form.is_valid():
            number = form.cleaned_data["number"]

            ok, error = validate_payment_number(number)
            if not ok:
                form.add_error("number", error)
                return render(
                    request,
                    "frontend/payment.html",
                    {"order": order, "form": form},
                )

            order.payment_status = Order.PaymentStatus.PROCESSING
            order.payment_error = ""
            order.payment_number = number
            order.save(update_fields=[
                "payment_status", "payment_error",
                "payment_number", "updated_at",
            ])

            process_payment.delay(order.id, number)

            messages.info(
                request,
                "Ждём подтверждения оплаты от платёжной системы.",
            )
            return redirect("orders:detail", order_id=order.id)
    else:
        form = PaymentForm()

    return render(
        request,
        "frontend/payment.html",
        {"order": order, "form": form},
    )


def generate_account_api_view(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Метод не поддерживается."}, status=405)

    return JsonResponse({"number": generate_random_account()})


@login_required
def order_history_view(request):
    orders = request.user.orders.filter(is_deleted=False)
    return render(
        request,
        "frontend/historyorder.html",
        {"orders": orders},
    )


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(
        request.user.orders.filter(is_deleted=False).prefetch_related("items"),
        pk=order_id,
    )
    return render(
        request,
        "frontend/oneorder.html",
        {"order": order},
    )
