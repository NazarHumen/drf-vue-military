from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.carts.mixins import CartMixin
from apps.carts.models import Cart
from apps.goods.models import Products


class BasketAPIView(CartMixin, APIView):
    """View для сторінки кошика з Vue.js"""

    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get(self, request):
        # Return HTML template for browser requests
        if request.accepted_renderer.format == "html":
            return Response(
                {
                    "title": _("Кошик"),
                    "request": request,
                    "user": request.user,
                },
                template_name="carts/basket.html",
            )

        # Return JSON for API requests
        return Response(self.get_cart_data(request), status=status.HTTP_200_OK)


class CartListAPIView(CartMixin, APIView):
    def get(self, request):
        data = self.get_cart_data(request)
        return Response(data, status=status.HTTP_200_OK)


class CartAddAPIView(CartMixin, APIView):
    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response(
                {"error": _("Не вказано ID товару")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Валідація quantity
        try:
            quantity = int(quantity)
            if quantity < 1:
                quantity = 1
        except (TypeError, ValueError):
            quantity = 1

        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response(
                {"error": _("Товар не знайдено")},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Перевірка статусу наявності
        if product.availability_status == "out_of_stock":
            return Response(
                {"error": _("Товар відсутній на складі")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart = self.get_cart(request, product=product)
        current_quantity = cart.quantity if cart else 0

        # Визначаємо максимальну кількість залежно від статусу
        if product.availability_status == "last_item":
            max_quantity = min(5, product.quantity)
        else:  # ready_to_ship
            max_quantity = product.quantity

        # Перевіряємо чи не перевищуємо ліміт
        new_quantity = current_quantity + quantity
        if new_quantity > max_quantity:
            if product.availability_status == "last_item":
                return Response(
                    {
                        "error": _(
                            "Максимальна кількість "
                            "для цього товару: %(max)s шт."
                        )
                        % {"max": max_quantity}
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                return Response(
                    {
                        "error": _("На складі залишилось лише %(max)s шт.")
                        % {"max": max_quantity}
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if cart:
            cart.quantity = new_quantity
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
                quantity=quantity,
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

        product = cart.product

        # Перевірка статусу наявності
        if product.availability_status == "out_of_stock":
            return Response(
                {"error": _("Товар відсутній на складі")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Визначаємо максимальну кількість залежно від статусу
        if product.availability_status == "last_item":
            max_quantity = min(5, product.quantity)
        else:  # ready_to_ship
            max_quantity = product.quantity

        # Перевіряємо чи не перевищуємо ліміт
        if quantity > max_quantity:
            return Response(
                {
                    "error": _("Максимальна кількість: %(max)s шт.")
                    % {"max": max_quantity},
                    "max_quantity": max_quantity,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

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
