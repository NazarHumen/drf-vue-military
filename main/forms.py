from django import forms
from .models import Feedback
import re

# class FeedbackForm(forms.ModelForm):
#     class Meta:
#         model = Feedback
#         fields = ["last_name", "first_name", "phone", "email", "comment"]
#         widgets = {
#             "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введіть ваше прізвище"}),
#             "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введіть ваше ім'я"}),
#             "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "(000) 000-0000"}),
#             "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Введіть ваш email"}),
#             "comment": forms.Textarea(attrs={"class": "form-control", "placeholder": "Введіть ваш коментар", "rows": 4}),
#         }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ("last_name", "first_name", "phone", "email", "comment")



    first_name = forms.CharField()
    last_name = forms.CharField()
    phone = forms.CharField()
    email = forms.CharField()
    comment = forms.CharField()
