from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import (
    LoginForm,
    ProfileForm,
    RegistrationForm,
)


@ensure_csrf_cookie
def register_view(request):
    if request.user.is_authenticated:
        return redirect("catalog:index")

    if request.method == "POST":
        form = RegistrationForm(
            request.POST,
        )

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                "Регистрация выполнена.",
            )

            return redirect("catalog:index")
    else:
        form = RegistrationForm()

    return render(
        request,
        "frontend/signUp.html",
        {
            "form": form,
        },
    )


@method_decorator(
    ensure_csrf_cookie,
    name="dispatch",
)
class UserLoginView(LoginView):
    template_name = "frontend/signIn.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


def logout_view(request):
    logout(request)
    return redirect("catalog:index")


@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Профиль изменён.",
            )

            return redirect("users:profile")
    else:
        form = ProfileForm(
            instance=request.user,
        )

    return render(
        request,
        "frontend/profile.html",
        {
            "form": form,
        },
    )