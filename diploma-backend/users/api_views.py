import json

from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.http import JsonResponse


User = get_user_model()


def get_request_data(request):
    content_type = request.headers.get(
        "Content-Type",
        "",
    ).lower()

    if "application/json" in content_type:
        try:
            data = json.loads(
                request.body.decode("utf-8"),
            )

            if isinstance(data, dict):
                return data

        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
        ):
            return {}

    if request.POST:
        return request.POST

    return {}


def sign_in_api_view(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "detail": "Метод не поддерживается.",
            },
            status=405,
        )

    data = get_request_data(request)

    username = str(
        data.get("username", ""),
    ).strip()

    password = str(
        data.get("password", ""),
    )

    if not username or not password:
        return JsonResponse(
            {
                "detail": (
                    "Имя пользователя "
                    "и пароль обязательны."
                ),
                "received_fields": list(data.keys()),
            },
            status=400,
        )

    user = authenticate(
        request,
        username=username,
        password=password,
    )

    if user is None:
        return JsonResponse(
            {
                "detail": "Неверное имя пользователя или пароль.",
            },
            status=400,
        )

    if user.is_deleted or not user.is_active:
        return JsonResponse(
            {
                "detail": "Пользователь заблокирован.",
            },
            status=403,
        )

    login(request, user)

    return JsonResponse(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": user.get_full_name(),
        },
    )


def sign_out_api_view(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "detail": "Метод не поддерживается.",
            },
            status=405,
        )

    logout(request)

    return JsonResponse(
        {
            "detail": "Выход выполнен.",
        },
    )


def sign_up_api_view(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "detail": "Метод не поддерживается.",
            },
            status=405,
        )

    data = get_request_data(request)

    name = str(
        data.get("name", ""),
    ).strip()

    username = str(
        data.get("username", ""),
    ).strip()

    password = str(
        data.get("password", ""),
    )

    if not username or not password:
        return JsonResponse(
            {
                "detail": (
                    "Имя пользователя "
                    "и пароль обязательны."
                ),
                "received_fields": list(data.keys()),
            },
            status=400,
        )

    if len(password) < 6:
        return JsonResponse(
            {
                "detail": (
                    "Пароль должен содержать "
                    "минимум 6 символов."
                ),
            },
            status=400,
        )

    if User.objects.filter(
        username=username,
    ).exists():
        return JsonResponse(
            {
                "detail": (
                    "Пользователь с таким логином "
                    "уже существует."
                ),
            },
            status=400,
        )

    if "@" in username:
        email = username.lower()
    else:
        email = f"{username}@example.com"

    if User.objects.filter(
        email=email,
    ).exists():
        return JsonResponse(
            {
                "detail": (
                    "Пользователь с таким email "
                    "уже существует."
                ),
            },
            status=400,
        )

    first_name = name
    last_name = ""

    if " " in name:
        first_name, last_name = name.split(
            " ",
            1,
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )

    login(request, user)

    return JsonResponse(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": user.get_full_name(),
        },
        status=201,
    )