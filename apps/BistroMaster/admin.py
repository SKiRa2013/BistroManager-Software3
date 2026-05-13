from django.contrib import admin

from .models import (
    Administrador, Domiciliario, Mesero, RestauranteConfig,
    Restaurante, Order, Producto
)


@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ("usuario", "correo")
    search_fields = ("usuario", "correo")


@admin.register(Mesero)
class MeseroAdmin(admin.ModelAdmin):
    list_display = ("nombre", "usuario", "tipo_contrato", "disponible")
    search_fields = ("nombre", "usuario")
    list_filter = ("tipo_contrato", "disponible")


@admin.register(Domiciliario)
class DomiciliarioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "usuario", "tipo_contrato", "disponible")
    search_fields = ("nombre", "usuario")
    list_filter = ("tipo_contrato", "disponible")


@admin.register(RestauranteConfig)
class RestauranteConfigAdmin(admin.ModelAdmin):
    list_display = ("is_open", "updated_at")


@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug")

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "is_available", "stock_quantity")
    list_filter = ("is_available", "restaurante")
