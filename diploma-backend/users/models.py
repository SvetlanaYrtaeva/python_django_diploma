from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        "email",
        unique=True,
    )

    phone = models.CharField(
        "телефон",
        max_length=30,
        unique=True,
        blank=True,
        null=True,
    )

    avatar = models.ImageField(
        "аватар",
        upload_to="avatars/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp",
                ],
            ),
        ],
    )

    is_deleted = models.BooleanField(
        "удалён",
        default=False,
    )

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        full_name = self.get_full_name()
        return full_name or self.email