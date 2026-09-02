from django.conf import settings
from django.db import models


class ShopSettings(models.Model):
    delivery_free_from = models.DecimalField(
        "бесплатная доставка от",
        max_digits=12,
        decimal_places=2,
        default=2000,
    )

    delivery_price = models.DecimalField(
        "обычная доставка",
        max_digits=12,
        decimal_places=2,
        default=200,
    )

    express_delivery_extra = models.DecimalField(
        "доплата за экспресс-доставку",
        max_digits=12,
        decimal_places=2,
        default=500,
    )

    class Meta:
        verbose_name = "настройки магазина"
        verbose_name_plural = "настройки магазина"

    def __str__(self):
        return "Настройки магазина"

    def save(self, *args, **kwargs):
        if not self.pk and ShopSettings.objects.exists():
            raise ValueError("Настройки магазина уже существуют")
        super().save(*args, **kwargs)


class Order(models.Model):
    class DeliveryType(models.TextChoices):
        STANDARD = "standard", "Доставка"
        EXPRESS = "express", "Экспресс-доставка"

    class PaymentType(models.TextChoices):
        CARD = "card", "Онлайн картой"
        SOMEONE = "someone", "Онлайн со случайного чужого счёта"

    class PaymentStatus(models.TextChoices):
        WAITING = "waiting", "Ожидает оплаты"
        PROCESSING = "processing", "Обрабатывается"
        PAID = "paid", "Оплачен"
        ERROR = "error", "Ошибка оплаты"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        blank=True,
        null=True,
        verbose_name="пользователь",
    )

    full_name = models.CharField("Ф. И. О.", max_length=255)
    email = models.EmailField("email")
    phone = models.CharField("телефон", max_length=30)
    city = models.CharField("город", max_length=150)
    address = models.CharField("адрес", max_length=500)

    delivery_type = models.CharField(
        "способ доставки",
        max_length=20,
        choices=DeliveryType.choices,
    )

    payment_type = models.CharField(
        "способ оплаты",
        max_length=20,
        choices=PaymentType.choices,
    )

    payment_number = models.CharField(
        "номер карты/счёта",
        max_length=8,
        blank=True,
        default="",
    )

    comment = models.TextField("комментарий к заказу", blank=True)

    products_total = models.DecimalField(
        "стоимость товаров",
        max_digits=12,
        decimal_places=2,
    )

    delivery_total = models.DecimalField(
        "стоимость доставки",
        max_digits=12,
        decimal_places=2,
    )

    total = models.DecimalField(
        "итого",
        max_digits=12,
        decimal_places=2,
    )

    payment_status = models.CharField(
        "статус оплаты",
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.WAITING,
    )

    payment_error = models.CharField(
        "ошибка оплаты",
        max_length=500,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField("дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("дата изменения", auto_now=True)
    is_deleted = models.BooleanField("удалён", default=False)

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "заказы"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Заказ №{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="заказ",
    )

    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        verbose_name="товар",
    )

    product_name = models.CharField("название товара", max_length=255)

    price = models.DecimalField(
        "цена на момент покупки",
        max_digits=12,
        decimal_places=2,
    )

    quantity = models.PositiveIntegerField("количество")

    class Meta:
        verbose_name = "товар заказа"
        verbose_name_plural = "товары заказа"

    @property
    def total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"
