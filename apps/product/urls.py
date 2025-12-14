from django.urls import path
from .views import ProductViewSet

urlpatterns = [
    path("products/", ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-list'),
    path("products/my_products/", ProductViewSet.as_view({'get': 'my_products'}), name='my-products'),
    path("products/search_products/", ProductViewSet.as_view({'get': 'search_products'}), name='search-products'),
    # Soporte para ID (compatibilidad con frontend existente) - DEBE IR PRIMERO
    path("products/<int:pk>/", ProductViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='product-detail-by-id'),
    # Soporte para slug (preferido)
    path("products/<slug:slug>/", ProductViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='product-detail'),
]
