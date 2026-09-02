import random
from decimal import Decimal
from typing import Tuple

from .models import Order, ShopSettings


def get_shop_settings() -> ShopSettings:
    settings_obj, _ = ShopSettings.objects.get_or_create(pk=1)
    return settings_obj


def calculate_delivery(
    products_total: Decimal,
    delivery_type: str,
) -> Decimal:
    settings_obj = get_shop_settings()

    if delivery_type == Order.DeliveryType.EXPRESS:
        return settings_obj.delivery_price + settings_obj.express_delivery_extra

    # standard
    if products_total >= settings_obj.delivery_free_from:
        return Decimal("0")
    return settings_obj.delivery_price


def validate_payment_number(number: str) -> Tuple[bool, str]:
    if not number:
        return False, "Введите номер."
    if not number.isdigit():
        return False, "Номер должен содержать только цифры."
    if len(number) > 8:
        return False, "Номер не должен быть длиннее 8 цифр."
    if int(number) % 2 != 0:
        return False, "Номер должен быть чётным."
    return True, ""


def fake_payment_service(number: str) -> Tuple[bool, str]:
    if int(number) % 2 != 0 or number.endswith("0"):
        errors = [
            "Недостаточно средств на счёте.",
            "Сервис оплаты временно недоступен.",
            "Превышен лимит транзакций.",
            "Неверный реквизит получателя.",
        ]
        return False, random.choice(errors)
    return True, ""


def generate_random_account() -> str:
    number = random.randint(10, 99999999)
    if number % 2 != 0:
        number += 1
    return str(number)
