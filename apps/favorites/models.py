from django.conf import settings
from django.db import models

from apps.goods.models import Products


class FavoriteQueryset(models.QuerySet):
    def total_count(self):
        return self.count()


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        blank=True,
        null=True,
    )
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE, related_name="favorited_by"
    )
    session_key = models.CharField(max_length=32, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "favorite"
        verbose_name = "Обраний товар"
        verbose_name_plural = "Обрані товари"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                condition=models.Q(user__isnull=False),
                name="unique_user_product",
            ),
            models.UniqueConstraint(
                fields=["session_key", "product"],
                condition=models.Q(session_key__isnull=False),
                name="unique_session_product",
            ),
        ]

    objects = FavoriteQueryset().as_manager()

    def __str__(self):
        user_info = self.user.username if self.user else "Anonymous"
        return f"{user_info} - {self.product}"
