from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from auditorias.models import AccionMejoramiento, AuditoriaAuditor, NotificacionAlerta


ESTADOS_FINALIZADOS = ("Cerrada", "Completada")
TIPO_ALERTA_VENCIMIENTO = "Vencimiento próximo"


class Command(BaseCommand):
    help = "Genera alertas dos dias antes del vencimiento y marca acciones vencidas."

    def handle(self, *args, **options):
        hoy = timezone.localdate()
        fecha_alerta = hoy + timedelta(days=2)
        acciones_activas = AccionMejoramiento.objects.exclude(estado__in=ESTADOS_FINALIZADOS)

        vencidas = acciones_activas.filter(fecha_limite__lt=hoy).exclude(estado="Vencida")
        actualizadas = vencidas.update(estado="Vencida")

        proximas = acciones_activas.filter(fecha_limite=fecha_alerta).exclude(estado="Vencida")
        creadas = 0

        for accion in proximas.select_related("hallazgo__auditoria"):
            auditor = (
                AuditoriaAuditor.objects.filter(
                    auditoria=accion.hallazgo.auditoria,
                    activo=True,
                )
                .select_related("auditor")
                .order_by("fecha_asignacion")
                .first()
            )

            if auditor is None:
                continue

            mensaje = (
                f"La acción de mejora '{accion.descripcion}' vence el "
                f"{accion.fecha_limite.isoformat()}."
            )
            existe = NotificacionAlerta.objects.filter(
                accion=accion,
                usuario=auditor.auditor,
                tipo_alerta=TIPO_ALERTA_VENCIMIENTO,
                mensaje=mensaje,
            ).exists()

            if not existe:
                NotificacionAlerta.objects.create(
                    accion=accion,
                    usuario=auditor.auditor,
                    tipo_alerta=TIPO_ALERTA_VENCIMIENTO,
                    mensaje=mensaje,
                )
                creadas += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Acciones vencidas: {actualizadas}. Alertas creadas: {creadas}."
            )
        )
