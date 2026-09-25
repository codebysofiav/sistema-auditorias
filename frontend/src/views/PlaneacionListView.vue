<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import AppSidebar from '@/components/AppSidebar.vue'

const router = useRouter()
const auth = useAuthStore()
const planes = ref([])
const auditoriasPorId = ref({})
const loading = ref(true)
const errorMsg = ref('')

const puedeEscribir = auth.isAdmin || auth.isAuditor

async function cargar() {
  loading.value = true
  errorMsg.value = ''
  try {
    const [planesRes, auditoriasRes] = await Promise.all([
      apiClient.get('/planes-auditoria/'),
      apiClient.get('/auditorias/'),
    ])
    planes.value = planesRes.data.results ?? planesRes.data
    const auditorias = auditoriasRes.data.results ?? auditoriasRes.data
    auditoriasPorId.value = Object.fromEntries(auditorias.map((auditoria) => [auditoria.id, auditoria.codigo]))
  } catch {
    errorMsg.value = 'No se pudo cargar la información de planeación.'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<template>
  <div class="shell">
    <AppSidebar />
    <main class="main">
      <div class="header-row">
        <div>
          <h1>Planeación de auditorías</h1>
          <p class="sub">{{ puedeEscribir ? 'Planes de sus auditorías disponibles.' : 'Listado en modo solo lectura.' }}</p>
        </div>
        <button v-if="puedeEscribir" class="btn-primary" @click="router.push({ name: 'plan-auditoria-nuevo' })">+ Nuevo plan</button>
      </div>

      <p v-if="loading" class="empty-note">Cargando...</p>
      <p v-else-if="errorMsg" class="empty-note">{{ errorMsg }}</p>
      <p v-else-if="planes.length === 0" class="empty-note">No hay planes de auditoría para mostrar.</p>
      <table v-else>
        <thead><tr><th>Auditoría</th><th>Fecha de creación</th><th></th></tr></thead>
        <tbody>
          <tr v-for="plan in planes" :key="plan.id">
            <td class="code">{{ auditoriasPorId[plan.auditoria] ?? plan.auditoria }}</td>
            <td>{{ plan.fecha_creacion }}</td>
            <td class="actions-cell"><button class="btn-link" @click="router.push({ name: 'plan-auditoria-detalle', params: { id: plan.id } })">Ver detalle</button></td>
          </tr>
        </tbody>
      </table>
    </main>
  </div>
</template>

<style scoped>
.shell { display: flex; min-height: 100vh; } .main { flex: 1; min-width: 0; padding: 28px 36px; }
.header-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 24px; }
h1 { margin: 0 0 2px; font-size: 20px; font-weight: 600; } .sub { margin: 0; color: var(--ink-soft); font-size: 13px; }
.btn-primary { border: 0; border-radius: var(--radius); background: var(--ink); color: #f6f5f2; cursor: pointer; font-size: 13px; padding: 9px 16px; }
table { width: 100%; border: 1px solid var(--line); border-collapse: collapse; background: var(--surface); } th, td { padding: 11px 14px; border-bottom: 1px solid var(--line); font-size: 13px; text-align: left; } th { background: #fbfaf8; color: var(--ink-soft); font-size: 11px; font-weight: 500; } tr:last-child td { border-bottom: 0; }
.code { font-family: 'IBM Plex Mono', monospace; } .actions-cell { text-align: right; } .btn-link { border: 1px solid var(--line); border-radius: var(--radius); background: var(--surface); color: var(--ink); cursor: pointer; font-size: 12px; padding: 5px 10px; }
.empty-note { border: 1px dashed var(--line); background: var(--surface); color: var(--ink-soft); font-size: 12px; padding: 18px 14px; }
</style>
