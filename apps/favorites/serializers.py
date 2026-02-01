from rest_framework import serializers

from apps.favorites.models import Favorite
from apps.goods.models import Products


class ProductMinimalSerializer(serializers.ModelSerializer):
    sell_price = serializers.SerializerMethodField()
    price_usd = serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = [
            "id",
            "name",
            "slug",
            "image",
            "sell_price",
            "price_usd",
            "availability_status",
        ]

    def get_sell_price(self, obj):
        return round(obj.sell_price(), 2)

    def get_price_usd(self, obj):
        return round(obj.price_in_usd, 2)


class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductMinimalSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "product", "created_at"]


class FavoriteCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Products.objects.filter(id=value).exists():
            raise serializers.ValidationError("Товар не знайдено")
        return value
