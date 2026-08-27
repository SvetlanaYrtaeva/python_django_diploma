from django.urls import path

from .views import (
    product_reviews_api_view,
    review_create_view,
)


app_name = "reviews"


urlpatterns = [
    path(
        "product/<slug:slug>/create/",
        review_create_view,
        name="create",
    ),

    path(
        "api/product/<int:product_id>/reviews",
        product_reviews_api_view,
        name="api_product_reviews",
    ),
]