from rest_framework import serializers

from main.models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["last_name", "first_name", "phone", "email", "comment"]
