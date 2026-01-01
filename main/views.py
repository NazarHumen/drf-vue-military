from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView
from django.http import JsonResponse
from apps.goods.models import Categories
from main.models import Feedback
from main.forms import FeedbackForm
from django.urls import reverse
from django.utils.translation import gettext as _


# Create your views here.
class IndexView(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Home - Головна")
        # context['content'] = "Магазин військового спорядження"
        return context


class AboutView(TemplateView):
    template_name = "main/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Home - Про нас")
        # context['content'] = "Про нас"
        # context['text_on_page'] = "Ми спеціалізуємося на продажу військового спорядження, включаючи одяг, рюкзаки, обладнання для тактичних операцій та інші необхідні аксесуари. У нас ви знайдете все, що потрібно для активного відпочинку, туризму або служби."
        return context


class DeliveryAndPaymentView(TemplateView):
    template_name = "main/delivery.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Home - Доставка та оплата")
        return context





def contact(request):
    if request.method == "POST":
        # Якщо користувач не авторизований
        if not request.user.is_authenticated:
            # Зберігаємо дані форми в сесію
            request.session["form_data"] = request.POST
            messages.error(
                request,
                _("Ви повинні увійти в систему, щоб надіслати відгук.")
            )
            # Додаємо параметр next для перенаправлення після авторизації
            login_url = f"/user/login/?next={reverse('main:contact')}"
            return redirect(login_url)

        # Якщо користувач авторизований, обробляємо форму
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()  # Зберігаємо дані в базу
            messages.success(
                request,
                _("Дякуємо за ваш відгук! Ваше повідомлення було успішно надіслано."),
            )
            return redirect("main:contact")  # Перенаправлення після успіху

    else:
        # Якщо у сесії є дані форми, попередньо заповнюємо її
        form_data = request.session.pop("form_data", None)
        if form_data:
            form = FeedbackForm(form_data)
        else:
            form = FeedbackForm()
    context = {
        "form": form,
        "title": _("Home - Зв'яжіться з нами"),
    }

    return render(request, "main/contact.html",  context)

# def index(request):
#
#     context = {
#         "title": "Home - Головна",
#         "content": "Магазин військового спорядження",
#     }
#
#     return render(request, "main/index.html", context)


# def about(request):
#     context = {
#         "title": "Home - Про нас",
#         "content": "Про нас ",
#         "text_on_page": "Ми спеціалізуємося на "
#         "продажу військового спорядження, включаючи одяг, рюкзаки, обладнання для тактичних операцій та "
#         "інші необхідні аксесуари. У нас ви знайдете все, що потрібно для активного відпочинку, туризму або служби.",
#     }
#     return render(request, "main/about.html", context)
