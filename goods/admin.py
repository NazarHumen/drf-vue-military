# from django.contrib import admin
#
# # Register your models here.
# from goods.models import Categories, Products, ProductAttribute
#
#
# # admin.site.register(Products)
#
#
# @admin.register(Categories)
# class CategoriesAdmin(admin.ModelAdmin):
#     prepopulated_fields = {"slug": ("name",)}
#
#
# @admin.register(Products)
# class ProductsAdmin(admin.ModelAdmin):
#     prepopulated_fields = {"slug": ("name",)}
#
# class ProductAttributeInline(admin.TabularInline):
#     model = ProductAttribute  # Додаємо модель характеристик у вигляді інлайн-форми
#     extra = 1  # Кількість порожніх рядків для додавання
#     verbose_name = "Характеристика"
#     verbose_name_plural = "Характеристики"
#
# @admin.register(Products)
# class ProductsAdmin(admin.ModelAdmin):
#     prepopulated_fields = {"slug": ("name",)}
#     inlines = [ProductAttributeInline]
from modeltranslation.admin import TranslationAdmin
from django.contrib import admin

from goods.models import (
    Categories,
    Products,
    ProductAttribute,
    ExchangeRate,
)  # Додано ProductAttribute


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute  # Підключаємо модель характеристик
    extra = 1  # Скільки порожніх рядків буде додано для заповнення
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
    prepopulated_fields = {
        "slug": ("name",)
    }  # Автоматичне заповнення поля `slug`
    inlines = [
        ProductAttributeInline
    ]  # Додаємо характеристики як інлайн-редактор

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


# class ExchangeRateAdmin(admin.ModelAdmin):
#     list_display = ('base_currency', 'target_currency', 'rate', 'updated_at')  # Показуємо ці поля в списку
#     list_filter = ('base_currency', 'target_currency')  # Додаємо фільтри по валютам
#     search_fields = ('base_currency', 'target_currency')  # Додаємо пошук по валютам
#
# admin.site.register(ExchangeRate, ExchangeRateAdmin)


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ("base_currency", "target_currency", "rate", "updated_at")
    search_fields = ("base_currency", "target_currency")
    list_filter = ("base_currency", "target_currency")
