from rest_framework import serializers

from apps.goods.models import (
    Categories,
    ExchangeRate,
    ProductAttribute,
    Products,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = "__all__"


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ["id", "key", "value"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    attributes = ProductAttributeSerializer(many=True, read_only=True)

    sell_price = serializers.SerializerMethodField()
    price_in_usd = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    price_in_uah = serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "price",
            "currency",
            "discount",
            "discounted_price",
            "sell_price",
            "price_in_usd",
            "price_in_uah",
            "exchange_rate",
            "quantity",
            "category",
            "attributes",
        ]

    def get_sell_price(self, obj):
        return obj.sell_price()

    def get_price_in_uah(self, obj):
        return obj.price_in_uah


class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = [
            "id",
            "base_currency",
            "target_currency",
            "rate",
            "updated_at",
        ]
