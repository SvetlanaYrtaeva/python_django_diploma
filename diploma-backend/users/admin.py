from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
        "is_staff",
        "is_active",
        "is_deleted",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "is_deleted",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Дополнительные данные",
            {
                "fields": (
                    "phone",
                    "avatar",
                    "is_deleted",
                ),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Дополнительные данные",
            {
                "fields": (
                    "email",
                    "phone",
                    "avatar",
                ),
            },
        ),
    )

    actions = [
        "soft_delete_users",
    ]

    @admin.action(
        description="Мягко удалить пользователей",
    )
    def soft_delete_users(self, request, queryset):
        queryset.update(
            is_deleted=True,
            is_active=False,
        )