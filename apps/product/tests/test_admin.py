from django.test import TestCase
from unittest.mock import Mock

from apps.product.admin import ProductAdmin
from apps.product.models import Product


class ProductAdminTest(TestCase):
    """Pruebas unitarias para el admin de Product (método admin_image)."""

    def setUp(self):
        """Configuración inicial para cada prueba."""
        # Instanciamos ProductAdmin con un admin_site simulado
        self.product_admin = ProductAdmin(model=Product, admin_site=Mock())

    def test_admin_image_con_imagen(self):
        """Si el producto tiene imagen, debe retornar la etiqueta <img> con la URL."""
        mock_obj = Mock()
        mock_obj.image = Mock()
        mock_obj.image.url = "/media/products/test.jpg"

        result = self.product_admin.admin_image(mock_obj)

        # format_html produce un SafeString; convertimos a str para comparar
        expected = '<img src="/media/products/test.jpg" style="max-height:100px;"/>'
        self.assertEqual(str(result), expected)

    def test_admin_image_sin_imagen(self):
        """Si el producto no tiene imagen, debe retornar '-'."""
        mock_obj = Mock()
        mock_obj.image = None

        result = self.product_admin.admin_image(mock_obj)

        self.assertEqual(result, "-")