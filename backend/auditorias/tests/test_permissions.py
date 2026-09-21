"""
Tests de permisos por rol (Administrador / Auditor / Usuario consulta)
para el Sistema de Gestión de Auditorías.

UBICACIÓN SUGERIDA: auditorias/tests/test_permissions.py
(si no tienes carpeta tests/, créala con un __init__.py vacío,
o coloca el archivo directamente como auditorias/tests_permissions.py)

CÓMO EJECUTAR:
    python manage.py test auditorias.tests.test_permissions

NOTA IMPORTANTE:
Ajusta los nombres de los campos si en tu código real difieren de los
que aparecen en tu documentación (por ejemplo, si UnidadAuditada usa
otro nombre de campo distinto a 'nombre_unidad', o si Auditoria usa
otro valor de 'estado' por defecto). Busca los comentarios "# AJUSTAR"
para ubicar rápido los puntos que dependen de tu implementación exacta.
"""

from django.contrib.auth.models import Group
from django.db import connection
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from usuarios.models import Usuario
from auditorias.models import (
    AccionMejoramiento,
    Auditoria,
    AuditoriaAuditor,
    CronogramaActividades,
    DocumentoGenerado,
    Hallazgo,
    HistorialCambio,
    Informe,
    NotificacionAlerta,
    OportunidadMejora,
    PlanAuditoria,
    PlanMejoramiento,
    SeguimientoAccion,
    UnidadAuditada,
)


