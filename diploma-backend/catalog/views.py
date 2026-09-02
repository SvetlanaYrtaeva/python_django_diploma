from django.shortcuts import get_object_or_404, redirect, render

from .models import Category, Product


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
