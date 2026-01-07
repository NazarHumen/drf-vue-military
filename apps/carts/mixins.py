from apps.carts.models import Cart
from apps.carts.utils import get_user_carts


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

    def get_cart_totals(self, request):
        carts = get_user_carts(request)
        total_price_uah = round(carts.total_price(), 2)
        total_price_usd = round(carts.total_price_usd(), 2)
        return total_price_uah, total_price_usd

    def get_cart_data(self, request):
        # Отримуємо кошики користувача
        user_cart = get_user_carts(request)
        cart_data = []

        total_price_uah = 0
        total_price_usd = 0
        total_quantity = 0

        for item in user_cart:
            products_price_uah = float(
                item.product.sell_price() * item.quantity
            )
            products_price_usd = float(
                item.product.price_in_usd * item.quantity
            )

            cart_data.append(
                {
                    "id": item.id,
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "product_sell_price": round(item.product.sell_price(), 2),
                    "product_price_usd": round(item.product.price_in_usd, 2),
                    "quantity": item.quantity,
                    "products_price": round(products_price_uah, 2),
                    "products_price_usd": round(products_price_usd, 2),
                }
            )
            total_price_uah += products_price_uah
            total_price_usd += products_price_usd
            total_quantity += item.quantity

        return {
            "items": cart_data,
            "total_price": round(total_price_uah, 2),
            "total_price_usd": round(total_price_usd, 2),
            "total_quantity": total_quantity,
        }
