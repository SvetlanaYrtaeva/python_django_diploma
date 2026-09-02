from celery import shared_task

from .models import Order
from .services import fake_payment_service


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def process_payment(self, order_id: int, number: str = ""):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return f"Order {order_id} not found"

    if order.payment_status not in (
        Order.PaymentStatus.WAITING,
        Order.PaymentStatus.PROCESSING,
    ):
        return f"Order {order_id} already processed"

    order.payment_status = Order.PaymentStatus.PROCESSING
    order.payment_number = number
    order.save(update_fields=["payment_status", "payment_number", "updated_at"])

    success, error = fake_payment_service(number)

    if success:
        order.payment_status = Order.PaymentStatus.PAID
        order.payment_error = ""
    else:
        order.payment_status = Order.PaymentStatus.ERROR
        order.payment_error = error

    order.save(update_fields=["payment_status", "payment_error", "updated_at"])

    return f"Order {order_id}: {order.payment_status}"
