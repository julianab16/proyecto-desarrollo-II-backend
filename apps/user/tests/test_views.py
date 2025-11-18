from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.product.models import Product
from apps.user.models import User


class ProductViewSetBasicTest(TestCase):
    """Pruebas básicas del ProductViewSet (solo queryset y retrieve)."""

    def setUp(self):
        """Configura usuarios, cliente y productos de prueba."""
        self.client = APIClient()

        # Usuario autenticado
        self.user = User.objects.create_user(
            username="usuario",
            email="user@test.com",
            dni="2000000000",
            phone_number="3000000001",
            password="userpass"
        )

        # Producto activo
        self.product_active = Product.objects.create(
            name="Producto Activo",
            code="A1",
            description="Activo",
            price=100,
            slug="producto-activo",
            is_active=True,
            owner=self.user
        )

        # Producto inactivo
        self.product_inactive = Product.objects.create(
            name="Producto Inactivo",
            code="A2",
            description="Inactivo",
            price=200,
            slug="producto-inactivo",
            is_active=False,
            owner=self.user
        )

        # URLs reales del proyecto
        # Cambia '/api/products/' si tu urls.py principal tiene prefijo 'api/'
        self.url_list = "/api/products/"

    # ----------------------------------------------------------------------
    # GET QUERYSET
    # ----------------------------------------------------------------------

    def test_anonymous_user_sees_only_active_products(self):
        """Usuarios no autenticados solo ven productos activos."""
        response = self.client.get(self.url_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["slug"], "producto-activo")

    def test_authenticated_user_sees_all_products(self):
        """Usuarios autenticados ven todos los productos (activos e inactivos)."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    # ----------------------------------------------------------------------
    # RETRIEVE
    # ----------------------------------------------------------------------

    def test_retrieve_product_by_slug(self):
        """Se puede obtener un producto por su slug."""
        # Usamos URL directa con slug porque lookup_field='slug'
        url = f"/api/products/{self.product_active.slug}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["slug"], "producto-activo")
=======
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse

User = get_user_model()

class RegisterUserViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'

    def test_register_creates_user(self):
        payload = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'dni': '111222333',
            'phone_number': '3000000000',
            'role': getattr(User, 'CLIENTE', 1)
        }
        resp = self.client.post(self.register_url, payload, format='json')
        self.assertIn(resp.status_code, (200, 201))
        self.assertTrue(User.objects.filter(username='newuser').exists())
