from django.db import migrations
from django.contrib.auth import get_user_model


def create_initial_data(apps, schema_editor):
    User = get_user_model()
    ShopSettings = apps.get_model("orders", "ShopSettings")

    # ── Администратор ──
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            password="admin123",
        )

    # ── Настройки магазина ──
    if not ShopSettings.objects.exists():
        ShopSettings.objects.create(
            delivery_free_from=2000,
            delivery_price=200,
            express_delivery_extra=500,
        )


def reverse_initial_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_initial_data,
            reverse_initial_data,
        ),
    ]
