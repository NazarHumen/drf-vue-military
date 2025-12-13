from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    SearchHeadline,
)

# from pygments.lexers.webassembly import keywords

from goods.models import Products
from django.db.models import Q
from django.utils.translation import get_language
from decimal import Decimal
import requests
from goods.models import ExchangeRate


def update_exchange_rate_via_api(base_currency: str, target_currency: str):
    API_URL = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # перевірка, що запит пройшов успішно
        data = response.json()
        rate = data["rates"].get(target_currency)

        if rate:
            obj, created = ExchangeRate.objects.update_or_create(
                base_currency=base_currency,
                target_currency=target_currency,
                defaults={"rate": Decimal(str(rate))}
            )
            if created:
                print(
                    f"Створено новий курс: {base_currency} -> {target_currency} = {rate}")
            else:
                print(
                    f"Оновлено курс: {base_currency} -> {target_currency} = {rate}")
            return Decimal(str(rate))
        else:
            print(f"Курс для {target_currency} не знайдено в API.")
    except requests.RequestException as e:
        print(f"Помилка HTTP запиту: {e}")
    except Exception as e:
        print(f"Інша помилка: {e}")

    return None


# def q_search(query):
#     if query.isdigit() and len(query) <= 5:
#         return Products.objects.filter(id=int(query))
#
#     vector = SearchVector("name", "description","name_en", "description_en")
#     query = SearchQuery(query)
#     result = (
#         Products.objects.annotate(rank=SearchRank(vector, query))
#         .filter(rank__gt=0)
#         .order_by("-rank")
#     )
#     result = result.annotate(
#         headline=SearchHeadline(
#             "name",
#             query,
#             start_sel='<span style="background-color: red;">',
#             stop_sel="</span>",
#         )
#     )
#     result = result.annotate(
#         bodyline=SearchHeadline(
#             "description",
#             query,
#             start_sel='<span style="background-color: red;">',
#             stop_sel="</span>",
#         )
#     )
#     return result


def q_search(request, query):
    lang = get_language()  # або можна: lang = request.LANGUAGE_CODE

    if query.isdigit() and len(query) <= 5:
        return Products.objects.filter(id=int(query))

    vector = SearchVector("name", "description", "name_en", "description_en")
    search_query = SearchQuery(query)

    result = (
        Products.objects.annotate(rank=SearchRank(vector, search_query))
        .filter(rank__gt=0)
        .order_by("-rank")
    )

    if lang == "en":
        result = result.annotate(
            title=SearchHeadline(
                "name_en", search_query,
                start_sel='<span style="background-color: red;">',
                stop_sel="</span>",
            ),
            body=SearchHeadline(
                "description_en", search_query,
                start_sel='<span style="background-color: red;">',
                stop_sel="</span>",
            ),
        )
    else:
        result = result.annotate(
            title=SearchHeadline(
                "name", search_query,
                start_sel='<span style="background-color: red;">',
                stop_sel="</span>",
            ),
            body=SearchHeadline(
                "description", search_query,
                start_sel='<span style="background-color: red;">',
                stop_sel="</span>",
            ),
        )

    return result



    # keywords = [word for word in query.split() if len(word) > 2]
    #
    # q_objects = Q()
    #
    # for token in keywords:
    #     q_objects |= Q(description__icontains=token)
    #     q_objects |= Q(name__icontains=token)
    #
    #
    #
    # return Products.objects.filter(q_objects)
