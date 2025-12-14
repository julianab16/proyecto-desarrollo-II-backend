from rest_framework.test import APITestCase, APIClient
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from apps.user.models import User

class UserViewSetTest(TestCase):
    """Tests para el ViewSet de usuarios"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            first_name='Admin',
            last_name='User',
            email='admin@test.com',
            dni='3333333333',
            phone_number='3003333333',
            password='adminpass',
            role=User.ADMINISTRADOR,
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            first_name='Regular',
            last_name='User',
            email='regular@test.com',
            dni='4444444444',
            phone_number='3004444444',
            password='userpass',
            role=User.CLIENTE
        )

    def test_list_users_as_admin(self):
        """Test: Admin puede listar todos los usuarios"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user:user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

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

    def test_register_usuario_duplicado(self):
        """Verifica que falla al intentar registrar un usuario duplicado"""
        # Crear usuario inicial
        User.objects.create_user(
            username='existente',
            email='existe@example.com',
            password='password123',
            first_name='Usuario',
            last_name='Existente',
            dni='1111111111',
            phone_number='3001111111',
            role=User.CLIENTE
        )
        
        # Intentar crear usuario con el mismo username
        payload = {
            'username': 'existente',
            'email': 'nuevo@example.com',
            'password': 'newpass123',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'dni': '2222222222',
            'phone_number': '3002222222',
            'role': User.CLIENTE
        }
        
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_email_duplicado(self):
        """Verifica que falla al intentar registrar un email duplicado"""
        # Crear usuario inicial
        User.objects.create_user(
            username='user1',
            email='duplicate@example.com',
            password='password123',
            first_name='Usuario',
            last_name='Uno',
            dni='3333333333',
            phone_number='3003333333',
            role=User.CLIENTE
        )
        
        # Intentar crear usuario con el mismo email
        payload = {
            'username': 'user2',
            'email': 'duplicate@example.com',
            'password': 'newpass123',
            'first_name': 'Usuario',
            'last_name': 'Dos',
            'dni': '4444444444',
            'phone_number': '3004444444',
            'role': User.CLIENTE
        }
        
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_dni_duplicado(self):
        """Verifica que falla al intentar registrar un DNI duplicado"""
        # Crear usuario inicial
        User.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='password123',
            first_name='Usuario',
            last_name='Tres',
            dni='5555555555',
            phone_number='3005555555',
            role=User.CLIENTE
        )
        
        # Intentar crear usuario con el mismo DNI
        payload = {
            'username': 'user4',
            'email': 'user4@example.com',
            'password': 'newpass123',
            'first_name': 'Usuario',
            'last_name': 'Cuatro',
            'dni': '5555555555',
            'phone_number': '3006666666',
            'role': User.CLIENTE
        }
        
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_campos_faltantes(self):
        """Verifica que falla cuando faltan campos requeridos"""
        payload = {
            'username': 'incomplete',
            'password': 'pass123'
            # Faltan campos requeridos
        }
        
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_dni_invalido_corto(self):
        """Verifica que falla con DNI muy corto"""
        payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'pass123',
            'first_name': 'Test',
            'last_name': 'User',
            'dni': '123',  # Muy corto
            'phone_number': '3001234567',
            'role': User.CLIENTE
        }
        
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_dni_invalido_largo(self):
        """Verifica que falla con DNI muy largo"""
        payload = {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password': 'pass123',
            'first_name': 'Test',
            'last_name': 'User',
            'dni': '12345678901',  # Muy largo
            'phone_number': '3001234567',
            'role': User.CLIENTE
        }
        
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_telefono_invalido(self):
        """Verifica que falla con teléfono inválido"""
        payload = {
            'username': 'testuser3',
            'email': 'test3@example.com',
            'password': 'pass123',
            'first_name': 'Test',
            'last_name': 'User',
            'dni': '1234567890',
            'phone_number': '1234567890',  # No empieza con 3 o 6
            'role': User.CLIENTE
        }
        
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_logging_error_sin_password(self):
        """Verifica que el logging de errores no incluye la contraseña"""
        from unittest.mock import patch
        
        # Intentar registrar con datos duplicados para provocar error
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='password123',
            first_name='Existing',
            last_name='User',
            dni='9999999999',
            phone_number='3009999999',
            role=User.CLIENTE
        )
        
        with patch('apps.user.views.logger.warning') as mock_logger:            
            # Verificar que se llamó al logger
            self.assertTrue(mock_logger.called)
            
            # Obtener los argumentos de la llamada al logger
            call_args = mock_logger.call_args
            
            # Verificar que 'password' no aparece en los argumentos del log
            log_message = str(call_args)
            self.assertNotIn('secretpassword123', log_message)

    def test_register_exitoso_retorna_usuario(self):
        """Verifica que registro exitoso retorna los datos del usuario"""
        payload = {
            'username': 'successuser',
            'email': 'success@example.com',
            'password': 'pass123',
            'first_name': 'Success',
            'last_name': 'User',
            'dni': '7777777777',
            'phone_number': '3007777777',
            'role': User.CLIENTE
        }
        
        response = self.client.post(self.register_url, payload, format='json')
        
        self.assertIn(response.status_code, (200, 201))
        self.assertIn('username', response.data)
        self.assertEqual(response.data['username'], 'successuser')
        self.assertEqual(response.data['email'], 'success@example.com')


class MeViewTest(TestCase):
    """Tests para la vista Me (perfil del usuario)"""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('user:me')
        self.user = User.objects.create_user(
            username='meuser',
            first_name='Me',
            last_name='Test',
            email='me@test.com',
            dni='2222222222',
            phone_number='3002222222',
            password='testpass123',
            role=User.CLIENTE
        )
        self.client.force_authenticate(user=self.user)

    def test_get_me_authenticated(self):
        """Test: Obtener información del usuario autenticado"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'meuser')
        self.assertEqual(response.data['email'], 'me@test.com')

    def test_get_me_unauthenticated(self):
        """Test: Acceso sin autenticación"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_me_partial(self):
        """Test: Actualización parcial del perfil"""
        data = {'first_name': 'Updated'}
        response = self.client.put(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'UPDATED')

    def test_delete_me(self):
        """Test: Eliminar cuenta propia"""
        response = self.client.delete(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

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

    def test_login_usuario_no_existe(self):
        """Verifica que falla el login cuando el usuario no existe"""
        data = {
            "username": "usuarioinexistente",
            "password": "password123"
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Credenciales inválidas.')

    def test_login_password_incorrecta(self):
        """Verifica que falla el login cuando la contraseña es incorrecta"""
        data = {
            "username": "usuarioactivo",
            "password": "passwordincorrecta"
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Credenciales inválidas.')

    def test_login_usuario_inactivo(self):
        """Verifica que falla el login cuando el usuario está inactivo"""
        data = {
            "username": "usuarioinactivo",
            "password": "password123"
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)
        self.assertEqual(
            response.data['detail'], 
            "Usuario inactivo. Contacta al administrador."
        )

    def test_login_exitoso(self):
        """Verifica que el login es exitoso con credenciales válidas"""
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