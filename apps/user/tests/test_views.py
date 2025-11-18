from django.test import TestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient

from apps.user.models import User

class UserViewSetBasicTest(TestCase):
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
