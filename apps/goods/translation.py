from modeltranslation.translator import TranslationOptions, register

from .models import Categories, ProductAttribute, Products


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
