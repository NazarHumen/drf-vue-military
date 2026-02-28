from django.urls import path

from apps.orders import views

app_name = "orders"

urlpatterns = [
    path(
        "create-order/",
        views.CreateOrderAPIView.as_view(),
        name="create_order",
    ),
    path(
        "<int:order_id>/receipt/",
        views.OrderReceiptView.as_view(),
        name="receipt",
    ),
]
