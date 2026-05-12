import json
from apps.BistroMaster.models import RestauranteConfig
from django.test import TestCase, Client
from django.urls import reverse
from apps.BistroMaster.models import Administrador

class RestauranteConfigTests(TestCase):
    def setUp(self):
        self.admin = Administrador.objects.create(usuario="admin_cfg", contrasena="123")
        # Forzamos sesión
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()
        self.config = RestauranteConfig.objects.create(is_open=True)

    def test_cp15_restaurante_abierto(self):
        """Prueba de restaurante abierto (HU-04)"""
        url = reverse('restaurante_config_api')
        payload = {"is_open": True}
        
        response = self.client.put(url, data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.config.refresh_from_db()
        self.assertTrue(self.config.is_open)
        self.assertEqual(response.json()['restaurante']['is_open'], True)

    def test_cp16_restaurante_cerrado(self):
        """Prueba de restaurante cerrado (HU-04)"""
        url = reverse('restaurante_config_api')
        payload = {"is_open": False}
        
        response = self.client.put(url, data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.config.refresh_from_db()
        self.assertFalse(self.config.is_open)
        self.assertEqual(response.json()['restaurante']['is_open'], False)
        
        
        
        