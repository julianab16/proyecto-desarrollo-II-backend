from rest_framework.test import APITestCase, APIClient
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
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
    """Tests para la vista de login"""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('user:login')
        self.user = User.objects.create_user(
            username='loginuser',
            first_name='Test',
            last_name='User',
            email='login@test.com',
            dni='1111111111',
            phone_number='3001111111',
            password='testpass123',
            role=User.CLIENTE
        )

    def test_login_success(self):
        """Test: Login exitoso"""
        data = {'username': 'loginuser', 'password': 'testpass123'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'loginuser')

    def test_login_invalid_credentials(self):
        """Test: Login con credenciales inválidas"""
        data = {'username': 'loginuser', 'password': 'wrongpassword'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Credenciales inválidas', response.data['detail'])

    def test_login_nonexistent_user(self):
        """Test: Login con usuario inexistente"""
        data = {'username': 'noexiste', 'password': 'testpass123'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_username(self):
        """Test: Login sin username"""
        data = {'password': 'testpass123'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('obligatorios', response.data['detail'])
