from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "email",
        "username",
        "phone",
        "is_staff",
        "is_superuser",
        "is_deleted",
    )
    list_filter = ("is_staff", "is_superuser", "is_deleted")
    search_fields = ("email", "username", "phone")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_deleted=False)

    actions = ["soft_delete"]

    @admin.action(description="Удалить (мягко)")
    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)
        self.message_user(request, "Выбранные пользователи помечены как удалённые.")
