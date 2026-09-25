from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Category, Product, Seller


def _placeholder_url():
    return "/static/frontend/assets/img/logo.png"


def _category_icon_url(category):
    """
    Возвращает URL иконки категории.
    Если иконка не загружена — отдаёт запасную картинку,
    чтобы фронтенд всегда получал валидный src.
    """
    if category.icon:
        return category.icon.url
    return "/static/frontend/assets/img/icons/allDep.svg"


def serialize_product(product):
    image_url = product.image.url if product.image else _placeholder_url()
    return {
        "id": product.id,
        "title": product.name,
        "name": product.name,
        "slug": product.slug,
        "description": product.description,
        "short_description": product.short_description,
        "price": str(product.price) if product.price is not None else None,
        "old_price": (
            str(product.old_price)
            if product.old_price is not None
            else None
        ),
        "image": {"src": image_url, "alt": product.name},
        "images": [{"src": image_url, "alt": product.name}],
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
        "tags": [
            {"id": t.id, "name": t.name, "title": t.name}
            for t in product.tags.all()
        ],
        "characteristics": product.characteristics,
        "purchases_count": product.purchases_count,
        "sorting_index": product.sorting_index,
        "limited_edition": product.limited_edition,
        "reviews_count": product.reviews_count,
    }


def serialize_product_detail(product):
    data = serialize_product(product)
    reviews = (
        product.reviews
        .filter(is_deleted=False)
        .select_related("user")
    )
    data["reviews"] = [
        {
            "id": r.id,
            "author": r.user.get_full_name() or r.user.username,
            "email": r.user.email,
            "text": r.text,
            "rate": r.rating,
            "created_at": r.created_at.isoformat(),
        }
        for r in reviews
    ]
    return data


def serialize_category(cat):
    return {
        "id": cat.id,
        "title": cat.name,
        "name": cat.name,
        "slug": cat.slug,
        "url": f"/catalog/{cat.id}/",
        "image": {
            "src": _category_icon_url(cat),
            "alt": cat.name,
        },
        "subcategories": [
            serialize_category(child)
            for child in cat.children.filter(
                is_active=True, is_deleted=False
            )
        ],
    }


@api_view(["GET"])
def catalog_api_view(request: Request) -> Response:
    from django.db.models import Count, Avg, Q

    products = (
        Product.objects.active()
        .select_related("category", "seller")
        .prefetch_related("tags")
        .annotate(
            reviews_count_annotated=Count(
                "reviews",
                filter=Q(reviews__is_deleted=False),
            ),
            avg_rating_annotated=Avg(
                "reviews__rating",
                filter=Q(reviews__is_deleted=False),
            ),
        )
    )

    category_id = request.query_params.get("category")
    if category_id and category_id != "null":
        try:
            products = products.filter(category_id=int(category_id))
        except (TypeError, ValueError):
            pass

    name = request.query_params.get("filter[name]")
    if name:
        products = products.filter(name__icontains=name)

    min_price = request.query_params.get("filter[minPrice]")
    max_price = request.query_params.get("filter[maxPrice]")
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except (TypeError, ValueError):
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except (TypeError, ValueError):
            pass

    tags = request.query_params.getlist("tags")
    if tags:
        products = products.filter(seller_id__in=tags)

    free_delivery = request.query_params.get("filter[freeDelivery]")
    if free_delivery and free_delivery.lower() == "true":
        from orders.services import get_shop_settings
        settings_obj = get_shop_settings()
        products = products.filter(
            price__gte=settings_obj.delivery_free_from
        )

    for key in request.query_params:
        if key.startswith("filter[spec"):
            spec_name = key[12:-1]
            spec_value = request.query_params.get(key)
            if spec_value:
                products = products.filter(
                    **{
                        f"characteristics__{spec_name}__icontains": (
                            spec_value
                        )
                    }
                )

    sort = request.query_params.get("sort", "price")
    sort_type = request.query_params.get("sortType", "inc")
    prefix = "" if sort_type == "inc" else "-"

    sort_map = {
        "price": "price",
        "reviews": "reviews_count_annotated",
        "rating": "avg_rating_annotated",
        "popular": "purchases_count",
        "date": "created_at",
        "novelty": "created_at",
    }
    sort_field = sort_map.get(sort, "price")
    products = products.order_by(f"{prefix}{sort_field}")

    try:
        page = int(request.query_params.get("currentPage", 1))
    except (TypeError, ValueError):
        page = 1
    try:
        limit = int(request.query_params.get("limit", 20))
    except (TypeError, ValueError):
        limit = 20

    start = (page - 1) * limit
    end = start + limit

    total = products.count()
    last_page = (total + limit - 1) // limit if limit > 0 else 1

    items = [serialize_product(p) for p in products[start:end]]

    return Response({
        "items": items,
        "count": limit,
        "total": total,
        "currentPage": page,
        "lastPage": last_page,
    })


