from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils.text import slugify

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


class Restaurante(models.Model):
    nombre = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='productos')
    nombre = models.CharField(max_length=120)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    is_available = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} - {self.restaurante.nombre}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En preparación', 'En preparación'),
        ('En camino', 'En camino'),
        ('Entregado', 'Entregado'),
    ]
    
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE)
    mesa = models.IntegerField(null=True, blank=True) # Solo para comandas
    estado = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendiente')
    total = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Datos para domicilios
    cliente_nombre = models.CharField(max_length=100, null=True, blank=True)
    direccion = models.CharField(max_length=200, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.estado}"
