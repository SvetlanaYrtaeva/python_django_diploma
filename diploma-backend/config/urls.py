from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from cart.views import basket_api_view
from users.api_views import (
    sign_in_api_view,
    sign_out_api_view,
    sign_up_api_view,
)
from users.views import (
    UserLoginView,
    profile_view,
    register_view,
)


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "",
        include("catalog.urls"),
    ),

    path(
        "users/",
        include("users.urls"),
    ),

    path(
        "profile",
        profile_view,
        name="profile_page",
    ),

    path(
        "sign-in",
        UserLoginView.as_view(),
        name="sign_in_page",
    ),

    path(
        "sign-up",
        register_view,
        name="sign_up_page",
    ),

    path(
        "cart/",
        include("cart.urls"),
    ),

    path(
        "orders/",
        include("orders.urls"),
    ),

    path(
        "reviews/",
        include("reviews.urls"),
    ),

    path(
        "api/basket",
        basket_api_view,
        name="api_basket",
    ),

    path(
        "api/sign-in",
        sign_in_api_view,
        name="api_sign_in",
    ),

    path(
        "api/sign-out",
        sign_out_api_view,
        name="api_sign_out",
    ),

    path(
        "api/sign-up",
        sign_up_api_view,
        name="api_sign_up",
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )