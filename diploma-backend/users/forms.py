from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)

from .models import User


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)

        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"].lower()

        if commit:
            user.save()

        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
    )

    def clean_username(self):
        return self.cleaned_data["username"].lower()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "avatar",
        )

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")

        if avatar and avatar.size > 2 * 1024 * 1024:
            raise forms.ValidationError(
                "Размер аватарки не должен превышать 2 Мб.",
            )

        return avatar