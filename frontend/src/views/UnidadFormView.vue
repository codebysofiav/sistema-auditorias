<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import AppSidebar from '@/components/AppSidebar.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const esEdicion = computed(() => Boolean(route.params.id))
const esSoloLectura = computed(() => auth.isConsulta)
const loading = ref(false)
const guardando = ref(false)
const errorMsg = ref('')
const form = ref({ nombre_unidad: '', tipo: '', descripcion: '', activo: true })

async function cargar() {
  if (!esEdicion.value) return
  loading.value = true
  try { const { data } = await apiClient.get(`/unidades/${route.params.id}/`); form.value = data } catch { errorMsg.value = 'No se pudo cargar la unidad.' } finally { loading.value = false }
}
async function guardar() {
  guardando.value = true; errorMsg.value = ''
  try { if (esEdicion.value) await apiClient.patch(`/unidades/${route.params.id}/`, form.value); else await apiClient.post('/unidades/', form.value); router.push({ name: 'unidades' }) } catch (err) { errorMsg.value = err.response?.status === 403 ? 'No tiene permiso para realizar esta acción.' : 'No se pudo guardar la unidad. Revise los datos.' } finally { guardando.value = false }
}
onMounted(cargar)
</script>

<template>
  <div class="shell"><AppSidebar /><main class="main"><button class="btn-back" @click="router.push({ name: 'unidades' })">Volver al listado</button><h1>{{ esSoloLectura ? 'Unidad auditada' : esEdicion ? 'Editar unidad auditada' : 'Nueva unidad auditada' }}</h1><p v-if="loading" class="empty-note">Cargando...</p><form v-else class="form-card" @submit.prevent="guardar"><p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p><div class="field"><label>Nombre de la unidad</label><input v-model="form.nombre_unidad" type="text" :disabled="esSoloLectura" required></div><div class="field"><label>Tipo</label><input v-model="form.tipo" type="text" :disabled="esSoloLectura" required></div><div class="field"><label>Descripción</label><textarea v-model="form.descripcion" rows="4" :disabled="esSoloLectura"></textarea></div><label v-if="!esSoloLectura && esEdicion" class="checkbox"><input v-model="form.activo" type="checkbox"> Unidad activa</label><button v-if="!esSoloLectura" class="btn-primary" type="submit" :disabled="guardando">{{ guardando ? 'Guardando...' : 'Guardar' }}</button></form></main></div>
</template>

<style scoped>
.shell { display: flex; min-height: 100vh; }.main { flex: 1; max-width: 640px; min-width: 0; padding: 28px 36px; }h1 { margin: 4px 0 20px; font-size: 20px; }.btn-back { border: 0; background: none; color: var(--ink-soft); cursor: pointer; padding: 0; }.form-card { border: 1px solid var(--line); background: var(--surface); padding: 24px; }.field { margin-bottom: 16px; }.field label { display: block; color: var(--ink-soft); font-size: 13px; margin-bottom: 6px; }.field input, .field textarea { width: 100%; border: 1px solid var(--line); background: var(--bg); color: var(--ink); font: inherit; padding: 9px 11px; }.field textarea { resize: vertical; }.checkbox { display: block; font-size: 13px; margin-bottom: 16px; }.checkbox input { width: auto; margin-right: 7px; }.btn-primary { border: 0; background: var(--ink); color: #f6f5f2; cursor: pointer; padding: 10px 18px; }.btn-primary:disabled { opacity: .6; }.error-msg { color: var(--warn); font-size: 13px; }.empty-note { color: var(--ink-soft); font-size: 12px; }
</style>
