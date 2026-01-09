from django.urls import path
from django.urls import include

urlpatterns = [
    path("catalog/", include("apps.goods.urls", namespace="catalog")),
    path("cart/", include("apps.carts.urls", namespace="cart")),
    path("orders/", include("apps.orders.urls", namespace="orders")),
    path("users/", include("apps.users.urls")),
    path("accounts/", include("allauth.urls")),
]
