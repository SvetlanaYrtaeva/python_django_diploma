from django.contrib import admin

from .models import Order, OrderItem, ShopSettings


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "price", "quantity")


@admin.register(ShopSettings)
class ShopSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "delivery_free_from",
        "delivery_price",
        "express_delivery_extra",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "total",
        "delivery_type",
        "payment_type",
        "payment_status",
        "created_at",
    )
    list_filter = (
        "delivery_type",
        "payment_type",
        "payment_status",
        "is_deleted",
    )
    search_fields = ("full_name", "email", "phone")
    readonly_fields = ("created_at", "updated_at")
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_deleted=False)

    actions = ["soft_delete"]

    @admin.action(description="Удалить (мягко)")
    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)
        self.message_user(request, "Выбранные заказы помечены как удалённые.")
