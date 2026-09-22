<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import AppSidebar from '@/components/AppSidebar.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const plan = ref(null)
const acciones = ref([])
const auditoriaCodigo = ref('')
const loading = ref(true)
const errorMsg = ref('')

const puedeEscribir = auth.isAdmin || auth.isAuditor

async function cargar() {
  loading.value = true
  errorMsg.value = ''
  try {
    const { data: planData } = await apiClient.get(`/planes-mejoramiento/${route.params.id}/`)
    plan.value = planData

    const { data: auditoriaData } = await apiClient.get(`/auditorias/${planData.auditoria}/`)
    auditoriaCodigo.value = auditoriaData.codigo

    const { data: accionesData } = await apiClient.get('/acciones-mejoramiento/')
    const todas = accionesData.results ?? accionesData
    acciones.value = todas.filter((a) => a.plan === planData.id)
  } catch (err) {
    errorMsg.value = 'No se pudo cargar el plan.'
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
      <button class="btn-back" @click="router.push({ name: 'planes-mejoramiento' })">← Volver al listado</button>

      <p v-if="loading" class="empty-note">Cargando...</p>
      <p v-else-if="errorMsg" class="empty-note">{{ errorMsg }}</p>

      <template v-else>
        <div class="header-row">
          <div>
            <h1>Plan de mejoramiento — {{ auditoriaCodigo }}</h1>
            <p class="sub">Estado: {{ plan.estado }} · Creado: {{ plan.fecha_creacion }}</p>
          </div>
          <button v-if="puedeEscribir" class="btn-primary" @click="router.push({ name: 'accion-nueva', params: { planId: plan.id } })">
            + Nueva acción
          </button>
        </div>

        <p v-if="plan.observaciones" class="observaciones">{{ plan.observaciones }}</p>

        <div class="table-title">Acciones de mejora</div>

        <p v-if="acciones.length === 0" class="empty-note">
          Este plan todavía no tiene acciones registradas.
        </p>

        <table v-else>
          <thead>
            <tr>
              <th>Descripción</th>
              <th>Responsable</th>
              <th>Avance</th>
              <th>Estado</th>
              <th>Vence</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in acciones" :key="a.id">
              <td>{{ a.descripcion }}</td>
              <td>{{ a.responsable }}</td>
              <td class="code">{{ a.porcentaje_avance }}%</td>
              <td>{{ a.estado }}</td>
              <td class="code">{{ a.fecha_limite }}</td>
              <td class="actions-cell">
                <button class="btn-link" @click="router.push({ name: 'accion-detalle', params: { planId: plan.id, accionId: a.id } })">
                  {{ puedeEscribir ? 'Ver / Editar' : 'Ver' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </template>
    </main>
  </div>
</template>

<style scoped>
.shell { display: flex; min-height: 100vh; }
.main { flex: 1; padding: 28px 36px; min-width: 0; }
.btn-back { background: none; border: none; color: var(--ink-soft); font-size: 12px; cursor: pointer; padding: 0; margin-bottom: 14px; display: block; }
.header-row { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; gap: 16px; }
.main h1 { font-size: 20px; font-weight: 600; margin: 0 0 2px; }
.sub { font-size: 13px; color: var(--ink-soft); margin: 0; }
.observaciones { font-size: 13px; color: var(--ink-soft); background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 12px 14px; margin: 14px 0 24px; }
.btn-primary { background: var(--ink); color: #F6F5F2; border: none; border-radius: var(--radius); padding: 9px 16px; font-size: 13px; font-weight: 500; cursor: pointer; white-space: nowrap; }
.table-title { font-size: 13px; font-weight: 600; margin: 24px 0 10px; color: var(--ink-soft); }
table { width: 100%; border-collapse: collapse; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; }
th { text-align: left; font-size: 11px; color: var(--ink-soft); font-weight: 500; padding: 10px 14px; border-bottom: 1px solid var(--line); background: #FBFAF8; }
td { padding: 11px 14px; font-size: 13px; border-bottom: 1px solid var(--line); }
tr:last-child td { border-bottom: none; }
.code { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: var(--ink-soft); }
.actions-cell { text-align: right; }
.btn-link { background: none; border: 1px solid var(--line); border-radius: var(--radius); padding: 5px 10px; font-size: 12px; cursor: pointer; color: var(--ink); }
.empty-note { font-size: 12px; color: var(--ink-soft); padding: 18px 14px; background: var(--surface); border: 1px dashed var(--line); border-radius: var(--radius); }
</style>