from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from auditorias.models import Auditoria, AuditoriaAuditor, UnidadAuditada
from usuarios.models import Usuario


class EquipoAuditorApiTests(APITestCase):
    def setUp(self):
        self.grupo_admin = Group.objects.create(name="Administrador")
        self.grupo_auditor = Group.objects.create(name="Auditor")
        self.admin = Usuario.objects.create_user(
            email="admin-equipo@test.com", password="Test1234!"
        )
        self.admin.groups.add(self.grupo_admin)
        self.auditor_creador = Usuario.objects.create_user(
            email="creador-equipo@test.com", password="Test1234!"
        )
        self.auditor_creador.groups.add(self.grupo_auditor)
        self.auditor_equipo = Usuario.objects.create_user(
            email="equipo-auditor@test.com", password="Test1234!"
        )
        self.auditor_equipo.groups.add(self.grupo_auditor)
        self.unidad = UnidadAuditada.objects.create(
            nombre_unidad="Unidad de pruebas", tipo="Académica"
        )

    def datos_auditoria(self, codigo):
        return {
            "codigo": codigo,
            "unidad_auditada": self.unidad.id,
            "responsable_unidad": "Responsable",
            "tipo_auditoria": "Interna",
            "fecha_inicio": "2026-09-01",
            "fecha_fin": "2026-09-30",
            "objetivo": "Objetivo",
            "alcance": "Alcance",
            "estado": "En planeación",
        }

    def test_auditor_puede_crear_auditoria_con_equipo_una_sola_vez(self):
        self.client.force_authenticate(self.auditor_creador)
        payload = self.datos_auditoria("AUD-EQUIPO-001")
        payload["equipo_auditor"] = [self.auditor_creador.id, self.auditor_equipo.id]

        response = self.client.post("/api/auditorias/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        auditoria = Auditoria.objects.get(codigo="AUD-EQUIPO-001")
        self.assertSetEqual(
            set(
                AuditoriaAuditor.objects.filter(auditoria=auditoria).values_list(
                    "auditor_id", flat=True
                )
            ),
            {self.auditor_creador.id, self.auditor_equipo.id},
        )

        response = self.client.post(
            "/api/auditoria-auditores/",
            {"auditoria": auditoria.id, "auditor": self.auditor_equipo.id, "activo": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(
            f"/api/auditorias/{auditoria.id}/",
            {"equipo_auditor": [self.auditor_creador.id]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            AuditoriaAuditor.objects.filter(auditoria=auditoria, activo=True).count(), 2
        )

    def test_administrador_puede_desactivar_y_reactivar_asignacion(self):
        self.client.force_authenticate(self.admin)
        payload = self.datos_auditoria("AUD-EQUIPO-002")
        response = self.client.post("/api/auditorias/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        asignacion = AuditoriaAuditor.objects.create(
            auditoria_id=response.data["id"], auditor=self.auditor_equipo, activo=True
        )
        url = f"/api/auditoria-auditores/{asignacion.id}/"

        response = self.client.patch(url, {"activo": False}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        asignacion.refresh_from_db()
        self.assertFalse(asignacion.activo)

        response = self.client.patch(url, {"activo": True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        asignacion.refresh_from_db()
        self.assertTrue(asignacion.activo)
