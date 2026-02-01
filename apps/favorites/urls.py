from django.urls import path

from apps.favorites import views

app_name = "favorites"

urlpatterns = [
    path("list/", views.FavoritesListAPIView.as_view(), name="favorites_list"),
    path("add/", views.FavoriteAddAPIView.as_view(), name="favorite_add"),
    path(
        "remove/",
        views.FavoriteRemoveAPIView.as_view(),
        name="favorite_remove",
    ),
    path(
        "toggle/",
        views.FavoriteToggleAPIView.as_view(),
        name="favorite_toggle",
    ),
    path(
        "check/", views.FavoriteCheckAPIView.as_view(), name="favorite_check"
    ),
]
