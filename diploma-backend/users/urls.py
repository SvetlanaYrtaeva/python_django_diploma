from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    UserLoginView,
    logout_view,
    profile_view,
    register_view,
)


app_name = "users"


urlpatterns = [
    path(
        "register/",
        register_view,
        name="register",
    ),
    path(
        "login/",
        UserLoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        logout_view,
        name="logout",
    ),
    path(
        "profile/",
        profile_view,
        name="profile",
    ),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="frontend/signIn.html",
        ),
        name="password_reset",
    ),
]