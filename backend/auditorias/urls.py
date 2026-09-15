from rest_framework.routers import DefaultRouter

from .views import (
    AccionMejoramientoViewSet,
    AuditoriaAuditorViewSet,
    AuditoriaViewSet,
    CronogramaActividadesViewSet,
    DocumentoGeneradoViewSet,
    HallazgoViewSet,
    HistorialCambioViewSet,
    InformeViewSet,
    NotificacionAlertaViewSet,
    OportunidadMejoraViewSet,
    PlanAuditoriaViewSet,
    PlanMejoramientoViewSet,
    SeguimientoAccionViewSet,
    UnidadAuditadaViewSet,
)

router = DefaultRouter()
router.register("unidades", UnidadAuditadaViewSet)
router.register("auditorias", AuditoriaViewSet)
router.register("auditoria-auditores", AuditoriaAuditorViewSet)
router.register("informes", InformeViewSet)
router.register("hallazgos", HallazgoViewSet)
router.register("planes-auditoria", PlanAuditoriaViewSet)
router.register("oportunidades-mejora", OportunidadMejoraViewSet)
router.register("cronogramas", CronogramaActividadesViewSet)
router.register("historial-cambios", HistorialCambioViewSet)
router.register("planes-mejoramiento", PlanMejoramientoViewSet)
router.register("acciones-mejoramiento", AccionMejoramientoViewSet)
router.register("seguimientos", SeguimientoAccionViewSet)
router.register("documentos", DocumentoGeneradoViewSet)
router.register("notificaciones", NotificacionAlertaViewSet)

urlpatterns = router.urls
