from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views import View

from carts.mixins import CartMixin
from carts.models import Cart
from carts.utils import get_user_carts
from apps.goods.models import Products
from django.urls import reverse
from django.utils.translation import gettext as _


class CartAddView(CartMixin, View):
    def post(self, request):
        product_id = request.POST.get("product_id")
        product = Products.objects.get(id=product_id)

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

        # Перевіряємо, чи користувач авторизований, перш ніж виконувати фільтрацію за user
        if request.user.is_authenticated:
            total_price_uah = round(
                Cart.objects.filter(user=request.user).total_price(), 2
            )
            total_price_usd = round(
                Cart.objects.filter(user=request.user).total_price_usd(), 2
            )
        else:
            total_price_uah = 0
            total_price_usd = 0

        response_data = {
            "message": _("Товар доданий до кошика"),
            "cart_items_html": self.render_cart(request),
            "total_price_uah": total_price_uah,
            "total_price_usd": total_price_usd,
        }

        return JsonResponse(response_data)





class CartChangeView(CartMixin, View):
    def post(self, request):
        cart_id = request.POST.get("cart_id")
        cart = self.get_cart(request, cart_id=cart_id)

        try:
            quantity = int(request.POST.get("quantity", 1))
            if quantity < 1:
                quantity = 1
        except (TypeError, ValueError):
            quantity = 1  # fallback на безпечне значення

        cart.quantity = quantity
        cart.save()

        response_data = {
            "message": _("Кількість змінено"),
            "quantity": cart.quantity,
            "cart_items_html": self.render_cart(request),
        }

        return JsonResponse(response_data)



class CartRemoveView(CartMixin, View):
    def post(self, request):
        cart_id = request.POST.get("cart_id")

        cart = self.get_cart(request, cart_id=cart_id)
        quantity = cart.quantity
        cart.delete()

        response_data = {
            "message": _("Товар видалено"),
            "quantity_deleted": quantity,
            "cart_items_html": self.render_cart(request),
        }

        return JsonResponse(response_data)



#First invalid example (original)
# class CartChangeView(CartMixin, View):
#     def post(self, request):
#         cart_id = request.POST.get("cart_id")
#
#         cart = self.get_cart(request, cart_id=cart_id)
#
#         cart.quantity = request.POST.get("quantity")
#         cart.save()
#
#         quantity = cart.quantity
#
#         response_data = {
#             "message": _("Кількість змінено"),
#             "quantity": quantity,
#             "cart_items_html": self.render_cart(request),
#         }
#
#         return JsonResponse(response_data)

# def cart_add(request):
#     product_id = request.POST.get("product_id")
#     product = Products.objects.get(id=product_id)
#
#     if request.user.is_authenticated:
#         carts = Cart.objects.filter(user=request.user, product=product)
#
#         if carts.exists():
#             cart = carts.first()
#             if cart:
#                 cart.quantity += 1
#                 cart.save()
#         else:
#             Cart.objects.create(user=request.user, product=product, quantity=1)
#
#     else:
#         carts = Cart.objects.filter(
#             session_key=request.session.session_key, product=product
#         )
#         if carts.exists():
#             cart = carts.first()
#             if cart:
#                 cart.quantity += 1
#                 cart.save()
#         else:
#             Cart.objects.create(
#                 session_key=request.session.session_key,
#                 product=product,
#                 quantity=1,
#             )
#
#     user_cart = get_user_carts(request)
#
#     cart_items_html = render_to_string(
#         "carts/includes/included_carts.html",
#         {"carts": user_cart},
#         request=request,
#     )
#
#     response_data = {
#         "message": "Товар доданий до кошика",
#         "cart_items_html": cart_items_html,
#     }
#
#     return JsonResponse(response_data)

# comment
# def cart_change(request):
#     cart_id = request.POST.get("cart_id")
#     quantity = request.POST.get("quantity")
#
#     cart = Cart.objects.get(id=cart_id)
#
#     cart.quantity = quantity
#     cart.save()
#     # updated_quantity = cart.quantity
#
#     # cart = get_user_carts(request)
#     user_cart = get_user_carts(request)
#     context = {"carts": user_cart}
#
#     referer = request.META.get('HTTP_REFERER')
#     if reverse('orders:create_order') in referer:
#         context["orders"] = True
#
#
#
#     cart_items_html = render_to_string(
#         "carts/includes/included_carts.html", context, request=request
#     )
#
#     response_data = {
#         "message": "Кількість змінено",
#         "cart_items_html": cart_items_html,
#         "quantity": quantity,
#     }
#     return JsonResponse(response_data)

# comment
# def cart_change(request):
#     if request.method == "POST":
#         # Отримуємо дані з POST-запиту
#         cart_id = request.POST.get("cart_id")
#         action = request.POST.get("action")
#
#         # Отримуємо відповідний елемент кошика
#         cart = Cart.objects.get(id=cart_id)
#
#         # Оновлюємо кількість товару
#         if action == "increment":
#             cart.quantity += 1
#         elif action == "decrement" and cart.quantity > 1:
#             cart.quantity -= 1
#
#         cart.save()
#
#         # Отримуємо оновлений кошик користувача
#         user_cart = get_user_carts(request)
#
#         # Підготовка контексту для рендерингу шаблону
#         context = {"carts": user_cart}
#         referer = request.META.get("HTTP_REFERER")
#         if reverse("orders:create_order") in referer:
#             context["orders"] = True
#
#         # Рендеринг оновленого HTML
#         cart_items_html = render_to_string(
#             "carts/includes/included_carts.html", context, request=request
#         )
#
#         # Повернення JSON-даних
#         response_data = {
#             "message": "Кількість змінено",
#             "cart_items_html": cart_items_html,
#             "quantity": cart.quantity,
#             "products_price": cart.products_price,
#             "total_quantity": user_cart.total_quantity(),
#             "total_price": user_cart.total_price(),
#         }
#         return JsonResponse(response_data)
#
#     return JsonResponse({"error": "Некоректний запит"}, status=400)


# def cart_remove(request):
#     cart_id = request.POST.get("cart_id")
#
#     cart = Cart.objects.get(id=cart_id)
#     quantity = cart.quantity
#     cart.delete()
#
#     user_cart = get_user_carts(request)
#
#     context = {"carts": user_cart}
#     referer = request.META.get("HTTP_REFERER")
#     if reverse("orders:create_order") in referer:
#         context["orders"] = True
#
#     cart_items_html = render_to_string(
#         "carts/includes/included_carts.html",
#         context,
#         request=request,
#     )
#
#     response_data = {
#         "message": "Товар видалено",
#         "cart_items_html": cart_items_html,
#         "quantity_deleted": quantity,
#     }
#
#     return JsonResponse(response_data)
