from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from orders.models import Order

from .forms import ProfileForm

User = get_user_model()

@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return render(
                request,
                "frontend/profile.html",
                {"form": form, "success": True},
            )
    else:
        form = ProfileForm(instance=request.user)

    user_orders = Order.objects.filter(user=request.user).order_by("-created_at")

    return render(
        request,
        "frontend/profile.html",
        {"form": form, "user_orders": user_orders},
    )
