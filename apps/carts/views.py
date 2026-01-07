from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.carts.mixins import CartMixin
from apps.carts.models import Cart
from apps.goods.models import Products


class CartListAPIView(CartMixin, APIView):
    def get(self, request):
        data = self.get_cart_data(request)
        return Response(data, status=status.HTTP_200_OK)


class CartAddAPIView(CartMixin, APIView):
    def post(self, request):
        product_id = request.data.get("product_id")

        if not product_id:
            return Response(
                {"error": _("Не вказано ID товару")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response(
                {"error": _("Товар не знайдено")},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart = self.get_cart(request, product=product)

        if cart:
            cart.quantity += 1
            cart.save()
        else:
            Cart.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=(
                    request.session.session_key
                    if not request.user.is_authenticated
                    else None
                ),
                product=product,
                quantity=1,
            )

        total_price_uah, total_price_usd = self.get_cart_totals(request)

        response_data = {
            "message": _("Товар доданий до кошика"),
            "total_price_uah": total_price_uah,
            "total_price_usd": total_price_usd,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class CartChangeAPIView(CartMixin, APIView):
    def post(self, request):
        cart_id = request.data.get("cart_id")
        quantity = request.data.get("quantity")
        if not cart_id:
            return Response(
                {"error": _("Не вказано ID елемента кошика")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart = self.get_cart(request, cart_id=cart_id)
        if not cart:
            return Response(
                {"error": _("Елемент кошика не знайдено")},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            quantity = int(quantity)
            if quantity < 1:
                quantity = 1
        except (TypeError, ValueError):
            quantity = 1  # fallback на безпечне значення

        cart.quantity = quantity
        cart.save()

        response_data = {
            "message": _("Кількість змінено"),
            "quantity": cart.quantity,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class CartRemoveAPIView(CartMixin, APIView):
    def post(self, request):
        cart_id = request.data.get("cart_id")
        if not cart_id:
            return Response(
                {"error": _("Не вказано ID елемента кошика")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart = self.get_cart(request, cart_id=cart_id)
        if not cart:
            return Response(
                {"error": _("Елемент кошика не знайдено")},
                status=status.HTTP_404_NOT_FOUND,
            )

        quantity = cart.quantity
        total_price_uah, total_price_usd = self.get_cart_totals(request)
        cart.delete()

        response_data = {
            "message": _("Товар видалено"),
            "quantity_deleted": quantity,
            "total_price_uah": total_price_uah,
            "total_price_usd": total_price_usd,
        }

        return Response(response_data, status=status.HTTP_200_OK)
