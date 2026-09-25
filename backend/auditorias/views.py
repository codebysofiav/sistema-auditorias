from datetime import timedelta

from django.contrib.auth.models import Group
from django.db.models import Count, Exists, OuterRef
from django.utils import timezone
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

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


ESTADOS_ACCION_FINALIZADA = ("Cerrada", "Completada")
ESTADO_HALLAZGO_CERRADO = "Cerrado"


def auditorias_visibles_para_usuario(user):
    if user.is_superuser or user.groups.filter(name="Administrador").exists():
        return Auditoria.objects.all()

    if user.groups.filter(name="Usuario consulta").exists():
        return Auditoria.objects.all()

    if user.groups.filter(name="Auditor").exists():
        return Auditoria.objects.filter(
            auditoriaauditor__auditor=user,
            auditoriaauditor__activo=True,
        ).distinct()

    return Auditoria.objects.none()


class AuditoriaAccessMixin:
    permission_classes = [AuditoriaRolePermission]
    admin_write_only = False
    auditoria_active_filter = None
    autor_field = None

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
        auditoria_active_filter = getattr(self, "auditoria_active_filter", None)

        if auditoria_filter:
            filters = {auditoria_filter: user}

            if auditoria_active_filter:
                filters[auditoria_active_filter] = True

            return queryset.filter(**filters).distinct()

        if self.queryset.model == Auditoria:
            return auditorias_visibles_para_usuario(user)

        if self.queryset.model == UnidadAuditada:
            return queryset

        return queryset.none()

    def perform_create(self, serializer):
        if not self._can_create_for_request():
            raise PermissionDenied("No tiene permiso para crear este recurso.")

        if self.autor_field:
            serializer.save(**{self.autor_field: self.request.user})
        else:
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

        if model in (Auditoria, UnidadAuditada):
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
    queryset = UnidadAuditada.objects.all()
    serializer_class = UnidadAuditadaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        incluir_inactivas = self.request.query_params.get("incluir_inactivas") == "true"
        return queryset if incluir_inactivas else queryset.filter(activo=True)

    def perform_destroy(self, instance):
        # Evita eliminar en cascada las auditorias relacionadas con la unidad.
        instance.activo = False
        instance.save(update_fields=["activo"])


class AuditoriaViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    queryset = Auditoria.objects.all()
    serializer_class = AuditoriaSerializer
    autor_field = "creado_por"


class AuditoriaAuditorViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    admin_write_only = True
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    auditoria_active_filter = "auditoria__auditoriaauditor__activo"
    queryset = AuditoriaAuditor.objects.all()
    serializer_class = AuditoriaAuditorSerializer


class InformeViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    auditoria_active_filter = "auditoria__auditoriaauditor__activo"
    queryset = Informe.objects.all()
    serializer_class = InformeSerializer
    autor_field = "creado_por"

class HallazgoViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    auditoria_active_filter = "auditoria__auditoriaauditor__activo"
    queryset = Hallazgo.objects.all()
    serializer_class = HallazgoSerializer


class PlanAuditoriaViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    auditoria_active_filter = "auditoria__auditoriaauditor__activo"
    queryset = PlanAuditoria.objects.all()
    serializer_class = PlanAuditoriaSerializer


class OportunidadMejoraViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    auditoria_active_filter = "auditoria__auditoriaauditor__activo"
    queryset = OportunidadMejora.objects.all()
    serializer_class = OportunidadMejoraSerializer


class CronogramaActividadesViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "plan_auditoria__auditoria__auditoriaauditor__auditor"
    auditoria_active_filter = "plan_auditoria__auditoria__auditoriaauditor__activo"
    queryset = CronogramaActividades.objects.all()
    serializer_class = CronogramaActividadesSerializer


class HistorialCambioViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    auditoria_active_filter = "auditoria__auditoriaauditor__activo"
    queryset = HistorialCambio.objects.all()
    serializer_class = HistorialCambioSerializer
    autor_field = "usuario"

class PlanMejoramientoViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    auditoria_active_filter = "auditoria__auditoriaauditor__activo"
    queryset = PlanMejoramiento.objects.all()
    serializer_class = PlanMejoramientoSerializer


class AccionMejoramientoViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "plan__auditoria__auditoriaauditor__auditor"
    auditoria_active_filter = "plan__auditoria__auditoriaauditor__activo"
    queryset = AccionMejoramiento.objects.all()
    serializer_class = AccionMejoramientoSerializer

class SeguimientoAccionViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "accion__plan__auditoria__auditoriaauditor__auditor"
    auditoria_active_filter = "accion__plan__auditoria__auditoriaauditor__activo"
    queryset = SeguimientoAccion.objects.all()
    serializer_class = SeguimientoAccionSerializer
    autor_field = "registrado_por"


class DocumentoGeneradoViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "auditoria__auditoriaauditor__auditor"
    auditoria_active_filter = "auditoria__auditoriaauditor__activo"
    queryset = DocumentoGenerado.objects.all()
    serializer_class = DocumentoGeneradoSerializer
    autor_field = "generado_por"


class NotificacionAlertaViewSet(AuditoriaAccessMixin, viewsets.ModelViewSet):
    auditoria_filter = "accion__plan__auditoria__auditoriaauditor__auditor"
    auditoria_active_filter = "accion__plan__auditoria__auditoriaauditor__activo"
    queryset = NotificacionAlerta.objects.all()
    serializer_class = NotificacionAlertaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        es_admin = user.is_superuser or user.groups.filter(name="Administrador").exists()
        es_auditor = user.groups.filter(name="Auditor").exists()

        if es_auditor and not es_admin:
            queryset = queryset.filter(usuario=user)

        return queryset

    @action(detail=False, methods=["get"], url_path="no-leidas")
    def no_leidas(self, request):
        queryset = NotificacionAlerta.objects.filter(
            usuario=request.user,
            leida=False,
        ).order_by("-fecha_notificacion")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="marcar-leida")
    def marcar_leida(self, request, pk=None):
        alerta = NotificacionAlerta.objects.filter(
            pk=pk,
            usuario=request.user,
        ).first()

        if alerta is None:
            raise PermissionDenied("No tiene permiso para modificar esta alerta.")

        alerta.leida = True
        alerta.save(update_fields=["leida"])
        return Response(self.get_serializer(alerta).data)


class DashboardResumenView(APIView):
    permission_classes = [AuditoriaRolePermission]

    @extend_schema(
        responses=OpenApiTypes.OBJECT,
        summary="Resumen del dashboard",
        description="Estadísticas agregadas según el alcance del usuario autenticado.",
    )
    def get(self, request):
        user = request.user
        auditorias = auditorias_visibles_para_usuario(user)
        hoy = timezone.localdate()
        proxima_semana = hoy + timedelta(days=7)
        acciones = AccionMejoramiento.objects.filter(plan__auditoria__in=auditorias)
        hallazgos = Hallazgo.objects.filter(auditoria__in=auditorias)
        informe_preliminar = Informe.objects.filter(
            auditoria=OuterRef("pk"),
            tipo_informe__iexact="preliminar",
        )
        informe_definitivo = Informe.objects.filter(
            auditoria=OuterRef("pk"),
            tipo_informe__iexact="definitivo",
        )

        resumen = {
            "total_auditorias_activas": auditorias.exclude(estado="Cerrada").count(),
            "auditorias_por_estado": {
                item["estado"]: item["total"]
                for item in auditorias.values("estado").annotate(total=Count("id")).order_by("estado")
            },
            "alertas_pendientes": NotificacionAlerta.objects.filter(usuario=user, leida=False).count(),
            "acciones_vencidas": acciones.filter(estado="Vencida").count(),
            "acciones_proximas_vencer": acciones.filter(
                fecha_limite__range=(hoy, proxima_semana),
            ).exclude(estado__in=("Vencida", *ESTADOS_ACCION_FINALIZADA)).count(),
            "acciones_sin_seguimiento": acciones.filter(seguimientoaccion__isnull=True).count(),
            "hallazgos_abiertos": hallazgos.exclude(estado=ESTADO_HALLAZGO_CERRADO).count(),
            "hallazgos_sin_accion": hallazgos.filter(accionmejoramiento__isnull=True).count(),
            "auditorias_preliminar_sin_definitivo": auditorias.filter(
                Exists(informe_preliminar),
            ).filter(~Exists(informe_definitivo)).count(),
        }

        es_administrador = user.is_superuser or user.groups.filter(name="Administrador").exists()
        es_auditor = user.groups.filter(name="Auditor").exists()

        if es_administrador:
            roles = ("Administrador", "Auditor", "Usuario consulta")
            conteos_roles = {
                item["name"]: item["total"]
                for item in Group.objects.filter(name__in=roles)
                .values("name")
                .annotate(total=Count("user"))
            }
            resumen["usuarios_por_rol"] = {role: conteos_roles.get(role, 0) for role in roles}
            resumen["unidades_activas"] = UnidadAuditada.objects.filter(activo=True).count()
            resumen["unidades_inactivas"] = UnidadAuditada.objects.filter(activo=False).count()

        if es_auditor and not es_administrador:
            resumen["mis_auditorias"] = list(
                auditorias.values("id", "codigo", "estado").order_by("codigo")
            )

        return Response(resumen)
