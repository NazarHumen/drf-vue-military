from rest_framework import serializers

from apps.orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "name",
            "price",
            "quantity",
            "created_timestamp",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        source="orderitem_set", many=True, read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "created_timestamp",
            "phone_number",
            "email",
            "requires_delivery",
            "delivery_address",
            "payment_on_get",
            "items",
        ]
        read_only_fields = ["user", "is_paid", "status", "created_timestamp"]
