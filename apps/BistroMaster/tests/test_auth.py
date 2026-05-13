import json

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

    def _login_manual(self):
        """Función auxiliar para simular sesión iniciada"""
        session = self.client.session
        session['admin_id'] = self.admin_db.id
        session.save()
    
    
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
     
    def test_cp04_editar_correo_administrador(self):
        """Prueba de edición de correo administrador (HU-01)"""
        self._login_manual() 
        url = reverse('admin_profile_api')
        payload = {
            "usuario": "Bistro",
            "correo": "nuevo_correo@test.com",
            "contrasena": "",
            "contrasena_confirm": ""
        }

        response = self.client.put(url, data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.admin_db.refresh_from_db()
        self.assertEqual(self.admin_db.correo, "nuevo_correo@test.com")

    def test_cp05_editar_usuario_administrador(self):
        """Prueba de edición de usuario administrador (HU-01)"""
        self._login_manual()
        url = reverse('admin_profile_api')
        payload = {
            "usuario": "BistroNuevo",
            "correo": "admin@test.com",
            "contrasena": "",
            "contrasena_confirm": ""
        }
        response = self.client.put(url, data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.admin_db.refresh_from_db()
        self.assertEqual(self.admin_db.usuario, "BistroNuevo")

    def test_cp06_eliminar_cuenta_administrador(self):
        """Prueba de eliminar cuenta administrador con confirmación (HU-01)"""
        self._login_manual()
        url = reverse('admin_delete_api')
        
        payload = {
            "contrasena": "12345" 
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(payload), 
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['ok'], True)
        self.assertEqual(response.json()['redirect'], "/admin/")
        
        self.assertFalse(Administrador.objects.filter(id=self.admin_db.id).exists())
        self.assertNotIn('admin_id', self.client.session)
       
    def test_cp07_campos_vacios(self):
        """Prueba de campos vacíos (HU-01 / Validación)"""
        response = self.client.post(reverse('admin_login'), {
            'usuario': '',
            'contrasena': ''
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuario o contraseña incorrectos", msg_prefix="El sistema no advirtió que los campos son obligatorios")
        self.assertNotIn('admin_id', self.client.session)    
        
    