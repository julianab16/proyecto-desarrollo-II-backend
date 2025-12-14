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

    def test_get_object_by_slug(self):
        """Verifica que se puede obtener un producto por slug"""
        self.client.force_authenticate(user=self.owner_user)
        url = f'/api/products/{self.product.slug}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['slug'], self.product.slug)
        self.assertEqual(response.data['name'], self.product.name)

    def test_get_object_by_pk(self):
        """Verifica que se puede obtener un producto por pk"""
        self.client.force_authenticate(user=self.owner_user)
        url = f'/api/products/{self.product.pk}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.product.pk)
        self.assertEqual(response.data['name'], self.product.name)

    def test_get_object_not_found(self):
        """Verifica que retorna 404 cuando el producto no existe"""
        self.client.force_authenticate(user=self.owner_user)
        url = '/api/products/producto-inexistente/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ordering_by_created_at_desc(self):
        """Verifica que los productos se ordenan por created_at descendente por defecto"""
        # Crear productos adicionales
        product2 = Product.objects.create(
            code="PROD002",
            name="Producto Segundo",
            description="Segundo producto",
            price=200.00,
            stock=5,
            is_active=True,
            owner=self.owner_user,
        )
        
        product3 = Product.objects.create(
            code="PROD003",
            name="Producto Tercero",
            description="Tercer producto",
            price=300.00,
            stock=8,
            is_active=True,
            owner=self.owner_user,
        )

        self.client.force_authenticate(user=self.owner_user)
        url = '/api/products/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que el producto más reciente aparece primero
        self.assertEqual(response.data[0]['code'], 'PROD003')
        self.assertEqual(response.data[1]['code'], 'PROD002')
        self.assertEqual(response.data[2]['code'], 'PROD001')

    def test_get_queryset_usuarios_no_autenticados_solo_ven_activos(self):
        """Verifica que usuarios no autenticados solo ven productos activos"""
        # Crear producto inactivo
        inactive_product = Product.objects.create(
            code="PROD_INACTIVE",
            name="Producto Inactivo",
            description="Este producto está inactivo",
            price=100.00,
            stock=5,
            is_active=False,
            owner=self.owner_user,
        )
        
        # Crear producto activo adicional
        active_product = Product.objects.create(
            code="PROD_ACTIVE",
            name="Producto Activo",
            description="Este producto está activo",
            price=200.00,
            stock=10,
            is_active=True,
            owner=self.owner_user,
        )

        # Sin autenticación
        url = '/api/products/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que solo se devuelven productos activos
        product_codes = [p['code'] for p in response.data]
        self.assertIn('PROD001', product_codes)  # Producto activo del setUp
        self.assertIn('PROD_ACTIVE', product_codes)
        self.assertNotIn('PROD_INACTIVE', product_codes)  # No debe aparecer el inactivo

    def test_get_queryset_usuarios_autenticados_ven_todos(self):
        """Verifica que usuarios autenticados ven todos los productos (activos e inactivos)"""
        # Crear producto inactivo
        inactive_product = Product.objects.create(
            code="PROD_INACTIVE2",
            name="Producto Inactivo 2",
            description="Este producto está inactivo",
            price=100.00,
            stock=5,
            is_active=False,
            owner=self.owner_user,
        )
        
        # Crear producto activo adicional
        active_product = Product.objects.create(
            code="PROD_ACTIVE2",
            name="Producto Activo 2",
            description="Este producto está activo",
            price=200.00,
            stock=10,
            is_active=True,
            owner=self.owner_user,
        )

        # Con autenticación
        self.client.force_authenticate(user=self.owner_user)
        url = '/api/products/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que se devuelven tanto productos activos como inactivos
        product_codes = [p['code'] for p in response.data]
        self.assertIn('PROD001', product_codes)  # Producto activo del setUp
        self.assertIn('PROD_ACTIVE2', product_codes)
        self.assertIn('PROD_INACTIVE2', product_codes)  # Debe aparecer el inactivo

    def test_get_queryset_filtro_activos_solo_afecta_no_autenticados(self):
        """Verifica que el filtro de productos activos solo afecta a usuarios no autenticados"""
        # Crear productos
        Product.objects.create(
            code="INACTIVE1",
            name="Inactivo 1",
            description="Inactivo",
            price=50.00,
            stock=3,
            is_active=False,
            owner=self.owner_user,
        )
        
        Product.objects.create(
            code="ACTIVE1",
            name="Activo 1",
            description="Activo",
            price=75.00,
            stock=7,
            is_active=True,
            owner=self.owner_user,
        )

        url = '/api/products/'
        
        # Sin autenticación - solo activos
        response_no_auth = self.client.get(url)
        codes_no_auth = [p['code'] for p in response_no_auth.data]
        
        # Con autenticación - todos
        self.client.force_authenticate(user=self.staff_user)
        response_auth = self.client.get(url)
        codes_auth = [p['code'] for p in response_auth.data]

        # Verificar diferencia en resultados
        self.assertNotIn('INACTIVE1', codes_no_auth)
        self.assertIn('ACTIVE1', codes_no_auth)
        
        self.assertIn('INACTIVE1', codes_auth)
        self.assertIn('ACTIVE1', codes_auth)
        
        # Usuario autenticado ve más productos que el no autenticado
        self.assertGreater(len(codes_auth), len(codes_no_auth))
