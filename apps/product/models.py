from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify

User = get_user_model()

class Product(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nombre")
    code_validator = RegexValidator(
        regex=r"^[A-Z0-9\-]+$",
        message="Solo letras mayúsculas, números y guiones.")
    code = models.CharField(
        max_length=30,
        unique=True,
        validators=[code_validator],
        verbose_name="Código")
    slug = models.SlugField(
        max_length=160, unique=True, blank=True, verbose_name="Slug"
    )
    description = models.TextField(blank=True, verbose_name="Descripción")
    comment = models.TextField(blank=True, verbose_name="Comentario")
    image = models.ImageField(
        upload_to="products/%Y/%m/%d/",
        blank=True,
        null=True,
        verbose_name="Imagen")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Precio"
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Actualizado")
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Creador",
        null=True,
        blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or self.code
            slug = base
            counter = 1
            while Product.objects.filter(
                    slug=slug).exclude(
                    pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-created_at"]
