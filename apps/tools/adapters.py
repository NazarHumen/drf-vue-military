from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from apps.carts.models import Cart
from apps.favorites.utils import merge_favorites_on_login


def merge_session_data_on_login(request, user):
    """Об'єднує кошик та обране з сесії після логіну."""
    session_key = request.session.session_key
    if not session_key:
        return

    # Merge cart
    forgot_carts = Cart.objects.filter(user=user)
    if forgot_carts.exists():
        forgot_carts.delete()
    Cart.objects.filter(session_key=session_key).update(user=user)

    # Merge favorites
    merge_favorites_on_login(request, user)


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom adapter for regular account login"""

    def add_message(
        self,
        request,
        level,
        message_template,
        message_context=None,
        extra_tags="",
    ):
        """Override to customize login/logout messages"""
        # Replace default login message with our custom one
        if message_template == "account/messages/logged_in.txt":
            user = request.user
            messages.success(
                request,
                _("%(username)s, Ви увійшли до облікового запису")
                % {"username": user.username},
            )
            return
        # Replace default logout message
        if message_template == "account/messages/logged_out.txt":
            messages.success(request, _("Ви вийшли з облікового запису"))
            return
        # For all other messages, use default behavior
        super().add_message(
            request, level, message_template, message_context, extra_tags
        )

    def login(self, request, user):
        """Override login to merge cart and favorites from session."""
        merge_session_data_on_login(request, user)
        return super().login(request, user)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter for social account login"""

    def pre_social_login(self, request, sociallogin):
        """Merge cart and favorites before social login completes."""
        user = sociallogin.user
        if user.pk:
            merge_session_data_on_login(request, user)
        return super().pre_social_login(request, sociallogin)
