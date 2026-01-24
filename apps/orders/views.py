from django.db import transaction
from django.forms import ValidationError
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.carts.models import Cart
from apps.orders.forms import CreateOrderForm
from apps.orders.models import Order, OrderItem
from apps.orders.serializers import OrderSerializer


class CreateOrderAPIView(APIView):
    """View для сторінки замовлення з підтримкою HTML та JSON"""

    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get(self, request):
        """Рендеринг сторінки замовлення"""
        if request.accepted_renderer.format == "html":
            form = CreateOrderForm()

            # Попереднє заповнення даних користувача
            if request.user.is_authenticated:
                form = CreateOrderForm(
                    initial={
                        "first_name": request.user.first_name,
                        "last_name": request.user.last_name,
                        "email": request.user.email,
                    }
                )

            return Response(
                {
                    "title": _("Оформлення замовлення"),
                    "form": form,
                    "request": request,
                    "user": request.user,
                },
                template_name="orders/create_order.html",
            )

        # Для API - повертаємо інформацію про endpoint
        return Response(
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        user = request.user

        # Перевірка для HTML форми
        if request.accepted_renderer.format == "html":
            return self._handle_form_submission(request, user)

        # Обробка API запиту
        return self._handle_api_submission(request, user)

    def _handle_form_submission(self, request, user):
        """Обробка HTML форми"""
        form = CreateOrderForm(request.POST)

        if not user.is_authenticated:
            form.add_error(None, _("Потрібно увійти в систему"))
            return Response(
                {
                    "title": _("Оформлення замовлення"),
                    "form": form,
                    "request": request,
                    "user": user,
                },
                template_name="orders/create_order.html",
            )

        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            form.add_error(None, _("Ваш кошик порожній"))
            return Response(
                {
                    "title": _("Оформлення замовлення"),
                    "form": form,
                    "request": request,
                    "user": user,
                },
                template_name="orders/create_order.html",
            )

        if form.is_valid():
            try:
                order = self._create_order(user, form.cleaned_data, cart_items)
                # Redirect до профілю або сторінки успіху
                from django.shortcuts import redirect

                return redirect("users:profile")
            except ValidationError as e:
                form.add_error(None, str(e))

        return Response(
            {
                "title": _("Оформлення замовлення"),
                "form": form,
                "request": request,
                "user": user,
            },
            template_name="orders/create_order.html",
        )

    def _handle_api_submission(self, request, user):
        """Обробка API запиту"""
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
            order = self._create_order(user, data, cart_items)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _create_order(self, user, data, cart_items):
        """Створення замовлення"""
        with transaction.atomic():
            # Отримання даних з форми або API
            if hasattr(data, "get"):
                # dict-like (API або cleaned_data)
                phone_number = data.get("phone_number")
                email = data.get("email")
                requires_delivery = data.get("requires_delivery", False)
                delivery_address = data.get("delivery_address")
                payment_on_get = data.get("payment_on_get", False)
            else:
                # form cleaned_data
                phone_number = data.phone_number
                email = data.email
                requires_delivery = data.requires_delivery
                delivery_address = data.delivery_address
                payment_on_get = data.payment_on_get

            # Конвертація requires_delivery та payment_on_get
            if isinstance(requires_delivery, str):
                requires_delivery = requires_delivery == "1"
            if isinstance(payment_on_get, str):
                payment_on_get = payment_on_get == "1"

            order = Order.objects.create(
                user=user,
                phone_number=phone_number,
                email=email,
                requires_delivery=requires_delivery,
                delivery_address=delivery_address,
                payment_on_get=payment_on_get,
            )

            for cart_item in cart_items:
                product = cart_item.product
                quantity = cart_item.quantity

                if product.quantity < quantity:
                    raise ValidationError(
                        _(
                            "Недостатня кількість товару %(name)s "
                            "на складі. В наявності — %(quantity)d"
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

                product.quantity -= quantity
                product.save()

            cart_items.delete()
            return order
