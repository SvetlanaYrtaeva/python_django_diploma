from django.urls import path

from .api_views import (
    banners_api_view,
    categories_api_view,
    catalog_api_view,
    limited_products_api_view,
    popular_products_api_view,
    product_detail_api_view,
    tags_api_view,
)
from .views import (
    category_view,
    catalog_view,
    index_view,
    product_detail_view,
)


app_name = "catalog"


urlpatterns = [
    path(
        "",
        index_view,
        name="index",
    ),

    path(
        "catalog/",
        catalog_view,
        name="catalog",
    ),

    path(
        "catalog/<int:category_id>/",
        catalog_view,
        name="catalog_by_id",
    ),

    path(
        "category/<slug:slug>/",
        category_view,
        name="category",
    ),

    path(
        "product/<slug:slug>/",
        product_detail_view,
        name="product",
    ),

    path(
        "api/catalog",
        catalog_api_view,
        name="api_catalog",
    ),

    path(
        "api/tags",
        tags_api_view,
        name="api_tags",
    ),

    path(
        "api/categories",
        categories_api_view,
        name="api_categories",
    ),

    path(
        "api/products/popular",
        popular_products_api_view,
        name="api_products_popular",
    ),

    path(
        "api/products/limited",
        limited_products_api_view,
        name="api_products_limited",
    ),

    path(
        "api/products/<int:product_id>",
        product_detail_api_view,
        name="api_product_detail",
    ),

    path(
        "api/banners",
        banners_api_view,
        name="api_banners",
    ),
]