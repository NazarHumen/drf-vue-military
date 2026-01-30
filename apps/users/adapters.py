from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


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


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter for social account login"""

    pass
