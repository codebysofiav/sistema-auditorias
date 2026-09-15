from django.contrib import admin
from .models import *


admin.site.register(UnidadAuditada)
admin.site.register(Auditoria)
admin.site.register(AuditoriaAuditor)
admin.site.register(Informe)
admin.site.register(Hallazgo)
admin.site.register(PlanAuditoria)
admin.site.register(OportunidadMejora)
admin.site.register(CronogramaActividades)
admin.site.register(HistorialCambio)
admin.site.register(PlanMejoramiento)
admin.site.register(AccionMejoramiento)
admin.site.register(SeguimientoAccion)
admin.site.register(DocumentoGenerado)
admin.site.register(NotificacionAlerta)
# Register your models here.
