from rest_framework import serializers

from apps.orders.models import Order
from apps.payments.models import Payment


class CreateCheckoutSessionSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()

    def validate_order_id(self, value):
        user = self.context["request"].user
        try:
            order = Order.objects.get(id=value, user=user)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Замовлення не знайдено")

        if order.is_paid:
            raise serializers.ValidationError("Замовлення вже оплачено")

        if order.payment_on_get:
            raise serializers.ValidationError(
                "Для цього замовлення обрано оплату при отриманні"
            )

        if hasattr(order, "payment") and order.payment.status == "pending":
            raise serializers.ValidationError(
                "Для цього замовлення вже створено сесію оплати"
            )

        return value


class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="order.id", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_id",
            "amount",
            "currency",
            "status",
            "created_at",
            "paid_at",
        ]
        read_only_fields = fields
