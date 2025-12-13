from django.template.loader import render_to_string
from django.urls import reverse
from carts.models import Cart
from carts.utils import get_user_carts


class CartMixin:
    def get_cart(self, request, product=None, cart_id=None):
        # Якщо користувач авторизований, шукаємо за user, інакше за session_key
        query_kwargs = (
            {"user": request.user}
            if request.user.is_authenticated
            else {"session_key": request.session.session_key}
        )

        if product:
            query_kwargs["product"] = product
        if cart_id:
            query_kwargs["id"] = cart_id

        # Повертаємо перший знайдений кошик або None, якщо його немає
        return Cart.objects.filter(**query_kwargs).first()

    def render_cart(self, request):
        # Отримуємо кошики користувача
        user_cart = get_user_carts(request)
        context = {"carts": user_cart}

        # Якщо реферер вказує на сторінку створення замовлення, додаємо ключ 'order'
        referer = request.META.get("HTTP_REFERER")
        if referer and reverse("orders:create_order") in referer:
            context["order"] = True

        # Рендеримо HTML-частину кошика
        return render_to_string(
            "carts/includes/included_carts.html", context, request=request
        )
