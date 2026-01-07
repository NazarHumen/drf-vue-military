from rest_framework import serializers

from apps.carts.models import Cart, CartQueryset


class CartQuerysetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartQueryset
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"
