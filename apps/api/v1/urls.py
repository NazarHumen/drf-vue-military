from django.urls import include, path

urlpatterns = [
    path("catalog/", include("apps.goods.urls", namespace="catalog")),
    path("cart/", include("apps.carts.urls", namespace="cart")),
    path("orders/", include("apps.orders.urls", namespace="orders")),
    path("users/", include("apps.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
]
