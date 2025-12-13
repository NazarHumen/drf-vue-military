from django.urls import path, include
from users import views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetConfirmView, CustomPasswordResetView

# app_name = "users"
urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path(
        "registration/",
        views.UserRegistrationView.as_view(),
        name="registration",
    ),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path("users-cart/", views.UserCartView.as_view(), name="users_cart"),
    path("logout/", views.logout, name="logout"),
    path(
        "password_reset/",
        CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    # path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
