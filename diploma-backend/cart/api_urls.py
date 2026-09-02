from django.urls import path
from .views import (
    basket_api_view,
    basket_api_add_view,
    basket_api_update_view,
    basket_api_remove_view,
)

app_name = 'cart_api'

urlpatterns = [
    path('', basket_api_view, name='basket_api'),
    path('add/<int:product_id>', basket_api_add_view, name='add'),
    path('update/<int:item_id>', basket_api_update_view, name='update'),
    path('remove/<int:item_id>', basket_api_remove_view, name='remove'),
]