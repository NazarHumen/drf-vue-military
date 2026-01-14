from django.db.models import Count, Max, Min
from django.http import Http404
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.goods.models import Categories, Products
from apps.goods.serializers import CategorySerializer, ProductSerializer
from apps.goods.utils import q_search
from apps.tools.pagination import CustomPageNumberPagination


class CatalogAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    pagination_class = CustomPageNumberPagination

    def get(self, request, category_slug=None):
        query = request.query_params.get("q")
        on_sale = request.query_params.get("on_sale")
        order_by = request.query_params.get("order_by")
        # Підтримка множинних категорій через query параметр
        categories_param = request.query_params.get("categories")
        # Фільтр по ціні
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")

        if query:
            goods = q_search(request, query)
        elif categories_param:
            # Фільтрація по множинних категоріях
            category_slugs = [
                slug.strip()
                for slug in categories_param.split(",")
                if slug.strip()
            ]
            if category_slugs:
                goods = Products.objects.filter(
                    category__slug__in=category_slugs
                )
            else:
                goods = Products.objects.all()
        elif category_slug == "all" or not category_slug:
            goods = Products.objects.all()
        elif category_slug:
            # Перевірка чи категорія існує
            if not Categories.objects.filter(slug=category_slug).exists():
                raise Http404(_("Категорію не знайдено"))
            goods = Products.objects.filter(category__slug=category_slug)
        else:
            goods = Products.objects.all()

        # Фільтр по знижках
        if on_sale:
            goods = goods.filter(discount__gt=0)

        # Фільтр по ціні (використовуємо discounted_price - ціна зі знижкою)
        if min_price:
            try:
                goods = goods.filter(discounted_price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                goods = goods.filter(discounted_price__lte=float(max_price))
            except ValueError:
                pass

        # Сортування
        if order_by and order_by != "default":
            # Маппінг для сортування по ціні зі знижкою
            sort_mapping = {
                "price": "discounted_price",
                "-price": "-discounted_price",
            }
            order_field = sort_mapping.get(order_by, order_by)
            goods = goods.order_by(order_field)

        # Отримуємо глобальний діапазон цін (до фільтрації по ціні)
        price_range = Products.objects.aggregate(
            min_price=Min("discounted_price"),
            max_price=Max("discounted_price"),
        )

        # Пагінація
        paginator = self.pagination_class()
        paginated_goods = paginator.paginate_queryset(goods, request)
        serializer = ProductSerializer(paginated_goods, many=True)

        # Return HTML template for browser requests
        if request.accepted_renderer.format == "html":
            return Response(
                {
                    "title": _("Catalog"),
                    "category_slug": category_slug or "all",
                    "request": request,
                    "user": request.user,
                },
                template_name="goods/catalog.html",
            )

        # Return JSON for API requests
        response = paginator.get_paginated_response(serializer.data)
        response.data["price_range"] = {
            "min": float(price_range["min_price"] or 0),
            "max": float(price_range["max_price"] or 0),
        }
        return response


class ProductAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get(self, request, product_slug):
        try:
            product = Products.objects.get(slug=product_slug)
        except Products.DoesNotExist:
            raise Http404(_("Товар не знайдено"))

        serializer = ProductSerializer(product)

        # Return HTML template for browser requests
        if request.accepted_renderer.format == "html":
            return Response(
                {
                    "title": product.name,
                    "product_slug": product_slug,
                    "request": request,
                    "user": request.user,
                },
                template_name="goods/product.html",
            )

        # Return JSON for API requests
        return Response(
            {
                "title": product.name,
                "product": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class CategoriesAPIView(APIView):
    def get(self, request):
        categories = Categories.objects.annotate(
            products_count=Count("products")
        )
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
