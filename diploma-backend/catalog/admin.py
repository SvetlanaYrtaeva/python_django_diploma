from django.contrib import admin

from .models import Category, Product, Seller


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "parent",
        "is_featured",
        "is_active",
        "is_deleted",
    )

    list_filter = (
        "is_featured",
        "is_active",
        "is_deleted",
    )

    search_fields = (
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    actions = [
        "soft_delete_categories",
    ]

    @admin.action(
        description="Мягко удалить категории",
    )
    def soft_delete_categories(self, request, queryset):
        queryset.update(
            is_deleted=True,
            is_active=False,
        )


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_deleted",
    )

    search_fields = (
        "name",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "seller",
        "price",
        "sorting_index",
        "purchases_count",
        "limited_edition",
        "is_active",
        "is_deleted",
    )

    list_filter = (
        "category",
        "seller",
        "limited_edition",
        "is_active",
        "is_deleted",
    )

    search_fields = (
        "name",
        "short_description",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    list_editable = (
        "price",
        "sorting_index",
        "is_active",
    )

    actions = [
        "soft_delete_products",
    ]

    @admin.action(
        description="Мягко удалить товары",
    )
    def soft_delete_products(self, request, queryset):
        queryset.update(
            is_deleted=True,
            is_active=False,
        )