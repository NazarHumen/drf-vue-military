from django.urls import path

from apps.goods import views

app_name = "goods"
urlpatterns = [
    path("search/", views.CatalogAPIView.as_view(), name="search"),
    path(
        "<slug:category_slug>/", views.CatalogAPIView.as_view(), name="index"
    ),
    path(
        "product/<slug:product_slug>/",
        views.ProductAPIView.as_view(),
        name="product",
    ),
]
