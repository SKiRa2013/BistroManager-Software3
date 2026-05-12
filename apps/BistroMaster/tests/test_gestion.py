import json
from django.test import TestCase, Client
from django.urls import reverse
from apps.BistroMaster.models import Administrador, Mesero, Domiciliario

class GestionUsuariosTests(TestCase):
    def setUp(self):
        self.admin = Administrador.objects.create(
            usuario="admin_test",
            correo="admin@test.com",
            contrasena="pbkdf2_sha256$..." 
        )
        self.client = Client()
        
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

    def test_cp05_crear_mesero_valido(self):
        """Prueba de crear mesero válido (HU-02 / Positiva)"""
        url = reverse('meseros_api')
        payload = {
            "nombre": "Juan Mesero",
            "usuario": "juanito",
            "contrasena": "Mesero123!",
            "contrasena_confirm": "Mesero123!",
            "contrato": "Tiempo completo",
            "disponible": True
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(payload), 
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Mesero.objects.filter(usuario="juanito").exists())
        self.assertEqual(response.json()['ok'], True)

    def test_cp06_crear_domiciliario_valido(self):
        """Prueba de crear domiciliario válido (HU-02 / Positiva)"""
        url = reverse('domiciliarios_api')
        payload = {
            "nombre": "Carlos Domicilios",
            "usuario": "carlos_dom",
            "contrasena": "Password123!",
            "contrasena_confirm": "Password123!",
            "contrato": "Prestación de servicios",
            "disponible": True
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(payload), 
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Domiciliario.objects.filter(usuario="carlos_dom").exists())
        self.assertEqual(response.json()['ok'], True)
    
    
    def test_cp07_campos_incompletos_mesero(self):
        """Prueba de campos incompletos (HU-02 / Negativa)"""
        url = reverse('meseros_api')
        payload = {
            "nombre": "", 
            "usuario": "mesero_error",
            "contrasena": "123",
            "contrato": "Medio tiempo"
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(payload), 
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Faltan campos", response.json()['error'])

    def test_cp08_campos_incompletos_domiciliario(self):
        """Prueba de campos incompletos domiciliario (HU-02 / Validación)"""
        url = reverse('domiciliarios_api')
        payload = {
            "nombre": "Incompleto Test",
            "usuario": "incompleto_user"
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(payload), 
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Faltan campos", response.json()['error'])
    
    def test_cp09_crear_domiciliario_valido(self):
        """Prueba de crear domiciliario (HU-03 / Positiva)"""
        url = reverse('domiciliarios_api')
        payload = {
            "nombre": "Pedro Domicilios",
            "usuario": "pedrito",
            "contrasena": "Pass123!",
            "contrasena_confirm": "Pass123!",
            "contrato": "Por horas",
            "disponible": True
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(payload), 
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Domiciliario.objects.filter(usuario="pedrito").exists())

    def test_cp10_usuario_duplicado_domiciliario(self):
        """Prueba de usuario duplicado domiciliario (HU-02 / Negativa)"""
        Domiciliario.objects.create(
            nombre="Original",
            usuario="duplicado_user",
            contrasena="123",
            tipo_contrato="Tiempo completo"
        )
        
        url = reverse('domiciliarios_api')
        payload = {
            "nombre": "Copia",
            "usuario": "duplicado_user",
            "contrasena": "456",
            "contrasena_confirm": "456",
            "contrato": "Medio tiempo"
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(payload), 
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Ya existe un domiciliario con ese usuario", response.json()['error'])

    def test_cp11_desactivar_mesero(self):
        """Prueba de desactivar mesero (HU-03)"""
        m = Mesero.objects.create(
            nombre="Mesero Activo", usuario="mes_act", 
            tipo_contrato="Medio tiempo", disponible=True
        )
        url = reverse('mesero_api', kwargs={'mesero_id': m.id})
        
        payload = {
            "nombre": m.nombre,
            "usuario": m.usuario,
            "contrato": m.tipo_contrato,
            "disponible": False 
        }
        
        response = self.client.put(
            url, data=json.dumps(payload), content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 200)
        m.refresh_from_db() 
        self.assertFalse(m.disponible)
        
        
    def test_cp12_desactivar_domiciliario(self):
        """Prueba de desactivar domiciliario (HU-03)"""
        # Creamos uno activo (disponible=True)
        d = Domiciliario.objects.create(
            nombre="Domi Activo", usuario="domi_act", 
            tipo_contrato="Por horas", disponible=True
        )
        url = reverse('domiciliario_api', kwargs={'domiciliario_id': d.id})
        
        # Enviamos disponible: False para desactivarlo
        payload = {
            "nombre": d.nombre,
            "usuario": d.usuario,
            "contrato": d.tipo_contrato,
            "disponible": False 
        }
        
        response = self.client.put(
            url, data=json.dumps(payload), content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 200)
        d.refresh_from_db() 
        self.assertFalse(d.disponible)

    def test_cp13_activar_mesero(self):
        """Prueba de activar mesero (HU-03)"""
        m = Mesero.objects.create(
            nombre="Mesero Inactivo", usuario="mes_in", 
            tipo_contrato="Medio tiempo", disponible=False
        )
        url = reverse('mesero_api', kwargs={'mesero_id': m.id})
        
        payload = {
            "nombre": m.nombre, "usuario": m.usuario,
            "contrato": m.tipo_contrato, "disponible": True
        }
        
        response = self.client.put(url, data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        m.refresh_from_db()
        self.assertTrue(m.disponible)

    def test_cp14_activar_domiciliario(self):
        """Prueba de activar domiciliario (HU-03)"""
        d = Domiciliario.objects.create(
            nombre="Domi Inactivo", usuario="domi_in", 
            tipo_contrato="Por horas", disponible=False
        )
        url = reverse('domiciliario_api', kwargs={'domiciliario_id': d.id})
        
        payload = {
            "nombre": d.nombre, "usuario": d.usuario,
            "contrato": d.tipo_contrato, "disponible": True
        }
        
        response = self.client.put(url, data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        d.refresh_from_db()
        self.assertTrue(d.disponible)
        
        
    