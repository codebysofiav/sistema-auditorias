<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'
import AppSidebar from '@/components/AppSidebar.vue'

const route = useRoute()
const router = useRouter()
const esEdicion = computed(() => Boolean(route.params.id))
const auditoriasDisponibles = ref([])
const loading = ref(true)
const guardando = ref(false)
const errorMsg = ref('')
const form = ref({ auditoria: '', criterios: '', riesgos_oportunidades: '', documentos_referencia: '', fecha_creacion: '' })

function hoy() { return new Date().toISOString().slice(0, 10) }

async function cargar() {
  loading.value = true
  try {
    const [auditoriasRes, planesRes] = await Promise.all([apiClient.get('/auditorias/'), apiClient.get('/planes-auditoria/')])
    const auditorias = auditoriasRes.data.results ?? auditoriasRes.data
    const planes = planesRes.data.results ?? planesRes.data
    if (esEdicion.value) {
      const { data } = await apiClient.get(`/planes-auditoria/${route.params.id}/`)
      form.value = { ...data }
      auditoriasDisponibles.value = auditorias.filter((auditoria) => auditoria.id === data.auditoria)
    } else {
      const conPlan = new Set(planes.map((plan) => plan.auditoria))
      auditoriasDisponibles.value = auditorias.filter((auditoria) => !conPlan.has(auditoria.id))
      form.value.fecha_creacion = hoy()
    }
  } catch {
    errorMsg.value = 'No se pudo cargar la información necesaria.'
  } finally {
    loading.value = false
  }
}

async function guardar() {
  guardando.value = true
  errorMsg.value = ''
  try {
    if (esEdicion.value) await apiClient.patch(`/planes-auditoria/${route.params.id}/`, form.value)
    else await apiClient.post('/planes-auditoria/', form.value)
    router.push({ name: 'planeacion' })
  } catch (err) {
    errorMsg.value = err.response?.status === 403 ? 'No tiene permiso para realizar esta acción.' : 'No se pudo guardar el plan. Revise los datos.'
  } finally { guardando.value = false }
}

onMounted(cargar)
</script>

<template>
  <div class="shell"><AppSidebar /><main class="main">
    <button class="btn-back" @click="router.push({ name: esEdicion ? 'plan-auditoria-detalle' : 'planeacion', params: { id: route.params.id } })">Volver</button>
    <h1>{{ esEdicion ? 'Editar plan de auditoría' : 'Nuevo plan de auditoría' }}</h1>
    <p v-if="loading" class="empty-note">Cargando...</p>
    <form v-else class="form-card" @submit.prevent="guardar">
      <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
      <div class="field"><label>Auditoría</label><select v-model="form.auditoria" :disabled="esEdicion" required><option value="" disabled>Seleccione una auditoría</option><option v-for="auditoria in auditoriasDisponibles" :key="auditoria.id" :value="auditoria.id">{{ auditoria.codigo }}</option></select></div>
      <div class="field"><label>Criterios</label><textarea v-model="form.criterios" rows="4" required /></div>
      <div class="field"><label>Riesgos y oportunidades</label><textarea v-model="form.riesgos_oportunidades" rows="4" required /></div>
      <div class="field"><label>Documentos de referencia</label><textarea v-model="form.documentos_referencia" rows="4" required /></div>
      <div class="field"><label>Fecha de creación</label><input v-model="form.fecha_creacion" type="date" required /></div>
      <button class="btn-primary" type="submit" :disabled="guardando">{{ guardando ? 'Guardando...' : esEdicion ? 'Guardar cambios' : 'Crear plan' }}</button>
    </form>
  </main></div>
</template>

<style scoped>
.shell { display: flex; min-height: 100vh; } .main { flex: 1; max-width: 720px; min-width: 0; padding: 28px 36px; } h1 { margin: 4px 0 20px; font-size: 20px; font-weight: 600; }.btn-back { border: 0; background: none; color: var(--ink-soft); cursor: pointer; padding: 0; }.form-card { border: 1px solid var(--line); background: var(--surface); padding: 24px; }.field { margin-bottom: 16px; }.field label { display: block; color: var(--ink-soft); font-size: 13px; margin-bottom: 6px; }.field input, .field select, .field textarea { width: 100%; border: 1px solid var(--line); background: var(--bg); color: var(--ink); font: inherit; padding: 9px 11px; }.field textarea { resize: vertical; }.btn-primary { border: 0; background: var(--ink); color: #f6f5f2; cursor: pointer; padding: 10px 18px; }.btn-primary:disabled { opacity: .6; }.error-msg { color: var(--warn); font-size: 13px; }.empty-note { color: var(--ink-soft); font-size: 12px; }
</style>
