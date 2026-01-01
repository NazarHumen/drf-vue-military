from django.urls import path
from django.urls import include

urlpatterns = [
    path("catalog/", include("apps.goods.urls", namespace="catalog")),
]