class BasePermissionTestCase(APITestCase):
    """
    Clase base: crea los 3 roles, 3 usuarios (uno por rol) y datos
    mínimos de auditoría para reutilizar en todos los tests.
    """

    @classmethod
    def setUpClass(cls):
        cls.ensure_cronograma_actividades_table()
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        # --- Grupos (deben coincidir EXACTO con los que ya tienes creados) ---
        cls.grupo_admin, _ = Group.objects.get_or_create(name="Administrador")
        cls.grupo_auditor, _ = Group.objects.get_or_create(name="Auditor")
        cls.grupo_consulta, _ = Group.objects.get_or_create(name="Usuario consulta")

        # --- Usuarios de prueba ---
        cls.user_admin = Usuario.objects.create_user(
            email="admin_test@test.com", password="Test1234!"
        )
        cls.user_admin.groups.add(cls.grupo_admin)

        cls.user_auditor = Usuario.objects.create_user(
            email="auditor_test@test.com", password="Test1234!"
        )
        cls.user_auditor.groups.add(cls.grupo_auditor)

        # Auditor "ajeno": mismo rol, pero NO asignado a la auditoría de prueba
        cls.user_auditor_ajeno = Usuario.objects.create_user(
            email="auditor_ajeno@test.com", password="Test1234!"
        )
        cls.user_auditor_ajeno.groups.add(cls.grupo_auditor)

        cls.user_consulta = Usuario.objects.create_user(
            email="consulta_test@test.com", password="Test1234!"
        )
        cls.user_consulta.groups.add(cls.grupo_consulta)

        # --- Datos base ---
        cls.unidad = UnidadAuditada.objects.create(
            nombre_unidad="Facultad de Ingeniería",  # AJUSTAR si el campo se llama distinto
            tipo="Académica",
            descripcion="Unidad de prueba",
            activo=True,
        )

        cls.auditoria = Auditoria.objects.create(
            codigo="AUD-TEST-001",
            unidad_auditada=cls.unidad,
            responsable_unidad="Responsable Test",
            tipo_auditoria="Interna",
            fecha_inicio="2026-01-01",
            fecha_fin="2026-01-31",
            objetivo="Objetivo de prueba",
            alcance="Alcance de prueba",
            estado="En planeación",  # AJUSTAR al valor real que uses
            creado_por=cls.user_admin,
        )

        # Asignamos user_auditor (NO el ajeno) a esta auditoría
        AuditoriaAuditor.objects.create(
            auditoria=cls.auditoria,
            auditor=cls.user_auditor,
            activo=True,
        )

        cls.hallazgo = Hallazgo.objects.create(
            auditoria=cls.auditoria,
            numero_hallazgo=1,
            titulo="Hallazgo de prueba",
            condicion="Condición X",
            criterio="Criterio Y",
            causa="Causa Z",
            efecto="Efecto W",
            estado="Abierto",  # AJUSTAR al valor real
            recomendaciones="Recomendación de prueba",
        )

        # AJUSTAR: nombres de las rutas según tu urls.py / router de DRF
        cls.url_auditorias_list = "/api/auditorias/"
        cls.url_auditoria_detail = f"/api/auditorias/{cls.auditoria.id}/"
        cls.url_hallazgos_list = "/api/hallazgos/"
        cls.url_hallazgo_detail = f"/api/hallazgos/{cls.hallazgo.id}/"

        cls.auditoria_ajena = Auditoria.objects.create(
            codigo="AUD-TEST-AJENA",
            unidad_auditada=cls.unidad,
            responsable_unidad="Responsable Ajeno",
            tipo_auditoria="Interna",
            fecha_inicio="2026-05-01",
            fecha_fin="2026-05-31",
            objetivo="Objetivo ajeno",
            alcance="Alcance ajeno",
            estado="En planeación",
            creado_por=cls.user_admin,
        )
        AuditoriaAuditor.objects.create(
            auditoria=cls.auditoria_ajena,
            auditor=cls.user_auditor_ajeno,
            activo=True,
        )

        cls.auditoria_inactiva = Auditoria.objects.create(
            codigo="AUD-TEST-INACTIVA",
            unidad_auditada=cls.unidad,
            responsable_unidad="Responsable Inactivo",
            tipo_auditoria="Interna",
            fecha_inicio="2026-06-01",
            fecha_fin="2026-06-30",
            objetivo="Objetivo inactivo",
            alcance="Alcance inactivo",
            estado="En planeación",
            creado_por=cls.user_admin,
        )
        AuditoriaAuditor.objects.create(
            auditoria=cls.auditoria_inactiva,
            auditor=cls.user_auditor,
            activo=False,
        )

        cls.hallazgo_ajeno = Hallazgo.objects.create(
            auditoria=cls.auditoria_ajena,
            numero_hallazgo=2,
            titulo="Hallazgo ajeno",
            condicion="Condición ajena",
            criterio="Criterio ajeno",
            causa="Causa ajena",
            efecto="Efecto ajeno",
            estado="Abierto",
            recomendaciones="Recomendación ajena",
        )
        cls.hallazgo_inactivo = Hallazgo.objects.create(
            auditoria=cls.auditoria_inactiva,
            numero_hallazgo=3,
            titulo="Hallazgo inactivo",
            condicion="Condición inactiva",
            criterio="Criterio inactivo",
            causa="Causa inactiva",
            efecto="Efecto inactivo",
            estado="Abierto",
            recomendaciones="Recomendación inactiva",
        )

        cls.informe = Informe.objects.create(
            auditoria=cls.auditoria,
            tipo_informe="Final",
            fecha_informe="2026-01-31",
            actividades_realizadas="Actividades",
            conclusiones="Conclusiones",
            creado_por=cls.user_admin,
        )
        cls.informe_ajeno = Informe.objects.create(
            auditoria=cls.auditoria_ajena,
            tipo_informe="Final",
            fecha_informe="2026-05-31",
            actividades_realizadas="Actividades ajenas",
            conclusiones="Conclusiones ajenas",
            creado_por=cls.user_admin,
        )

        cls.plan_auditoria = PlanAuditoria.objects.create(
            auditoria=cls.auditoria,
            criterios="Criterios",
            riesgos_oportunidades="Riesgos",
            documentos_referencia="Documentos",
            fecha_creacion="2026-01-01",
        )
        cls.plan_auditoria_ajeno = PlanAuditoria.objects.create(
            auditoria=cls.auditoria_ajena,
            criterios="Criterios ajenos",
            riesgos_oportunidades="Riesgos ajenos",
            documentos_referencia="Documentos ajenos",
            fecha_creacion="2026-05-01",
        )

        cls.oportunidad = OportunidadMejora.objects.create(
            auditoria=cls.auditoria,
            numero_oportunidad="OP-1",
            descripcion="Oportunidad",
            recomendacion="Recomendación",
            fecha_creacion="2026-01-02",
            estado="Abierta",
        )
        cls.oportunidad_ajena = OportunidadMejora.objects.create(
            auditoria=cls.auditoria_ajena,
            numero_oportunidad="OP-2",
            descripcion="Oportunidad ajena",
            recomendacion="Recomendación ajena",
            fecha_creacion="2026-05-02",
            estado="Abierta",
        )

        cls.cronograma = CronogramaActividades.objects.create(
            plan_auditoria=cls.plan_auditoria,
            fecha_actividad="2026-01-03",
            hora="09:00",
            actividad="Actividad",
            auditado="Auditado",
        )
        cls.cronograma_ajeno = CronogramaActividades.objects.create(
            plan_auditoria=cls.plan_auditoria_ajeno,
            fecha_actividad="2026-05-03",
            hora="09:00",
            actividad="Actividad ajena",
            auditado="Auditado ajeno",
        )

        cls.historial = HistorialCambio.objects.create(
            usuario=cls.user_admin,
            auditoria=cls.auditoria,
            tipo_accion="Creación",
            descripcion="Historial",
        )
        cls.historial_ajeno = HistorialCambio.objects.create(
            usuario=cls.user_admin,
            auditoria=cls.auditoria_ajena,
            tipo_accion="Creación",
            descripcion="Historial ajeno",
        )

        cls.plan_mejoramiento = PlanMejoramiento.objects.create(
            auditoria=cls.auditoria,
            fecha_creacion="2026-01-04",
            estado="Abierto",
        )
        cls.plan_mejoramiento_ajeno = PlanMejoramiento.objects.create(
            auditoria=cls.auditoria_ajena,
            fecha_creacion="2026-05-04",
            estado="Abierto",
        )

        cls.accion = AccionMejoramiento.objects.create(
            plan=cls.plan_mejoramiento,
            hallazgo=cls.hallazgo,
            descripcion="Acción",
            responsable="Responsable",
            fecha_inicio="2026-01-05",
            fecha_limite="2026-01-20",
            estado="Abierta",
        )
        cls.accion_ajena = AccionMejoramiento.objects.create(
            plan=cls.plan_mejoramiento_ajeno,
            hallazgo=cls.hallazgo_ajeno,
            descripcion="Acción ajena",
            responsable="Responsable ajeno",
            fecha_inicio="2026-05-05",
            fecha_limite="2026-05-20",
            estado="Abierta",
        )

        cls.seguimiento = SeguimientoAccion.objects.create(
            accion=cls.accion,
            porcentaje_avance=10,
            descripcion="Seguimiento",
            fecha_seguimiento="2026-01-06",
            observaciones="Observaciones",
            estado="En proceso",
            registrado_por=cls.user_admin,
        )
        cls.seguimiento_ajeno = SeguimientoAccion.objects.create(
            accion=cls.accion_ajena,
            porcentaje_avance=10,
            descripcion="Seguimiento ajeno",
            fecha_seguimiento="2026-05-06",
            observaciones="Observaciones ajenas",
            estado="En proceso",
            registrado_por=cls.user_admin,
        )

        cls.documento = DocumentoGenerado.objects.create(
            auditoria=cls.auditoria,
            tipo_documento="Informe",
            formato="PDF",
            fecha_generacion="2026-01-07",
            generado_por=cls.user_admin,
        )
        cls.documento_ajeno = DocumentoGenerado.objects.create(
            auditoria=cls.auditoria_ajena,
            tipo_documento="Informe",
            formato="PDF",
            fecha_generacion="2026-05-07",
            generado_por=cls.user_admin,
        )

        cls.notificacion = NotificacionAlerta.objects.create(
            accion=cls.accion,
            usuario=cls.user_auditor,
            tipo_alerta="Recordatorio",
            mensaje="Mensaje",
        )
        cls.notificacion_ajena = NotificacionAlerta.objects.create(
            accion=cls.accion_ajena,
            usuario=cls.user_auditor_ajeno,
            tipo_alerta="Recordatorio",
            mensaje="Mensaje ajeno",
        )

    def response_ids(self, response):
        data = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        return {item["id"] for item in data}

    @classmethod
    def ensure_cronograma_actividades_table(cls):
        table_name = CronogramaActividades._meta.db_table

        if table_name in connection.introspection.table_names():
            return

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(CronogramaActividades)


