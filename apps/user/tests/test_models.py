from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.user.models import User


class UserModelTest(TestCase):
    """Tests para el modelo User"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.user_data = {
            'username': 'testuser',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan@test.com',
            'dni': '1234567890',
            'phone_number': '3001234567',
            'role': User.CLIENTE,
            'password': 'testpass123'
        }

    def test_create_user_success(self):
        """Test: Crear usuario correctamente"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.first_name, 'JUAN')  # Debe convertirse a mayúsculas
        self.assertEqual(user.last_name, 'PÉREZ')
        self.assertEqual(user.email, 'juan@test.com')
        self.assertEqual(user.dni, '1234567890')
        self.assertEqual(user.phone_number, '3001234567')
        self.assertEqual(user.role, User.CLIENTE)
        self.assertTrue(user.password.startswith('pbkdf2_'))  # Password hasheada

    def test_user_str_method(self):
        """Test: Método __str__ del usuario"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')

    def test_user_str_method_with_dni_fallback(self):
        """Test: __str__ usa DNI si no hay username"""
        user = User.objects.create_user(**self.user_data)
        user.username = ''
        self.assertEqual(str(user), '1234567890')

    def test_uppercase_transformation_on_save(self):
        """Test: Nombres se convierten a mayúsculas al guardar"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.first_name, 'JUAN')
        self.assertEqual(user.last_name, 'PÉREZ')

    def test_lowercase_email_on_save(self):
        """Test: Email se convierte a minúsculas al guardar"""
        data = self.user_data.copy()
        data['email'] = 'JUAN@TEST.COM'
        user = User.objects.create_user(**data)
        self.assertEqual(user.email, 'juan@test.com')

    def test_password_hashing_on_save(self):
        """Test: Password se hashea automáticamente"""
        user = User(**self.user_data)
        user.save()
        self.assertTrue(user.password.startswith('pbkdf2_'))
        self.assertTrue(user.check_password('testpass123'))

    def test_duplicate_dni_raises_error(self):
        """Test: DNI duplicado genera error"""
        User.objects.create_user(**self.user_data)
        
        data = self.user_data.copy()
        data['username'] = 'otrouser'
        data['email'] = 'otro@test.com'
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**data)

    def test_duplicate_username_raises_error(self):
        """Test: Username duplicado genera error"""
        User.objects.create_user(**self.user_data)
        
        data = self.user_data.copy()
        data['dni'] = '9876543210'
        data['email'] = 'otro@test.com'
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**data)

    def test_invalid_phone_number(self):
        """Test: Número de teléfono inválido"""
        data = self.user_data.copy()
        data['phone_number'] = '1234567890'  # No empieza con 3 o 6
        
        user = User(**data)
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_valid_phone_number_starting_with_3(self):
        """Test: Teléfono válido que inicia con 3"""
        data = self.user_data.copy()
        data['phone_number'] = '3101234567'
        user = User(**data)
        user.full_clean()  # No debe lanzar excepción
        self.assertEqual(user.phone_number, '3101234567')

    def test_valid_phone_number_starting_with_6(self):
        """Test: Teléfono válido que inicia con 6"""
        data = self.user_data.copy()
        data['phone_number'] = '6011234567'
        user = User(**data)
        user.full_clean()  # No debe lanzar excepción
        self.assertEqual(user.phone_number, '6011234567')

    def test_invalid_dni_too_short(self):
        """Test: DNI muy corto es inválido"""
        data = self.user_data.copy()
        data['dni'] = '123456'  # Menos de 7 dígitos
        
        user = User(**data)
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_invalid_dni_too_long(self):
        """Test: DNI muy largo es inválido"""
        data = self.user_data.copy()
        data['dni'] = '12345678901'  # Más de 10 dígitos
        
        user = User(**data)
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_valid_dni_7_digits(self):
        """Test: DNI válido de 7 dígitos"""
        data = self.user_data.copy()
        data['dni'] = '1234567'
        user = User(**data)
        user.full_clean()
        self.assertEqual(user.dni, '1234567')

    def test_valid_dni_10_digits(self):
        """Test: DNI válido de 10 dígitos"""
        data = self.user_data.copy()
        data['dni'] = '1234567890'
        user = User(**data)
        user.full_clean()
        self.assertEqual(user.dni, '1234567890')

    def test_user_roles(self):
        """Test: Roles de usuario disponibles"""
        self.assertEqual(User.ADMINISTRADOR, 'ADMINISTRADOR')
        self.assertEqual(User.CLIENTE, 'CLIENTE')
        self.assertEqual(User.VENDEDOR, 'VENDEDOR')

    def test_default_role_is_cliente(self):
        """Test: Role por defecto es CLIENTE"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.role, User.CLIENTE)

    def test_create_admin_user(self):
        """Test: Crear usuario administrador"""
        data = self.user_data.copy()
        data['role'] = User.ADMINISTRADOR
        user = User.objects.create_user(**data)
        self.assertEqual(user.role, User.ADMINISTRADOR)

    def test_create_vendedor_user(self):
        """Test: Crear usuario vendedor"""
        data = self.user_data.copy()
        data['role'] = User.VENDEDOR
        user = User.objects.create_user(**data)
        self.assertEqual(user.role, User.VENDEDOR)

    def test_user_ordering(self):
        """Test: Usuarios se ordenan por ID"""
        User.objects.create_user(username='user1', email='u1@test.com', 
                                dni='1111111111', phone_number='3001111111', password='pass')
        User.objects.create_user(username='user2', email='u2@test.com', 
                                dni='2222222222', phone_number='3002222222', password='pass')
        
        users = User.objects.all()
        self.assertTrue(users[0].id < users[1].id)

    def test_user_meta_db_table(self):
        """Test: Tabla en DB es 'user'"""
        self.assertEqual(User._meta.db_table, 'user')

    def test_user_meta_verbose_names(self):
        """Test: Nombres verbose del modelo"""
        self.assertEqual(User._meta.verbose_name, 'user')
        self.assertEqual(User._meta.verbose_name_plural, 'users')