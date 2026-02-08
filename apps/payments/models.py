from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.orders.models import Order
from apps.users.models import User


class PaymentStatus(models.TextChoices):
    PENDING = "pending", _("Очікує оплати")
    COMPLETED = "completed", _("Оплачено")
    FAILED = "failed", _("Помилка оплати")
    CANCELED = "canceled", _("Скасовано")


class Payment(models.Model):
    order = models.OneToOneField(
        to=Order,
        on_delete=models.PROTECT,
        related_name="payment",
        verbose_name="Замовлення",
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT,
        verbose_name="Користувач",
    )
    stripe_checkout_session_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Stripe Checkout Session ID",
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Stripe Payment Intent ID",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сума",
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
        verbose_name="Валюта",
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата створення",
    )
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата оплати",
    )

    class Meta:
        db_table = "payment"
        verbose_name = "Платіж"
        verbose_name_plural = "Платежі"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Платіж #{self.pk} для замовлення #{self.order.pk}"
