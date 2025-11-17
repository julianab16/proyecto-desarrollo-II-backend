from django.test import TestCase

from apps.user.models import User


class UserModelTest(TestCase):
    """Pruebas unitarias para el modelo User"""

    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.user_data = {
            "username": "juanperez",
            "first_name": "Juan",
            "last_name": "Pérez",
            "email": "juan@example.com",
            "dni": "1234567890",
            "phone_number": "3001234567",
            "password": "password123",
            "role": User.CLIENTE,
        }

    def test_crear_usuario_cliente_exitoso(self):
        """Verifica que se puede crear un usuario con rol CLIENTE"""
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.username, "juanperez")
        self.assertEqual(user.role, User.CLIENTE)
        self.assertEqual(user.dni, "1234567890")
        self.assertEqual(user.phone_number, "3001234567")
        self.assertTrue(user.check_password("password123"))
