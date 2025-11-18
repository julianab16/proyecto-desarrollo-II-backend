from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, MeView, RegisterView, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),  # -> /api/users/...
    path(
        "auth/register/", RegisterView.as_view(), name="register"
    ),  # -> /api/auth/register/
    path("auth/login/", LoginView.as_view(), name="login"),
    path(
        "auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"),
    path("auth/me/", MeView.as_view(), name="me"),
]
