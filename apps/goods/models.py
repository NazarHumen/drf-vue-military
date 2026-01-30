from decimal import Decimal

import requests
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def product_image_path(instance, filename):
    """Генерує шлях: goods_images/product_<id>/<filename>"""
    # Для Products
    if hasattr(instance, 'category'):
        product_id = instance.pk or 'new'
    # Для ProductImage (галерея)
    else:
        product_id = instance.product_id or 'new'
    return f'goods_images/product_{product_id}/{filename}'


# Create your models here.


class Categories(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Назва")
    slug = models.SlugField(
        max_length=200, unique=True, blank=True, null=True, verbose_name="URL"
    )

    class Meta:
        db_table = "category"
        verbose_name = "Категорію"
        verbose_name_plural = "Категорії"
        ordering = ("id",)

    def __str__(self):
        return self.name


class ExchangeRate(models.Model):
    base_currency = models.CharField(
        max_length=3, verbose_name="Базова валюта"
    )
    target_currency = models.CharField(
        max_length=3, verbose_name="Цільова валюта"
    )
    rate = models.DecimalField(
        max_digits=10, decimal_places=4, verbose_name="Курс обміну"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    class Meta:
        unique_together = ("base_currency", "target_currency")
        verbose_name = "Курс валют"
        verbose_name_plural = "Курси валют"

    def __str__(self):
        return f"1 {self.base_currency} = {self.rate} {self.target_currency}"


class Products(models.Model):
    CURRENCY_CHOICES = (
        ("UAH", "Грн"),
        ("USD", "Долар"),
    )

    AVAILABILITY_CHOICES = (
        ("ready_to_ship", _("Готовий до відправлення")),
        ("last_item", _("Останній товар!")),
        ("out_of_stock", _("Немає в наявності")),
    )

    name = models.CharField(max_length=150, unique=True, verbose_name="Назва")
    slug = models.SlugField(
        max_length=200, unique=True, blank=True, null=True, verbose_name="URL"
    )

    description = models.TextField(blank=True, null=True, verbose_name="Опис")

    image = models.ImageField(
        upload_to=product_image_path,
        blank=True,
        null=True,
        verbose_name="Зображення",
    )

    price = models.DecimalField(
        default=0.00,
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Ціна",
    )

    # discount = models.DecimalField(
    #     default=0.00,
    #     max_digits=10,
    #     decimal_places=2,
    #     blank=True,
    #     null=True,
    #     verbose_name="Знижка в %",
    # )
    discount = models.PositiveSmallIntegerField(
        default=0,
        blank=True,
        null=True,
        verbose_name="Знижка в %",
    )

    quantity = models.PositiveSmallIntegerField(
        default=0, verbose_name="Кількість"
    )

    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default="ready_to_ship",
        verbose_name="Статус наявності",
    )

    category = models.ForeignKey(
        to=Categories, on_delete=models.CASCADE, verbose_name="Категорія"
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="UAH",
        verbose_name="Валюта",
    )

    # Зберігаємо доларову ціну
    price_in_usd = models.DecimalField(
        default=0.00,
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Ціна в доларах",
    )
    # price_in_uah = models.DecimalField(
    #     default=0.00,
    #     max_digits=10,
    #     decimal_places=2,
    #     blank=True,
    #     null=True,
    #     verbose_name="Ціна в гривнях"
    # )

    exchange_rate = models.DecimalField(
        default=1.0,
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name="Курс валют USD->UAH",
    )

    discounted_price = models.DecimalField(
        default=0.00,
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Ціна зі знижкою",
    )

    class Meta:
        db_table = "product"
        verbose_name = "Продукт"
        verbose_name_plural = "Продукти"
        ordering = ("id",)

    def __str__(self):
        return f"{self.name} Кількість - {self.quantity}"

    def get_absolute_url(self):
        return reverse("catalog:product", kwargs={"product_slug": self.slug})

    def display_id(self):
        return f"{self.id:05}"

    def sell_price(self):
        if self.discount:
            return round(self.price - self.price * self.discount / 100, 2)
        return round(self.price)

    # def get_exchange_rate(self, base_currency='USD', target_currency='UAH'):
    #     """Отримуємо курс валют або використовуємо вручну заданий курс."""
    #     if self.exchange_rate and self.currency ==
    #     base_currency and target_currency != base_currency:
    #         return self.exchange_rate
    #     return None  # Не викликаємо API

    def get_exchange_rate(self, base_currency="USD", target_currency="UAH"):
        """
        Отримуємо курс валют з БД або через API,
        якщо він не знайдений.
        """
        try:
            rate = ExchangeRate.objects.get(
                base_currency=base_currency, target_currency=target_currency
            ).rate
            return rate
        except ExchangeRate.DoesNotExist:
            return self.fetch_exchange_rate_from_api(
                base_currency, target_currency
            )

    def fetch_exchange_rate_from_api(self, base_currency, target_currency):
        """Отримує курс валют через API та зберігає його в БД."""
        API_URL = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        try:
            response = requests.get(API_URL)
            data = response.json()
            rate = data["rates"].get(target_currency)

            if rate:
                # Зберігаємо курс у БД, щоб використовувати його надалі
                ExchangeRate.objects.update_or_create(
                    base_currency=base_currency,
                    target_currency=target_currency,
                    defaults={"rate": Decimal(str(rate))},
                )
                return Decimal(str(rate))
        except Exception as e:
            print(f"Помилка отримання курсу валют: {e}")

        return None  # Якщо API не відповідає

    def convert_currency(self, target_currency="USD", price=None):
        """Конвертує задану ціну у вказану валюту."""
        if price is None:
            price = (
                self.sell_price()
            )  # Використовуємо ціну зі знижкою за замовчуванням

        if self.currency == target_currency:
            return price

        exchange_rate = self.get_exchange_rate(
            base_currency=self.currency, target_currency=target_currency
        )

        if exchange_rate:
            return round(Decimal(str(price)) * Decimal(str(exchange_rate)), 2)

        return price  # Якщо немає курсу, повертаємо вихідну ціну

    # @property
    # def price_in_usd(self):
    #     """Повертає ціну в доларах."""
    #     return self.convert_currency('USD')
    #
    @property
    def price_in_uah(self):
        """Повертає ціну в гривнях."""
        return self.convert_currency("UAH")

    # курс обміну
    def save(self, *args, **kwargs):
        # Отримуємо актуальний курс USD -> UAH
        self.exchange_rate = self.get_exchange_rate("USD", "UAH")

        # Розрахунок ціни зі знижкою
        self.discounted_price = self.sell_price()

        # Перерахунок ціни в USD з урахуванням знижки
        if self.currency == "UAH" and self.exchange_rate:
            # Якщо ціна в грн, ділимо на курс щоб отримати USD
            self.price_in_usd = round(
                self.discounted_price / self.exchange_rate, 2
            )
        elif self.currency == "USD":
            # Якщо ціна вже в USD
            self.price_in_usd = self.discounted_price

        super().save(*args, **kwargs)


class ProductImage(models.Model):
    ORDER_CHOICES = (
        (0, "1-е зображення"),
        (1, "2-е зображення"),
        (2, "3-є зображення"),
        (3, "4-е зображення"),
    )

    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Продукт",
    )
    image = models.ImageField(
        upload_to=product_image_path,
        verbose_name="Зображення",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Порядок",
        choices=ORDER_CHOICES,
    )

    class Meta:
        db_table = "product_image"
        verbose_name = "Зображення продукту"
        verbose_name_plural = "Зображення продукту"
        ordering = ("order",)

    def __str__(self):
        return f"Зображення {self.order} для {self.product.name}"


class ProductAttribute(models.Model):
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        related_name="attributes",
        verbose_name="Продукт",
    )
    key = models.CharField(max_length=100, verbose_name="Назва характеристики")
    value = models.CharField(max_length=255, verbose_name="Значення")

    class Meta:
        db_table = "product_attribute"
        verbose_name = "Характеристика продукту"
        verbose_name_plural = "Характеристики продукту"

    def __str__(self):
        return f"{self.key}: {self.value}"
