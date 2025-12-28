from django.db import models
from django.conf import (
    settings,
)  # Використовується для доступу до AUTH_USER_MODEL
from apps.goods.models import (
    Products,
)  # Припускаємо, що ваша модель товарів називається Products


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Використовується динамічне посилання на модель користувача
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "user",
            "product",
        )  # Один і той самий товар не можна додати двічі.
        verbose_name = "Обраний товар"
        verbose_name_plural = "Обрані товари"

    def __str__(self):
        return f"{self.user} - {self.product}"
