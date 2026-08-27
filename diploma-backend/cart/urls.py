from django.urls import path

from .views import (
    basket_api_add_view,
    basket_api_remove_view,
    basket_api_update_view,
    basket_api_view,
    cart_detail_view,
)


app_name = "cart"


urlpatterns = [
    path(
        "",
        cart_detail_view,
        name="detail",
    ),

    path(
        "api/basket",
        basket_api_view,
        name="basket_api",
    ),

    path(
        "api/basket/add/<int:product_id>",
        basket_api_add_view,
        name="add",
    ),

    path(
        "api/basket/update/<int:item_id>",
        basket_api_update_view,
        name="update",
    ),

    path(
        "api/basket/remove/<int:item_id>",
        basket_api_remove_view,
        name="remove",
    ),
]