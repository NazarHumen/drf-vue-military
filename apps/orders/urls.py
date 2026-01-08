from django.urls import path

from apps.orders import views

app_name = "orders"

urlpatterns = [
    path(
        "create-order/",
        views.CreateOrderAPIView.as_view(),
        name="create_order",
    ),
]
