from django.contrib import admin

from .models import Order, OrderItem, ShopSettings


@admin.register(ShopSettings)
class ShopSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "delivery_free_from",
        "delivery_price",
        "express_delivery_extra",
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = (
        "product_name",
        "price",
        "quantity",
        "total_value",
    )

    fields = (
        "product",
        "product_name",
        "price",
        "quantity",
        "total_value",
    )

    def total_value(self, obj):
        return obj.total

    total_value.short_description = "Сумма"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "phone",
        "total",
        "delivery_type",
        "payment_type",
        "payment_status",
        "created_at",
        "is_deleted",
    )

    list_filter = (
        "delivery_type",
        "payment_type",
        "payment_status",
        "is_deleted",
        "created_at",
    )

    search_fields = (
        "full_name",
        "email",
        "phone",
    )

    readonly_fields = (
        "products_total",
        "delivery_total",
        "total",
        "created_at",
        "updated_at",
    )

    inlines = [
        OrderItemInline,
    ]

    actions = [
        "soft_delete_orders",
    ]

    @admin.action(
        description="Мягко удалить выбранные заказы",
    )
    def soft_delete_orders(self, request, queryset):
        queryset.update(
            is_deleted=True,
        )