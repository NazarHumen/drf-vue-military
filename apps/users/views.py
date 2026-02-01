from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.carts.models import Cart
from apps.favorites.utils import merge_favorites_on_login
from apps.orders.models import Order, OrderItem
from apps.users.models import User
from apps.users.serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileSerializer,
    RegistrationSerializer,
    UserOrderSerializer,
    UserSerializer,
)


def is_html_request(request):
    """Перевіряє чи запит очікує HTML відповідь"""
    accept = request.META.get("HTTP_ACCEPT", "")
    content_type = request.content_type or ""
    # Якщо явно запитує JSON - це API запит
    if "application/json" in accept or "application/json" in content_type:
        return False
    # Якщо це браузерний запит (text/html або */*)
    return "text/html" in accept or "*/*" in accept or not accept


@method_decorator(csrf_exempt, name="dispatch")
class LoginAPIView(APIView):
    """Гібридний view для логіну - HTML сторінка + JSON API"""

    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    authentication_classes = []  # Без authentication для login

    def get(self, request):
        """Рендеринг сторінки логіну"""
        if is_html_request(request):
            # Якщо користувач вже авторизований - редірект на профіль
            if request.user.is_authenticated:
                return redirect("users:profile")

            return Response(
                {
                    "title": _("Авторизація"),
                    "request": request,
                },
                template_name="users/login.html",
            )

        return Response(
            {"detail": "Use POST to login"},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            # Для HTML - показуємо сторінку з помилками
            if is_html_request(request):
                return Response(
                    {
                        "title": _("Авторизація"),
                        "request": request,
                        "errors": serializer.errors,
                    },
                    template_name="users/login.html",
                    status=status.HTTP_400_BAD_REQUEST,
                )
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
            # merge favorites from anonymous session
            merge_favorites_on_login(request, user)

        # Django session login
        login(
            request, user, backend="django.contrib.auth.backends.ModelBackend"
        )

        tokens = serializer.get_tokens(user)

        # Для HTML - редірект
        if is_html_request(request):
            next_url = request.GET.get("next", "/api/v1/users/profile/")
            return redirect(next_url)

        return Response(
            {
                "message": _("%(username)s, Ви увійшли до облікового запису")
                % {"username": user.username},
                "user": UserSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class RegistrationAPIView(APIView):
    """Гібридний view для реєстрації - HTML сторінка + JSON API"""

    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    authentication_classes = []  # Без authentication для registration

    def get(self, request):
        """Рендеринг сторінки реєстрації"""
        if is_html_request(request):
            # Якщо користувач вже авторизований - редірект на профіль
            if request.user.is_authenticated:
                return redirect("users:profile")

            return Response(
                {
                    "title": _("Реєстрація"),
                    "request": request,
                },
                template_name="users/registration.html",
            )

        return Response(
            {"detail": "Use POST to register"},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            # Для HTML - показуємо сторінку з помилками
            if is_html_request(request):
                return Response(
                    {
                        "title": _("Реєстрація"),
                        "request": request,
                        "errors": serializer.errors,
                    },
                    template_name="users/registration.html",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()
        session_key = request.session.session_key

        if session_key:
            Cart.objects.filter(session_key=session_key).update(user=user)
            # merge favorites from anonymous session
            merge_favorites_on_login(request, user)

        # Django session login
        login(
            request, user, backend="django.contrib.auth.backends.ModelBackend"
        )

        tokens = serializer.get_tokens(user)

        # Для HTML - редірект
        if is_html_request(request):
            return redirect("users:profile")

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
    """Гібридний view для профілю - HTML сторінка + JSON API"""

    permission_classes = [AllowAny]  # Перевіряємо вручну для кращого UX
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        # Перевірка авторизації з редіректом для HTML
        if not request.user.is_authenticated:
            if is_html_request(request):
                return redirect(f"/api/v1/users/login/?next={request.path}")
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

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

        # HTML рендеринг
        if is_html_request(request):
            return Response(
                {
                    "title": _("Профіль користувача"),
                    "request": request,
                    "user": request.user,
                    "orders": orders,
                },
                template_name="users/profile.html",
            )

        # JSON API
        return Response(
            {
                "user": serializer.data,
                "orders": orders_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        # Перевірка авторизації
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

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
    """Гібридний view для виходу - підтримує і API і редірект"""

    permission_classes = [AllowAny]  # Дозволяємо всім, logout безпечний
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get(self, request):
        """GET запит для виходу (для посилань в навігації)"""
        # Django session logout (якщо авторизований)
        if request.user.is_authenticated:
            from django.contrib import messages

            messages.success(request, _("Ви вийшли з облікового запису"))
            logout(request)

        # Завжди редірект на головну для GET
        return redirect("main:index")

    def post(self, request):
        """POST запит для API виходу"""
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass

        # Django session logout (якщо авторизований)
        if request.user.is_authenticated:
            logout(request)

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
    """Гібридний view для запиту скидання пароля - HTML сторінка + JSON API"""

    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get(self, request):
        """Рендеринг сторінки скидання пароля"""
        if is_html_request(request):
            return Response(
                {
                    "title": _("Скидання пароля"),
                    "request": request,
                },
                template_name="registration/password_reset_form.html",
            )

        return Response(
            {"detail": "Use POST to request password reset"},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)

        if not serializer.is_valid():
            if is_html_request(request):
                return Response(
                    {
                        "title": _("Скидання пароля"),
                        "request": request,
                        "errors": serializer.errors,
                    },
                    template_name="registration/password_reset_form.html",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)

        # Generate token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build context for email
        protocol = "https" if request.is_secure() else "http"
        domain = request.get_host()

        # Send email
        subject = _("Скидання пароля")
        message = render_to_string(
            "registration/password_reset_email.html",
            {
                "user": user,
                "uid": uid,
                "token": token,
                "protocol": protocol,
                "domain": domain,
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
            if is_html_request(request):
                return Response(
                    {
                        "title": _("Скидання пароля"),
                        "request": request,
                        "errors": {"email": [_("Помилка відправки email")]},
                    },
                    template_name="registration/password_reset_form.html",
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            return Response(
                {"error": _("Помилка відправки email")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Для HTML - редірект на сторінку успіху
        if is_html_request(request):
            return redirect("users:password_reset_done")

        return Response(
            {
                "message": _(
                    "Перевірте вашу пошту. "
                    "Ми надіслали інструкції для скидання пароля."
                )
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetDoneView(APIView):
    """View для сторінки успішного запиту скидання пароля"""

    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get(self, request):
        if is_html_request(request):
            return Response(
                {
                    "title": _("Скидання пароля"),
                    "request": request,
                },
                template_name="registration/password_reset_done.html",
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
    """Гібридний view для підтвердження скидання пароля - HTML + JSON API"""

    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get(self, request, uidb64=None, token=None):
        """Рендеринг форми для введення нового пароля"""
        if is_html_request(request):
            # Перевіряємо валідність токена
            valid_link = False
            if uidb64 and token:
                try:
                    uid = force_str(urlsafe_base64_decode(uidb64))
                    user = User.objects.get(pk=uid)
                    valid_link = default_token_generator.check_token(
                        user, token
                    )
                except (
                    TypeError,
                    ValueError,
                    OverflowError,
                    User.DoesNotExist,
                ):
                    valid_link = False

            return Response(
                {
                    "title": _("Новий пароль"),
                    "request": request,
                    "uidb64": uidb64,
                    "token": token,
                    "valid_link": valid_link,
                },
                template_name="registration/password_reset_confirm.html",
            )

        return Response(
            {"detail": "Use POST to confirm password reset"},
            status=status.HTTP_200_OK,
        )

    def post(self, request, uidb64=None, token=None):
        # Отримуємо uidb64 і token з URL або з request.data
        uidb64 = uidb64 or request.data.get("uidb64")
        token = token or request.data.get("token")

        # Додаємо до data для серіалізатора
        data = (
            request.data.copy()
            if hasattr(request.data, "copy")
            else dict(request.data)
        )
        if uidb64:
            data["uidb64"] = uidb64
        if token:
            data["token"] = token

        serializer = PasswordResetConfirmSerializer(data=data)

        if not serializer.is_valid():
            if is_html_request(request):
                return Response(
                    {
                        "title": _("Новий пароль"),
                        "request": request,
                        "uidb64": uidb64,
                        "token": token,
                        "valid_link": True,
                        "errors": serializer.errors,
                    },
                    template_name="registration/password_reset_confirm.html",
                    status=status.HTTP_400_BAD_REQUEST,
                )
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
            if is_html_request(request):
                return Response(
                    {
                        "title": _("Новий пароль"),
                        "request": request,
                        "valid_link": False,
                    },
                    template_name="registration/password_reset_confirm.html",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"error": _("Невірне посилання для скидання пароля")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            if is_html_request(request):
                return Response(
                    {
                        "title": _("Новий пароль"),
                        "request": request,
                        "valid_link": False,
                    },
                    template_name="registration/password_reset_confirm.html",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"error": _("Токен недійсний або прострочений")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        # Для HTML - редірект на сторінку успіху
        if is_html_request(request):
            return redirect("users:password_reset_complete")

        return Response(
            {"message": _("Пароль успішно змінено")},
            status=status.HTTP_200_OK,
        )


class PasswordResetCompleteView(APIView):
    """View для сторінки успішної зміни пароля"""

    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get(self, request):
        if is_html_request(request):
            return Response(
                {
                    "title": _("Пароль змінено"),
                    "request": request,
                },
                template_name="registration/password_reset_complete.html",
            )

        return Response(
            {"message": _("Пароль успішно змінено")},
            status=status.HTTP_200_OK,
        )


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCartView(APIView):
    """View для сторінки кошика користувача"""

    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get(self, request):
        if not request.user.is_authenticated:
            if is_html_request(request):
                return redirect(f"/api/v1/users/login/?next={request.path}")
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if is_html_request(request):
            return Response(
                {
                    "title": _("Кошик"),
                    "request": request,
                },
                template_name="users/user_cart.html",
            )

        return Response(
            {"detail": "Use cart API for JSON data"},
            status=status.HTTP_200_OK,
        )


class UserOrdersView(APIView):
    """View для сторінки замовлень користувача"""

    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get(self, request):
        if not request.user.is_authenticated:
            if is_html_request(request):
                return redirect(f"/api/v1/users/login/?next={request.path}")
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if is_html_request(request):
            return Response(
                {
                    "title": _("Мої замовлення"),
                    "request": request,
                },
                template_name="users/user_orders.html",
            )

        # JSON - redirect to profile API
        user = request.user
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
            {"orders": orders_serializer.data},
            status=status.HTTP_200_OK,
        )
