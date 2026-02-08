from django.urls import path

from apps.payments import views

app_name = "payments"

urlpatterns = [
    path(
        "checkout/",
        views.CreateCheckoutSessionAPIView.as_view(),
        name="checkout",
    ),
    path(
        "success/",
        views.PaymentSuccessAPIView.as_view(),
        name="success",
    ),
    path(
        "cancel/",
        views.PaymentCancelAPIView.as_view(),
        name="cancel",
    ),
    path(
        "webhook/",
        views.StripeWebhookAPIView.as_view(),
        name="webhook",
    ),
    path(
        "status/<int:order_id>/",
        views.PaymentStatusAPIView.as_view(),
        name="status",
    ),
]
