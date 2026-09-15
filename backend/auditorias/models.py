from django.db import models
from django.conf import settings

# Create your models here.
class UnidadAuditada(models.Model):
    nombre_unidad = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_unidad

class Auditoria(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    unidad_auditada = models.ForeignKey(UnidadAuditada, on_delete=models.CASCADE)
    responsable_unidad = models.CharField(max_length=100)
    tipo_auditoria = models.CharField(max_length=50)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    objetivo = models.TextField()
    alcance = models.TextField()
    estado  = models.CharField(max_length=50)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.codigo

class AuditoriaAuditor(models.Model):
    auditoria = models.ForeignKey(Auditoria, on_delete=models.CASCADE)
    auditor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.auditor} asignado a {self.auditoria}"

class Informe(models.Model):
    auditoria = models.ForeignKey(Auditoria, on_delete=models.CASCADE)
    tipo_informe = models.CharField(max_length=50)
    fecha_informe = models.DateField(null=True, blank=True)
    actividades_realizadas = models.TextField()
    conclusiones = models.TextField()
    observaciones = models.TextField(blank=True, null=True)
    evidencias = models.TextField(blank=True, null=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Informe de {self.auditoria} - {self.fecha_informe}"
    #de esta parte no estoy segura si el id que toma esta bien


class Hallazgo(models.Model):
    auditoria = models.ForeignKey(Auditoria, on_delete=models.CASCADE)
    numero_hallazgo = models.CharField(max_length=20)
    condicion = models.TextField()
    criterio = models.TextField()
    causa = models.TextField()
    efecto = models.TextField()
    estado = models.CharField(max_length=50)
    titulo = models.CharField(max_length=100)
    recomendaciones = models.TextField()

    def __str__(self):
        return f"Hallazgo {self.numero_hallazgo} de {self.auditoria}"

class PlanAuditoria(models.Model):
    auditoria = models.OneToOneField(Auditoria, on_delete=models.CASCADE)
    criterios = models.TextField()
    riesgos_oportunidades = models.TextField()
    documentos_referencia = models.TextField()
    fecha_creacion = models.DateField()

    def __str__(self):
        return f"Plan de Auditoría de {self.auditoria} - {self.fecha_creacion}"

class OportunidadMejora(models.Model):
    auditoria = models.ForeignKey(Auditoria, on_delete=models.CASCADE)
    numero_oportunidad = models.CharField(max_length=20)
    descripcion = models.TextField()
    recomendacion = models.TextField()
    fecha_creacion = models.DateField()
    estado = models.CharField(max_length=50)

    def __str__(self):
        return f"Oportunidad {self.numero_oportunidad} - {self.auditoria}"

class CronogramaActividades(models.Model):
    plan_auditoria = models.ForeignKey(PlanAuditoria, on_delete=models.CASCADE)
    fecha_actividad = models.DateField()
    hora = models.TimeField()
    actividad = models.TextField()
    auditado = models.CharField(max_length=100)

    def __str__(self):
        return self.actividad[:50]

class HistorialCambio(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    auditoria = models.ForeignKey(Auditoria, on_delete=models.CASCADE)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    tipo_accion = models.CharField(max_length=50)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.tipo_accion} - {self.fecha_cambio}"

class PlanMejoramiento(models.Model):
    auditoria = models.OneToOneField(Auditoria, on_delete=models.CASCADE)
    fecha_creacion = models.DateField()
    estado = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Plan de mejoramiento - {self.auditoria}"

class AccionMejoramiento(models.Model):
    plan = models.ForeignKey(PlanMejoramiento, on_delete=models.CASCADE)
    hallazgo = models.ForeignKey(Hallazgo, on_delete=models.CASCADE)
    descripcion = models.TextField()
    responsable = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_limite = models.DateField()
    porcentaje_avance = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Acción para {self.hallazgo}"

class SeguimientoAccion(models.Model):
    accion = models.ForeignKey(AccionMejoramiento, on_delete=models.CASCADE)
    porcentaje_avance = models.DecimalField(max_digits=5, decimal_places=2)
    descripcion = models.TextField()
    fecha_seguimiento = models.DateField()
    observaciones = models.TextField()
    estado = models.CharField(max_length=50)
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    evidencias = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Seguimiento {self.fecha_seguimiento}"

class DocumentoGenerado(models.Model):
    auditoria = models.ForeignKey(Auditoria, on_delete=models.CASCADE)
    tipo_documento = models.CharField(max_length=50)
    formato = models.CharField(max_length=20)
    fecha_generacion = models.DateField()
    generado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='documentos_generados')

    def __str__(self):
        return f"{self.tipo_documento} - {self.auditoria}"

class NotificacionAlerta(models.Model):
    accion = models.ForeignKey(AccionMejoramiento, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo_alerta = models.CharField(max_length=50)
    mensaje = models.TextField()
    fecha_notificacion = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    def __str__(self):
        return self.tipo_alerta
