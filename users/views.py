from django.contrib import auth, messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.carts.models import Cart
from users.forms import UserLoginForm, UserRegistrationForm, ProfileForm
from django.db.models import Prefetch
from orders.models import Order, OrderItem
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetView
from django.utils.translation import gettext as _


class UserLoginView(LoginView):
    template_name = "users/login.html"
    form_class = UserLoginForm

    # success_url = reverse_lazy('main:index')

    def get_success_url(self):
        redirect_page = self.request.POST.get("next", None)
        if redirect_page and redirect_page != reverse("logout"):
            return redirect_page
        return reverse_lazy("main:index")

    def form_valid(self, form):
        session_key = self.request.session.session_key

        user = form.get_user()

        if user:
            auth_login(
                self.request,
                user,
                backend="allauth.account.auth_backends.AuthenticationBackend",
            )
            # auth.login(self.request, user)
            if session_key:
                # delete old authorized user carts
                forgot_carts = Cart.objects.filter(user=user)
                if forgot_carts.exists():
                    forgot_carts.delete()
                # add new authorized user carts from anonimous session
                Cart.objects.filter(session_key=session_key).update(user=user)

                messages.success(
                    # self.request,
                    # f"{user.username}, Ви увійшли до облікового запису",
                    self.request,
                    _("%(username)s, Ви увійшли до облікового запису") % {
                        "username": user.username}
                )

                return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Home - Authorization"
        return context


class UserRegistrationView(CreateView):
    template_name = "users/registration.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        session_key = self.request.session.session_key
        user = form.instance

        if user:
            form.save()
            auth_login(
                self.request,
                user,
                backend="allauth.account.auth_backends.AuthenticationBackend",
            )
            # auth.login(self.request, user)

        if session_key:
            Cart.objects.filter(session_key=session_key).update(user=user)

        messages.success(
            self.request,
            # f"{user.username}, Ви успішно зареєстровані та увійшли до облікового запису",
            _("%(username)s, Ви успішно зареєстровані та увійшли до облікового запису") % {
                "username": user.username
            }
        )
        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Home - Registration"
        return context


class UserProfileView(LoginRequiredMixin, UpdateView):
    template_name = "users/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _("Профіль успішно оновлено"))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Сталася помилка"))
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Home - Office"
        context["orders"] = (
            Order.objects.filter(user=self.request.user)
            .prefetch_related(
                Prefetch(
                    "orderitem_set",
                    queryset=OrderItem.objects.select_related("product"),
                )
            )
            .order_by("-id")
        )

        # Можно вынести сам запрос в отдельный метод этого класса контроллера
        # orders = Order.objects.filter(user=self.request.user).prefetch_related(
        #     Prefetch(
        #         "orderitem_set",
        #         queryset=OrderItem.objects.select_related("product"),
        #     )
        # ).order_by("-id")
        #
        # context['orders'] = self.set_get_cache(orders,
        #                                        f"user_{self.request.user.id}_orders",
        #                                        60)

        return context


class UserCartView(TemplateView):
    template_name = "users/users_cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Home - Cart"
        return context


# def login(request):
#     if request.method == "POST":
#         form = UserLoginForm(data=request.POST)
#         if form.is_valid():
#             username = request.POST["username"]
#             password = request.POST["password"]
#
#             user = auth.authenticate(username=username, password=password)
#
#             session_key = request.session.session_key
#
#             if user:
#                 auth.login(request, user)
#                 # if session_key:
#                 #     Cart.objects.filter(session_key=session_key).update(
#                 #         user=user
#                 #     )
#                 # messages.success(
#                 #     request, f"{username}, Ви увійшли до облікового запису"
#                 # )
#                 messages.success(
#                     request, f"{username}, Ви увійшли до облікового запису"
#                 )
#                 if session_key:
#                     forgot_carts = Cart.objects.filter(user=user)
#                     if forgot_carts.exists():
#                         forgot_carts.delete()
#                     Cart.objects.filter(session_key=session_key).update(
#                         user=user)
#
#
#
#
#
#
#
#
#                 redirect_page = request.POST.get("next", None)
#                 if redirect_page and redirect_page != reverse("user:logout"):
#                     return HttpResponseRedirect(request.POST.get("next"))
#
#                 return HttpResponseRedirect(reverse("main:index"))
#     else:
#         form = UserLoginForm()
#
#     context = {"title": "Home - Авторизація", "form": form}
#     return render(request, "users/login.html", context)


# def registration(request):
#     if request.method == "POST":
#         form = UserRegistrationForm(data=request.POST)
#         if form.is_valid():
#             form.save()
#             session_key = request.session.session_key
#
#             user = form.instance
#             auth.login(request, user)
#
#             if session_key:
#                 Cart.objects.filter(session_key=session_key).update(user=user)
#
#             messages.success(
#                 request,
#                 f"{user.username}, Ви успішно зареєстровані та увійшли до облікового запису ",
#             )
#
#             return HttpResponseRedirect(reverse("main:index"))
#     else:
#         form = UserRegistrationForm()
#
#     context = {"title": "Home - Реєстрація", "form": form}
#
#     return render(request, "users/registration.html", context)


# @login_required
# def profile(request):
#     if request.method == "POST":
#         form = ProfileForm(
#             data=request.POST, instance=request.user, files=request.FILES
#         )
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Профіль успішно оновлено")
#             return HttpResponseRedirect(reverse("user:profile"))
#     else:
#         form = ProfileForm(instance=request.user)
#
#
#     orders = Order.objects.filter(user=request.user).prefetch_related(
#                 Prefetch(
#                     "orderitem_set",
#                     queryset=OrderItem.objects.select_related("product"),
#                 )
#             ).order_by("-id")
#
#
#     context = {
#         'title': 'Home - Кабінет',
#         'form': form,
#         'orders': orders,
#     }
#     return render(request, 'users/profile.html', context)
#
#
# def users_cart(request):
#     return render(request, "users/users_cart.html")


@login_required
def logout(request):
    messages.success(
        request, f"{request.user.username},Ви вийшли з облікового запису"
    )

    auth.logout(request)
    return redirect(reverse("main:index"))


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy("login")  # Назва URL, що веде на сторінку входу

    def form_valid(self, form):
        messages.success(self.request, _("Пароль успішно змінено!"))
        return super().form_valid(form)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset')  # на ту ж саму сторінку

    def form_valid(self, form):
        # Відправляє лист, як зазвичай
        response = super().form_valid(form)
        # Додає повідомлення
        messages.success(self.request,
                         _("Перевірте вашу пошту. Ми надіслали інструкції для скидання пароля."))
        # Повертаємо редірект назад на цю ж сторінку (password_reset)
        return redirect('password_reset')
