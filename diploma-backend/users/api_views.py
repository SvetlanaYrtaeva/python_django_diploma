import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

User = get_user_model()


def _extract_data(request):
    try:
        body = request.body.decode("utf-8")
        if body:
            parsed = json.loads(body)
            if isinstance(parsed, dict):
                return parsed
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass
    return dict(request.data) if request.data else {}


@api_view(["POST"])
def sign_in_api_view(request: Request) -> Response:
    data = _extract_data(request)
    login_field = data.get("username") or data.get("email") or data.get("login")
    password = data.get("password") or data.get("pass")

    if not login_field or not password:
        return Response(
            {"success": False, "error": "Укажите логин и пароль"},
            status=400,
        )

    username = login_field
    try:
        user_obj = User.objects.get(email=login_field.lower())
        username = user_obj.username
    except User.DoesNotExist:
        pass

    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return Response({"success": True})
    return Response(
        {"success": False, "error": "Неверный логин или пароль"},
        status=401,
    )


@api_view(["POST"])
def sign_up_api_view(request: Request) -> Response:
    data = _extract_data(request)
    name = data.get("name", "")
    login_field = data.get("username") or data.get("email") or data.get("login")
    password = data.get("password") or data.get("pass")

    if not login_field or not password:
        return Response(
            {"success": False, "error": "Укажите логин и пароль"},
            status=400,
        )

    if "@" in login_field:
        email = login_field.lower()
        username = email.split("@")[0]
    else:
        email = f"{login_field}@example.com"
        username = login_field

    # Проверяем уникальность
    if User.objects.filter(email=email).exists():
        return Response(
            {"success": False, "error": "Пользователь с таким email уже существует"},
            status=400,
        )

    base = username
    i = 1
    while User.objects.filter(username=username).exists():
        username = f"{base}{i}"
        i += 1

    first_name = ""
    last_name = ""
    if name:
        parts = name.strip().split()
        first_name = parts[0] if parts else ""
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    login(request, user)
    return Response({"success": True})


@api_view(["POST"])
def sign_out_api_view(request: Request) -> Response:
    logout(request)
    return Response({"success": True})


@api_view(["GET", "POST"])
def profile_api_view(request: Request) -> Response:
    if not request.user.is_authenticated:
        return Response({"detail": "Не авторизован"}, status=401)

    user = request.user

    if request.method == "POST":
        data = _extract_data(request)
        if "first_name" in data or "name" in data:
            user.first_name = data.get("first_name") or data.get("name") or ""
        if "last_name" in data or "lastName" in data:
            user.last_name = data.get("last_name") or data.get("lastName") or ""
        if "email" in data:
            new_email = data["email"].lower()
            if (
                User.objects
                .filter(email=new_email)
                .exclude(pk=user.pk)
                .exists()
            ):
                return Response(
                    {"error": "Пользователь с таким email уже существует"},
                    status=400,
                )
            user.email = new_email
        if "phone" in data:
            phone = data["phone"]
            if phone and (
                User.objects
                .filter(phone=phone)
                .exclude(pk=user.pk)
                .exists()
            ):
                return Response(
                    {"error": "Пользователь с таким телефоном уже существует"},
                    status=400,
                )
            user.phone = phone
        if "password" in data and data["password"]:
            user.set_password(data["password"])
        user.save()

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.full_name,
        "phone": user.phone or "",
        "avatar": user.avatar.url if user.avatar else "",
    })


@api_view(["POST"])
def avatar_api_view(request: Request) -> Response:
    if not request.user.is_authenticated:
        return Response({"detail": "Не авторизован"}, status=401)

    avatar = request.FILES.get("avatar")
    if not avatar:
        return Response({"error": "Файл не передан"}, status=400)

    if avatar.size > 2 * 1024 * 1024:
        return Response(
            {"error": "Размер изображения не должен превышать 2 Мб"},
            status=400,
        )

    user = request.user
    user.avatar = avatar
    user.save(update_fields=["avatar"])

    return Response({
        "success": True,
        "avatar": user.avatar.url,
    })
