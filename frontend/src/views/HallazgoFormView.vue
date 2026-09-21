<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'
import AppSidebar from '@/components/AppSidebar.vue'

// AJUSTAR: texto libre en el backend; esta lista es solo convención
// del frontend para mantener valores consistentes.
const ESTADOS = ['Abierto', 'En seguimiento', 'Cerrado']

const route = useRoute()
const router = useRouter()

const esEdicion = computed(() => !!route.params.id)

const auditorias = ref([])
const loading = ref(true)
const guardando = ref(false)
const errorMsg = ref('')
const siguienteNumero = ref(null)

const form = ref({
  auditoria: '',
  titulo: '',
  condicion: '',
  criterio: '',
  causa: '',
  efecto: '',
  estado: ESTADOS[0],
  recomendaciones: '',
})

async function cargarAuditorias() {
  const { data } = await apiClient.get('/auditorias/')
  auditorias.value = data.results ?? data
}

// Calcula el siguiente número de hallazgo para la auditoría seleccionada,
// consultando cuántos hallazgos ya tiene esa auditoría.
// NOTA: es un cálculo simple del lado del frontend. Si dos personas crean
// un hallazgo para la misma auditoría al mismo tiempo, podrían coincidir
// en el número — para un equipo pequeño esto es poco probable, pero si
// se vuelve un problema, se debería mover este cálculo al backend.
async function calcularSiguienteNumero(auditoriaId) {
  if (!auditoriaId) {
    siguienteNumero.value = null
    return
  }
  const { data } = await apiClient.get('/hallazgos/')
  const todos = data.results ?? data
  const deEstaAuditoria = todos.filter((h) => h.auditoria === auditoriaId)
  const maxActual = deEstaAuditoria.reduce((max, h) => Math.max(max, h.numero_hallazgo), 0)
  siguienteNumero.value = maxActual + 1
}

async function onAuditoriaChange() {
  await calcularSiguienteNumero(form.value.auditoria)
}

async function cargarHallazgo() {
  const { data } = await apiClient.get(`/hallazgos/${route.params.id}/`)
  form.value = {
    auditoria: data.auditoria,
    titulo: data.titulo,
    condicion: data.condicion,
    criterio: data.criterio,
    causa: data.causa,
    efecto: data.efecto,
    estado: data.estado,
    recomendaciones: data.recomendaciones,
  }
  siguienteNumero.value = data.numero_hallazgo
}

onMounted(async () => {
  loading.value = true
  try {
    await cargarAuditorias()
    if (esEdicion.value) {
      await cargarHallazgo()
    }
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
    const payload = { ...form.value, numero_hallazgo: siguienteNumero.value }

    if (esEdicion.value) {
      await apiClient.patch(`/hallazgos/${route.params.id}/`, payload)
    } else {
      await apiClient.post('/hallazgos/', payload)
    }
    router.push({ name: 'hallazgos' })
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
      <button class="btn-back" @click="router.push({ name: 'hallazgos' })">← Volver al listado</button>
      <h1>{{ esEdicion ? 'Editar hallazgo' : 'Nuevo hallazgo' }}</h1>

      <p v-if="loading" class="empty-note">Cargando...</p>

      <form v-else class="form-card" @submit.prevent="guardar">
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <div class="field">
          <label>Auditoría</label>
          <select v-model="form.auditoria" required :disabled="esEdicion" @change="onAuditoriaChange">
            <option value="" disabled>Seleccione una auditoría</option>
            <option v-for="a in auditorias" :key="a.id" :value="a.id">{{ a.codigo }}</option>
          </select>
        </div>

        <div class="field" v-if="siguienteNumero !== null">
          <label>Número de hallazgo</label>
          <input :value="siguienteNumero" type="text" disabled class="readonly-input" />
        </div>

        <div class="field">
          <label>Título</label>
          <input v-model="form.titulo" type="text" required />
        </div>

        <div class="grid-2">
          <div class="field">
            <label>Condición</label>
            <textarea v-model="form.condicion" rows="2" required></textarea>
          </div>
          <div class="field">
            <label>Criterio</label>
            <textarea v-model="form.criterio" rows="2" required></textarea>
          </div>
        </div>

        <div class="grid-2">
          <div class="field">
            <label>Causa</label>
            <textarea v-model="form.causa" rows="2" required></textarea>
          </div>
          <div class="field">
            <label>Efecto</label>
            <textarea v-model="form.efecto" rows="2" required></textarea>
          </div>
        </div>

        <div class="field">
          <label>Recomendaciones</label>
          <textarea v-model="form.recomendaciones" rows="2" required></textarea>
        </div>

        <div class="field">
          <label>Estado</label>
          <select v-model="form.estado" required>
            <option v-for="e in ESTADOS" :key="e" :value="e">{{ e }}</option>
          </select>
        </div>

        <button type="submit" class="btn-primary" :disabled="guardando || !form.auditoria">
          {{ guardando ? 'Guardando...' : esEdicion ? 'Guardar cambios' : 'Crear hallazgo' }}
        </button>
      </form>
    </main>
  </div>
</template>

<style scoped>
.shell { display: flex; min-height: 100vh; }
.main { flex: 1; padding: 28px 36px; min-width: 0; max-width: 640px; }
.main h1 { font-size: 20px; font-weight: 600; margin: 4px 0 20px; }

.btn-back { background: none; border: none; color: var(--ink-soft); font-size: 12px; cursor: pointer; padding: 0; }

.form-card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.field { margin-bottom: 16px; }
.field label { display: block; font-size: 13px; color: var(--ink-soft); margin-bottom: 6px; }
.field input, .field select, .field textarea {
  width: 100%;
  padding: 9px 11px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  font-size: 13px;
  font-family: inherit;
  background: var(--bg);
  color: var(--ink);
}
.field textarea { resize: vertical; }
.field input:focus, .field select:focus, .field textarea:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
.readonly-input { background: var(--accent-soft) !important; color: #6B4E1F; font-family: 'IBM Plex Mono', monospace; }

.error-msg { color: var(--warn); font-size: 13px; margin: 0 0 16px; }

.btn-primary {
  background: var(--ink);
  color: #F6F5F2;
  border: none;
  border-radius: var(--radius);
  padding: 10px 18px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; cursor: default; }

.empty-note { font-size: 12px; color: var(--ink-soft); padding: 18px 14px; background: var(--surface); border: 1px dashed var(--line); border-radius: var(--radius); }
</style>