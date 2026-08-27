from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Category, Product


def active_products_queryset():
    return (
        Product.objects
        .filter(
            is_active=True,
            is_deleted=False,
        )
        .select_related(
            "category",
            "seller",
        )
        .annotate(
            review_total=Count(
                "reviews",
                filter=Q(
                    reviews__is_deleted=False,
                ),
            ),
        )
    )


@ensure_csrf_cookie
def index_view(request):
    return render(
        request,
        "frontend/index.html",
    )


def catalog_view(
    request,
    category_id=None,
):
    products = active_products_queryset()

    if category_id is not None:
        products = products.filter(
            category_id=category_id,
        )

    search_value = request.GET.get(
        "filter",
        "",
    ).strip()

    if not search_value:
        search_value = request.GET.get(
            "name",
            "",
        ).strip()

    if search_value:
        products = products.filter(
            name__icontains=search_value,
        )

    min_price = request.GET.get(
        "min_price",
        "",
    ).strip()

    max_price = request.GET.get(
        "max_price",
        "",
    ).strip()

    if min_price:
        products = products.filter(
            price__gte=min_price,
        )

    if max_price:
        products = products.filter(
            price__lte=max_price,
        )

    seller = request.GET.get(
        "seller",
        "",
    ).strip()

    if seller:
        products = products.filter(
            seller__name__icontains=seller,
        )

    sort = request.GET.get(
        "sort",
        "popular",
    )

    direction = request.GET.get(
        "direction",
        "desc",
    )

    sort_fields = {
        "popular": "purchases_count",
        "rating": "purchases_count",
        "price": "price",
        "reviews": "review_total",
        "date": "created_at",
        "new": "created_at",
    }

    sort_field = sort_fields.get(
        sort,
        "purchases_count",
    )

    if direction == "asc":
        order_field = sort_field
    else:
        order_field = f"-{sort_field}"

    products = products.order_by(
        order_field,
        "name",
    )

    paginator = Paginator(
        products,
        12,
    )

    page_obj = paginator.get_page(
        request.GET.get("page"),
    )

    return render(
        request,
        "frontend/catalog.html",
        {
            "products": page_obj,
            "page_obj": page_obj,
            "current_sort": sort,
            "current_direction": direction,
            "search_value": search_value,
            "category_id": category_id,
            "min_price": min_price,
            "max_price": max_price,
            "seller": seller,
        },
    )


def category_view(
    request,
    slug,
):
    category = get_object_or_404(
        Category.objects.filter(
            is_active=True,
            is_deleted=False,
        ),
        slug=slug,
    )

    return catalog_view(
        request,
        category_id=category.id,
    )


def product_detail_view(
    request,
    slug,
):
    product = get_object_or_404(
        active_products_queryset(),
        slug=slug,
    )

    reviews = (
        product.reviews
        .filter(
            is_deleted=False,
        )
        .select_related(
            "user",
        )
    )

    return render(
        request,
        "frontend/product.html",
        {
            "product": product,
            "reviews": reviews,
        },
    )