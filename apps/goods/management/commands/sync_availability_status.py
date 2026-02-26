from django.core.management.base import BaseCommand

from apps.goods.models import Products


class Command(BaseCommand):
    help = "Синхронізує availability_status всіх продуктів на основі quantity"

    def handle(self, *args, **kwargs):
        out_of_stock = Products.objects.filter(quantity=0).update(
            availability_status="out_of_stock"
        )
        last_item = Products.objects.filter(
            quantity__gt=0, quantity__lte=5
        ).update(availability_status="last_item")
        ready = Products.objects.filter(quantity__gt=5).update(
            availability_status="ready_to_ship"
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Статуси оновлено: "
                f"{out_of_stock} немає в наявності, "
                f"{last_item} останній товар, "
                f"{ready} готовий до відправлення"
            )
        )
