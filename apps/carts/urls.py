from django.urls import path

from apps.carts import views

app_name = "carts"

urlpatterns = [
path("cart_list/", views.CartListAPIView.as_view(), name="cart_list"),
    path("cart_add/", views.CartAddAPIView.as_view(), name="cart_add"),
    path(
        "cart_change/",
        views.CartChangeAPIView.as_view(),
        name="cart_change",
    ),
    path(
        "cart_remove/",
        views.CartRemoveAPIView.as_view(),
        name="cart_remove",
    ),
]
