from django import forms

from .models import Order


class CustomerDataForm(forms.Form):
    full_name = forms.CharField(label="Ф. И. О.", max_length=255)
    email = forms.EmailField(label="Email")
    phone = forms.CharField(label="Телефон", max_length=30)
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
        required=False,
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput,
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p1 != p2:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data


class DeliveryForm(forms.Form):
    delivery_type = forms.ChoiceField(
        label="Способ доставки",
        choices=Order.DeliveryType.choices,
    )
    city = forms.CharField(label="Город", max_length=150)
    address = forms.CharField(label="Адрес", max_length=500)


class PaymentMethodForm(forms.Form):
    payment_type = forms.ChoiceField(
        label="Способ оплаты",
        choices=Order.PaymentType.choices,
    )


class PaymentForm(forms.Form):
    number = forms.CharField(
        label="Номер",
        max_length=8,
        widget=forms.TextInput(
            attrs={"pattern": "[0-9]+", "inputmode": "numeric"},
        ),
    )

    def clean_number(self):
        number = self.cleaned_data["number"]
        if not number.isdigit():
            raise forms.ValidationError(
                "Номер должен содержать только цифры.",
            )
        if len(number) > 8:
            raise forms.ValidationError(
                "Номер не должен быть длиннее 8 цифр.",
            )
        if int(number) % 2 != 0:
            raise forms.ValidationError("Номер должен быть чётным.")
        return number
