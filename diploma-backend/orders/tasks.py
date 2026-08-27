import random

from celery import shared_task

from .models import Order


@shared_task
def process_payment(
    order_id,
    payment_number,
):
    try:
        order = Order.objects.get(
            pk=order_id,
            is_deleted=False,
        )
    except Order.DoesNotExist:
        return

    number = str(payment_number)

    if (
        int(number) % 2 == 0
        and not number.endswith("0")
    ):
        order.payment_status = (
            Order.PaymentStatus.PAID
        )

        order.payment_error = ""
    else:
        order.payment_status = (
            Order.PaymentStatus.ERROR
        )

        order.payment_error = random.choice(
            [
                "Платёж отклонён.",
                "Ошибка платёжной системы.",
                "Не удалось подтвердить оплату.",
            ],
        )

    order.save(
        update_fields=[
            "payment_status",
            "payment_error",
            "updated_at",
        ],
    )