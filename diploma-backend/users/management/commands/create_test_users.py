from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

TEST_USERS = [
    {
        "email": "buyer1@example.com",
        "username": "buyer1",
        "password": "123456",
        "first_name": "Иван",
        "last_name": "Иванов",
        "phone": "+79001110011",
    },
    {
        "email": "buyer2@example.com",
        "username": "buyer2",
        "password": "123456",
        "first_name": "Мария",
        "last_name": "Петрова",
        "phone": "+79002220022",
    },
    {
        "email": "buyer3@example.com",
        "username": "buyer3",
        "password": "123456",
        "first_name": "Пётр",
        "last_name": "Сидоров",
        "phone": "+79003330033",
    },
]


class Command(BaseCommand):
    help = "Создаёт тестовых покупателей с паролем 123456"

    def handle(self, *args, **options):
        created = 0
        for data in TEST_USERS:
            user, was_created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "username": data["username"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "phone": data["phone"],
                },
            )
            user.set_password(data["password"])
            user.save()
            if was_created:
                created += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Создан пользователь: {data['email']}")
                )
            else:
                self.stdout.write(
                    f"Обновлён пароль для: {data['email']}"
                )
        self.stdout.write(
            self.style.SUCCESS(f"Готово. Создано: {created}. Пароль: 123456")
        )
