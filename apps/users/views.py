from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.carts.models import Cart
from apps.orders.models import Order, OrderItem
from apps.users.models import User
from apps.users.serializers import (
    LoginSerializer,
    RegistrationSerializer,
    ProfileSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserSerializer,
    UserOrderSerializer,
)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.validated_data["user"]
        session_key = request.session.session_key

        if session_key:
            # delete old authorized user carts
            forgot_carts = Cart.objects.filter(user=user)
            if forgot_carts.exists():
                forgot_carts.delete()
            # add new authorized user carts from anonymous session
            Cart.objects.filter(session_key=session_key).update(user=user)

        tokens = serializer.get_tokens(user)

        return Response(
            {
                "message": _("%(username)s, Ви увійшли до облікового запису")
                % {"username": user.username},
                "user": UserSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()
        session_key = request.session.session_key

        if session_key:
            Cart.objects.filter(session_key=session_key).update(user=user)

        tokens = serializer.get_tokens(user)

        return Response(
            {
                "message": _(
                    "%(username)s, Ви успішно зареєстровані "
                    "та увійшли до облікового запису"
                )
                % {"username": user.username},
                "user": UserSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = ProfileSerializer(user)

        orders = (
            Order.objects.filter(user=user)
            .prefetch_related(
                Prefetch(
                    "orderitem_set",
                    queryset=OrderItem.objects.select_related("product"),
                )
            )
            .order_by("-id")
        )

        orders_serializer = UserOrderSerializer(orders, many=True)

        return Response(
            {
                "user": serializer.data,
                "orders": orders_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        return Response(
            {
                "message": _("Профіль успішно оновлено"),
                "user": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass

        return Response(
            {"message": _("Ви вийшли з облікового запису")},
            status=status.HTTP_200_OK,
        )


class PasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        return Response(
            {"message": _("Пароль успішно змінено")},
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)

        # Generate token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build reset URL (frontend should handle this)
        reset_url = f"{request.build_absolute_uri('/api/v1/users/password-reset-confirm/')}"

        # Send email
        subject = _("Скидання пароля")
        message = render_to_string(
            "registration/password_reset_email.html",
            {
                "user": user,
                "uid": uid,
                "token": token,
                "reset_url": reset_url,
            },
        )

        try:
            send_mail(
                subject,
                message,
                None,  # From email (uses DEFAULT_FROM_EMAIL)
                [email],
                fail_silently=False,
            )
        except Exception:
            return Response(
                {"error": _("Помилка відправки email")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "message": _(
                    "Перевірте вашу пошту. "
                    "Ми надіслали інструкції для скидання пароля."
                )
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        uidb64 = serializer.validated_data["uidb64"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password1"]

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": _("Невірне посилання для скидання пароля")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": _("Токен недійсний або прострочений")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": _("Пароль успішно змінено")},
            status=status.HTTP_200_OK,
        )


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
