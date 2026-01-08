from django.contrib import admin

from apps.carts.admin import CartTabAdmin
from apps.goods.models import Categories
from apps.orders.admin import OrderTabulareAdmin
from apps.users.models import User


# Register your models here.
# admin.site.register(User)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "first_name",
        "last_name",
        "email",
    ]
    search_fields = [
        "username",
        "first_name",
        "last_name",
        "email",
    ]

    inlines = [CartTabAdmin, OrderTabulareAdmin]
