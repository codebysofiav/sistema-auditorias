<script setup>
import { ref, onMounted, computed } from 'vue'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import AppSidebar from '@/components/AppSidebar.vue'

const auth = useAuthStore()
const auditorias = ref([])
const loading = ref(true)
const errorMsg = ref('')

const titulo = computed(() => {
  if (auth.isAdmin) return 'Panel general'
  if (auth.isAuditor) return 'Mis auditorías asignadas'
  return 'Auditorías (solo lectura)'
})

const subtitulo = computed(() => {
  if (auth.isAdmin) return 'Vista completa del estado de todas las auditorías activas.'
  if (auth.isAuditor) return 'Solo se muestran las auditorías donde usted está asignado como auditor activo.'
  return 'Puede ver el estado de las auditorías, pero no editar ni crear registros.'
})

onMounted(async () => {
  // El backend ya filtra por rol automáticamente (AuditoriaRolePermission),
  // así que aquí simplemente pedimos el listado y confiamos en ese filtro.
  try {
    const { data } = await apiClient.get('/auditorias/')
    auditorias.value = data.results ?? data // AJUSTAR: según si tu API pagina o no
  } catch (err) {
    errorMsg.value = 'No se pudo cargar el listado de auditorías.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="shell">
    <AppSidebar />

    <main class="main">
      <h1>{{ titulo }}</h1>
      <p class="sub">{{ subtitulo }}</p>

      <div class="kpi-row">
        <div class="kpi">
          <div class="n">{{ auditorias.length }}</div>
          <div class="l">Auditorías visibles</div>
        </div>
      </div>

      <div class="table-title">
        {{ auth.isAdmin ? 'Todas las auditorías' : 'Auditorías asignadas' }}
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
            <th>Estado</th>
            <th>Vence</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in auditorias" :key="a.id">
            <td class="code">{{ a.codigo }}</td>
            <td>{{ a.unidad_auditada }}</td>
            <td>{{ a.estado }}</td>
            <td class="code">{{ a.fecha_fin }}</td>
          </tr>
        </tbody>
      </table>
    </main>
  </div>
</template>

<style scoped>
.shell { display: flex; min-height: 100vh; }
.main { flex: 1; padding: 28px 36px; min-width: 0; }
.main h1 { font-size: 20px; font-weight: 600; margin: 0 0 2px; }
.sub { font-size: 13px; color: var(--ink-soft); margin-bottom: 24px; }

.kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 28px; max-width: 260px; }
.kpi { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 16px; }
.kpi .n { font-family: 'IBM Plex Mono', monospace; font-size: 26px; font-weight: 500; }
.kpi .l { font-size: 12px; color: var(--ink-soft); margin-top: 4px; }

.table-title { font-size: 13px; font-weight: 600; margin: 0 0 10px; color: var(--ink-soft); }

table { width: 100%; border-collapse: collapse; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; }
th { text-align: left; font-size: 11px; color: var(--ink-soft); font-weight: 500; padding: 10px 14px; border-bottom: 1px solid var(--line); background: #FBFAF8; }
td { padding: 11px 14px; font-size: 13px; border-bottom: 1px solid var(--line); }
tr:last-child td { border-bottom: none; }
.code { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: var(--ink-soft); }

.empty-note { font-size: 12px; color: var(--ink-soft); padding: 18px 14px; background: var(--surface); border: 1px dashed var(--line); border-radius: var(--radius); }
</style>