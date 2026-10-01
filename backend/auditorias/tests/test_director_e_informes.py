from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from auditorias.models import (
    Auditoria,
    AuditoriaAuditor,
    Hallazgo,
    Informe,
    PlanMejoramiento,
    SeguimientoAccion,
    UnidadAuditada,
)
from usuarios.models import Usuario


class DirectorEInformesTests(APITestCase):
    def setUp(self):
        self.grupo_admin, _ = Group.objects.get_or_create(name="Administrador")
        self.grupo_auditor, _ = Group.objects.get_or_create(name="Auditor")
        self.grupo_director, _ = Group.objects.get_or_create(name="Director")

        self.admin = Usuario.objects.create_user(email="admin-dir@test.com", password="Test1234!")
        self.admin.groups.add(self.grupo_admin)
        self.auditor = Usuario.objects.create_user(email="auditor-dir@test.com", password="Test1234!")
        self.auditor.groups.add(self.grupo_auditor)
        self.director = Usuario.objects.create_user(email="director@test.com", password="Test1234!")
        self.director.groups.add(self.grupo_director)

        self.unidad = UnidadAuditada.objects.create(nombre_unidad="Unidad", tipo="Académica")
        self.auditoria_asignada = self.crear_auditoria("AUD-DIR-001")
        self.auditoria_ajena = self.crear_auditoria("AUD-DIR-002")
        AuditoriaAuditor.objects.create(
            auditoria=self.auditoria_asignada, auditor=self.auditor, activo=True
        )
        AuditoriaAuditor.objects.create(
            auditoria=self.auditoria_asignada, auditor=self.director, activo=True
        )

        self.hallazgo_asignado = self.crear_hallazgo(self.auditoria_asignada, "H-001")
        self.hallazgo_ajeno = self.crear_hallazgo(self.auditoria_ajena, "H-002")
        plan = PlanMejoramiento.objects.create(
            auditoria=self.auditoria_asignada, fecha_creacion="2026-09-01", estado="Abierto"
        )
        self.plan = plan
        self.seguimiento = SeguimientoAccion.objects.create(
            accion=self.crear_accion(plan, self.hallazgo_asignado),
            porcentaje_avance=10,
            descripcion="Seguimiento",
            fecha_seguimiento="2026-09-02",
            observaciones="Observaciones",
            estado="En proceso",
            registrado_por=self.auditor,
        )

    def crear_auditoria(self, codigo):
        return Auditoria.objects.create(
            codigo=codigo,
            unidad_auditada=self.unidad,
            responsable_unidad="Responsable",
            tipo_auditoria="Interna",
            fecha_inicio="2026-09-01",
            objetivo="Objetivo",
            alcance="Alcance",
            estado="En planeación",
            creado_por=self.admin,
        )

    def crear_hallazgo(self, auditoria, numero):
        return Hallazgo.objects.create(
            auditoria=auditoria,
            numero_hallazgo=numero,
            titulo="Hallazgo",
            condicion="Condición",
            criterio="Criterio",
            causa="Causa",
            efecto="Efecto",
            estado="Abierto",
            recomendaciones="Recomendación",
        )

    def crear_accion(self, plan, hallazgo):
        from auditorias.models import AccionMejoramiento

        return AccionMejoramiento.objects.create(
            plan=plan,
            hallazgo=hallazgo,
            descripcion="Acción",
            responsable="Responsable",
            fecha_inicio="2026-09-01",
            fecha_limite="2026-09-20",
            estado="Abierta",
        )

    def datos_informe(self, auditoria, tipo="Preliminar"):
        return {
            "auditoria": auditoria.id,
            "tipo_informe": tipo,
            "fecha_informe": "2026-09-10",
            "actividades_realizadas": "Actividades",
            "conclusiones": "Conclusiones",
            "observaciones": "",
            "evidencias": "",
        }

    def test_director_lee_auditorias_y_hallazgos_globalmente(self):
        self.client.force_authenticate(self.director)

        auditorias = self.client.get("/api/auditorias/")
        hallazgos = self.client.get("/api/hallazgos/")
        planes = self.client.get("/api/planes-mejoramiento/")
        seguimientos = self.client.get("/api/seguimientos/")
        usuarios = self.client.get("/api/auth/usuarios/")

        self.assertEqual(auditorias.status_code, status.HTTP_200_OK)
        self.assertEqual(hallazgos.status_code, status.HTTP_200_OK)
        self.assertEqual(planes.status_code, status.HTTP_200_OK)
        self.assertEqual(seguimientos.status_code, status.HTTP_200_OK)
        self.assertEqual(usuarios.status_code, status.HTTP_403_FORBIDDEN)
        self.assertSetEqual(
            {item["id"] for item in auditorias.data},
            {self.auditoria_asignada.id, self.auditoria_ajena.id},
        )
        self.assertSetEqual(
            {item["id"] for item in hallazgos.data},
            {self.hallazgo_asignado.id, self.hallazgo_ajeno.id},
        )
        self.assertIn(self.plan.id, {item["id"] for item in planes.data})
        self.assertIn(self.seguimiento.id, {item["id"] for item in seguimientos.data})

    def test_director_administra_recursos_de_auditoria_sin_asignacion(self):
        self.client.force_authenticate(self.director)
        unidad = self.client.post(
            "/api/unidades/",
            {"nombre_unidad": "Unidad del Director", "tipo": "Administrativa"},
            format="json",
        )
        self.assertEqual(unidad.status_code, status.HTTP_201_CREATED)

        auditoria = self.client.post(
            "/api/auditorias/",
            {
                "codigo": "AUD-DIR-003",
                "unidad_auditada": unidad.data["id"],
                "responsable_unidad": "Responsable",
                "tipo_auditoria": "Interna",
                "fecha_inicio": "2026-09-01",
                "fecha_fin": "2026-09-30",
                "objetivo": "Objetivo",
                "alcance": "Alcance",
                "estado": "En planeación",
            },
            format="json",
        )
        self.assertEqual(auditoria.status_code, status.HTTP_201_CREATED)

        asignacion = self.client.post(
            "/api/auditoria-auditores/",
            {"auditoria": auditoria.data["id"], "auditor": self.director.id, "activo": True},
            format="json",
        )
        self.assertEqual(asignacion.status_code, status.HTTP_201_CREATED)

        actualizado = self.client.patch(
            f"/api/hallazgos/{self.hallazgo_ajeno.id}/",
            {"titulo": "Editado por Director sin asignación"},
            format="json",
        )
        eliminado = self.client.delete(f"/api/hallazgos/{self.hallazgo_ajeno.id}/")
        self.assertEqual(actualizado.status_code, status.HTTP_200_OK)
        self.assertEqual(eliminado.status_code, status.HTTP_204_NO_CONTENT)

    def test_director_no_puede_gestionar_usuarios(self):
        self.client.force_authenticate(self.director)

        creado = self.client.post(
            "/api/auth/usuarios/crear/",
            {
                "email": "no-permitido@test.com",
                "first_name": "No",
                "last_name": "Permitido",
                "password": "Test1234!",
                "rol": "Auditor",
            },
            format="json",
        )
        editado = self.client.patch(
            f"/api/auth/usuarios/{self.auditor.id}/",
            {"first_name": "Intento"},
            format="json",
        )

        self.assertEqual(creado.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(editado.status_code, status.HTTP_403_FORBIDDEN)

    def test_dashboard_director_reporta_unidades_activas_e_inactivas(self):
        UnidadAuditada.objects.create(
            nombre_unidad="Unidad inactiva", tipo="Administrativa", activo=False
        )
        self.client.force_authenticate(self.director)

        response = self.client.get("/api/dashboard/resumen/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UnidadAuditada.objects.filter(activo=True).count(), 1)
        self.assertEqual(UnidadAuditada.objects.filter(activo=False).count(), 1)
        self.assertEqual(response.data["unidades_activas"], 1)
        self.assertEqual(response.data["unidades_inactivas"], 1)

    def test_auditor_asignado_crea_y_consulta_seguimiento_con_payload_completo(self):
        accion = self.seguimiento.accion
        self.client.force_authenticate(self.auditor)

        incompleto = self.client.post(
            "/api/seguimientos/",
            {
                "accion": accion.id,
                "porcentaje_avance": 25,
                "descripcion": "Avance sin observaciones",
                "fecha_seguimiento": "2026-09-03",
                "estado": "En proceso",
            },
            format="json",
        )
        self.assertEqual(incompleto.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("observaciones", incompleto.data)

        creado = self.client.post(
            "/api/seguimientos/",
            {
                "accion": accion.id,
                "porcentaje_avance": 25,
                "descripcion": "Avance registrado",
                "fecha_seguimiento": "2026-09-03",
                "observaciones": "Evidencia revisada",
                "estado": "En proceso",
                "evidencias": "acta.pdf",
            },
            format="json",
        )
        self.assertEqual(creado.status_code, status.HTTP_201_CREATED)
        self.assertEqual(creado.data["accion"], accion.id)
        self.assertEqual(creado.data["registrado_por"], self.auditor.id)

        listados = self.client.get("/api/seguimientos/")
        self.assertIn(creado.data["id"], {item["id"] for item in listados.data})

    def test_director_edita_recursos_de_cualquier_auditoria(self):
        self.client.force_authenticate(self.director)

        permitida = self.client.patch(
            f"/api/hallazgos/{self.hallazgo_asignado.id}/",
            {"titulo": "Editado por Director"},
            format="json",
        )
        tambien_permitida = self.client.patch(
            f"/api/hallazgos/{self.hallazgo_ajeno.id}/",
            {"titulo": "No autorizado"},
            format="json",
        )

        self.assertEqual(permitida.status_code, status.HTTP_200_OK)
        self.assertEqual(tambien_permitida.status_code, status.HTTP_200_OK)

    def test_preliminar_pendiente_se_aprueba_y_habilita_definitivo(self):
        self.client.force_authenticate(self.auditor)
        response = self.client.post(
            "/api/informes/", self.datos_informe(self.auditoria_asignada), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        preliminar = Informe.objects.get(pk=response.data["id"])
        self.assertEqual(preliminar.estado, Informe.EstadoRevision.PENDIENTE)

        bloqueado = self.client.post(
            "/api/informes/",
            self.datos_informe(self.auditoria_asignada, "Definitivo"),
            format="json",
        )
        self.assertEqual(bloqueado.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("preliminar aprobado", str(bloqueado.data).lower())

        self.client.force_authenticate(self.director)
        revision = self.client.post(
            f"/api/informes/{preliminar.id}/revisar/",
            {"estado": "Aprobado", "observaciones_revision": "Conforme"},
            format="json",
        )
        self.assertEqual(revision.status_code, status.HTTP_200_OK)
        preliminar.refresh_from_db()
        self.assertEqual(preliminar.estado, Informe.EstadoRevision.APROBADO)
        self.assertEqual(preliminar.revisado_por, self.director)
        self.assertEqual(preliminar.observaciones_revision, "Conforme")
        self.assertIsNotNone(preliminar.fecha_revision)

        self.client.force_authenticate(self.auditor)
        permitido = self.client.post(
            "/api/informes/",
            self.datos_informe(self.auditoria_asignada, "Definitivo"),
            format="json",
        )
        self.assertEqual(permitido.status_code, status.HTTP_201_CREATED)

    def test_auditor_corrige_y_reenvia_preliminar_a_revision(self):
        self.client.force_authenticate(self.auditor)
        creado = self.client.post(
            "/api/informes/", self.datos_informe(self.auditoria_asignada), format="json"
        )
        self.assertEqual(creado.status_code, status.HTTP_201_CREATED)
        informe_id = creado.data["id"]

        self.client.force_authenticate(self.director)
        primera_revision = self.client.post(
            f"/api/informes/{informe_id}/revisar/",
            {
                "estado": "Requiere correcciones",
                "observaciones_revision": "Ajustar las evidencias.",
            },
            format="json",
        )
        self.assertEqual(primera_revision.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.auditor)
        reenvio = self.client.patch(
            f"/api/informes/{informe_id}/",
            {"evidencias": "Evidencias ajustadas"},
            format="json",
        )
        self.assertEqual(reenvio.status_code, status.HTTP_200_OK)
        self.assertEqual(reenvio.data["estado"], Informe.EstadoRevision.PENDIENTE)
        self.assertIsNone(reenvio.data["revisado_por"])
        self.assertIsNone(reenvio.data["fecha_revision"])
        self.assertEqual(reenvio.data["observaciones_revision"], "Ajustar las evidencias.")

        self.client.force_authenticate(self.director)
        segunda_revision = self.client.post(
            f"/api/informes/{informe_id}/revisar/",
            {
                "estado": "Requiere correcciones",
                "observaciones_revision": "Agregar el soporte final.",
            },
            format="json",
        )
        self.assertEqual(segunda_revision.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.auditor)
        segundo_reenvio = self.client.patch(
            f"/api/informes/{informe_id}/",
            {"conclusiones": "Conclusiones corregidas"},
            format="json",
        )
        self.assertEqual(segundo_reenvio.status_code, status.HTTP_200_OK)
        self.assertEqual(segundo_reenvio.data["estado"], Informe.EstadoRevision.PENDIENTE)
        self.assertEqual(
            segundo_reenvio.data["observaciones_revision"],
            "Agregar el soporte final.",
        )

        self.client.force_authenticate(self.director)
        aprobacion = self.client.post(
            f"/api/informes/{informe_id}/revisar/",
            {"estado": "Aprobado"},
            format="json",
        )
        self.assertEqual(aprobacion.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.auditor)
        bloqueado = self.client.patch(
            f"/api/informes/{informe_id}/",
            {"conclusiones": "No debe guardarse"},
            format="json",
        )
        self.assertEqual(bloqueado.status_code, status.HTTP_403_FORBIDDEN)

    def test_director_revisa_informe_aun_sin_asignacion_y_patch_no_cambia_revision(self):
        datos_preliminar = self.datos_informe(self.auditoria_ajena)
        datos_preliminar["auditoria"] = self.auditoria_ajena
        preliminar = Informe.objects.create(
            **datos_preliminar, creado_por=self.admin
        )
        self.client.force_authenticate(self.director)

        patch = self.client.patch(
            f"/api/informes/{preliminar.id}/",
            {"estado": "Aprobado"},
            format="json",
        )
        self.assertEqual(patch.status_code, status.HTTP_400_BAD_REQUEST)

        revision = self.client.post(
            f"/api/informes/{preliminar.id}/revisar/",
            {"estado": "Requiere correcciones", "observaciones_revision": "Ajustar evidencia"},
            format="json",
        )
        self.assertEqual(revision.status_code, status.HTTP_200_OK)
        preliminar.refresh_from_db()
        self.assertEqual(preliminar.estado, Informe.EstadoRevision.CORRECCIONES)
