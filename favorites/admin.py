from django.contrib import admin
from favorites.models import Favorite


# Register your models here.
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "created_at",
    )  # Поля, які будуть відображатися в списку
    search_fields = (
        "user__username",
        "product__name",
    )  # Додайте пошук за пов’язаними полями
    list_filter = ("created_at",)  # Фільтр за датою створення
