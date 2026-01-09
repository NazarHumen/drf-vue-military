from django.db import models

from apps.goods.models import Products
from apps.users.models import User


# Create your models here.
class CartQueryset(models.QuerySet):
    def total_price(self):
        return sum(cart.products_price() for cart in self)

    def total_quantity(self):
        if self:
            return sum(cart.quantity for cart in self)
        return 0

    # def total_price_usd(self):
    #     return sum(
    #         cart.product.convert_currency("USD") *
    #         cart.quantity for cart in self)

    def total_price_usd(self):
        return sum(cart.products_price_usd() for cart in self)


class Cart(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Користувач",
    )
    product = models.ForeignKey(
        to=Products, on_delete=models.CASCADE, verbose_name="Товар"
    )
    quantity = models.PositiveSmallIntegerField(
        default=0, verbose_name="Кількість"
    )
    session_key = models.CharField(max_length=32, null=True, blank=True)
    created_timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата додавання"
    )

    class Meta:
        db_table = "cart"
        verbose_name = "Кошик"
        verbose_name_plural = "Кошик"
        ordering = ("id",)

    objects = CartQueryset().as_manager()

    def products_price(self):
        return round(self.product.sell_price() * self.quantity, 2)

    # def products_price_usd(self):
    #     return round(self.product.convert_currency("USD") * self.quantity, 2)
    def products_price_usd(self):
        return round(self.product.price_in_usd * self.quantity, 2)

    def __str__(self):
        user_info = self.user.username if self.user else "Anonymous user"
        product_info = self.product.name if self.product else "Unknown product"
        # if self.user:
        #     return f"Кошик {self.user.username}
        #     | Товар {self.product.name}
        #     | Кількість {self.quantity}"
        # return f"Кошик {self.user.username}
        # | Товар {self.product.name}
        # | Кількість {self.quantity}"
        return (
            f"Кошик {user_info} "
            f"| Товар {product_info} "
            f"| Кількість {self.quantity}"
        )
