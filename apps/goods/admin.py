from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from apps.goods.models import (
    Categories,
    ExchangeRate,
    ProductAttribute,
    ProductImage,
    Products,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 4
    max_num = 4
    verbose_name = "Додаткове зображення"
    verbose_name_plural = "Додаткові зображення"


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1
    verbose_name = "Характеристика"
    verbose_name_plural = "Характеристики"


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug": ("name",)
    }  # Автоматичне заповнення поля `slug`
    list_display = ["name"]


@admin.register(Products)
class ProductsAdmin(TranslationAdmin):
    prepopulated_fields = {"slug": ("name",)}
    inlines = [
        ProductImageInline,
        ProductAttributeInline,
    ]

    list_display = [
        "name",
        "quantity",
        "price",
        "discount",
        "discounted_price",
        "currency",
        "price_in_usd",
        "price_in_uah",
        "exchange_rate",
    ]
    list_editable = ["discount", "exchange_rate"]
    search_fields = ["name", "description"]
    list_filter = ["discount", "quantity", "category", "currency"]
    fields = [
        "name",
        "category",
        "slug",
        "description",
        "image",
        ("price", "discount", "discounted_price"),
        "currency",  # Додаємо поле валюту
        "price_in_usd",  # Додаємо поле ціни в доларах
        "price_in_uah",  # Додаємо поле ціни в гривнях
        "quantity",
        "exchange_rate",
    ]
    readonly_fields = ["price_in_usd", "price_in_uah"]


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ("base_currency", "target_currency", "rate", "updated_at")
    search_fields = ("base_currency", "target_currency")
    list_filter = ("base_currency", "target_currency")
