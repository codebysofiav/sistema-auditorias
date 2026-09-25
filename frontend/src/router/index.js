import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import AuditoriasListView from '@/views/AuditoriasListView.vue'
import AuditoriaFormView from '@/views/AuditoriaFormView.vue'
import HallazgosListView from '@/views/HallazgosListView.vue'
import HallazgoFormView from '@/views/HallazgoFormView.vue'
import PlanesListView from '@/views/PlanesListView.vue'
import PlanFormView from '@/views/PlanFormView.vue'
import PlanDetalleView from '@/views/PlanDetalleView.vue'
import AccionFormView from '@/views/AccionFormView.vue'
import InformesListView from '@/views/InformesListView.vue'
import InformeFormView from '@/views/InformeFormView.vue'
import DocumentosListView from '@/views/DocumentosListView.vue'
import DocumentoGenerarView from '@/views/DocumentoGenerarView.vue'
import UsuariosListView from '@/views/UsuariosListView.vue'
import UsuarioFormView from '@/views/UsuarioFormView.vue'
import PlaneacionListView from '@/views/PlaneacionListView.vue'
import PlanAuditoriaFormView from '@/views/PlanAuditoriaFormView.vue'
import PlaneacionDetalleView from '@/views/PlaneacionDetalleView.vue'
import CronogramaFormView from '@/views/CronogramaFormView.vue'
import UnidadesListView from '@/views/UnidadesListView.vue'
import UnidadFormView from '@/views/UnidadFormView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/login', name: 'login', component: LoginView },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true },
    },
    {
      path: '/auditorias',
      name: 'auditorias',
      component: AuditoriasListView,
      meta: { requiresAuth: true },
    },
    {
      path: '/auditorias/nueva',
      name: 'auditoria-nueva',
      component: AuditoriaFormView,
      meta: { requiresAuth: true },
    },
    {
      path: '/auditorias/:id',
      name: 'auditoria-detalle',
      component: AuditoriaFormView,
      meta: { requiresAuth: true },
    },
    {
      path: '/unidades',
      name: 'unidades',
      component: UnidadesListView,
      meta: { requiresAuth: true },
    },
    {
      path: '/unidades/nueva',
      name: 'unidad-nueva',
      component: UnidadFormView,
      meta: { requiresAuth: true, requiresWrite: true },
    },
    {
      path: '/unidades/:id',
      name: 'unidad-detalle',
      component: UnidadFormView,
      meta: { requiresAuth: true },
    },
    {
      path: '/hallazgos',
      name: 'hallazgos',
      component: HallazgosListView,
      meta: { requiresAuth: true },
    },
    {
      path: '/hallazgos/nuevo',
      name: 'hallazgo-nuevo',
      component: HallazgoFormView,
      meta: { requiresAuth: true },
    },
    {
      path: '/hallazgos/:id',
      name: 'hallazgo-detalle',
      component: HallazgoFormView,
      meta: { requiresAuth: true },
    },
    {
      path: '/plan-mejoramiento',
      name: 'planes-mejoramiento',
      component: PlanesListView,
      meta: { requiresAuth: true },
    },
    {
      path: '/plan-mejoramiento/nuevo',
      name: 'plan-nuevo',
      component: PlanFormView,
      meta: { requiresAuth: true },
    },
    {
      path: '/plan-mejoramiento/:id',
      name: 'plan-detalle',
      component: PlanDetalleView,
      meta: { requiresAuth: true },
    },
    {
      path: '/plan-mejoramiento/:planId/acciones/nueva',
      name: 'accion-nueva',
      component: AccionFormView,
      meta: { requiresAuth: true },
    },
    {
      path: '/plan-mejoramiento/:planId/acciones/:accionId',
      name: 'accion-detalle',
      component: AccionFormView,
      meta: { requiresAuth: true },
    },
    {
      path: '/informes',
      name: 'informes',
      component: InformesListView,
      meta: { requiresAuth: true },
    },
    {
      path: '/informes/nuevo',
      name: 'informe-nuevo',
      component: InformeFormView,
      meta: { requiresAuth: true },
    },
    {
      path: '/informes/:id',
      name: 'informe-detalle',
      component: InformeFormView,
      meta: { requiresAuth: true },
    },
    {
      path: '/documentos',
      name: 'documentos',
      component: DocumentosListView,
      meta: { requiresAuth: true },
    },
    {
      path: '/documentos/generar',
      name: 'documento-generar',
      component: DocumentoGenerarView,
      meta: { requiresAuth: true },
    },
    // --- Usuarios (solo Administrador) ---
    {
      path: '/usuarios',
      name: 'usuarios',
      component: UsuariosListView,
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/usuarios/nuevo',
      name: 'usuario-nuevo',
      component: UsuarioFormView,
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/usuarios/:id/editar',
      name: 'usuario-editar',
      component: UsuarioFormView,
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/planeacion',
      name: 'planeacion',
      component: PlaneacionListView,
      meta: { requiresAuth: true },
    },
    {
      path: '/planeacion/nueva',
      name: 'plan-auditoria-nuevo',
      component: PlanAuditoriaFormView,
      meta: { requiresAuth: true, requiresWrite: true },
    },
    {
      path: '/planeacion/:id',
      name: 'plan-auditoria-detalle',
      component: PlaneacionDetalleView,
      meta: { requiresAuth: true },
    },
    {
      path: '/planeacion/:id/editar',
      name: 'plan-auditoria-editar',
      component: PlanAuditoriaFormView,
      meta: { requiresAuth: true, requiresWrite: true },
    },
    {
      path: '/planeacion/:planId/cronogramas/nuevo',
      name: 'cronograma-nuevo',
      component: CronogramaFormView,
      meta: { requiresAuth: true, requiresWrite: true },
    },
    {
      path: '/planeacion/:planId/cronogramas/:cronogramaId',
      name: 'cronograma-detalle',
      component: CronogramaFormView,
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }

  if (auth.isAuthenticated && !auth.user) {
    try {
      await auth.fetchUser()
    } catch {
      await auth.logout()
      return { name: 'login' }
    }
  }

  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { name: 'dashboard' }
  }

  if (to.meta.requiresWrite && !(auth.isAdmin || auth.isAuditor)) {
    return { name: 'dashboard' }
  }

  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
})

export default router
