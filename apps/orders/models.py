from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.goods.models import Products
from apps.users.models import User


class OrderitemQueryset(models.QuerySet):

    def total_price(self):
        return sum(cart.products_price() for cart in self)

    def total_quantity(self):
        if self:
            return sum(cart.quantity for cart in self)
        return 0


class OrderStatus(models.TextChoices):
    PROCESSING = "processing", _("В обробці")
    SHIPPED = "shipped", _("Відправлено")
    DELIVERED = "delivered", _("Доставлено")


class Order(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT,
        verbose_name="Користувач",
    )
    created_timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата створення замовлення"
    )
    phone_number = models.CharField(
        max_length=20, verbose_name="Номер телефона"
    )
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    requires_delivery = models.BooleanField(
        default=False, verbose_name="Потрібна доставка"
    )
    delivery_address = models.TextField(
        null=True, blank=True, verbose_name="Адрес доставки"
    )
    payment_on_get = models.BooleanField(
        default=False, verbose_name="Оплата при отриманні"
    )
    is_paid = models.BooleanField(default=False, verbose_name="Сплачено")
    status = models.CharField(
        max_length=50,
        choices=OrderStatus.choices,
        default=OrderStatus.PROCESSING,
        verbose_name="Статус замовлення",
    )

    class Meta:
        db_table = "order"
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ("id",)

    def __str__(self):
        return (
            f"Замовлення № {self.pk} | "
            f"Покупець {self.user.first_name} "
            f"{self.user.last_name}"
        )


class OrderItem(models.Model):
    order = models.ForeignKey(
        to=Order, on_delete=models.CASCADE, verbose_name="Замовлення"
    )
    product = models.ForeignKey(
        to=Products,
        on_delete=models.SET_DEFAULT,
        null=True,
        verbose_name="Продукт",
        default=None,
    )
    name = models.CharField(max_length=150, verbose_name="Назва")
    price = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name="Ціна"
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name="Кількість")
    created_timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата продажу"
    )

    class Meta:
        db_table = "order_item"
        verbose_name = "Проданий товар"
        verbose_name_plural = "Проданні товари"
        ordering = ("id",)

    objects = OrderitemQueryset.as_manager()

    def products_price(self):
        return round(self.price * self.quantity, 2)

    def products_price_usd(self):
        """Конвертує загальну ціну товару у долари, враховуючи знижку."""
        if self.product:
            discounted_price = (
                self.product.sell_price()
            )  # Ціна з урахуванням знижки
            price_in_usd = self.product.convert_currency(
                "USD", discounted_price
            )
            return round(price_in_usd * self.quantity, 2)
        return None  # Якщо продукт видалений, повертаємо None

    def __str__(self):
        return f"Товар {self.name} | Замовлення № {self.order.pk}"
