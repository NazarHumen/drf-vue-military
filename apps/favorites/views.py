from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.favorites.mixins import FavoriteMixin
from apps.favorites.models import Favorite
from apps.goods.models import Products


class FavoritesPageAPIView(FavoriteMixin, APIView):
    """View for the favorites page with Vue.js."""

    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get(self, request):
        if request.accepted_renderer.format == "html":
            return Response(
                {
                    "title": _("Обране"),
                    "request": request,
                    "user": request.user,
                },
                template_name="favorites/list.html",
            )

        return Response(
            self.get_favorites_data(request), status=status.HTTP_200_OK
        )


class FavoritesListAPIView(FavoriteMixin, APIView):
    """API for retrieving the list of favorite products."""

    def get(self, request):
        data = self.get_favorites_data(request)
        return Response(data, status=status.HTTP_200_OK)


class FavoriteAddAPIView(FavoriteMixin, APIView):
    """API for adding a product to favorites."""

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

        # Check if the product is already in favorites
        existing = self.get_favorite(request, product=product)
        if existing:
            return Response(
                {"error": _("Товар вже в обраному")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a session if it doesn't exist
        if (
                not request.user.is_authenticated
                and not request.session.session_key
        ):
            request.session.create()

        Favorite.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=(
                request.session.session_key
                if not request.user.is_authenticated
                else None
            ),
            product=product,
        )

        return Response(
            {
                "message": _("Товар додано до обраного"),
                "product_id": product_id,
                "is_favorited": True,
                "total_count": len(self.get_favorite_ids(request)),
            },
            status=status.HTTP_201_CREATED,
        )


class FavoriteRemoveAPIView(FavoriteMixin, APIView):
    """API for removing a product from favorites."""

    def post(self, request):
        product_id = request.data.get("product_id")
        favorite_id = request.data.get("favorite_id")

        if not product_id and not favorite_id:
            return Response(
                {"error": _("Не вказано ID товару або елемента обраного")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if favorite_id:
            favorite = self.get_favorite(request, favorite_id=favorite_id)
        else:
            try:
                product = Products.objects.get(id=product_id)
                favorite = self.get_favorite(request, product=product)
            except Products.DoesNotExist:
                return Response(
                    {"error": _("Товар не знайдено")},
                    status=status.HTTP_404_NOT_FOUND,
                )

        if not favorite:
            return Response(
                {"error": _("Товар не знайдено в обраному")},
                status=status.HTTP_404_NOT_FOUND,
            )

        favorite.delete()

        return Response(
            {
                "message": _("Товар видалено з обраного"),
                "product_id": product_id,
                "is_favorited": False,
                "total_count": len(self.get_favorite_ids(request)),
            },
            status=status.HTTP_200_OK,
        )


class FavoriteToggleAPIView(FavoriteMixin, APIView):
    """API for toggling the favorite status of a product."""

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

        existing = self.get_favorite(request, product=product)

        if existing:
            existing.delete()
            is_favorited = False
            message = _("Товар видалено з обраного")
        else:
            # Create a session if it doesn't exist
            if (
                    not request.user.is_authenticated
                    and not request.session.session_key
            ):
                request.session.create()

            Favorite.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=(
                    request.session.session_key
                    if not request.user.is_authenticated
                    else None
                ),
                product=product,
            )
            is_favorited = True
            message = _("Товар додано до обраного")

        return Response(
            {
                "message": message,
                "product_id": product_id,
                "is_favorited": is_favorited,
                "total_count": len(self.get_favorite_ids(request)),
            },
            status=status.HTTP_200_OK,
        )


class FavoriteCheckAPIView(FavoriteMixin, APIView):
    """API for checking if a product is in favorites."""

    def get(self, request):
        product_id = request.query_params.get("product_id")

        if not product_id:
            # Return a list of all product IDs in favorites
            return Response(
                {"favorite_ids": self.get_favorite_ids(request)},
                status=status.HTTP_200_OK,
            )

        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response(
                {"error": _("Товар не знайдено")},
                status=status.HTTP_404_NOT_FOUND,
            )

        existing = self.get_favorite(request, product=product)

        return Response(
            {
                "product_id": product_id,
                "is_favorited": existing is not None,
            },
            status=status.HTTP_200_OK,
        )
