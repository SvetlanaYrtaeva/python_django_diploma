from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Product

from .forms import ReviewForm
from .models import Review


def _serialize_reviews(product):
    reviews = (
        Review.objects
        .filter(product=product, is_deleted=False)
        .select_related("user")
    )
    return [
        {
            "id": r.id,
            "author": r.user.get_full_name() or r.user.username,
            "email": r.user.email,
            "text": r.text,
            "rate": r.rating,
            "created_at": r.created_at.isoformat(),
        }
        for r in reviews
    ]


@api_view(["GET", "POST"])
def review_api_view(request: Request, product_id: int) -> Response:
    product = get_object_or_404(
        Product.objects.active(), pk=product_id, is_active=True
    )

    if request.method == "GET":
        return Response(_serialize_reviews(product))

    # POST — создание отзыва
    if not request.user.is_authenticated:
        return Response(
            {"error": "Необходимо авторизоваться"},
            status=401,
        )

    data = request.data
    text = data.get("text", "")
    rate = data.get("rate", 5)

    try:
        rate = int(rate)
    except (TypeError, ValueError):
        rate = 5
    if rate < 1:
        rate = 1
    if rate > 5:
        rate = 5

    Review.objects.create(
        product=product,
        user=request.user,
        text=text,
        rating=rate,
    )

    return Response(_serialize_reviews(product))


def product_reviews_api_view(request, product_id):
    if request.method != "GET":
        return JsonResponse(
            {"detail": "Метод не поддерживается."}, status=405
        )

    product = get_object_or_404(
        Product.objects.active(), pk=product_id, is_active=True
    )

    return JsonResponse(
        _serialize_reviews(product),
        safe=False,
        json_dumps_params={"ensure_ascii": False},
    )


@login_required
def review_create_view(request, slug):
    product = get_object_or_404(
        Product.objects.active(), slug=slug, is_active=True
    )

    if request.method != "POST":
        return redirect("catalog:product", slug=slug)

    form = ReviewForm(request.POST)

    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()

    return redirect("catalog:product", slug=slug)
