from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "created_at")
    ordering = ["-created_at"]
