from django.urls import include, path

from main.views import FeedbackCreateAPIView

urlpatterns = [
    path("catalog/", include("apps.goods.urls", namespace="catalog")),
    path("cart/", include("apps.carts.urls", namespace="cart")),
    path("orders/", include("apps.orders.urls", namespace="orders")),
    path("favorites/", include("apps.favorites.urls", namespace="favorites")),
    path("users/", include("apps.users.urls", namespace="users")),
    path("payments/", include("apps.payments.urls", namespace="payments")),
    path("accounts/", include("allauth.urls")),
    path(
        "main/feedback/",
        FeedbackCreateAPIView.as_view(),
        name="feedback_create",
    ),
]
