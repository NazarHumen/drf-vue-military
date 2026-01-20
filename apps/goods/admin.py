from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from modeltranslation.admin import TranslationAdmin

from apps.goods.models import (
    Categories,
    ExchangeRate,
    ProductAttribute,
    ProductImage,
    Products,
)


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get("quantity")
        availability_status = cleaned_data.get("availability_status")

        if quantity is not None and availability_status:
            if quantity <= 5 and availability_status == "ready_to_ship":
                raise ValidationError(
                    "Не можна встановити 'Готовий до відправлення' "
                    "коли кількість товару 5 або менше."
                )
            if quantity == 0 and availability_status != "out_of_stock":
                raise ValidationError(
                    "Коли кількість товару 0, статус має бути "
                    "'Немає в наявності'."
                )

        return cleaned_data


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
    form = ProductAdminForm
    prepopulated_fields = {"slug": ("name",)}
    inlines = [
        ProductImageInline,
        ProductAttributeInline,
    ]

    list_display = [
        "name",
        "quantity",
        "availability_status",
        "price",
        "discount",
        "discounted_price",
        "currency",
        "price_in_usd",
        "price_in_uah",
        "exchange_rate",
    ]
    list_editable = ["discount", "exchange_rate", "availability_status"]
    search_fields = ["name", "description"]
    list_filter = [
        "discount",
        "quantity",
        "category",
        "currency",
        "availability_status",
    ]
    fields = [
        "name",
        "category",
        "slug",
        "description",
        "image",
        ("price", "discount", "discounted_price"),
        "currency",
        "price_in_usd",
        "price_in_uah",
        ("quantity", "availability_status"),
        "exchange_rate",
    ]
    readonly_fields = ["price_in_usd", "price_in_uah"]


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ("base_currency", "target_currency", "rate", "updated_at")
    search_fields = ("base_currency", "target_currency")
    list_filter = ("base_currency", "target_currency")
