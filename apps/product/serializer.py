from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "code",
            "name",
            "slug",
            "description",
            "comment",
            "image",
            "price",
            "stock",
            "is_active",
            "created_at",
            "updated_at",
            "owner",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at", "owner"]

    def validate_code(self, value):
        if value is None:
            raise serializers.ValidationError("El código es obligatorio.")
        # normaliza: elimina espacios y convierte a mayúsculas
        return value.strip().upper()
