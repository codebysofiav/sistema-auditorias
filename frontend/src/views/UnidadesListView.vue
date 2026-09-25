<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import AppSidebar from '@/components/AppSidebar.vue'

const router = useRouter()
const auth = useAuthStore()
const unidades = ref([])
const loading = ref(true)
const errorMsg = ref('')
const desactivandoId = ref(null)
const puedeEscribir = auth.isAdmin || auth.isAuditor

async function cargar() {
  loading.value = true
  errorMsg.value = ''
  try {
    const { data } = await apiClient.get('/unidades/')
    unidades.value = data.results ?? data
  } catch {
    errorMsg.value = 'No se pudo cargar el listado de unidades.'
  } finally { loading.value = false }
}

async function desactivar(unidad) {
  if (!window.confirm(`¿Desactivar la unidad ${unidad.nombre_unidad}? Las auditorías asociadas se conservarán.`)) return
  desactivandoId.value = unidad.id
  try {
    await apiClient.delete(`/unidades/${unidad.id}/`)
    unidades.value = unidades.value.filter((item) => item.id !== unidad.id)
  } catch (err) {
    errorMsg.value = err.response?.status === 403 ? 'No tiene permiso para desactivar esta unidad.' : 'No se pudo desactivar la unidad.'
  } finally { desactivandoId.value = null }
}

onMounted(cargar)
</script>

<template>
  <div class="shell"><AppSidebar /><main class="main">
    <div class="header-row"><div><h1>Unidades auditadas</h1><p class="sub">{{ puedeEscribir ? 'Gestione las unidades disponibles para auditorías.' : 'Listado en modo solo lectura.' }}</p></div><button v-if="puedeEscribir" class="btn-primary" @click="router.push({ name: 'unidad-nueva' })">+ Nueva unidad</button></div>
    <p v-if="loading" class="empty-note">Cargando...</p><p v-else-if="errorMsg" class="empty-note">{{ errorMsg }}</p><p v-else-if="unidades.length === 0" class="empty-note">No hay unidades activas para mostrar.</p>
    <table v-else><thead><tr><th>Nombre</th><th>Tipo</th><th>Descripción</th><th></th></tr></thead><tbody><tr v-for="unidad in unidades" :key="unidad.id"><td>{{ unidad.nombre_unidad }}</td><td>{{ unidad.tipo }}</td><td>{{ unidad.descripcion || '—' }}</td><td class="actions-cell"><button class="btn-link" @click="router.push({ name: 'unidad-detalle', params: { id: unidad.id } })">{{ puedeEscribir ? 'Ver / Editar' : 'Ver' }}</button><button v-if="puedeEscribir" class="btn-danger" :disabled="desactivandoId === unidad.id" @click="desactivar(unidad)">{{ desactivandoId === unidad.id ? 'Desactivando...' : 'Desactivar' }}</button></td></tr></tbody></table>
  </main></div>
</template>

<style scoped>
.shell { display: flex; min-height: 100vh; }.main { flex: 1; min-width: 0; padding: 28px 36px; }.header-row { display: flex; justify-content: space-between; gap: 16px; margin-bottom: 24px; }h1 { margin: 0 0 2px; font-size: 20px; }.sub { margin: 0; color: var(--ink-soft); font-size: 13px; }.btn-primary { border: 0; background: var(--ink); color: #f6f5f2; cursor: pointer; padding: 9px 16px; }table { width: 100%; border: 1px solid var(--line); border-collapse: collapse; background: var(--surface); }th, td { border-bottom: 1px solid var(--line); font-size: 13px; padding: 11px 14px; text-align: left; }th { color: var(--ink-soft); font-size: 11px; font-weight: 500; }tr:last-child td { border-bottom: 0; }.actions-cell { display: flex; justify-content: flex-end; gap: 8px; white-space: nowrap; }.btn-link, .btn-danger { border: 1px solid var(--line); background: var(--surface); cursor: pointer; font-size: 12px; padding: 5px 10px; }.btn-danger { color: var(--warn); }.btn-danger:disabled { opacity: .6; }.empty-note { border: 1px dashed var(--line); background: var(--surface); color: var(--ink-soft); font-size: 12px; padding: 18px 14px; }
</style>
