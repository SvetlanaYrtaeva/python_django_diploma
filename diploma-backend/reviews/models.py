from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models


class Review(models.Model):
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="товар",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="пользователь",
    )

    text = models.TextField(
        "текст отзыва",
    )

    rating = models.PositiveSmallIntegerField(
        "оценка",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    created_at = models.DateTimeField(
        "дата создания",
        auto_now_add=True,
    )

    is_deleted = models.BooleanField(
        "удалён",
        default=False,
    )

    class Meta:
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"
        ordering = (
            "-created_at",
        )

    def __str__(self):
        return (
            f"{self.product.name} — "
            f"{self.user.username}"
        )