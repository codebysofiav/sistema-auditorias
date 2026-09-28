from rest_framework import serializers
from usuarios.models import Usuario

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
    equipo_auditor = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Usuario.objects.filter(groups__name__in=("Auditor", "Director")).distinct(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Auditoria
        fields = "__all__"
        read_only_fields = ["creado_por", "fecha_creacion"]

    def validate_equipo_auditor(self, auditores):
        ids = [auditor.id for auditor in auditores]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("No puede asignar un auditor más de una vez.")
        return auditores

    def create(self, validated_data):
        auditores = validated_data.pop("equipo_auditor", [])
        auditoria = super().create(validated_data)

        AuditoriaAuditor.objects.bulk_create(
            [AuditoriaAuditor(auditoria=auditoria, auditor=auditor) for auditor in auditores]
        )
        return auditoria

    def update(self, instance, validated_data):
        if "equipo_auditor" in validated_data:
            raise serializers.ValidationError(
                {"equipo_auditor": "El equipo se administra desde sus asignaciones."}
            )
        return super().update(instance, validated_data)


class AuditoriaAuditorSerializer(serializers.ModelSerializer):
    auditor = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.filter(groups__name__in=("Auditor", "Director")).distinct()
    )

    class Meta:
        model = AuditoriaAuditor
        fields = "__all__"


class InformeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Informe
        fields = "__all__"
        read_only_fields = [
            "creado_por",
            "fecha_creacion",
            "estado",
            "revisado_por",
            "fecha_revision",
            "observaciones_revision",
        ]

    def validate(self, attrs):
        tipo_informe = attrs.get("tipo_informe", getattr(self.instance, "tipo_informe", ""))
        auditoria = attrs.get("auditoria", getattr(self.instance, "auditoria", None))

        if tipo_informe.lower() == "definitivo" and auditoria:
            preliminar_aprobado = Informe.objects.filter(
                auditoria=auditoria,
                tipo_informe__iexact="preliminar",
                estado=Informe.EstadoRevision.APROBADO,
            )
            if self.instance:
                preliminar_aprobado = preliminar_aprobado.exclude(pk=self.instance.pk)
            if not preliminar_aprobado.exists():
                raise serializers.ValidationError(
                    {
                        "tipo_informe": (
                            "Solo puede crear un informe definitivo cuando exista un "
                            "informe preliminar aprobado para esta auditoría."
                        )
                    }
                )

        return attrs

    def create(self, validated_data):
        if validated_data.get("tipo_informe", "").lower() == "preliminar":
            validated_data["estado"] = Informe.EstadoRevision.PENDIENTE
        return super().create(validated_data)


class RevisionInformeSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(
        choices=(
            Informe.EstadoRevision.APROBADO,
            Informe.EstadoRevision.CORRECCIONES,
        )
    )
    observaciones_revision = serializers.CharField(required=False, allow_blank=True)


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
        read_only_fields = ["usuario", "fecha_cambio"]


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
        read_only_fields = ["registrado_por"]


class DocumentoGeneradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoGenerado
        fields = "__all__"
        read_only_fields = ["generado_por", "fecha_generacion"]


class NotificacionAlertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificacionAlerta
        fields = "__all__"
