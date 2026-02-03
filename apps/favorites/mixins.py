from apps.favorites.models import Favorite
from apps.favorites.utils import get_user_favorites


class FavoriteMixin:
    def get_favorite(self, request, product=None, favorite_id=None):
        """Отримує конкретний елемент обраного."""
        query_kwargs = (
            {"user": request.user}
            if request.user.is_authenticated
            else {"session_key": request.session.session_key}
        )

        if product:
            query_kwargs["product"] = product
        if favorite_id:
            query_kwargs["id"] = favorite_id

        return Favorite.objects.filter(**query_kwargs).first()

    def get_favorites_data(self, request):
        """Отримує дані про всі обрані товари."""
        user_favorites = get_user_favorites(request)
        favorites_data = []

        for item in user_favorites:
            product_image = None
            if item.product.image:
                product_image = item.product.image.url

            favorites_data.append(
                {
                    "id": item.id,
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "product_description": item.product.description,
                    "product_image": product_image,
                    "product_slug": item.product.slug,
                    "product_price": round(item.product.price, 2),
                    "product_sell_price": round(item.product.sell_price(), 2),
                    "product_price_usd": round(item.product.price_in_usd, 2),
                    "product_discount": item.product.discount,
                    "availability_status": item.product.availability_status,
                    "availability_status_display": item.product.get_availability_status_display(),
                    "created_at": item.created_at.isoformat(),
                }
            )

        return {
            "items": favorites_data,
            "total_count": len(favorites_data),
        }

    def get_favorite_ids(self, request):
        """Повертає список ID товарів в обраному."""
        user_favorites = get_user_favorites(request)
        return list(user_favorites.values_list("product_id", flat=True))
