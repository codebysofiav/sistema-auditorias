from rest_framework import serializers

from .models import (
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


class UnidadAuditadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadAuditada
        fields = "__all__"


class AuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auditoria
        fields = "__all__"


class AuditoriaAuditorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditoriaAuditor
        fields = "__all__"


class InformeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Informe
        fields = "__all__"


class HallazgoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hallazgo
        fields = "__all__"


class PlanAuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanAuditoria
        fields = "__all__"


class OportunidadMejoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = OportunidadMejora
        fields = "__all__"


class CronogramaActividadesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CronogramaActividades
        fields = "__all__"


class HistorialCambioSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialCambio
        fields = "__all__"


class PlanMejoramientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanMejoramiento
        fields = "__all__"


class AccionMejoramientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccionMejoramiento
        fields = "__all__"


class SeguimientoAccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeguimientoAccion
        fields = "__all__"


class DocumentoGeneradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoGenerado
        fields = "__all__"


class NotificacionAlertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificacionAlerta
        fields = "__all__"
