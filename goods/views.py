from trace import Trace

from django.http import Http404, request
from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import Http404
from django.utils.text import slugify
from django.views.generic import DetailView, ListView

from goods.models import Products
from goods.utils import q_search
from django.urls import reverse
from django.utils.translation import gettext as _


# Create your views here.


class ProductView(DetailView):
    # model = Products
    # slug_field = "slug"
    template_name = "goods/product.html"
    slug_url_kwarg = "product_slug"
    context_object_name = "product"

    def get_object(self, queryset=None):
        product = Products.objects.get(
            slug=self.kwargs.get(self.slug_url_kwarg)
        )
        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.name
        return context

    # Profile
    def get_absolute_url(self):
        if not self.slug:
            return reverse("catalog:index")  # Або якийсь інший маршрут
        return reverse("catalog:product", kwargs={"product_slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                self.name
            )  # Автоматично генеруємо slug, якщо його немає
        super().save(*args, **kwargs)

    # def is_favorited(self, user):
    #     return self.favorited_by.filter(user=user).exists()
    #
    # for product in goods:
    #     product.is_favorited = product.is_favorited(request.user)


def catalog(request, category_slug=None):
    page = request.GET.get("page", 1)
    on_sale = request.GET.get("on_sale", None)
    order_by = request.GET.get("order_by", None)
    query = request.GET.get("q", None)

    # Перевірка на порожній запит
    if query == "":
        query = None

    # if query:
    #     goods = q_search(query)

    if query:
        goods = q_search(request, query)

    elif category_slug == "all" or not category_slug:
        goods = Products.objects.all()
    elif category_slug:
        goods = Products.objects.filter(category__slug=category_slug)
        if not goods.exists():
            raise Http404()
    else:
        goods = Products.objects.all()

    # Застосування фільтрів
    if on_sale:
        goods = goods.filter(discount__gt=0)

    if order_by and order_by != "default":
        goods = goods.order_by(order_by)

    paginator = Paginator(goods, 3)
    current_page = paginator.page(int(page))

    context = {
        "title": _("Home - Каталог"),
        "goods": current_page,
        "slug_url": category_slug,
        "show_filters": True,
    }
    return render(request, "goods/catalog.html", context)