class AdministradorPermissionTests(BasePermissionTestCase):
    def test_admin_puede_listar_auditorias(self):
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.get(self.url_auditorias_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_puede_crear_auditoria(self):
        self.client.force_authenticate(user=self.user_admin)
        payload = {
            "codigo": "AUD-TEST-002",
            "unidad_auditada": self.unidad.id,
            "responsable_unidad": "Otro responsable",
            "tipo_auditoria": "Interna",
            "fecha_inicio": "2026-02-01",
            "fecha_fin": "2026-02-28",
            "objetivo": "Objetivo 2",
            "alcance": "Alcance 2",
            "estado": "En planeación",
        }
        response = self.client.post(self.url_auditorias_list, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_puede_editar_cualquier_auditoria(self):
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.patch(
            self.url_auditoria_detail, {"objetivo": "Objetivo actualizado"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_puede_eliminar_auditoria(self):
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.delete(self.url_auditoria_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AuditorPermissionTests(BasePermissionTestCase):
    def test_auditor_puede_crear_auditoria(self):
        """Confirmado como comportamiento intencional: cualquier Auditor
        puede crear auditorías nuevas."""
        self.client.force_authenticate(user=self.user_auditor)
        payload = {
            "codigo": "AUD-TEST-003",
            "unidad_auditada": self.unidad.id,
            "responsable_unidad": "Responsable X",
            "tipo_auditoria": "Interna",
            "fecha_inicio": "2026-03-01",
            "fecha_fin": "2026-03-31",
            "objetivo": "Objetivo 3",
            "alcance": "Alcance 3",
            "estado": "En planeación",
        }
        response = self.client.post(self.url_auditorias_list, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_auditor_asignado_puede_editar_su_auditoria(self):
        self.client.force_authenticate(user=self.user_auditor)
        response = self.client.patch(
            self.url_auditoria_detail, {"objetivo": "Editado por auditor asignado"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auditor_ajeno_no_puede_editar_auditoria(self):
        """Punto crítico: un auditor NO asignado a esta auditoría no
        debe poder modificarla."""
        self.client.force_authenticate(user=self.user_auditor_ajeno)
        response = self.client.patch(
            self.url_auditoria_detail, {"objetivo": "Intento no autorizado"}
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND],
        )
    def test_auditor_ajeno_no_puede_ver_detalle_auditoria(self):
        self.client.force_authenticate(user=self.user_auditor_ajeno)
        response = self.client.get(self.url_auditoria_detail)
        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND],
        )

    def test_auditor_solo_lista_auditorias_asignadas_activas(self):
        self.client.force_authenticate(user=self.user_auditor)
        response = self.client.get(self.url_auditorias_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = self.response_ids(response)
        self.assertIn(self.auditoria.id, ids)
        self.assertNotIn(self.auditoria_ajena.id, ids)
        self.assertNotIn(self.auditoria_inactiva.id, ids)

    def test_auditor_asignado_puede_editar_hallazgo_de_su_auditoria(self):
        self.client.force_authenticate(user=self.user_auditor)
        response = self.client.patch(
            self.url_hallazgo_detail, {"titulo": "Hallazgo editado"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auditor_ajeno_no_puede_editar_hallazgo(self):
        self.client.force_authenticate(user=self.user_auditor_ajeno)
        response = self.client.patch(
            self.url_hallazgo_detail, {"titulo": "Intento no autorizado"}
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND],
        )

    def test_auditor_solo_lista_hallazgos_de_auditorias_asignadas_activas(self):
        self.client.force_authenticate(user=self.user_auditor)
        response = self.client.get(self.url_hallazgos_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = self.response_ids(response)
        self.assertIn(self.hallazgo.id, ids)
        self.assertNotIn(self.hallazgo_ajeno.id, ids)
        self.assertNotIn(self.hallazgo_inactivo.id, ids)

    def test_auditor_filtra_listados_relacionados_por_asignacion(self):
        self.client.force_authenticate(user=self.user_auditor)

        cases = [
            ("/api/informes/", self.informe.id, self.informe_ajeno.id),
            ("/api/planes-auditoria/", self.plan_auditoria.id, self.plan_auditoria_ajeno.id),
            ("/api/oportunidades-mejora/", self.oportunidad.id, self.oportunidad_ajena.id),
            ("/api/cronogramas/", self.cronograma.id, self.cronograma_ajeno.id),
            ("/api/historial-cambios/", self.historial.id, self.historial_ajeno.id),
            ("/api/planes-mejoramiento/", self.plan_mejoramiento.id, self.plan_mejoramiento_ajeno.id),
            ("/api/acciones-mejoramiento/", self.accion.id, self.accion_ajena.id),
            ("/api/seguimientos/", self.seguimiento.id, self.seguimiento_ajeno.id),
            ("/api/documentos/", self.documento.id, self.documento_ajeno.id),
            ("/api/notificaciones/", self.notificacion.id, self.notificacion_ajena.id),
        ]

        for url, propio_id, ajeno_id in cases:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                ids = self.response_ids(response)
                self.assertIn(propio_id, ids)
                self.assertNotIn(ajeno_id, ids)

    def test_auditor_no_puede_eliminar_auditoria_ajena(self):
        self.client.force_authenticate(user=self.user_auditor_ajeno)
        response = self.client.delete(self.url_auditoria_detail)
        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND],
        )

    def test_auditor_puede_ver_unidades_auditadas(self):
        """Caso especial: UnidadAuditada no pertenece a ninguna auditoría
        en particular, así que cualquier Auditor debería poder listarla."""
        self.client.force_authenticate(user=self.user_auditor_ajeno)
        response = self.client.get("/api/unidades/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ConsultaPermissionTests(BasePermissionTestCase):
    def test_consulta_puede_listar_auditorias(self):
        self.client.force_authenticate(user=self.user_consulta)
        response = self.client.get(self.url_auditorias_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_consulta_puede_ver_detalle_auditoria(self):
        self.client.force_authenticate(user=self.user_consulta)
        response = self.client.get(self.url_auditoria_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_consulta_no_puede_crear_auditoria(self):
        self.client.force_authenticate(user=self.user_consulta)
        payload = {
            "codigo": "AUD-TEST-004",
            "unidad_auditada": self.unidad.id,
            "responsable_unidad": "Responsable Y",
            "tipo_auditoria": "Interna",
            "fecha_inicio": "2026-04-01",
            "fecha_fin": "2026-04-30",
            "objetivo": "Objetivo 4",
            "alcance": "Alcance 4",
            "estado": "En planeación",
        }
        response = self.client.post(self.url_auditorias_list, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_consulta_no_puede_editar_auditoria(self):
        self.client.force_authenticate(user=self.user_consulta)
        response = self.client.patch(
            self.url_auditoria_detail, {"objetivo": "Intento de edición"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_consulta_no_puede_eliminar_auditoria(self):
        self.client.force_authenticate(user=self.user_consulta)
        response = self.client.delete(self.url_auditoria_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_consulta_no_puede_editar_hallazgo(self):
        self.client.force_authenticate(user=self.user_consulta)
        response = self.client.patch(
            self.url_hallazgo_detail, {"titulo": "Intento no autorizado"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UsuarioSinAutenticarTests(BasePermissionTestCase):
    def test_usuario_anonimo_no_puede_listar_auditorias(self):
        response = self.client.get(self.url_auditorias_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
