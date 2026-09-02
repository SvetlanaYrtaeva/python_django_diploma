from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "rating",
        "created_at",
        "is_deleted",
    )
    list_filter = ("rating", "is_deleted", "created_at")
    search_fields = ("text", "product__name", "user__email")
    readonly_fields = ("created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_deleted=False)

    actions = ["soft_delete"]

    @admin.action(description="Удалить (мягко)")
    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)
        self.message_user(request, "Выбранные отзывы помечены как удалённые.")
