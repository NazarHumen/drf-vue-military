from django.contrib import admin

from apps.favorites.models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "session_key", "created_at")
    search_fields = ("user__username", "product__name", "session_key")
    list_filter = ("created_at",)
    raw_id_fields = ("user", "product")
