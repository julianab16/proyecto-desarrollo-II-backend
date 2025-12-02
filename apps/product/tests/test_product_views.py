from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.user.models import User
from apps.product.models import Product


class ProductViewSetTest(TestCase):
    """Pruebas unitarias para ProductViewSet - perform_update y perform_destroy"""

    def setUp(self):
        """Configuración inicial para cada prueba"""
        # Crear usuarios
        self.staff_user = User.objects.create_user(
            username="admin",
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            dni="1234567890",
            phone_number="3001234567",
            password="admin123",
            role=User.ADMINISTRADOR,
            is_staff=True,
        )

        self.owner_user = User.objects.create_user(
            username="vendedor",
            first_name="Vendedor",
            last_name="Test",
            email="vendedor@example.com",
            dni="9876543210",
            phone_number="3009876543",
            password="vendedor123",
            role=User.VENDEDOR,
        )

        self.other_user = User.objects.create_user(
            username="otro",
            first_name="Otro",
            last_name="Usuario",
            email="otro@example.com",
            dni="5555555555",
            phone_number="3005555555",
            password="otro123",
            role=User.CLIENTE,
        )

        # Crear producto de prueba
        self.product = Product.objects.create(
            code="PROD001",
            name="Producto Test",
            description="Descripción de prueba",
            price=100.00,
            stock=10,
            is_active=True,
            owner=self.owner_user,
        )

        self.client = APIClient()

    def test_perform_update_owner_puede_actualizar(self):
        """Verifica que el propietario puede actualizar su propio producto"""
        self.client.force_authenticate(user=self.owner_user)
        url = f'/api/products/{self.product.slug}/'
        data = {
            "code": "PROD001",
            "name": "Producto Actualizado",
            "description": "Nueva descripción",
            "price": 150.00,
            "stock": 15,
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Producto Actualizado")  # Se convierte a mayúsculas
        self.assertEqual(float(self.product.price), 150.00)

    def test_perform_update_staff_puede_actualizar(self):
        """Verifica que un usuario staff puede actualizar cualquier producto"""
        self.client.force_authenticate(user=self.staff_user)
        url = f'/api/products/{self.product.slug}/'
        data = {
            "code": "PROD001",
            "name": "Actualizado por Admin",
            "description": "Descripción admin",
            "price": 200.00,
            "stock": 20,
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Actualizado por Admin")

    def test_perform_update_otro_usuario_no_puede_actualizar(self):
        """Verifica que un usuario no propietario ni staff no puede actualizar"""
        self.client.force_authenticate(user=self.other_user)
        url = f'/api/products/{self.product.slug}/'
        data = {
            "code": "PROD001",
            "name": "Intento Actualización",
            "description": "No debería funcionar",
            "price": 999.00,
            "stock": 99,
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.product.refresh_from_db()
        # Verificar que el producto no cambió
        self.assertEqual(self.product.name, "Producto Test")
        self.assertIn("No puedes actualizar productos", str(response.data))

    def test_perform_destroy_owner_puede_eliminar(self):
        """Verifica que el propietario puede eliminar su propio producto"""
        self.client.force_authenticate(user=self.owner_user)
        url = f'/api/products/{self.product.slug}/'

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verificar que el producto fue eliminado
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_perform_destroy_staff_puede_eliminar(self):
        """Verifica que un usuario staff puede eliminar cualquier producto"""
        self.client.force_authenticate(user=self.staff_user)
        url = f'/api/products/{self.product.slug}/'

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_perform_destroy_otro_usuario_no_puede_eliminar(self):
        """Verifica que un usuario no autorizado no puede eliminar productos"""
        self.client.force_authenticate(user=self.other_user)
        url = f'/api/products/{self.product.slug}/'

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Verificar que el producto todavía existe
        self.assertTrue(Product.objects.filter(id=self.product.id).exists())
        self.assertIn("No puedes eliminar productos", str(response.data))

    def test_perform_update_sin_autenticacion(self):
        """Verifica que usuarios no autenticados no pueden actualizar"""
        url = f'/api/products/{self.product.slug}/'
        data = {
            "code": "PROD001",
            "name": "Intento sin auth",
            "price": 100.00,
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_perform_destroy_sin_autenticacion(self):
        """Verifica que usuarios no autenticados no pueden eliminar"""
        url = f'/api/products/{self.product.slug}/'

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Verificar que el producto todavía existe
        self.assertTrue(Product.objects.filter(id=self.product.id).exists())

    def test_perform_update_partial_con_patch(self):
        """Verifica actualización parcial con PATCH"""
        self.client.force_authenticate(user=self.owner_user)
        url = f'/api/products/{self.product.slug}/'
        data = {"price": 250.00}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(float(self.product.price), 250.00)
        # Verificar que otros campos no cambiaron
        self.assertEqual(self.product.name, "Producto Test")
