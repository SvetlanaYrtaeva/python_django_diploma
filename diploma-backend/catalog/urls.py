from django.urls import path

from catalog import views

app_name = "catalog"

urlpatterns = [
    path("", views.catalog_view, name="index"),
    path("<int:category_id>/", views.catalog_view, name="category"),
    path("<slug:slug>/", views.product_detail_view, name="product"),
]
