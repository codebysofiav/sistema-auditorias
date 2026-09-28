from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from auditorias.management.commands.generar_alertas_vencimiento import (
    TIPO_ALERTA_VENCIMIENTO,
)
from auditorias.models import (
    AccionMejoramiento,
    Auditoria,
    AuditoriaAuditor,
    Hallazgo,
    NotificacionAlerta,
    PlanMejoramiento,
    UnidadAuditada,
)
from usuarios.models import Usuario


class GenerarAlertasVencimientoTests(TestCase):
    def setUp(self):
        self.unidad = UnidadAuditada.objects.create(
            nombre_unidad="Unidad de pruebas",
            tipo="Académica",
        )
        self.auditoria = Auditoria.objects.create(
            codigo="AUD-ALERTA-001",
            unidad_auditada=self.unidad,
            responsable_unidad="Responsable",
            tipo_auditoria="Interna",
            fecha_inicio=timezone.localdate(),
            objetivo="Objetivo de prueba",
            alcance="Alcance de prueba",
            estado="En ejecución",
        )
        self.hallazgo = Hallazgo.objects.create(
            auditoria=self.auditoria,
            numero_hallazgo="H-001",
            titulo="Hallazgo de prueba",
            condicion="Condición",
            criterio="Criterio",
            causa="Causa",
            efecto="Efecto",
            estado="Abierto",
            recomendaciones="Recomendación",
        )
        self.plan = PlanMejoramiento.objects.create(
            auditoria=self.auditoria,
            fecha_creacion=timezone.localdate(),
            estado="Abierto",
        )
        self.accion = AccionMejoramiento.objects.create(
            plan=self.plan,
            hallazgo=self.hallazgo,
            descripcion="Acción próxima a vencer",
            responsable="Responsable",
            fecha_inicio=timezone.localdate(),
            fecha_limite=timezone.localdate() + timedelta(days=2),
            estado="Abierta",
        )
        self.auditor_uno = Usuario.objects.create_user(
            email="auditor-uno-alertas@test.com", password="Test1234!"
        )
        self.auditor_dos = Usuario.objects.create_user(
            email="auditor-dos-alertas@test.com", password="Test1234!"
        )
        self.auditor_inactivo = Usuario.objects.create_user(
            email="auditor-inactivo-alertas@test.com", password="Test1234!"
        )

    def alertas_vencimiento(self):
        return NotificacionAlerta.objects.filter(
            accion=self.accion,
            tipo_alerta=TIPO_ALERTA_VENCIMIENTO,
        )

    def test_notifica_a_todos_los_auditores_activos_y_no_al_inactivo(self):
        AuditoriaAuditor.objects.create(
            auditoria=self.auditoria, auditor=self.auditor_uno, activo=True
        )
        AuditoriaAuditor.objects.create(
            auditoria=self.auditoria, auditor=self.auditor_dos, activo=True
        )
        AuditoriaAuditor.objects.create(
            auditoria=self.auditoria, auditor=self.auditor_inactivo, activo=False
        )

        call_command("generar_alertas_vencimiento")

        self.assertEqual(self.alertas_vencimiento().count(), 2)
        self.assertSetEqual(
            set(self.alertas_vencimiento().values_list("usuario_id", flat=True)),
            {self.auditor_uno.id, self.auditor_dos.id},
        )

    def test_ejecucion_repetida_no_duplica_alertas_por_usuario(self):
        AuditoriaAuditor.objects.create(
            auditoria=self.auditoria, auditor=self.auditor_uno, activo=True
        )
        AuditoriaAuditor.objects.create(
            auditoria=self.auditoria, auditor=self.auditor_dos, activo=True
        )

        call_command("generar_alertas_vencimiento")
        call_command("generar_alertas_vencimiento")

        self.assertEqual(self.alertas_vencimiento().count(), 2)

    def test_auditor_asignado_despues_recibe_alerta_en_siguiente_ejecucion(self):
        AuditoriaAuditor.objects.create(
            auditoria=self.auditoria, auditor=self.auditor_uno, activo=True
        )
        call_command("generar_alertas_vencimiento")

        AuditoriaAuditor.objects.create(
            auditoria=self.auditoria, auditor=self.auditor_dos, activo=True
        )
        call_command("generar_alertas_vencimiento")

        self.assertEqual(self.alertas_vencimiento().count(), 2)
        self.assertTrue(
            self.alertas_vencimiento().filter(usuario=self.auditor_dos).exists()
        )
