from decimal import Decimal

import requests
from django.utils.translation import get_language

from apps.goods.models import ExchangeRate, Products


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
                defaults={"rate": Decimal(str(rate))},
            )
            if created:
                print(
                    f"Створено новий курс: {base_currency} "
                    f"-> {target_currency} = {rate}"
                )
            else:
                print(
                    f"Оновлено курс: {base_currency} "
                    f"-> {target_currency} = {rate}"
                )
            return Decimal(str(rate))
        else:
            print(f"Курс для {target_currency} не знайдено в API.")
    except requests.RequestException as e:
        print(f"Помилка HTTP запиту: {e}")
    except Exception as e:
        print(f"Інша помилка: {e}")

    return None


def q_search(request, query):
    lang = get_language()  # або можна: lang = request.LANGUAGE_CODE

    if query.isdigit() and len(query) <= 5:
        return Products.objects.filter(id=int(query))

    # Частковий пошук по назві та описі (icontains)
    from django.db.models import Q

    if lang == "en":
        result = Products.objects.filter(
            Q(name_en__icontains=query) | Q(description_en__icontains=query)
        )
    else:
        result = Products.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    return result
