from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Prefetch
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

        for accion in proximas.select_related("hallazgo__auditoria").prefetch_related(
            Prefetch(
                "hallazgo__auditoria__auditoriaauditor_set",
                queryset=AuditoriaAuditor.objects.filter(activo=True).select_related("auditor"),
                to_attr="auditores_activos",
            )
        ):
            auditores_activos = accion.hallazgo.auditoria.auditores_activos

            if not auditores_activos:
                continue

            mensaje = (
                f"La acción de mejora '{accion.descripcion}' vence el "
                f"{accion.fecha_limite.isoformat()}."
            )
            usuarios_notificados = set()
            for asignacion in auditores_activos:
                usuario = asignacion.auditor

                # El modelo no impone unicidad en la asignación; se evita duplicar
                # la alerta aunque existan dos filas activas para el mismo usuario.
                if usuario.id in usuarios_notificados:
                    continue
                usuarios_notificados.add(usuario.id)

                existe = NotificacionAlerta.objects.filter(
                    accion=accion,
                    usuario=usuario,
                    tipo_alerta=TIPO_ALERTA_VENCIMIENTO,
                ).exists()

                if not existe:
                    NotificacionAlerta.objects.create(
                        accion=accion,
                        usuario=usuario,
                        tipo_alerta=TIPO_ALERTA_VENCIMIENTO,
                        mensaje=mensaje,
                    )
                    creadas += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Acciones vencidas: {actualizadas}. Alertas creadas: {creadas}."
            )
        )
