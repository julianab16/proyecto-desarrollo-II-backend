from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.product.models import Product
from apps.user.models import User


class ProductModelTest(TestCase):
    """Tests para el modelo Product"""

    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear un usuario para asociar con los productos
        self.user = User.objects.create_user(
            username='testuser',
            first_name='Juan',
            last_name='Pérez',
            email='juan@test.com',
            dni='1234567890',
            phone_number='3001234567',
            password='testpass123'
        )
        
        self.product_data = {
            'name': 'Producto de Prueba',
            'code': 'PROD-001',
            'description': 'Descripción del producto',
            'comment': 'Comentario adicional',
            'price': 25000.00,
            'stock': 10,
            'owner': self.user
        }

    def test_create_product_success(self):
        """Test: Crear producto correctamente"""
        product = Product.objects.create(**self.product_data)
        
        self.assertEqual(product.name, 'Producto de Prueba')
        self.assertEqual(product.code, 'PROD-001')
        self.assertEqual(product.price, 25000.00)
        self.assertEqual(product.stock, 10)
        self.assertTrue(product.is_active)
        self.assertEqual(product.owner, self.user)

    def test_product_str_method(self):
        """Test: Método __str__ del producto"""
        product = Product.objects.create(**self.product_data)
        self.assertEqual(str(product), 'Producto de Prueba (PROD-001)')

    def test_slug_auto_generation(self):
        """Test: Slug se genera automáticamente desde el nombre"""
        product = Product.objects.create(**self.product_data)
        self.assertEqual(product.slug, 'producto-de-prueba')

    def test_slug_unique_when_duplicate_name(self):
        """Test: Slug único cuando hay nombres duplicados"""
        Product.objects.create(**self.product_data)
        
        data = self.product_data.copy()
        data['code'] = 'PROD-002'
        product2 = Product.objects.create(**data)
        
        self.assertEqual(product2.slug, 'producto-de-prueba-1')

    def test_slug_from_code_when_name_empty(self):
        """Test: Slug se genera desde el código si nombre está vacío"""
        data = self.product_data.copy()
        data['name'] = ''
        product = Product.objects.create(**data)
        self.assertEqual(product.slug, 'PROD-001')

    def test_duplicate_code_raises_error(self):
        """Test: Código duplicado genera error"""
        Product.objects.create(**self.product_data)
        
        data = self.product_data.copy()
        data['name'] = 'Otro Producto'
        
        with self.assertRaises(IntegrityError):
            Product.objects.create(**data)

    def test_duplicate_slug_raises_error(self):
        """Test: Slug duplicado genera error"""
        product = Product.objects.create(**self.product_data)
        
        # Intentar crear producto con el mismo slug manualmente
        data = self.product_data.copy()
        data['code'] = 'PROD-002'
        data['slug'] = product.slug
        
        with self.assertRaises(IntegrityError):
            Product.objects.create(**data)

    def test_invalid_code_format(self):
        """Test: Código con formato inválido"""
        data = self.product_data.copy()
        data['code'] = 'prod-001'  # minúsculas no permitidas
        
        product = Product(**data)
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_valid_code_uppercase_letters(self):
        """Test: Código válido con letras mayúsculas"""
        data = self.product_data.copy()
        data['code'] = 'ABC-123-XYZ'
        product = Product(**data)
        product.full_clean()
        self.assertEqual(product.code, 'ABC-123-XYZ')

    def test_valid_code_numbers_only(self):
        """Test: Código válido solo con números"""
        data = self.product_data.copy()
        data['code'] = '123456'
        product = Product(**data)
        product.full_clean()
        self.assertEqual(product.code, '123456')

    def test_default_price_is_zero(self):
        """Test: Precio por defecto es 0.00"""
        data = self.product_data.copy()
        del data['price']
        product = Product.objects.create(**data)
        self.assertEqual(product.price, 0.00)

    def test_default_stock_is_zero(self):
        """Test: Stock por defecto es 0"""
        data = self.product_data.copy()
        del data['stock']
        product = Product.objects.create(**data)
        self.assertEqual(product.stock, 0)

    def test_default_is_active_is_true(self):
        """Test: is_active por defecto es True"""
        product = Product.objects.create(**self.product_data)
        self.assertTrue(product.is_active)

    def test_product_without_owner(self):
        """Test: Producto puede crearse sin propietario"""
        data = self.product_data.copy()
        del data['owner']
        product = Product.objects.create(**data)
        self.assertIsNone(product.owner)

    def test_product_ordering(self):
        """Test: Productos se ordenan por fecha de creación descendente"""
        product1 = Product.objects.create(
            name='Producto 1', code='PROD-001', price=100, owner=self.user
        )
        product2 = Product.objects.create(
            name='Producto 2', code='PROD-002', price=200, owner=self.user
        )
        
        products = Product.objects.all()
        self.assertEqual(products[0], product2)  # Más reciente primero
        self.assertEqual(products[1], product1)

    def test_product_price_decimal_places(self):
        """Test: Precio con 2 decimales"""
        data = self.product_data.copy()
        data['price'] = 99.99
        product = Product.objects.create(**data)
        self.assertEqual(product.price, 99.99)

    def test_product_price_max_digits(self):
        """Test: Precio con máximo de dígitos permitidos"""
        data = self.product_data.copy()
        data['price'] = 99999999.99  # 10 dígitos totales
        product = Product.objects.create(**data)
        self.assertEqual(product.price, 99999999.99)

    def test_product_blank_description(self):
        """Test: Descripción puede estar vacía"""
        data = self.product_data.copy()
        data['description'] = ''
        product = Product.objects.create(**data)
        self.assertEqual(product.description, '')

    def test_product_blank_comment(self):
        """Test: Comentario puede estar vacío"""
        data = self.product_data.copy()
        data['comment'] = ''
        product = Product.objects.create(**data)
        self.assertEqual(product.comment, '')

    def test_product_without_image(self):
        """Test: Producto puede crearse sin imagen"""
        product = Product.objects.create(**self.product_data)
        self.assertFalse(product.image)

    def test_product_deactivation(self):
        """Test: Producto puede ser desactivado"""
        product = Product.objects.create(**self.product_data)
        product.is_active = False
        product.save()
        self.assertFalse(product.is_active)

    def test_product_stock_update(self):
        """Test: Stock puede ser actualizado"""
        product = Product.objects.create(**self.product_data)
        product.stock = 50
        product.save()
        self.assertEqual(product.stock, 50)

    def test_product_created_at_auto_generated(self):
        """Test: created_at se genera automáticamente"""
        product = Product.objects.create(**self.product_data)
        self.assertIsNotNone(product.created_at)

    def test_product_updated_at_auto_updated(self):
        """Test: updated_at se actualiza automáticamente"""
        product = Product.objects.create(**self.product_data)
        old_updated_at = product.updated_at
        
        product.price = 30000.00
        product.save()
        
        self.assertGreater(product.updated_at, old_updated_at)

    def test_delete_owner_deletes_products(self):
        """Test: Eliminar propietario elimina sus productos (CASCADE)"""
        Product.objects.create(**self.product_data)
        
        user_id = self.user.id
        self.user.delete()
        
        # Verificar que no hay productos del usuario eliminado
        products = Product.objects.filter(owner_id=user_id)
        self.assertEqual(products.count(), 0)

    def test_product_meta_verbose_names(self):
        """Test: Nombres verbose del modelo"""
        self.assertEqual(Product._meta.verbose_name, 'Producto')
        self.assertEqual(Product._meta.verbose_name_plural, 'Productos')

    def test_multiple_products_same_owner(self):
        """Test: Un usuario puede tener múltiples productos"""
        Product.objects.create(
            name='Producto 1', code='PROD-001', price=100, owner=self.user
        )
        Product.objects.create(
            name='Producto 2', code='PROD-002', price=200, owner=self.user
        )
        
        products = Product.objects.filter(owner=self.user)
        self.assertEqual(products.count(), 2)

    def test_slug_persists_on_update(self):
        """Test: Slug no cambia al actualizar el producto"""
        product = Product.objects.create(**self.product_data)
        original_slug = product.slug
        
        product.name = 'Nombre Completamente Nuevo'
        product.save()
        
        self.assertEqual(product.slug, original_slug)

    def test_product_with_special_characters_in_name(self):
        """Test: Producto con caracteres especiales en nombre"""
        data = self.product_data.copy()
        data['name'] = 'Café & Té - Especial'
        data['code'] = 'PROD-SPEC'
        product = Product.objects.create(**data)
        self.assertEqual(product.slug, 'cafe-te-especial')
