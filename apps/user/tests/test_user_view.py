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

    def test_login_exitoso(self):
        """Verifica que un usuario con credenciales válidas puede iniciar sesión"""
        data = {
            "username": "usuarioactivo",
            "password": "password123"
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'usuarioactivo')
        self.assertEqual(response.data['user']['email'], 'activo@example.com')
        self.assertEqual(response.data['user']['role'], User.CLIENTE)

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