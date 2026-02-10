from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from main.serializers import FeedbackSerializer


# Create your views here.
class IndexView(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Home - Головна")
        return context


class AboutView(TemplateView):
    template_name = "main/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Home - Про нас")
        return context


class DeliveryAndPaymentView(TemplateView):
    template_name = "main/delivery.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Home - Доставка та оплата")
        return context


class ContactView(TemplateView):
    template_name = "main/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Home - Зв'яжіться з нами")
        return context


class FeedbackCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": _("Дякуємо за ваш відгук!")},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
