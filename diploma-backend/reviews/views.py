from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect

from catalog.models import Product

from .forms import ReviewForm
from .models import Review


def product_reviews_api_view(request, product_id):
    if request.method != "GET":
        return JsonResponse(
            {
                "detail": "Метод не поддерживается.",
            },
            status=405,
        )

    product = get_object_or_404(
        Product.objects.active(),
        pk=product_id,
        is_active=True,
    )

    reviews = (
        Review.objects
        .filter(
            product=product,
            is_deleted=False,
        )
        .select_related("user")
    )

    data = [
        {
            "id": review.id,
            "user": (
                review.user.get_full_name()
                or review.user.username
            ),
            "text": review.text,
            "rating": review.rating,
            "created_at": (
                review.created_at.isoformat()
            ),
        }
        for review in reviews
    ]

    return JsonResponse(
        data,
        safe=False,
        json_dumps_params={
            "ensure_ascii": False,
        },
    )


@login_required
def review_create_view(request, slug):
    product = get_object_or_404(
        Product.objects.active(),
        slug=slug,
        is_active=True,
    )

    if request.method != "POST":
        return redirect(
            "catalog:product",
            slug=slug,
        )

    form = ReviewForm(request.POST)

    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()

        messages.success(
            request,
            "Отзыв успешно добавлен.",
        )

    return redirect(
        "catalog:product",
        slug=slug,
    )