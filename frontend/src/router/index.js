import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import AuditoriasListView from '@/views/AuditoriasListView.vue'
import AuditoriaFormView from '@/views/AuditoriaFormView.vue'
import HallazgosListView from '@/views/HallazgosListView.vue'
import HallazgoFormView from '@/views/HallazgoFormView.vue'

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
    // AJUSTAR: aquí se van agregando las rutas de los demás módulos
    // (planes de mejoramiento, informes, documentos, etc.) a medida que se construyan.
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