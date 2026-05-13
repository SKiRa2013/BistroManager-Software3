from django.contrib.auth.hashers import make_password
from django.db import models


class Administrador(models.Model):
    usuario = models.CharField(max_length=50, unique=True)
    correo = models.EmailField(max_length=254, unique=True, null=True, blank=True)
    contrasena = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.usuario

    def set_password(self, raw_password: str) -> None:
        self.contrasena = make_password(raw_password)


class Mesero(models.Model):
    CONTRATO_CHOICES = [
        ("Tiempo completo", "Tiempo completo"),
        ("Medio tiempo", "Medio tiempo"),
        ("Por horas", "Por horas"),
        ("Prestación de servicios", "Prestación de servicios"),
    ]

    nombre = models.CharField(max_length=120, unique=True)
    usuario = models.CharField(max_length=50, unique=True)
    contrasena = models.CharField(max_length=128)
    tipo_contrato = models.CharField(max_length=40, choices=CONTRATO_CHOICES)
    disponible = models.BooleanField(default=True)

    def set_password(self, raw_password: str) -> None:
        self.contrasena = make_password(raw_password)

    def __str__(self) -> str:
        return self.nombre


class Domiciliario(models.Model):
    CONTRATO_CHOICES = Mesero.CONTRATO_CHOICES

    nombre = models.CharField(max_length=120, unique=True)
    usuario = models.CharField(max_length=50, unique=True)
    contrasena = models.CharField(max_length=128)
    tipo_contrato = models.CharField(max_length=40, choices=CONTRATO_CHOICES)
    disponible = models.BooleanField(default=True)

    def set_password(self, raw_password: str) -> None:
        self.contrasena = make_password(raw_password)

    def __str__(self) -> str:
        return self.nombre


class RestauranteConfig(models.Model):
    is_open = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return "RestauranteConfig"
