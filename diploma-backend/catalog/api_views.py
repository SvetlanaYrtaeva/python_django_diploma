from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Category, Product


def json_response(
    data,
    status=200,
):
    return JsonResponse(
        data,
        safe=False,
        status=status,
        json_dumps_params={
            "ensure_ascii": False,
        },
    )


def image_data(
    image_field,
    alt,
):
    if image_field:
        return {
            "src": image_field.url,
            "alt": alt,
        }

    return {
        "src": "",
        "alt": alt,
    }


def serialize_category(category):
    children = [
        child
        for child in category.children.all()
        if child.is_active
        and not child.is_deleted
    ]

    return {
        "id": category.id,
        "title": category.name,
        "name": category.name,
        "slug": category.slug,
        "url": f"/catalog/{category.id}/",
        "image": image_data(
            category.icon,
            category.name,
        ),
        "subcategories": [
            {
                "id": child.id,
                "title": child.name,
                "name": child.name,
                "slug": child.slug,
                "url": f"/catalog/{child.id}/",
                "image": image_data(
                    child.icon,
                    child.name,
                ),
                "subcategories": [],
            }
            for child in children
        ],
    }


def serialize_product(product):
    image = image_data(
        product.image,
        product.name,
    )

    return {
        "id": product.id,
        "title": product.name,
        "name": product.name,
        "slug": product.slug,
        "description": product.description,
        "short_description": product.short_description,
        "price": float(product.price),
        "old_price": (
            float(product.old_price)
            if product.old_price is not None
            else None
        ),
        "images": [image],
        "image": image,
        "category": {
            "id": product.category.id,
            "title": product.category.name,
            "name": product.category.name,
            "slug": product.category.slug,
        },
        "seller": {
            "id": product.seller.id,
            "title": product.seller.name,
            "name": product.seller.name,
        },
        "characteristics": product.characteristics,
        "purchases_count": product.purchases_count,
        "sorting_index": product.sorting_index,
        "limited_edition": product.limited_edition,
        "reviews_count": product.reviews_count,
    }


def categories_api_view(request):
    if request.method != "GET":
        return json_response(
            {
                "detail": "Метод не поддерживается.",
            },
            status=405,
        )

    categories = (
        Category.objects
        .filter(
            is_active=True,
            is_deleted=False,
            parent__isnull=True,
        )
        .prefetch_related("children")
    )

    data = [
        serialize_category(category)
        for category in categories
    ]

    return json_response(data)


def popular_products_api_view(request):
    if request.method != "GET":
        return json_response(
            {
                "detail": "Метод не поддерживается.",
            },
            status=405,
        )

    products = (
        Product.objects
        .filter(
            is_active=True,
            is_deleted=False,
        )
        .select_related(
            "category",
            "seller",
        )
        .order_by(
            "sorting_index",
            "-purchases_count",
        )[:8]
    )

    data = [
        serialize_product(product)
        for product in products
    ]

    return json_response(data)


def limited_products_api_view(request):
    if request.method != "GET":
        return json_response(
            {
                "detail": "Метод не поддерживается.",
            },
            status=405,
        )

    products = (
        Product.objects
        .filter(
            is_active=True,
            is_deleted=False,
            limited_edition=True,
        )
        .select_related(
            "category",
            "seller",
        )
        .order_by("-created_at")[:16]
    )

    data = [
        serialize_product(product)
        for product in products
    ]

    return json_response(data)


def banners_api_view(request):
    if request.method != "GET":
        return json_response(
            {
                "detail": "Метод не поддерживается.",
            },
            status=405,
        )

    return json_response([])


def product_detail_api_view(
    request,
    product_id,
):
    if request.method != "GET":
        return json_response(
            {
                "detail": "Метод не поддерживается.",
            },
            status=405,
        )

    product = get_object_or_404(
        Product.objects
        .filter(
            is_active=True,
            is_deleted=False,
        )
        .select_related(
            "category",
            "seller",
        ),
        pk=product_id,
    )

    return JsonResponse(
        serialize_product(product),
        json_dumps_params={
            "ensure_ascii": False,
        },
    )


def get_filter_value(
    request,
    name,
    default="",
):
    direct_value = request.GET.get(name)

    if direct_value is not None:
        return direct_value

    prefix = f"filter[{name}]"

    return request.GET.get(
        prefix,
        default,
    )


def catalog_api_view(request):
    if request.method != "GET":
        return json_response(
            {
                "detail": "Метод не поддерживается.",
            },
            status=405,
        )

    products = (
        Product.objects
        .filter(
            is_active=True,
            is_deleted=False,
        )
        .select_related(
            "category",
            "seller",
        )
    )

    name = get_filter_value(
        request,
        "name",
        "",
    ).strip()

    min_price = get_filter_value(
        request,
        "minPrice",
        "",
    ).strip()

    max_price = get_filter_value(
        request,
        "maxPrice",
        "",
    ).strip()

    seller = get_filter_value(
        request,
        "seller",
        "",
    ).strip()

    category_id = get_filter_value(
        request,
        "category",
        "",
    ).strip()

    if name:
        products = products.filter(
            name__icontains=name,
        )

    if seller:
        products = products.filter(
            seller__name__icontains=seller,
        )

    if category_id:
        try:
            products = products.filter(
                category_id=int(category_id),
            )
        except ValueError:
            pass

    if min_price:
        try:
            products = products.filter(
                price__gte=float(min_price),
            )
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(
                price__lte=float(max_price),
            )
        except ValueError:
            pass

    sort = request.GET.get(
        "sort",
        "price",
    )

    sort_type = request.GET.get(
        "sortType",
        "inc",
    )

    sort_fields = {
        "price": "price",
        "rating": "purchases_count",
        "popular": "purchases_count",
        "reviews": "review_total",
        "date": "created_at",
        "new": "created_at",
    }

    sort_field = sort_fields.get(
        sort,
        "price",
    )

    if sort == "reviews":
        from django.db.models import Count, Q

        products = products.annotate(
            review_total=Count(
                "reviews",
                filter=Q(
                    reviews__is_deleted=False,
                ),
            ),
        )

    if sort_type in (
        "desc",
        "decrease",
        "decreasing",
    ):
        sort_field = f"-{sort_field}"

    products = products.order_by(
        sort_field,
        "name",
    )

    try:
        current_page = int(
            request.GET.get(
                "currentPage",
                1,
            ),
        )
    except ValueError:
        current_page = 1

    try:
        limit = int(
            request.GET.get(
                "limit",
                20,
            ),
        )
    except ValueError:
        limit = 20

    limit = min(
        max(limit, 1),
        100,
    )

    start = (current_page - 1) * limit
    end = start + limit

    total = products.count()
    page_products = products[start:end]

    data = [
        serialize_product(product)
        for product in page_products
    ]

    last_page = (total + limit - 1) // limit if limit > 0 else 1

    return json_response(
        {
            "items": data,
            "results": data,
            "products": data,
            "count": total,
            "total": total,
            "currentPage": current_page,
            "lastPage": last_page,
            "limit": limit,
        },
    )


def tags_api_view(request):
    if request.method != "GET":
        return json_response(
            {
                "detail": "Метод не поддерживается.",
            },
            status=405,
        )

    sellers = (
        Product.objects
        .filter(
            is_active=True,
            is_deleted=False,
        )
        .values_list(
            "seller__name",
            flat=True,
        )
        .distinct()
        .order_by("seller__name")
    )

    data = [
        {
            "id": index,
            "title": seller,
            "name": seller,
        }
        for index, seller in enumerate(
            sellers,
            start=1,
        )
    ]

    return json_response(data)