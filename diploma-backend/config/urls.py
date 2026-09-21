from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from reviews.views import review_api_view

from cart.views import basket_api_view
from catalog.api_views import (
    banners_api_view,
    catalog_api_view,
    categories_api_view,
    limited_products_api_view,
    popular_products_api_view,
    product_detail_api_view,
    sales_api_view,
    tags_api_view,
)
from catalog import views as catalog_views
from orders.api_views import (
    create_order_api_view,
    order_detail_api_view,
    payment_api_view,
)
from orders.views import (
    generate_account_api_view,
    order_history_view,
    payment_view,
)
from users import views as user_views
from users.api_views import (
    avatar_api_view,
    profile_api_view,
    sign_in_api_view,
    sign_out_api_view,
    sign_up_api_view,
)

api_urls = [
    ("api/basket", basket_api_view),
    ("api/sign-in", sign_in_api_view),
    ("api/sign-out", sign_out_api_view),
    ("api/sign-up", sign_up_api_view),
    ("api/profile", profile_api_view),
    ("api/avatar", avatar_api_view),
    ("api/profile/avatar", avatar_api_view),
    ("api/profile/avatar/", avatar_api_view),

    ("api/catalog", catalog_api_view),
    ("api/categories", categories_api_view),
    ("api/tags", tags_api_view),
    ("api/products/popular", popular_products_api_view),
    ("api/products/limited", limited_products_api_view),
    ("api/banners", banners_api_view),
    ("api/sales", sales_api_view),

    ("api/generate-account", generate_account_api_view),
    ("api/orders", create_order_api_view),
]

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", catalog_views.index_view, name="index"),

    path("catalog/", include("catalog.urls")),
    path("product/<int:pk>/", catalog_views.product_by_id_view, name="product_by_id"),

    path("users/", include("users.urls")),
    path("profile/", user_views.profile_view, name="profile_page"),

    path("signIn/", TemplateView.as_view(template_name="frontend/signIn.html"), name="sign_in_page"),
    path("signUp/", TemplateView.as_view(template_name="frontend/signUp.html"), name="sign_up_page"),
    path("sign-in/", TemplateView.as_view(template_name="frontend/signIn.html"), name="sign_in_alt"),
    path("sign-up/", TemplateView.as_view(template_name="frontend/signUp.html"), name="sign_up_alt"),

    path("cart/", TemplateView.as_view(template_name="frontend/cart.html"), name="cart_page"),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),

    path("reviews/", include("reviews.urls")),

    path("sale/", TemplateView.as_view(template_name="frontend/sale.html"), name="sale"),

    path("history-order/", order_history_view, name="history_order_alt"),
    path("payment/<int:order_id>/", payment_view, name="payment_alt"),
]

for prefix, view in api_urls:
    urlpatterns.append(path(f"{prefix}", view))
    urlpatterns.append(path(f"{prefix}/", view))

urlpatterns.append(path("api/product/<int:product_id>", product_detail_api_view))
urlpatterns.append(path("api/product/<int:product_id>/", product_detail_api_view))

urlpatterns.append(path("api/product/<int:product_id>/reviews", review_api_view, name="api_product_reviews_alt"))
urlpatterns.append(path("api/product/<int:product_id>/reviews/", review_api_view))

urlpatterns.append(path("api/payment/<int:order_id>", payment_api_view))
urlpatterns.append(path("api/payment/<int:order_id>/", payment_api_view))

urlpatterns.append(path("api/order/<int:order_id>", order_detail_api_view))
urlpatterns.append(path("api/order/<int:order_id>/", order_detail_api_view))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
