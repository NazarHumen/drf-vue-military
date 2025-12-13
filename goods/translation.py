from modeltranslation.translator import register, TranslationOptions
from .models import Categories, Products, ProductAttribute


@register(Categories)
class CategoriesTranslationOptions(TranslationOptions):
    fields = ("name",)  # Вказуємо, які поля перекладати


@register(Products)
class ProductsTranslationOptions(TranslationOptions):
    fields = (
        "name",
        "description",

    )


@register(ProductAttribute)
class ProductAttributeTranslationOptions(TranslationOptions):
    fields = ("key", "value")
