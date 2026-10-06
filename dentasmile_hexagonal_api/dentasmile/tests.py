from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from dentasmile.domain.entities import Cita
from datetime import date, time


class EntidadesTests(APITestCase):
    def test_cita_cancelada_no_ocupa_horario(self):
        c = Cita("Ana", "123", 1, date(2026, 10, 5), time(10, 0), estado="cancelada")
        self.assertFalse(c.ocupa_horario())


class ApiBase(APITestCase):
    def setUp(self):
        user = User.objects.create_user("tester", password="pass12345")
        self.token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def crear_tratamiento(self, nombre="Limpieza Dental"):
        r = self.client.post("/api/tratamientos/", {"nombre": nombre, "precio": 35000}, format="json")
        self.assertEqual(r.status_code, 201)
        return r.json()

    def datos_cita(self, tratamiento_id, **extra):
        d = {"paciente_nombre": "Benja", "paciente_telefono": "+56911112222",
             "tratamiento_id": tratamiento_id, "fecha": "2026-10-05", "hora": "10:00"}
        d.update(extra)
        return d


class AutenticacionTests(APITestCase):
    def test_sin_token_401(self):
        for url in ("/api/tratamientos/", "/api/citas/"):
            self.assertEqual(self.client.get(url).status_code, 401)

    def test_obtener_token(self):
        User.objects.create_user("u", password="pass12345")
        r = self.client.post("/api/token/", {"username": "u", "password": "pass12345"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("token", r.json())


class TratamientoApiTests(ApiBase):
    def test_crud_completo(self):
        t = self.crear_tratamiento()
        self.assertEqual(len(self.client.get("/api/tratamientos/").json()), 1)
        self.assertEqual(self.client.get(f"/api/tratamientos/{t['id']}/").json()["nombre"], "Limpieza Dental")
        r = self.client.put(f"/api/tratamientos/{t['id']}/", {"precio": 40000}, format="json")
        self.assertEqual(r.json()["precio"], 40000)
        self.assertEqual(self.client.delete(f"/api/tratamientos/{t['id']}/").status_code, 204)
        self.assertEqual(self.client.get(f"/api/tratamientos/{t['id']}/").status_code, 404)

    def test_nombre_duplicado_400(self):
        self.crear_tratamiento()
        r = self.client.post("/api/tratamientos/", {"nombre": "limpieza dental"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_no_elimina_con_citas_409(self):
        t = self.crear_tratamiento()
        self.client.post("/api/citas/", self.datos_cita(t["id"]), format="json")
        self.assertEqual(self.client.delete(f"/api/tratamientos/{t['id']}/").status_code, 409)


class CitaApiTests(ApiBase):
    def test_crud_completo(self):
        t = self.crear_tratamiento()
        r = self.client.post("/api/citas/", self.datos_cita(t["id"]), format="json")
        self.assertEqual(r.status_code, 201)
        c = r.json()
        self.assertEqual(c["tratamiento_nombre"], "Limpieza Dental")
        self.assertEqual(c["estado"], "pendiente")
        self.assertEqual(c["hora"], "10:00")
        self.assertEqual(len(self.client.get("/api/citas/").json()), 1)
        self.assertEqual(self.client.get(f"/api/citas/{c['id']}/").status_code, 200)
        r = self.client.put(f"/api/citas/{c['id']}/", {"estado": "confirmada"}, format="json")
        self.assertEqual(r.json()["estado"], "confirmada")
        self.assertEqual(self.client.delete(f"/api/citas/{c['id']}/").status_code, 204)
        self.assertEqual(self.client.get(f"/api/citas/{c['id']}/").status_code, 404)

    def test_tratamiento_inexistente_400(self):
        r = self.client.post("/api/citas/", self.datos_cita(999), format="json")
        self.assertEqual(r.status_code, 400)

    def test_horario_ocupado_409_y_cancelada_libera(self):
        t = self.crear_tratamiento()
        primera = self.client.post("/api/citas/", self.datos_cita(t["id"]), format="json").json()
        r = self.client.post("/api/citas/", self.datos_cita(t["id"], paciente_nombre="Otro"), format="json")
        self.assertEqual(r.status_code, 409)
        self.client.put(f"/api/citas/{primera['id']}/", {"estado": "cancelada"}, format="json")
        r = self.client.post("/api/citas/", self.datos_cita(t["id"], paciente_nombre="Otro"), format="json")
        self.assertEqual(r.status_code, 201)

    def test_estado_invalido_400(self):
        t = self.crear_tratamiento()
        r = self.client.post("/api/citas/", self.datos_cita(t["id"], estado="inventado"), format="json")
        self.assertEqual(r.status_code, 400)
