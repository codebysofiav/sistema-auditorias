<script setup>
import { ref, onMounted } from 'vue'
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
      apiClient.get('/planes-mejoramiento/'),
      apiClient.get('/auditorias/'),
    ])
    planes.value = planesRes.data.results ?? planesRes.data
    const auditorias = auditoriasRes.data.results ?? auditoriasRes.data
    auditoriasPorId.value = Object.fromEntries(auditorias.map((a) => [a.id, a.codigo]))
  } catch (err) {
    errorMsg.value = 'No se pudo cargar el listado de planes.'
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
          <h1>Planes de mejoramiento</h1>
          <p class="sub">
            {{ auth.isAdmin ? 'Todos los planes registrados.' : puedeEscribir ? 'Planes de sus auditorías asignadas.' : 'Listado en modo solo lectura.' }}
          </p>
        </div>
        <button v-if="puedeEscribir" class="btn-primary" @click="router.push({ name: 'plan-nuevo' })">
          + Nuevo plan
        </button>
      </div>

      <p v-if="loading" class="empty-note">Cargando...</p>
      <p v-else-if="errorMsg" class="empty-note">{{ errorMsg }}</p>
      <p v-else-if="planes.length === 0" class="empty-note">
        No hay planes de mejoramiento para mostrar todavía.
      </p>

      <table v-else>
        <thead>
          <tr>
            <th>Auditoría</th>
            <th>Estado</th>
            <th>Creado</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in planes" :key="p.id">
            <td class="code">{{ auditoriasPorId[p.auditoria] ?? p.auditoria }}</td>
            <td>{{ p.estado }}</td>
            <td class="code">{{ p.fecha_creacion }}</td>
            <td class="actions-cell">
              <button class="btn-link" @click="router.push({ name: 'plan-detalle', params: { id: p.id } })">
                Ver detalle
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </main>
  </div>
</template>

<style scoped>
.shell { display: flex; min-height: 100vh; }
.main { flex: 1; padding: 28px 36px; min-width: 0; }
.header-row { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; gap: 16px; }
.main h1 { font-size: 20px; font-weight: 600; margin: 0 0 2px; }
.sub { font-size: 13px; color: var(--ink-soft); margin: 0; }
.btn-primary { background: var(--ink); color: #F6F5F2; border: none; border-radius: var(--radius); padding: 9px 16px; font-size: 13px; font-weight: 500; cursor: pointer; white-space: nowrap; }
table { width: 100%; border-collapse: collapse; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; }
th { text-align: left; font-size: 11px; color: var(--ink-soft); font-weight: 500; padding: 10px 14px; border-bottom: 1px solid var(--line); background: #FBFAF8; }
td { padding: 11px 14px; font-size: 13px; border-bottom: 1px solid var(--line); }
tr:last-child td { border-bottom: none; }
.code { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: var(--ink-soft); }
.actions-cell { text-align: right; }
.btn-link { background: none; border: 1px solid var(--line); border-radius: var(--radius); padding: 5px 10px; font-size: 12px; cursor: pointer; color: var(--ink); }
.empty-note { font-size: 12px; color: var(--ink-soft); padding: 18px 14px; background: var(--surface); border: 1px dashed var(--line); border-radius: var(--radius); }
</style>