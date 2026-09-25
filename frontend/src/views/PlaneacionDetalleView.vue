<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import AppSidebar from '@/components/AppSidebar.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const plan = ref(null)
const auditoria = ref(null)
const cronogramas = ref([])
const equipo = ref([])
const usuariosPorId = ref({})
const loading = ref(true)
const errorMsg = ref('')
const puedeEscribir = auth.isAdmin || auth.isAuditor

async function cargar() {
  loading.value = true
  try {
    const { data: planData } = await apiClient.get(`/planes-auditoria/${route.params.id}/`)
    plan.value = planData
    const [auditoriaRes, cronogramasRes, equipoRes] = await Promise.all([
      apiClient.get(`/auditorias/${planData.auditoria}/`),
      apiClient.get('/cronogramas/'),
      apiClient.get('/auditoria-auditores/'),
    ])
    auditoria.value = auditoriaRes.data
    const todosLosCronogramas = cronogramasRes.data.results ?? cronogramasRes.data
    cronogramas.value = todosLosCronogramas
      .filter((cronograma) => cronograma.plan_auditoria === planData.id)
      .sort((a, b) => `${a.fecha_actividad}${a.hora}`.localeCompare(`${b.fecha_actividad}${b.hora}`))
    const asignaciones = equipoRes.data.results ?? equipoRes.data
    equipo.value = asignaciones.filter((asignacion) => asignacion.auditoria === planData.auditoria && asignacion.activo)

    if (auth.isAdmin) {
      const { data } = await apiClient.get('/auth/usuarios/')
      const usuarios = data.results ?? data
      usuariosPorId.value = Object.fromEntries(usuarios.map((usuario) => [usuario.id, usuario]))
    }
  } catch {
    errorMsg.value = 'No se pudo cargar el detalle de planeación.'
  } finally { loading.value = false }
}

function nombreAuditor(id) {
  const usuario = usuariosPorId.value[id]
  return usuario ? `${usuario.first_name} ${usuario.last_name}`.trim() || usuario.email : `Usuario #${id}`
}

onMounted(cargar)
</script>

<template>
  <div class="shell"><AppSidebar /><main class="main">
    <button class="btn-back" @click="router.push({ name: 'planeacion' })">Volver al listado</button>
    <p v-if="loading" class="empty-note">Cargando...</p>
    <p v-else-if="errorMsg" class="empty-note">{{ errorMsg }}</p>
    <template v-else>
      <div class="header-row"><div><h1>Plan de auditoría {{ auditoria?.codigo }}</h1><p class="sub">Creado: {{ plan.fecha_creacion }}</p></div><button v-if="puedeEscribir" class="btn-primary" @click="router.push({ name: 'plan-auditoria-editar', params: { id: plan.id } })">Editar plan</button></div>
      <section><h2>Criterios</h2><p>{{ plan.criterios }}</p></section>
      <section><h2>Riesgos y oportunidades</h2><p>{{ plan.riesgos_oportunidades }}</p></section>
      <section><h2>Documentos de referencia</h2><p>{{ plan.documentos_referencia }}</p></section>
      <section><h2>Equipo auditor</h2><p v-if="equipo.length === 0" class="empty-note">No hay auditores activos asignados.</p><ul v-else><li v-for="asignacion in equipo" :key="asignacion.id">{{ nombreAuditor(asignacion.auditor) }}</li></ul></section>
      <div class="section-header"><h2>Cronograma de actividades</h2><button v-if="puedeEscribir" class="btn-primary" @click="router.push({ name: 'cronograma-nuevo', params: { planId: plan.id } })">Nueva actividad</button></div>
      <p v-if="cronogramas.length === 0" class="empty-note">No hay actividades programadas.</p>
      <table v-else><thead><tr><th>Fecha</th><th>Hora</th><th>Actividad</th><th>Auditado</th><th></th></tr></thead><tbody><tr v-for="cronograma in cronogramas" :key="cronograma.id"><td>{{ cronograma.fecha_actividad }}</td><td>{{ cronograma.hora }}</td><td>{{ cronograma.actividad }}</td><td>{{ cronograma.auditado }}</td><td class="actions-cell"><button class="btn-link" @click="router.push({ name: 'cronograma-detalle', params: { planId: plan.id, cronogramaId: cronograma.id } })">{{ puedeEscribir ? 'Ver / Editar' : 'Ver' }}</button></td></tr></tbody></table>
    </template>
  </main></div>
</template>

<style scoped>
.shell { display: flex; min-height: 100vh; } .main { flex: 1; min-width: 0; padding: 28px 36px; } .btn-back { border: 0; background: none; color: var(--ink-soft); cursor: pointer; padding: 0 0 14px; } .header-row, .section-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }.header-row { margin-bottom: 18px; }.section-header { align-items: center; margin-top: 28px; } h1 { margin: 0 0 2px; font-size: 20px; } h2 { color: var(--ink-soft); font-size: 13px; margin: 0 0 8px; } .sub, section p, li { font-size: 13px; } .sub { color: var(--ink-soft); margin: 0; } section { border: 1px solid var(--line); background: var(--surface); margin: 12px 0; padding: 14px; } section p { margin: 0; white-space: pre-line; } ul { margin: 0; padding-left: 20px; }.btn-primary { border: 0; background: var(--ink); color: #f6f5f2; cursor: pointer; font-size: 13px; padding: 9px 16px; } table { width: 100%; border-collapse: collapse; background: var(--surface); border: 1px solid var(--line); } th, td { border-bottom: 1px solid var(--line); font-size: 13px; padding: 11px 14px; text-align: left; } th { color: var(--ink-soft); font-size: 11px; font-weight: 500; } tr:last-child td { border-bottom: 0; }.actions-cell { text-align: right; }.btn-link { border: 1px solid var(--line); background: var(--surface); cursor: pointer; font-size: 12px; padding: 5px 10px; }.empty-note { color: var(--ink-soft); font-size: 12px; }
</style>
