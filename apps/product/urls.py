from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet  # crea este ViewSet en apps/product/views.py

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),  # -> /api/products/...
]
