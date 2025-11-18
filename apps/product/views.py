from rest_framework import filters, permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from .models import Product
from .serializer import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD para Productos.
    - Lectura pública (solo activos para usuarios anónimos).
    - Escritura solo para usuarios autenticados.
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

    def perform_create(self, serializer):
        # solo staff puede crear productos
        if not self.request.user.is_staff:
            raise PermissionDenied(
                "Solo administradores pueden crear productos.")
        serializer.save(owner=self.request.user)

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
