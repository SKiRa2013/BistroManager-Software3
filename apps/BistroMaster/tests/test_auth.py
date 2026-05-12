from django.test import TestCase, Client
from django.urls import reverse
from apps.BistroMaster.models import Administrador 
from django.contrib.auth.hashers import make_password

class LoginTests(TestCase):
    def setUp(self):
        self.admin_db = Administrador.objects.create(
            usuario="Bistro",
            correo="admin@test.com"
        )
        self.admin_db.contrasena = make_password("12345")
        self.admin_db.save()
        self.client = Client()

    def test_cp01_login_exitoso(self):
        """Prueba de login exitoso (HU-01 / Positiva)"""
        response = self.client.post(reverse('admin_login'), {
            'usuario': 'Bistro',
            'contrasena': '12345'
        })
        
        self.assertEqual(self.client.session['admin_id'], self.admin_db.id)
        self.assertRedirects(response, reverse('admin_panel'))

    def test_cp02_contrasena_incorrecta(self):
        """Prueba de contraseña incorrecta (HU-01 / Negativa)"""
        response = self.client.post(reverse('admin_login'), {
            'usuario': 'Bistro',
            'contrasena': '0000'
        })
        self.assertContains(response, "Usuario o contraseña incorrectos")
        
    def test_cp03_usuario_inexistente(self):
        """Prueba de usuario inexistente (HU-01 / Negativa)"""
        response = self.client.post(reverse('admin_login'), {
            'usuario': 'fake',
            'contrasena': '1234'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuario o contraseña incorrectos")
        self.assertNotIn('admin_id', self.client.session)
        
    def test_cp04_campos_vacios(self):
        """Prueba de campos vacíos (HU-01 / Validación)"""
        response = self.client.post(reverse('admin_login'), {
            'usuario': '',
            'contrasena': ''
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuario o contraseña incorrectos", msg_prefix="El sistema no advirtió que los campos son obligatorios")
        self.assertNotIn('admin_id', self.client.session)    
        
    