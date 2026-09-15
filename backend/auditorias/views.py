from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

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
from .permissions import AuditoriaRolePermission
from .serializers import (
    AccionMejoramientoSerializer,
    AuditoriaAuditorSerializer,
    AuditoriaSerializer,
    CronogramaActividadesSerializer,
    DocumentoGeneradoSerializer,
    HallazgoSerializer,
    HistorialCambioSerializer,
    InformeSerializer,
    NotificacionAlertaSerializer,
    OportunidadMejoraSerializer,
    PlanAuditoriaSerializer,
    PlanMejoramientoSerializer,
    SeguimientoAccionSerializer,
    UnidadAuditadaSerializer,
)


class AuditoriaAccessMixin:
    permission_classes = [AuditoriaRolePermission]
    admin_write_only = False

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user or not user.is_authenticated:
            return queryset.none()

        if user.is_superuser or user.groups.filter(name="Administrador").exists():
            return queryset

        if user.groups.filter(name="Usuario consulta").exists():
            return queryset

        if not user.groups.filter(name="Auditor").exists():
            return queryset.none()

        auditoria_filter = getattr(self, "auditoria_filter", None)

        if auditoria_filter:
            return queryset.filter(**{auditoria_filter: user}).distinct()

        if self.queryset.model == Auditoria:
            return queryset.filter(auditoriaauditor__auditor=user, auditoriaauditor__activo=True).distinct()

        if self.queryset.model == UnidadAuditada:
            return queryset

        return queryset.none()

    def perform_create(self, serializer):
        if not self._can_create_for_request():
            raise PermissionDenied("No tiene permiso para crear este recurso.")

        serializer.save()

    def _can_create_for_request(self):
        user = self.request.user

        if user.is_superuser or user.groups.filter(name="Administrador").exists():
            return True

        if self.admin_write_only:
            return False

        if user.groups.filter(name="Usuario consulta").exists():
            return False

        if not user.groups.filter(name="Auditor").exists():
            return False

        model = self.queryset.model

        if model == Auditoria:
            return True

        auditoria_id = self.request.data.get("auditoria")

        if auditoria_id:
            return AuditoriaAuditor.objects.filter(
                auditor=user,
                auditoria_id=auditoria_id,
                activo=True,
            ).exists()

        plan_auditoria_id = self.request.data.get("plan_auditoria")

        if plan_auditoria_id:
            return PlanAuditoria.objects.filter(
                id=plan_auditoria_id,
                auditoria__auditoriaauditor__auditor=user,
                auditoria__auditoriaauditor__activo=True,
            ).exists()

        plan_id = self.request.data.get("plan")

        if plan_id:
            return PlanMejoramiento.objects.filter(
                id=plan_id,
                auditoria__auditoriaauditor__auditor=user,
                auditoria__auditoriaauditor__activo=True,
            ).exists()

        accion_id = self.request.data.get("accion")

        if accion_id:
            return AccionMejoramiento.objects.filter(
                id=accion_id,
                plan__auditoria__auditoriaauditor__auditor=user,
                plan__auditoria__auditoriaauditor__activo=True,
            ).exists()

        hallazgo_id = self.request.data.get("hallazgo")

        if hallazgo_id:
            return Hallazgo.objects.filter(
                id=hallazgo_id,
                auditoria__auditoriaauditor__auditor=user,
                auditoria__auditoriaauditor__activo=True,
            ).exists()

        return False


class UnidadAuditadaViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    admin_write_only = True
    queryset = UnidadAuditada.objects.all()
    serializer_class = UnidadAuditadaSerializer


class AuditoriaViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    queryset = Auditoria.objects.all()
    serializer_class = AuditoriaSerializer


class AuditoriaAuditorViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    admin_write_only = True
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    queryset = AuditoriaAuditor.objects.all()
    serializer_class = AuditoriaAuditorSerializer


class InformeViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    queryset = Informe.objects.all()
    serializer_class = InformeSerializer


class HallazgoViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    queryset = Hallazgo.objects.all()
    serializer_class = HallazgoSerializer


class PlanAuditoriaViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    queryset = PlanAuditoria.objects.all()
    serializer_class = PlanAuditoriaSerializer


class OportunidadMejoraViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    queryset = OportunidadMejora.objects.all()
    serializer_class = OportunidadMejoraSerializer


class CronogramaActividadesViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "plan_auditoria__auditoria__auditoriaauditor__auditor"
    queryset = CronogramaActividades.objects.all()
    serializer_class = CronogramaActividadesSerializer


class HistorialCambioViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    queryset = HistorialCambio.objects.all()
    serializer_class = HistorialCambioSerializer


class PlanMejoramientoViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    queryset = PlanMejoramiento.objects.all()
    serializer_class = PlanMejoramientoSerializer


class AccionMejoramientoViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "plan__auditoria__auditoriaauditor__auditor"
    queryset = AccionMejoramiento.objects.all()
    serializer_class = AccionMejoramientoSerializer


class SeguimientoAccionViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "accion__plan__auditoria__auditoriaauditor__auditor"
    queryset = SeguimientoAccion.objects.all()
    serializer_class = SeguimientoAccionSerializer


class DocumentoGeneradoViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    queryset = DocumentoGenerado.objects.all()
    serializer_class = DocumentoGeneradoSerializer


class NotificacionAlertaViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "accion__plan__auditoria__auditoriaauditor__auditor"
    queryset = NotificacionAlerta.objects.all()
    serializer_class = NotificacionAlertaSerializer
