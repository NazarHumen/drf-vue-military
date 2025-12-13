from django.contrib import admin

from carts.admin import CartTabAdmin
from goods.models import Categories
from orders.admin import OrderTabulareAdmin
from users.models import User


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
