from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileForm(forms.ModelForm):
    password = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput,
        required=False,
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "avatar"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if (
            User.objects
            .filter(email=email)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError(
                "Пользователь с таким email уже существует",
            )
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and (
            User.objects
            .filter(phone=phone)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError(
                "Пользователь с таким телефоном уже существует",
            )
        return phone

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar and hasattr(avatar, "size"):
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError(
                    "Размер изображения не должен превышать 2 Мб",
                )
        return avatar

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
