import stripe
from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.payments.models import Payment, PaymentStatus
from apps.payments.serializers import (
    CreateCheckoutSessionSerializer,
    PaymentSerializer,
)

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateCheckoutSessionSerializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order_id = serializer.validated_data["order_id"]
        order = Order.objects.get(id=order_id, user=request.user)

        line_items = []
        for item in order.orderitem_set.all():
            price_usd = item.products_price_usd()
            if price_usd is None:
                return Response(
                    {"error": _("Помилка конвертації ціни товару")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            unit_amount = int(price_usd / item.quantity * 100)
            line_items.append(
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": item.name,
                        },
                        "unit_amount": unit_amount,
                    },
                    "quantity": item.quantity,
                }
            )

        total_usd = sum(
            item.products_price_usd() or 0
            for item in order.orderitem_set.all()
        )

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=request.build_absolute_uri(
                    "/api/v1/payments/success/"
                )
                + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=request.build_absolute_uri(
                    f"/api/v1/payments/cancel/?order_id={order.id}"
                ),
                client_reference_id=str(order.id),
                customer_email=order.email or request.user.email,
                metadata={
                    "order_id": order.id,
                    "user_id": request.user.id,
                },
            )

            Payment.objects.create(
                order=order,
                user=request.user,
                stripe_checkout_session_id=checkout_session.id,
                amount=total_usd,
                currency="USD",
                status=PaymentStatus.PENDING,
            )

            return Response(
                {
                    "checkout_url": checkout_session.url,
                    "session_id": checkout_session.id,
                },
                status=status.HTTP_201_CREATED,
            )

        except stripe.error.StripeError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PaymentSuccessAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    permission_classes = [AllowAny]

    def get(self, request):
        session_id = request.query_params.get("session_id")

        if not session_id:
            if request.accepted_renderer.format == "html":
                return Response(
                    {"error": _("Невірний запит")},
                    template_name="payments/error.html",
                )
            return Response(
                {"error": _("Невірний запит")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = Payment.objects.get(
                stripe_checkout_session_id=session_id
            )
        except Payment.DoesNotExist:
            if request.accepted_renderer.format == "html":
                return Response(
                    {"error": _("Платіж не знайдено")},
                    template_name="payments/error.html",
                )
            return Response(
                {"error": _("Платіж не знайдено")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if payment.status == PaymentStatus.PENDING:
            try:
                session = stripe.checkout.Session.retrieve(session_id)
                if session.payment_status == "paid":
                    payment.status = PaymentStatus.COMPLETED
                    payment.stripe_payment_intent_id = session.payment_intent
                    payment.paid_at = timezone.now()
                    payment.save()
                    payment.order.is_paid = True
                    payment.order.save()
                    try:
                        from apps.orders.utils import send_receipt_email

                        send_receipt_email(payment.order)
                    except Exception:
                        pass
            except stripe.error.StripeError:
                pass

        if request.accepted_renderer.format == "html":
            return Response(
                {
                    "title": _("Оплата успішна"),
                    "payment": payment,
                    "order": payment.order,
                },
                template_name="payments/success.html",
            )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_200_OK,
        )


class PaymentCancelAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    permission_classes = [AllowAny]

    def get(self, request):
        order_id = request.query_params.get("order_id")

        if request.accepted_renderer.format == "html":
            return Response(
                {
                    "title": _("Оплату скасовано"),
                    "order_id": order_id,
                },
                template_name="payments/cancel.html",
            )

        return Response(
            {"message": _("Оплату скасовано"), "order_id": order_id},
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        if not sig_header:
            return Response(
                {"error": "Missing signature"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET,
            )
        except ValueError:
            return Response(
                {"error": "Invalid payload"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except stripe.error.SignatureVerificationError:
            return Response(
                {"error": "Invalid signature"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            self._handle_checkout_completed(session)
        elif event["type"] == "checkout.session.expired":
            session = event["data"]["object"]
            self._handle_checkout_expired(session)

        return Response({"status": "success"}, status=status.HTTP_200_OK)

    def _handle_checkout_completed(self, session):
        try:
            payment = Payment.objects.get(
                stripe_checkout_session_id=session["id"]
            )
            payment.status = PaymentStatus.COMPLETED
            payment.stripe_payment_intent_id = session.get("payment_intent")
            payment.paid_at = timezone.now()
            payment.save()

            payment.order.is_paid = True
            payment.order.save()
            try:
                from apps.orders.utils import send_receipt_email

                send_receipt_email(payment.order)
            except Exception:
                pass
        except Payment.DoesNotExist:
            pass

    def _handle_checkout_expired(self, session):
        try:
            payment = Payment.objects.get(
                stripe_checkout_session_id=session["id"]
            )
            payment.status = PaymentStatus.CANCELED
            payment.save()
        except Payment.DoesNotExist:
            pass


class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            payment = Payment.objects.get(order_id=order_id, user=request.user)
        except Payment.DoesNotExist:
            return Response(
                {"error": _("Платіж не знайдено")},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_200_OK,
        )
