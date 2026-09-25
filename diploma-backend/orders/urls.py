from django.urls import path
from . import api_views
from .views import (
    checkout_confirm_view,
    checkout_customer_view,
    checkout_delivery_view,
    checkout_payment_method_view,
    generate_account_api_view,
    order_detail_view,
    order_history_view,
    payment_view,
)

app_name = "orders"

urlpatterns = [
    path("checkout/customer/", checkout_customer_view, name="customer"),
    path("checkout/delivery/", checkout_delivery_view, name="delivery"),
    path("checkout/payment-method/", checkout_payment_method_view, name="payment_method"),
    path("checkout/confirm/", checkout_confirm_view, name="confirm"),
    path("payment/<int:order_id>/", payment_view, name="payment"),
    path("history/", order_history_view, name="history"),
    path("<int:order_id>/", order_detail_view, name="detail"),
    path("api/orders/", api_views.create_order_api_view, name="api_orders"),
    path("history-order/", order_history_view, name="history_order_alt"),
]