@api_view(["GET"])
def product_detail_api_view(request: Request, product_id: int) -> Response:
    from django.shortcuts import get_object_or_404
    product = get_object_or_404(
        Product.objects.active()
        .select_related("category", "seller")
        .prefetch_related("tags"),
        pk=product_id,
    )
    return Response(serialize_product_detail(product))


@api_view(["GET"])
def categories_api_view(request: Request) -> Response:
    categories = (
        Category.objects.active()
        .filter(is_active=True, parent__isnull=True)
        .prefetch_related("children")
    )
    return Response([serialize_category(cat) for cat in categories])


@api_view(["GET"])
def tags_api_view(request: Request) -> Response:
    sellers = Seller.objects.filter(is_deleted=False)
    return Response([
        {"id": s.id, "title": s.name, "name": s.name}
        for s in sellers
    ])


@api_view(["GET"])
def popular_products_api_view(request: Request) -> Response:
    products = (
        Product.objects.active()
        .select_related("category", "seller")
        .order_by("sorting_index", "-purchases_count")[:8]
    )
    return Response([serialize_product(p) for p in products])


@api_view(["GET"])
def limited_products_api_view(request: Request) -> Response:
    products = (
        Product.objects.active()
        .select_related("category", "seller")
        .filter(limited_edition=True)[:16]
    )
    return Response([serialize_product(p) for p in products])


@api_view(["GET"])
def banners_api_view(request: Request) -> Response:
    featured = (
        Category.objects.active()
        .filter(is_featured=True, is_active=True)[:3]
    )
    result = []
    for cat in featured:
        min_price_product = (
            Product.objects.active()
            .filter(category=cat)
            .order_by("price")
            .first()
        )
        price = str(min_price_product.price) if min_price_product else "0"

        images = [
            {
                "src": _category_icon_url(cat),
                "alt": cat.name,
            }
        ]

        result.append({
            "title": cat.name,
            "category": cat.id,
            "price": price,
            "images": images,
        })
    return Response(result)


@api_view(["GET"])
def sales_api_view(request: Request) -> Response:
    """
    Возвращает товары со скидкой (у которых задан old_price).
    Поддерживает пагинацию через currentPage и limit.
    """
    try:
        page = int(request.query_params.get("currentPage", 1))
    except (TypeError, ValueError):
        page = 1
    try:
        limit = int(request.query_params.get("limit", 20))
    except (TypeError, ValueError):
        limit = 20

    products = (
        Product.objects.active()
        .select_related("category", "seller")
        .filter(old_price__isnull=False)
        .order_by("-purchases_count")
    )

    total = products.count()
    last_page = (total + limit - 1) // limit if limit > 0 else 1

    start = (page - 1) * limit
    end = start + limit

    items = [serialize_product(p) for p in products[start:end]]

    return Response({
        "items": items,
        "count": limit,
        "total": total,
        "currentPage": page,
        "lastPage": last_page,
    })
