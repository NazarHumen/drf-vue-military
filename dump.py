import codecs
import os

import django
from django.core.management import call_command
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dev_env.settings")
django.setup()


def create_fixture(label, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with codecs.open(file_path, "w", encoding="utf-8") as output:
        call_command("dumpdata", label, indent=2, stdout=output)


create_fixture("goods.Categories", "fixtures/goods/cats.json")
create_fixture("goods.Products", "fixtures/goods/prod.json")
create_fixture("goods.ProductImage", "fixtures/goods/images.json")
create_fixture("goods.ProductAttribute", "fixtures/goods/attributes.json")
create_fixture("goods.ExchangeRate", "fixtures/goods/rates.json")
