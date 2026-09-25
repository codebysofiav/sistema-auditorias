<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import AppSidebar from '@/components/AppSidebar.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const esEdicion = computed(() => Boolean(route.params.cronogramaId))
const esSoloLectura = computed(() => auth.isConsulta)
const loading = ref(true)
const guardando = ref(false)
const errorMsg = ref('')
const form = ref({ fecha_actividad: '', hora: '', actividad: '', auditado: '' })

async function cargar() {
  if (!esEdicion.value) { loading.value = false; return }
  try {
    const { data } = await apiClient.get(`/cronogramas/${route.params.cronogramaId}/`)
    form.value = { fecha_actividad: data.fecha_actividad, hora: data.hora?.slice(0, 5), actividad: data.actividad, auditado: data.auditado }
  } catch { errorMsg.value = 'No se pudo cargar la actividad.' } finally { loading.value = false }
}

async function guardar() {
  guardando.value = true
  errorMsg.value = ''
  try {
    const payload = { ...form.value, plan_auditoria: Number(route.params.planId) }
    if (esEdicion.value) await apiClient.patch(`/cronogramas/${route.params.cronogramaId}/`, payload)
    else await apiClient.post('/cronogramas/', payload)
    router.push({ name: 'plan-auditoria-detalle', params: { id: route.params.planId } })
  } catch (err) { errorMsg.value = err.response?.status === 403 ? 'No tiene permiso para realizar esta acción.' : 'No se pudo guardar la actividad. Revise los datos.' } finally { guardando.value = false }
}

onMounted(cargar)
</script>

<template>
  <div class="shell"><AppSidebar /><main class="main">
    <button class="btn-back" @click="router.push({ name: 'plan-auditoria-detalle', params: { id: route.params.planId } })">Volver al plan</button>
    <h1>{{ esSoloLectura ? 'Actividad del cronograma' : esEdicion ? 'Editar actividad' : 'Nueva actividad' }}</h1>
    <p v-if="loading" class="empty-note">Cargando...</p>
    <form v-else class="form-card" @submit.prevent="guardar"><p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p><div class="grid"><div class="field"><label>Fecha</label><input v-model="form.fecha_actividad" type="date" :disabled="esSoloLectura" required></div><div class="field"><label>Hora</label><input v-model="form.hora" type="time" :disabled="esSoloLectura" required></div></div><div class="field"><label>Actividad</label><textarea v-model="form.actividad" rows="4" :disabled="esSoloLectura" required></textarea></div><div class="field"><label>Auditado</label><input v-model="form.auditado" type="text" :disabled="esSoloLectura" required></div><button v-if="!esSoloLectura" class="btn-primary" type="submit" :disabled="guardando">{{ guardando ? 'Guardando...' : 'Guardar' }}</button></form>
  </main></div>
</template>

<style scoped>
.shell { display: flex; min-height: 100vh; }.main { flex: 1; max-width: 640px; min-width: 0; padding: 28px 36px; }h1 { margin: 4px 0 20px; font-size: 20px; }.btn-back { border: 0; background: none; color: var(--ink-soft); cursor: pointer; padding: 0; }.form-card { border: 1px solid var(--line); background: var(--surface); padding: 24px; }.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }.field { margin-bottom: 16px; }.field label { display: block; color: var(--ink-soft); font-size: 13px; margin-bottom: 6px; }.field input, .field textarea { width: 100%; border: 1px solid var(--line); background: var(--bg); color: var(--ink); font: inherit; padding: 9px 11px; }.field textarea { resize: vertical; }.btn-primary { border: 0; background: var(--ink); color: #f6f5f2; cursor: pointer; padding: 10px 18px; }.btn-primary:disabled { opacity: .6; }.error-msg { color: var(--warn); font-size: 13px; }.empty-note { color: var(--ink-soft); font-size: 12px; }
</style>
