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
    // AJUSTAR: aquí se van agregando las rutas de los módulos restantes
    // (Usuarios) a medida que se construyan.
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }

  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
})

export default router