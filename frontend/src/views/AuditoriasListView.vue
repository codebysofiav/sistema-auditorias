<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import AppSidebar from '@/components/AppSidebar.vue'

const router = useRouter()
const auth = useAuthStore()

const auditorias = ref([])
const loading = ref(true)
const errorMsg = ref('')

// Consulta no puede crear ni editar; Admin y Auditor sí.
const puedeEscribir = auth.isAdmin || auth.isAuditor

async function cargar() {
  loading.value = true
  errorMsg.value = ''
  try {
    const { data } = await apiClient.get('/auditorias/')
    auditorias.value = data.results ?? data // AJUSTAR según si tu API pagina
  } catch (err) {
    errorMsg.value = 'No se pudo cargar el listado de auditorías.'
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
          <h1>Auditorías</h1>
          <p class="sub">
            {{ auth.isAdmin ? 'Listado completo de auditorías.' : puedeEscribir ? 'Auditorías donde usted está asignado.' : 'Listado en modo solo lectura.' }}
          </p>
        </div>
        <button v-if="puedeEscribir" class="btn-primary" @click="router.push({ name: 'auditoria-nueva' })">
          + Nueva auditoría
        </button>
      </div>

      <p v-if="loading" class="empty-note">Cargando...</p>
      <p v-else-if="errorMsg" class="empty-note">{{ errorMsg }}</p>
      <p v-else-if="auditorias.length === 0" class="empty-note">
        No hay auditorías para mostrar todavía.
      </p>

      <table v-else>
        <thead>
          <tr>
            <th>Código</th>
            <th>Unidad</th>
            <th>Tipo</th>
            <th>Estado</th>
            <th>Inicio</th>
            <th>Fin</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in auditorias" :key="a.id">
            <td class="code">{{ a.codigo }}</td>
            <td>{{ a.unidad_auditada_nombre ?? a.unidad_auditada }}</td>
            <td>{{ a.tipo_auditoria }}</td>
            <td>{{ a.estado }}</td>
            <td class="code">{{ a.fecha_inicio }}</td>
            <td class="code">{{ a.fecha_fin }}</td>
            <td class="actions-cell">
              <button class="btn-link" @click="router.push({ name: 'auditoria-detalle', params: { id: a.id } })">
                {{ puedeEscribir ? 'Ver / Editar' : 'Ver' }}
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

.btn-primary {
  background: var(--ink);
  color: #F6F5F2;
  border: none;
  border-radius: var(--radius);
  padding: 9px 16px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
}

table { width: 100%; border-collapse: collapse; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; }
th { text-align: left; font-size: 11px; color: var(--ink-soft); font-weight: 500; padding: 10px 14px; border-bottom: 1px solid var(--line); background: #FBFAF8; }
td { padding: 11px 14px; font-size: 13px; border-bottom: 1px solid var(--line); }
tr:last-child td { border-bottom: none; }
.code { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: var(--ink-soft); }
.actions-cell { text-align: right; }

.btn-link {
  background: none;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 5px 10px;
  font-size: 12px;
  cursor: pointer;
  color: var(--ink);
}

.empty-note { font-size: 12px; color: var(--ink-soft); padding: 18px 14px; background: var(--surface); border: 1px dashed var(--line); border-radius: var(--radius); }
</style>