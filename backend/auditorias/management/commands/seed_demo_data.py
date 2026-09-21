"""
Comando de gestión de Django para crear datos de prueba end-to-end.

UBICACIÓN: auditorias/management/commands/seed_demo_data.py

Si las carpetas no existen, créalas así (deben tener __init__.py vacíos):
    auditorias/management/__init__.py
    auditorias/management/commands/__init__.py
    auditorias/management/commands/seed_demo_data.py   <- este archivo

CÓMO EJECUTAR:
    python manage.py seed_demo_data

Es seguro correrlo varias veces: usa get_or_create donde tiene sentido,
así que no duplica registros si ya existen. Si quieres empezar de cero,
puedes borrar los objetos de prueba manualmente o desde el admin.

NOTA: ajusta los nombres de campos y valores de 'estado' si tu implementación
real difiere de la documentación del proyecto (busca "# AJUSTAR").
"""

from datetime import date, timedelta

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from usuarios.models import Usuario
from auditorias.models import (
    UnidadAuditada,
    Auditoria,
    AuditoriaAuditor,
    PlanAuditoria,
    CronogramaActividades,
    Hallazgo,
    Informe,
    PlanMejoramiento,
    AccionMejoramiento,
    SeguimientoAccion,
)


class Command(BaseCommand):
    help = "Crea un flujo completo de datos de prueba: unidad, auditoría, auditor, plan, cronograma, hallazgo, informe, plan de mejoramiento, acción y seguimiento."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Creando grupos de roles...")
        grupo_admin, _ = Group.objects.get_or_create(name="Administrador")
        grupo_auditor, _ = Group.objects.get_or_create(name="Auditor")
        grupo_consulta, _ = Group.objects.get_or_create(name="Usuario consulta")

        self.stdout.write("Creando usuarios de prueba...")
        admin, created = Usuario.objects.get_or_create(
            email="admin_demo@auditorias.local",
            defaults={"first_name": "Admin", "last_name": "Demo"},
        )
        if created:
            admin.set_password("Demo1234!")
            admin.save()
        admin.groups.add(grupo_admin)

        auditor, created = Usuario.objects.get_or_create(
            email="auditor_demo@auditorias.local",
            defaults={"first_name": "Auditor", "last_name": "Demo"},
        )
        if created:
            auditor.set_password("Demo1234!")
            auditor.save()
        auditor.groups.add(grupo_auditor)

        consulta, created = Usuario.objects.get_or_create(
            email="consulta_demo@auditorias.local",
            defaults={"first_name": "Consulta", "last_name": "Demo"},
        )
        if created:
            consulta.set_password("Demo1234!")
            consulta.save()
        consulta.groups.add(grupo_consulta)

        self.stdout.write("Creando unidad auditada...")
        unidad, _ = UnidadAuditada.objects.get_or_create(
            nombre_unidad="Facultad de Ingeniería",  # AJUSTAR si el campo se llama distinto
            defaults={
                "tipo": "Académica",
                "descripcion": "Unidad de prueba para flujo end-to-end",
                "activo": True,
            },
        )

        self.stdout.write("Creando auditoría...")
        auditoria, _ = Auditoria.objects.get_or_create(
            codigo="AUD-DEMO-001",
            defaults={
                "unidad_auditada": unidad,
                "responsable_unidad": "Decano de Ingeniería",
                "tipo_auditoria": "Interna",
                "fecha_inicio": date.today(),
                "fecha_fin": date.today() + timedelta(days=30),
                "objetivo": "Evaluar el cumplimiento de procesos académicos",
                "alcance": "Procesos de matrícula y evaluación docente del periodo actual",
                "estado": "En planeación",  # AJUSTAR al valor real que uses
                "creado_por": admin,
            },
        )

        self.stdout.write("Asignando auditor...")
        AuditoriaAuditor.objects.get_or_create(
            auditoria=auditoria,
            auditor=auditor,
            defaults={"activo": True},
        )

        self.stdout.write("Creando plan de auditoría...")
        plan_auditoria, _ = PlanAuditoria.objects.get_or_create(
            auditoria=auditoria,
            defaults={
                "criterios": "ISO 9001, reglamento interno de la universidad",
                "riesgos_oportunidades": "Riesgo de documentación incompleta en matrícula",
                "documentos_referencia": "Manual de procesos académicos v3",
                "fecha_creacion": date.today(),
            },
        )

        self.stdout.write("Creando actividad de cronograma...")
        CronogramaActividades.objects.get_or_create(
            plan_auditoria=plan_auditoria,
            actividad="Reunión de apertura con la unidad auditada",
            defaults={
                "fecha_actividad": date.today() + timedelta(days=2),
                "hora": "09:00",
                "auditado": "Decano de Ingeniería",
            },
        )

        self.stdout.write("Creando hallazgo...")
        hallazgo, _ = Hallazgo.objects.get_or_create(
            auditoria=auditoria,
            numero_hallazgo=1,
            defaults={
                "titulo": "Documentación de matrícula incompleta",
                "condicion": "El 15% de los expedientes revisados no tienen firma del acudiente",
                "criterio": "Reglamento interno, artículo 12",
                "causa": "Falta de checklist en el proceso de recepción de documentos",
                "efecto": "Riesgo de invalidez de la matrícula ante una auditoría externa",
                "estado": "Abierto",  # AJUSTAR al valor real
                "recomendaciones": "Implementar checklist obligatorio de documentos al recibir matrícula",
            },
        )

        self.stdout.write("Creando informe preliminar...")
        Informe.objects.get_or_create(
            auditoria=auditoria,
            tipo_informe="Preliminar",  # AJUSTAR al valor real
            defaults={
                "fecha_informe": date.today(),
                "actividades_realizadas": "Revisión documental y entrevistas con personal de matrícula",
                "conclusiones": "Se identificó una oportunidad de mejora en el control documental",
                "observaciones": "Pendiente confirmar con la unidad la fecha del informe definitivo",
                "evidencias": "Carpeta compartida /evidencias/AUD-DEMO-001",
                "creado_por": auditor,
            },
        )

        self.stdout.write("Creando plan de mejoramiento...")
        plan_mejoramiento, _ = PlanMejoramiento.objects.get_or_create(
            auditoria=auditoria,
            defaults={
                "estado": "Abierto",  # AJUSTAR al valor real
                "observaciones": "Plan generado a partir del hallazgo AUD-DEMO-001-H1",
                "fecha_creacion": date.today(),
            },
        )

        self.stdout.write("Creando acción de mejoramiento...")
        accion, _ = AccionMejoramiento.objects.get_or_create(
            plan=plan_mejoramiento,
            hallazgo=hallazgo,
            defaults={
                "descripcion": "Diseñar e implementar checklist de documentos de matrícula",
                "responsable": "Coordinación de Admisiones",
                "fecha_inicio": date.today(),
                "fecha_limite": date.today() + timedelta(days=45),
                "porcentaje_avance": 0,
                "estado": "En progreso",  # AJUSTAR al valor real
                "observaciones": "",
            },
        )

        self.stdout.write("Creando seguimiento de la acción...")
        SeguimientoAccion.objects.get_or_create(
            accion=accion,
            fecha_seguimiento=date.today(),
            defaults={
                "porcentaje_avance": 20,
                "descripcion": "Se elaboró el borrador del checklist, pendiente validación",
                "observaciones": "Se espera validación de la Coordinación la próxima semana",
                "estado": "En progreso",  # AJUSTAR al valor real
                "registrado_por": auditor,
                "evidencias": "checklist_borrador_v1.pdf",
            },
        )

        self.stdout.write(self.style.SUCCESS("\n✅ Datos de prueba creados correctamente.\n"))
        self.stdout.write("Usuarios de prueba (password para todos: Demo1234!):")
        self.stdout.write(f"  Administrador: {admin.email}")
        self.stdout.write(f"  Auditor:       {auditor.email}")
        self.stdout.write(f"  Consulta:      {consulta.email}")
        self.stdout.write(f"\nAuditoría creada: {auditoria.codigo} (id={auditoria.id})")
