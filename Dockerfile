FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc pkg-config libcairo2-dev gettext \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


RUN python manage.py compilemessages

EXPOSE 8000

CMD ["gunicorn", "--workers", "2", "--timeout", "60", "--bind", "0.0.0.0:8000", "dev_env.wsgi:application"]
