from django.db import transaction
from django.forms import ValidationError
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.carts.models import Cart
from apps.orders.models import Order, OrderItem
from apps.orders.serializers import OrderSerializer


class CreateOrderAPIView(APIView):
    def post(self, request):
        user = request.user
        data = request.data

        if not user.is_authenticated:
            return Response(
                {"error": _("Потрібно увійти в систему")},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response(
                {"error": _("Ваш кошик порожній")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            with transaction.atomic():
                # створення замовлення
                order = Order.objects.create(
                    user=user,
                    phone_number=data.get("phone_number"),
                    email=data.get("email"),
                    requires_delivery=data.get("requires_delivery", False),
                    delivery_address=data.get("delivery_address"),
                    payment_on_get=data.get("payment_on_get", False),
                )

                # додавання товарів до замовлення
                for cart_item in cart_items:
                    product = cart_item.product
                    quantity = cart_item.quantity

                    if product.quantity < quantity:
                        raise ValidationError(
                            _(
                                "Недостатня кількість товару %(name)s "
                                "на складі. "
                                "В наявності — %(quantity)d"
                            )
                            % {
                                "name": product.name,
                                "quantity": product.quantity,
                            }
                        )

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        name=product.name,
                        price=product.sell_price(),
                        quantity=quantity,
                    )

                    # оновлення кількості товару
                    product.quantity -= quantity
                    product.save()

                # очищення кошика
                cart_items.delete()

                serializer = OrderSerializer(order)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )

        except ValidationError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
