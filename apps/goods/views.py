from django.http import Http404
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.goods.models import Products
from apps.goods.serializers import ProductSerializer
from apps.goods.utils import q_search
from apps.tools.pagination import CustomPageNumberPagination


class CatalogAPIView(APIView):
    pagination_class = CustomPageNumberPagination

    def get(self, request, category_slug=None):
        query = request.query_params.get("q")
        on_sale = request.query_params.get("on_sale")
        order_by = request.query_params.get("order_by")

        if query:
            goods = q_search(request, query)
        elif category_slug == "all" or not category_slug:
            goods = Products.objects.all()
        elif category_slug:
            goods = Products.objects.filter(category__slug=category_slug)
            if not goods.exists():
                raise Http404(_("Категорію не знайдено"))
        else:
            goods = Products.objects.all()

        # Фільтр по знижках
        if on_sale:
            goods = goods.filter(discount__gt=0)

        # Сортування
        if order_by and order_by != "default":
            goods = goods.order_by(order_by)

        # Пагінація
        paginator = self.pagination_class()
        paginated_goods = paginator.paginate_queryset(goods, request)
        serializer = ProductSerializer(paginated_goods, many=True)

        # return paginator.get_paginated_response({
        #     "title": _("Home - Каталог"),
        #     "slug_url": category_slug,
        #     "show_filters": True,
        #     "goods": serializer.data,
        # })
        return paginator.get_paginated_response(serializer.data)


class ProductAPIView(APIView):
    def get(self, request, product_slug):
        try:
            product = Products.objects.get(slug=product_slug)
        except Products.DoesNotExist:
            raise Http404(_("Товар не знайдено"))

        serializer = ProductSerializer(product)
        return Response(
            {
                "title": product.name,
                "product": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
