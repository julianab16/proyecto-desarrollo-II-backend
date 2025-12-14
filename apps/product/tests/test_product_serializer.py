from django.test import TestCase
from rest_framework import serializers
from apps.product.serializer import ProductSerializer
from apps.user.models import User
from apps.product.models import Product


class ProductSerializerTest(TestCase):
    """Tests para ProductSerializer"""

    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.user = User.objects.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            dni="1234567890",
            phone_number="3001234567",
            password="testpass123",
            role=User.VENDEDOR,
        )

    def test_validate_code_normaliza_mayusculas(self):
        """Verifica que el código se convierte a mayúsculas"""
        serializer = ProductSerializer()
        result = serializer.validate_code("prod001")
        self.assertEqual(result, "PROD001")

    def test_validate_code_elimina_espacios(self):
        """Verifica que el código elimina espacios al inicio y final"""
        serializer = ProductSerializer()
        result = serializer.validate_code("  PROD002  ")
        self.assertEqual(result, "PROD002")

    def test_validate_code_combina_mayusculas_y_espacios(self):
        """Verifica que normaliza mayúsculas y elimina espacios simultáneamente"""
        serializer = ProductSerializer()
        result = serializer.validate_code("  prod003  ")
        self.assertEqual(result, "PROD003")

    def test_validate_code_con_espacios_intermedios(self):
        """Verifica que mantiene espacios intermedios pero elimina los externos"""
        serializer = ProductSerializer()
        result = serializer.validate_code("  prod 004  ")
        self.assertEqual(result, "PROD 004")

    def test_validate_code_none_lanza_error(self):
        """Verifica que código None lanza ValidationError"""
        serializer = ProductSerializer()
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.validate_code(None)
        
        self.assertIn("El código es obligatorio", str(context.exception))

    def test_validate_code_vacio_no_lanza_error(self):
        """Verifica que una cadena vacía no lanza error (solo normaliza)"""
        serializer = ProductSerializer()
        result = serializer.validate_code("   ")
        self.assertEqual(result, "")

    def test_validate_code_ya_normalizado(self):
        """Verifica que un código ya normalizado se mantiene igual"""
        serializer = ProductSerializer()
        result = serializer.validate_code("PROD005")
        self.assertEqual(result, "PROD005")

    def test_validate_code_con_numeros_y_letras(self):
        """Verifica que normaliza correctamente códigos alfanuméricos"""
        serializer = ProductSerializer()
        result = serializer.validate_code("  abc123xyz  ")
        self.assertEqual(result, "ABC123XYZ")

    def test_validate_code_con_caracteres_especiales(self):
        """Verifica que mantiene caracteres especiales"""
        serializer = ProductSerializer()
        result = serializer.validate_code("  prod-001_test  ")
        self.assertEqual(result, "PROD-001_TEST")
