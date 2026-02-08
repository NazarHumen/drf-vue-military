from django.contrib import admin

from apps.payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "order",
        "user",
        "amount",
        "currency",
        "status",
        "created_at",
        "paid_at",
    ]
    list_filter = ["status", "currency", "created_at"]
    search_fields = [
        "stripe_checkout_session_id",
        "stripe_payment_intent_id",
        "order__id",
        "user__email",
    ]
    readonly_fields = [
        "stripe_checkout_session_id",
        "stripe_payment_intent_id",
        "created_at",
    ]
    raw_id_fields = ["order", "user"]
