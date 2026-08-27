from decimal import Decimal

from .models import ShopSettings


def get_shop_settings():
    settings = ShopSettings.objects.first()

    if settings:
        return settings

    return ShopSettings(
        delivery_free_from=Decimal("2000.00"),
        delivery_price=Decimal("200.00"),
        express_delivery_extra=Decimal("500.00"),
    )


def calculate_delivery(
    products_total,
    delivery_type,
):
    settings = get_shop_settings()

    if delivery_type == "express":
        return settings.express_delivery_extra

    if products_total < settings.delivery_free_from:
        return settings.delivery_price

    return Decimal("0.00")