from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileForm

User = get_user_model()


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect("sign_in_page")

    if request.method == "POST":
        form = ProfileForm(
            request.POST, request.FILES, instance=request.user
        )
        if form.is_valid():
            form.save()
            return render(
                request,
                "frontend/profile.html",
                {"form": form, "success": True},
            )
    else:
        form = ProfileForm(instance=request.user)

    return render(
        request,
        "frontend/profile.html",
        {"form": form},
    )
