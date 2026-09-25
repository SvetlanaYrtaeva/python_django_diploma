from django.shortcuts import get_object_or_404, render
from .models import Category, Product

from catalog.api_views import (
    banners_api_view,
    popular_products_api_view,
    limited_products_api_view,
)


def catalog_view(request, category_id=None):
    products = Product.objects.active().select_related("category", "seller")

    if category_id:
        category = get_object_or_404(
            Category, pk=category_id, is_active=True
        )
        products = products.filter(category=category)
    else:
        category = None

    categories = Category.objects.active().filter(is_active=True)

    return render(
        request,
        "frontend/catalog.html",
        {
            "products": products,
            "current_category": category,
            "categories": categories,
        },
    )


def product_detail_view(request, slug):
    product = get_object_or_404(
        Product.objects.active().select_related("category", "seller"),
        slug=slug,
    )
    reviews = product.reviews.filter(is_deleted=False).select_related("user")
    return render(
        request,
        "frontend/product.html",
        {"product": product, "reviews": reviews},
    )


def product_by_id_view(request, pk):
    product = get_object_or_404(
        Product.objects.active().select_related("category", "seller"),
        pk=pk,
    )
    reviews = product.reviews.filter(is_deleted=False).select_related("user")
    return render(
        request,
        "frontend/product.html",
        {"product": product, "reviews": reviews},
    )


def index_view(request):
    """
    Главная страница.
    Получает данные из API-функций и передаёт в шаблон.
    Фронтенд (Vue) также может запрашивать данные через AJAX-эндпоинты.
    """
    banners_response = banners_api_view(request)
    banners_data = banners_response.data if hasattr(banners_response, "data") else []
    if not isinstance(banners_data, list):
        banners_data = []

    popular_response = popular_products_api_view(request)
    popular_data = popular_response.data if hasattr(popular_response, "data") else []
    if not isinstance(popular_data, list):
        popular_data = []

    limited_response = limited_products_api_view(request)
    limited_data = limited_response.data if hasattr(limited_response, "data") else []
    if not isinstance(limited_data, list):
        limited_data = []

    return render(
        request,
        "frontend/index.html",
        {
            "banners": banners_data,
            "popularCards": popular_data,
            "limitedCards": limited_data,
        },
    )
