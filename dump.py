from django.core.management import call_command
import os
import django
import codecs
from dotenv import load_dotenv  # Завантаження змінних з .env

# Завантажуємо змінні з .env
load_dotenv()

# Налаштовуємо Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dev_env.settings")

# Встановлюємо пароль для PostgreSQL
os.environ["PGPASSWORD"] = os.getenv("DB_PASSWORD")

# Ініціалізуємо Django
django.setup()


# Створюємо дампи даних з кодуванням UTF-8
def create_fixture(app_name, model_name, file_path):
    os.makedirs(
        os.path.dirname(file_path), exist_ok=True
    )  # Створюємо директорію, якщо її немає
    with codecs.open(file_path, "w", encoding="utf-8") as output:
        call_command(
            "dumpdata", f"{app_name}.{model_name}", indent=2, stdout=output
        )


# Фікстури для категорій
create_fixture("goods", "Categories", "fixtures/goods/cats.json")

# Фікстури для продуктів
create_fixture("goods", "Products", "fixtures/goods/prod.json")

# Фікстури для характеристик продуктів
create_fixture("goods", "ProductAttribute", "fixtures/goods/attributes.json")
