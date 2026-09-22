<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/client'
import AppSidebar from '@/components/AppSidebar.vue'

// AJUSTAR: texto libre en el backend; convención sugerida del frontend.
const ESTADOS = ['Abierto', 'En progreso', 'Cerrado']

const router = useRouter()
const auditoriasDisponibles = ref([])
const loading = ref(true)
const guardando = ref(false)
const errorMsg = ref('')

const form = ref({
  auditoria: '',
  estado: ESTADOS[0],
  observaciones: '',
})

onMounted(async () => {
  loading.value = true
  try {
    const [auditoriasRes, planesRes] = await Promise.all([
      apiClient.get('/auditorias/'),
      apiClient.get('/planes-mejoramiento/'),
    ])
    const auditorias = auditoriasRes.data.results ?? auditoriasRes.data
    const planes = planesRes.data.results ?? planesRes.data
    // Como Auditoria 1---1 PlanMejoramiento, solo mostramos auditorías
    // que todavía NO tienen un plan creado.
    const auditoriasConPlan = new Set(planes.map((p) => p.auditoria))
    auditoriasDisponibles.value = auditorias.filter((a) => !auditoriasConPlan.has(a.id))
  } catch (err) {
    errorMsg.value = 'No se pudo cargar la información necesaria.'
  } finally {
    loading.value = false
  }
})

async function guardar() {
  guardando.value = true
  errorMsg.value = ''
  try {
    const { data } = await apiClient.post('/planes-mejoramiento/', form.value)
    router.push({ name: 'plan-detalle', params: { id: data.id } })
  } catch (err) {
    errorMsg.value =
      err.response?.status === 403
        ? 'No tiene permiso para realizar esta acción.'
        : 'Ocurrió un error al guardar. Revise los datos e intente de nuevo.'
  } finally {
    guardando.value = false
  }
}
</script>

<template>
  <div class="shell">
    <AppSidebar />

    <main class="main">
      <button class="btn-back" @click="router.push({ name: 'planes-mejoramiento' })">← Volver al listado</button>
      <h1>Nuevo plan de mejoramiento</h1>

      <p v-if="loading" class="empty-note">Cargando...</p>

      <form v-else class="form-card" @submit.prevent="guardar">
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <p v-if="auditoriasDisponibles.length === 0" class="empty-note">
          Todas las auditorías ya tienen un plan de mejoramiento creado.
        </p>

        <template v-else>
          <div class="field">
            <label>Auditoría</label>
            <select v-model="form.auditoria" required>
              <option value="" disabled>Seleccione una auditoría</option>
              <option v-for="a in auditoriasDisponibles" :key="a.id" :value="a.id">{{ a.codigo }}</option>
            </select>
          </div>

          <div class="field">
            <label>Estado</label>
            <select v-model="form.estado" required>
              <option v-for="e in ESTADOS" :key="e" :value="e">{{ e }}</option>
            </select>
          </div>

          <div class="field">
            <label>Observaciones</label>
            <textarea v-model="form.observaciones" rows="3"></textarea>
          </div>

          <button type="submit" class="btn-primary" :disabled="guardando">
            {{ guardando ? 'Guardando...' : 'Crear plan' }}
          </button>
        </template>
      </form>
    </main>
  </div>
</template>

<style scoped>
.shell { display: flex; min-height: 100vh; }
.main { flex: 1; padding: 28px 36px; min-width: 0; max-width: 560px; }
.main h1 { font-size: 20px; font-weight: 600; margin: 4px 0 20px; }
.btn-back { background: none; border: none; color: var(--ink-soft); font-size: 12px; cursor: pointer; padding: 0; }
.form-card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px; }
.field { margin-bottom: 16px; }
.field label { display: block; font-size: 13px; color: var(--ink-soft); margin-bottom: 6px; }
.field input, .field select, .field textarea { width: 100%; padding: 9px 11px; border: 1px solid var(--line); border-radius: var(--radius); font-size: 13px; font-family: inherit; background: var(--bg); color: var(--ink); }
.field textarea { resize: vertical; }
.field input:focus, .field select:focus, .field textarea:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
.error-msg { color: var(--warn); font-size: 13px; margin: 0 0 16px; }
.btn-primary { background: var(--ink); color: #F6F5F2; border: none; border-radius: var(--radius); padding: 10px 18px; font-size: 13px; font-weight: 500; cursor: pointer; }
.btn-primary:disabled { opacity: 0.6; cursor: default; }
.empty-note { font-size: 12px; color: var(--ink-soft); padding: 18px 14px; background: var(--surface); border: 1px dashed var(--line); border-radius: var(--radius); }
</style>