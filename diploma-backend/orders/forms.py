from django import forms

from .models import Order


class CustomerDataForm(forms.Form):
    full_name = forms.CharField(
        label="Ф. И. О.",
        max_length=255,
    )

    email = forms.EmailField(
        label="Email",
    )

    phone = forms.CharField(
        label="Телефон",
        max_length=30,
    )

    password1 = forms.CharField(
        label="Пароль",
        required=False,
        widget=forms.PasswordInput,
    )

    password2 = forms.CharField(
        label="Подтверждение пароля",
        required=False,
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get(
            "password1",
        )

        password2 = cleaned_data.get(
            "password2",
        )

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError(
                    "Пароли не совпадают.",
                )

            if len(password1) < 6:
                raise forms.ValidationError(
                    "Пароль должен содержать "
                    "минимум 6 символов.",
                )

        return cleaned_data


class DeliveryForm(forms.Form):
    delivery_type = forms.ChoiceField(
        label="Способ доставки",
        choices=Order.DeliveryType.choices,
        widget=forms.RadioSelect,
    )

    city = forms.CharField(
        label="Город",
        max_length=150,
    )

    address = forms.CharField(
        label="Адрес",
        max_length=500,
    )


class PaymentMethodForm(forms.Form):
    payment_type = forms.ChoiceField(
        label="Способ оплаты",
        choices=Order.PaymentType.choices,
        widget=forms.RadioSelect,
    )


class PaymentForm(forms.Form):
    number = forms.CharField(
        label="Номер карты или счёта",
        max_length=8,
        widget=forms.TextInput(
            attrs={
                "inputmode": "numeric",
                "maxlength": "8",
            },
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
            raise forms.ValidationError(
                "Номер должен быть чётным.",
            )

        return number