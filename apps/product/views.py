from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product
from .serializer import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD para Productos.
    - Lectura pública (solo activos para usuarios anónimos).
    - Cualquier usuario autenticado puede crear productos (vendedores).
    - Solo el propietario o staff puede editar/eliminar sus productos.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code", "description"]
    ordering_fields = ["created_at", "price", "name"]
    ordering = ["-created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        qs = super().get_queryset()
        # usuarios no autenticados ven solo productos activos
        if not self.request.user or not self.request.user.is_authenticated:
            qs = qs.filter(is_active=True)
        return qs

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_products(self, request):
        """
        Endpoint para que los vendedores vean solo sus propios productos.
        GET /api/products/my_products/
        """
        products = Product.objects.filter(owner=request.user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        if not (self.request.user.is_staff or self.request.user.role == "VENDEDOR"):
           raise PermissionDenied("Solo vendedores o administradores pueden crear productos.")
        serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Override update para verificar permisos antes de actualizar
        """
        instance = self.get_object()
        # Verificar que el usuario sea el propietario o staff
        if not (request.user.is_staff or instance.owner == request.user):
            raise PermissionDenied(
                "No puedes actualizar productos de otros usuarios.")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Override partial_update para verificar permisos antes de actualizar
        """
        instance = self.get_object()
        # Verificar que el usuario sea el propietario o staff
        if not (request.user.is_staff or instance.owner == request.user):
            raise PermissionDenied(
                "No puedes actualizar productos de otros usuarios.")
        return super().partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        # solo staff o creador pueden actualizar
        if not (
                self.request.user.is_staff or serializer.instance.owner == self.request.user):
            raise PermissionDenied(
                "No puedes actualizar productos de otros usuarios.")
        serializer.save()

    def perform_destroy(self, instance):
        # solo el creador puede eliminar el producto
        if instance.owner == self.request.user or self.request.user.is_staff:
            instance.delete()
        else:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "No puedes eliminar productos de otros usuarios.")
