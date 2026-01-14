from django.core.management.base import BaseCommand

from apps.goods.models import Products
from apps.goods.utils import update_exchange_rate_via_api


class Command(BaseCommand):
    help = "Оновлює курс валют USD -> UAH та перераховує ціни всіх продуктів"

    def handle(self, *args, **kwargs):
        # Оновлюємо курс валют
        rate = update_exchange_rate_via_api("USD", "UAH")
        if rate:
            self.stdout.write(
                self.style.SUCCESS(f"Курс валют оновлено: 1 USD = {rate} UAH")
            )

            # Пересейвлюємо всі продукти для оновлення цін
            products = Products.objects.all()
            count = products.count()
            for product in products:
                product.save()

            self.stdout.write(
                self.style.SUCCESS(f"Оновлено ціни для {count} продуктів")
            )
        else:
            self.stdout.write(
                self.style.ERROR("Не вдалося оновити курс валют")
            )
