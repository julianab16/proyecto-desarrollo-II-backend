from django.test import TestCase

from apps.product.models import Product


class ProductModelTest(TestCase):
    """Unit test for Product model save() method"""

    def test_slug_automatically_generated_on_save(self):
        """
        Verify that save() method automatically generates a slug
        based on the product name when none is provided.
        """
        # Create a product without specifying slug
        product = Product.objects.create(
            name="Premium Elegant Shirt",
            code="SHIRT-001",
            price=99.99,
            stock=10
        )

        # Verify that slug was automatically generated
        self.assertEqual(product.slug, "premium-elegant-shirt")
        
        # Verify that product was saved correctly
        self.assertIsNotNone(product.id)
        self.assertEqual(product.name, "Premium Elegant Shirt")
