from django import forms
import re

class CreateOrderForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    phone_number = forms.CharField()
    email = forms.EmailField()
    requires_delivery = forms.ChoiceField(
        choices=[("0", "False"), ("1", "True")],
    )
    delivery_address = forms.CharField(required=False)
    payment_on_get = forms.ChoiceField(
        choices=[("0", "False"), ("1", "True")],
    )

    def clean_phone_number(self):
        data = self.cleaned_data["phone_number"]

        # Дозволяємо + на початку, потім цифри
        pattern = re.compile(r'^\+?\d{10,15}$')

        if not pattern.match(data):
            raise forms.ValidationError(
                "Невірний формат номера. Приклад: +380931234567 або +46701234567"
            )
        return data

# class CreateOrderForm(forms.Form):
#     first_name = forms.CharField()
#     last_name = forms.CharField()
#     phone_number = forms.CharField()
#     requires_delivery = forms.ChoiceField(
#         choices=[
#             ("0", "False"),
#             ("1", "True"),
#         ],
#     )
#     delivery_address = forms.CharField(required=False)
#     payment_on_get = forms.ChoiceField(
#         choices=[
#             ("0", "False"),
#             ("1", "True"),
#         ],
#     )
#
#     def clean_phone_number(self):
#         data = self.cleaned_data["phone_number"]
#
#         if not data.isdigit():
#             raise forms.ValidationError(
#                 "Номер телефону повинен містити лише цифри"
#             )
#
#         pattern = re.compile(r"^\d{10}$")
#         if not pattern.match(data):
#             raise forms.ValidationError("Невірний формат номера")
#
#         return data

    # requires_delivery = forms.ChoiceField(
    #     choices=[
    #         ("0", False),
    #         ("1", True),
    #     ],
    # )
    # delivery_address = forms.CharField(required=False)
    # payment_on_get = forms.ChoiceField(
    #     choices=[
    #         ("0", 'False'),
    #         ("1", 'True'),
    #     ],
    # )
    #
    # def clean_phone_number(self):
    #     data = self.cleaned_data['phone_number']
    #
    #     if not data.isdigit():
    #         raise forms.ValidationError(
    #             "Номер телефона должен содержать только цифры")
    #
    #     pattern = re.compile(r'^\d{10}$')
    #     if not pattern.match(data):
    #         raise forms.ValidationError("Неверный формат номера")
    #
    #     return data
