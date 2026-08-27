from django.conf import settings
from django.db import models


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        blank=True,
        null=True,
    )

    session_key = models.CharField(
        "ключ сессии",
        max_length=40,
        unique=True,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        "дата создания",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "корзина"
        verbose_name_plural = "корзины"

    def __str__(self):
        if self.user:
            return f"Корзина пользователя {self.user}"

        return f"Гостевая корзина {self.session_key}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="cart_items",
    )

    quantity = models.PositiveIntegerField(
        "количество",
        default=1,
    )

    class Meta:
        verbose_name = "товар корзины"
        verbose_name_plural = "товары корзины"

        constraints = [
            models.UniqueConstraint(
                fields=(
                    "cart",
                    "product",
                ),
                name="unique_cart_product",
            ),
        ]

    @property
    def total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product} — {self.quantity}"