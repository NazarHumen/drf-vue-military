from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users import views

app_name = "users"

urlpatterns = [
    # Authentication
    path("login/", views.LoginAPIView.as_view(), name="login"),
    path(
        "registration/",
        views.RegistrationAPIView.as_view(),
        name="registration",
    ),
    path("logout/", views.LogoutAPIView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Profile
    path("profile/", views.ProfileAPIView.as_view(), name="profile"),
    path("cart/", views.UserCartView.as_view(), name="user_cart"),
    path("favorites/", views.UserFavoritesView.as_view(), name="user_favorites"),
    path("orders/", views.UserOrdersView.as_view(), name="user_orders"),
    path("me/", views.CurrentUserAPIView.as_view(), name="current_user"),
    # Password management
    path(
        "password-change/",
        views.PasswordChangeAPIView.as_view(),
        name="password_change",
    ),
    path(
        "password-reset/",
        views.PasswordResetRequestAPIView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/",
        views.PasswordResetConfirmAPIView.as_view(),
        name="password_reset_confirm_api",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.PasswordResetConfirmAPIView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
