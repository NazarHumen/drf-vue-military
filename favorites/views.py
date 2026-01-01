from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views import View
from .models import Favorite
from apps.goods.models import Products
from django.views.generic.list import ListView


class ToggleFavoriteView(View):
    # def post(self, request):
    #     product_id = request.POST.get("product_id")
    #     product = Products.objects.get(id=product_id)
    #
    #     favorite, created = Favorite.objects.get_or_create(
    #         user=request.user, product=product
    #     )
    #     if not created:
    #         favorite.delete()
    #         is_favorited = False
    #     else:
    #         is_favorited = True
    #
    #     return JsonResponse(
    #         {
    #             "is_favorited": is_favorited,
    #             "message": (
    #                 "Товар додано до обраних"
    #                 if is_favorited
    #                 else "Товар видалено з обраних"
    #             ),
    #         }
    #     )

    def post(self, request):
        product_id = request.POST.get("product_id")
        product = Products.objects.get(id=product_id)

        favorite, created = Favorite.objects.get_or_create(
            user=request.user, product=product
        )

        if not created:
            favorite.delete()
            is_favorited = False
        else:
            is_favorited = True

        # Отримуємо оновлену кількість
        favorites_count = Favorite.objects.filter(user=request.user).count()

        # Рендеримо новий список обраних товарів
        favorites_items_html = render_to_string(
            "favorites/list.html",
            {"favorites": Favorite.objects.filter(user=request.user)},
            request=request,
        )

        return JsonResponse(
            {
                "is_favorited": is_favorited,
                "message": (
                    "Товар додано до обраних"
                    if is_favorited
                    else "Товар видалено з обраних"
                ),
                "favorites_count": favorites_count,
                "favorites_items_html": favorites_items_html,
            }
        )

    # def post(self, request):
    #     product_id = request.POST.get("product_id")
    #     product = Products.objects.get(id=product_id)
    #
    #     favorite, created = Favorite.objects.get_or_create(user=request.user,
    #                                                        product=product)
    #
    #     if not created:
    #         favorite.delete()
    #         is_favorited = False
    #     else:
    #         is_favorited = True
    #
    #     # Отримуємо актуальну кількість обраних товарів
    #     favorites_count = Favorite.objects.filter(user=request.user).count()
    #
    #     # Рендеримо оновлений HTML для списку обраних товарів
    #     favorites_items_html = render_to_string(
    #         "favorites/list.html",  # Використовуємо твій шаблон
    #         {"favorites": Favorite.objects.filter(user=request.user)},
    #         request=request
    #     )
    #
    #     return JsonResponse({
    #         "is_favorited": is_favorited,
    #         "message": "Товар додано до обраних" if is_favorited else "Товар видалено з обраних",
    #         "favorites_count": favorites_count,
    #         "favorites_items_html": favorites_items_html
    #     })

    # def post(self, request):
    #     product_id = request.POST.get("product_id")
    #     product = Products.objects.get(id=product_id)
    #
    #     favorite, created = Favorite.objects.get_or_create(user=request.user,
    #                                                        product=product)
    #
    #     if not created:
    #         favorite.delete()
    #         is_favorited = False
    #     else:
    #         is_favorited = True
    #
    #     # Отримуємо актуальну кількість обраних товарів
    #     favorites_count = Favorite.objects.filter(user=request.user).count()
    #
    #     # Підготовка даних для повернення
    #     favorites_items_html = render_to_string(
    #         "favorites/list.html",  # Шаблон для списку обраних товарів
    #         {"favorites": Favorite.objects.filter(user=request.user)},
    #         request=request
    #     )
    #
    #     # Повертаємо відповіді
    #     return JsonResponse({
    #         "is_favorited": is_favorited,
    #         "message": "Товар додано до обраних" if is_favorited else "Товар видалено з обраних",
    #         "favorites_count": favorites_count,
    #         "favorites_items_html": favorites_items_html,
    #     })

    # def post(self, request):
    #     product_id = request.POST.get("product_id")
    #     product = Products.objects.get(id=product_id)
    #
    #     favorite, created = Favorite.objects.get_or_create(
    #         user=request.user, product=product
    #     )
    #     if not created:
    #         favorite.delete()
    #         is_favorited = False
    #     else:
    #         is_favorited = True
    #
    #     # Підрахунок обраних товарів для користувача
    #     favorites_count = Favorite.objects.filter(user=request.user).count()
    #
    #     return JsonResponse(
    #         {
    #             "is_favorited": is_favorited,
    #             "message": "Товар додано до обраних" if is_favorited else "Товар видалено з обраних",
    #             "favorites_count": favorites_count,
    #             # Передаємо кількість товарів
    #         }
    #     )


# class FavoritesListView(ListView):
#     model = Favorite
#     template_name = 'favorites/list.html'
#     context_object_name = 'favorites'
#
#     def get_queryset(self):
#         return Favorite.objects.filter(user=self.request.user)
#
#
#
#     def get_context_data(self, **kwargs):
#         # Оновлюємо контекст для передавання додаткової інформації
#         context = super().get_context_data(**kwargs)
#         context['favorites_count'] = Favorite.objects.filter(
#             user=self.request.user).count()  # кількість обраних товарів
#         return context
class FavoritesListView(ListView):
    model = Favorite
    template_name = "favorites/list.html"
    context_object_name = "favorites"

    def get_queryset(self):
        # Отримуємо обрані товари для поточного користувача
        return Favorite.objects.select_related("product").filter(
            user=self.request.user
        )

    def get_context_data(self, **kwargs):
        # Оновлюємо контекст для передавання додаткової інформації
        context = super().get_context_data(**kwargs)
        context["favorites_count"] = (
            self.get_queryset().count()
        )  # Кількість обраних товарів
        return context


class RemoveFavoriteView(View):
    def post(self, request):
        product_id = request.POST.get("product_id")
        product = Products.objects.get(id=product_id)
        try:
            favorite = Favorite.objects.get(user=request.user, product=product)
            favorite.delete()
            is_favorited = False
            message = "Товар видалено з обраних"
        except Favorite.DoesNotExist:
            is_favorited = True
            message = "Товар не знайдений в обраних"

        return JsonResponse({"is_favorited": is_favorited, "message": message})
