from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    ADMINISTRADOR = "ADMINISTRADOR"
    CLIENTE = "CLIENTE"
    VENDEDOR = "VENDEDOR"

    ROLES = [
        (ADMINISTRADOR, "Administrador"),
        (CLIENTE, "Cliente"),
        (VENDEDOR, "Vendedor"),
    ]

    role = models.CharField(
        max_length=15, choices=ROLES, default=CLIENTE, verbose_name="Rol"
    )

    phone_number = models.CharField(
        max_length=10,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r"^(3|6)\d{9}$",
                message="No es un número de teléfono válido",
                code="invalid_phonenumber",
            )
        ],
        verbose_name="Número teléfono",
    )

    dni = models.CharField(
        max_length=10,
        unique=True,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r"^\d{7,10}$",
                message="No es un número de documento válido",
                code="invalid_dni",
            )
        ],
        verbose_name="Cédula ciudadanía",
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "email",
        "dni",
        "phone_number",
        "role",
    ]

    class Meta:
        db_table = "user"
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["id"]

    def __str__(self):
        return self.username or self.dni

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.upper()
        self.last_name = self.last_name.upper()
        self.email = self.email.lower()
        if self.password and not self.password.startswith("pbkdf2_"):
            self.set_password(self.password)
        super().save(*args, **kwargs)
