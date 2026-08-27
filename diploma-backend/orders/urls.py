from django.urls import path

from .views import (
    checkout_confirm_view,
    checkout_customer_view,
    checkout_delivery_view,
    checkout_payment_method_view,
    order_detail_view,
    order_history_view,
    payment_view,
)


app_name = "orders"


urlpatterns = [
    path(
        "checkout/customer/",
        checkout_customer_view,
        name="customer",
    ),

    path(
        "checkout/delivery/",
        checkout_delivery_view,
        name="delivery",
    ),

    path(
        "checkout/payment-method/",
        checkout_payment_method_view,
        name="payment_method",
    ),

    path(
        "checkout/confirm/",
        checkout_confirm_view,
        name="confirm",
    ),

    path(
        "payment/<int:order_id>/",
        payment_view,
        name="payment",
    ),

    path(
        "history/",
        order_history_view,
        name="history",
    ),

    path(
        "<int:order_id>/",
        order_detail_view,
        name="detail",
    ),
]