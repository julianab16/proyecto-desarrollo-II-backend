from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.user.models import User


class LoginViewTest(TestCase):
    """Pruebas unitarias para la vista LoginView"""

    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.client = APIClient()
        self.login_url = '/api/auth/login/'  # Ruta basada en tu urls.py
        
        # Crear usuario de prueba activo
        self.active_user = User.objects.create_user(
            username="usuarioactivo",
            email="activo@example.com",
            password="password123",
            dni="1234567890",
            phone_number="3001234567",
            role=User.CLIENTE,
            is_active=True
        )
        
        # Crear usuario inactivo
        self.inactive_user = User.objects.create_user(
            username="usuarioinactivo",
            email="inactivo@example.com",
            password="password123",
            dni="0987654321",
            phone_number="3009876543",
            role=User.CLIENTE,
            is_active=False
        )

    def test_login_sin_username(self):
        """Verifica que falla el login cuando no se proporciona username"""
        data = {
            "password": "password123"
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertEqual(
            response.data['detail'], 
            "Usuario y contraseña son obligatorios."
        )
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from apps.user.models import User

class UserViewSetBasicTest(TestCase):

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
