from django.test import TestCase
from django.apps import apps
from apps.product.apps import UserConfig


class UserConfigTest(TestCase):
    """Tests para la configuración de la app Product"""

    def test_app_config_name(self):
        """Test: Verifica que el nombre del módulo es correcto"""
        self.assertEqual(UserConfig.name, "apps.product")

    def test_app_config_label(self):
        """Test: Verifica que el label de la app es correcto"""
        self.assertEqual(UserConfig.label, "product")

    def test_app_is_registered(self):
        """Test: La app debe estar registrada en Django"""
        app_config = apps.get_app_config("product")
        self.assertIsNotNone(app_config)
        self.assertIsInstance(app_config, UserConfig)

    def test_default_auto_field(self):
        """Test: Verifica el campo auto por defecto"""
        self.assertEqual(UserConfig.default_auto_field, "django.db.models.BigAutoField")
