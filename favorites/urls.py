from django.urls import path
from .views import ToggleFavoriteView, FavoritesListView, RemoveFavoriteView

app_name = "favorites"
urlpatterns = [
    path(
        "toggle_favorite/",
        ToggleFavoriteView.as_view(),
        name="toggle_favorite",
    ),
    path("list/", FavoritesListView.as_view(), name="list"),
    path(
        "remove_favorite/",
        RemoveFavoriteView.as_view(),
        name="remove_favorite",
    ),
]
