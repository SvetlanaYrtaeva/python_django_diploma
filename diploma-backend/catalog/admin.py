from django.contrib import admin

from .models import Category, Product, Seller, Tag


class SoftDeleteAdminMixin:

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_deleted=False)

    def delete_queryset(self, request, queryset):
        queryset.update(is_deleted=True)


@admin.register(Category)
class CategoryAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("name", "parent", "is_featured", "is_active")
    list_filter = ("is_active", "is_featured", "parent")
    search_fields = ("name",)
    list_editable = ("is_featured", "is_active")

    actions = ["soft_delete"]

    @admin.action(description="Удалить (мягко)")
    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)
        self.message_user(request, "Выбранные категории помечены как удалённые.")


@admin.register(Seller)
class SellerAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    actions = ["soft_delete"]

    @admin.action(description="Удалить (мягко)")
    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)
        self.message_user(request, "Выбранные производители помечены как удалённые.")


@admin.register(Tag)
class TagAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    actions = ["soft_delete"]

    @admin.action(description="Удалить (мягко)")
    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)
        self.message_user(request, "Выбранные теги помечены как удалённые.")


@admin.register(Product)
class ProductAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "old_price",
        "category",
        "seller",
        "sorting_index",
        "purchases_count",
        "limited_edition",
        "is_active",
    )
    list_filter = (
        "is_active",
        "limited_edition",
        "category",
        "seller",
    )
    search_fields = ("name", "description")
    list_editable = ("price", "sorting_index", "is_active")
    readonly_fields = ("slug",)

    actions = ["soft_delete"]

    @admin.action(description="Удалить (мягко)")
    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)
        self.message_user(request, "Выбранные товары помечены как удалённые.")
