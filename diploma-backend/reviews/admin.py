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

    list_filter = (
        "rating",
        "is_deleted",
        "created_at",
    )

    search_fields = (
        "product__name",
        "user__username",
        "user__email",
        "text",
    )

    actions = [
        "soft_delete_reviews",
    ]

    @admin.action(
        description="Мягко удалить отзывы",
    )
    def soft_delete_reviews(self, request, queryset):
        queryset.update(
            is_deleted=True,
        )