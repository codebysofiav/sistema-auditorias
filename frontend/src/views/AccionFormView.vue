<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'
import AppSidebar from '@/components/AppSidebar.vue'

// AJUSTAR: texto libre en el backend; convención sugerida del frontend.
const ESTADOS_ACCION = ['Pendiente', 'En progreso', 'Cerrada', 'Vencida']
const ESTADOS_SEGUIMIENTO = ['En progreso', 'Cumplido', 'Retrasado']

const route = useRoute()
const router = useRouter()

const esEdicion = computed(() => !!route.params.accionId)

const hallazgos = ref([])
const loading = ref(true)
const guardando = ref(false)
const errorMsg = ref('')

const form = ref({
  hallazgo: '',
  descripcion: '',
  responsable: '',
  fecha_inicio: '',
  fecha_limite: '',
  porcentaje_avance: 0,
  estado: ESTADOS_ACCION[0],
  observaciones: '',
})

// --- Seguimientos (solo visibles al editar una acción existente) ---
const seguimientos = ref([])
const nuevoSeguimiento = ref({
  porcentaje_avance: 0,
  descripcion: '',
  fecha_seguimiento: '',
  estado: ESTADOS_SEGUIMIENTO[0],
  observaciones: '',
  evidencias: '',
})
const guardandoSeguimiento = ref(false)

async function cargarHallazgosDeLaAuditoria() {
  // El plan no trae directamente la auditoría en esta vista, así que
  // la deducimos a partir del plan al que pertenece esta acción/ruta.
  const { data: plan } = await apiClient.get(`/planes-mejoramiento/${route.params.planId}/`)
  const { data: hallazgosData } = await apiClient.get('/hallazgos/')
  const todos = hallazgosData.results ?? hallazgosData
  hallazgos.value = todos.filter((h) => h.auditoria === plan.auditoria)
}

async function cargarAccion() {
  const { data } = await apiClient.get(`/acciones-mejoramiento/${route.params.accionId}/`)
  form.value = {
    hallazgo: data.hallazgo,
    descripcion: data.descripcion,
    responsable: data.responsable,
    fecha_inicio: data.fecha_inicio,
    fecha_limite: data.fecha_limite,
    porcentaje_avance: data.porcentaje_avance,
    estado: data.estado,
    observaciones: data.observaciones,
  }
}

async function cargarSeguimientos() {
  const { data } = await apiClient.get('/seguimientos/')
  const todos = data.results ?? data
  seguimientos.value = todos
    .filter((s) => s.accion === Number(route.params.accionId))
    .sort((a, b) => (a.fecha_seguimiento < b.fecha_seguimiento ? 1 : -1))
}

onMounted(async () => {
  loading.value = true
  try {
    await cargarHallazgosDeLaAuditoria()
    if (esEdicion.value) {
      await cargarAccion()
      await cargarSeguimientos()
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
    const payload = { ...form.value, plan: Number(route.params.planId) }
    if (esEdicion.value) {
      await apiClient.patch(`/acciones-mejoramiento/${route.params.accionId}/`, payload)
    } else {
      const { data } = await apiClient.post('/acciones-mejoramiento/', payload)
      router.push({ name: 'accion-detalle', params: { planId: route.params.planId, accionId: data.id } })
      return
    }
    router.push({ name: 'plan-detalle', params: { id: route.params.planId } })
  } catch (err) {
    errorMsg.value =
      err.response?.status === 403
        ? 'No tiene permiso para realizar esta acción.'
        : 'Ocurrió un error al guardar. Revise los datos e intente de nuevo.'
  } finally {
    guardando.value = false
  }
}

async function agregarSeguimiento() {
  guardandoSeguimiento.value = true
  try {
    await apiClient.post('/seguimientos/', {
      ...nuevoSeguimiento.value,
      accion: Number(route.params.accionId),
    })
    // Reflejamos el nuevo % de avance también en la acción, para mantenerlas sincronizadas.
    form.value.porcentaje_avance = nuevoSeguimiento.value.porcentaje_avance
    await apiClient.patch(`/acciones-mejoramiento/${route.params.accionId}/`, {
      porcentaje_avance: nuevoSeguimiento.value.porcentaje_avance,
    })
    nuevoSeguimiento.value = { porcentaje_avance: 0, descripcion: '', fecha_seguimiento: '', estado: ESTADOS_SEGUIMIENTO[0], observaciones: '', evidencias: '' }
    await cargarSeguimientos()
  } catch (err) {
    errorMsg.value = 'No se pudo guardar el seguimiento.'
  } finally {
    guardandoSeguimiento.value = false
  }
}
</script>

<template>
  <div class="shell">
    <AppSidebar />

    <main class="main">
      <button class="btn-back" @click="router.push({ name: 'plan-detalle', params: { id: route.params.planId } })">
        ← Volver al plan
      </button>
      <h1>{{ esEdicion ? 'Editar acción' : 'Nueva acción de mejora' }}</h1>

      <p v-if="loading" class="empty-note">Cargando...</p>

      <template v-else>
        <form class="form-card" @submit.prevent="guardar">
          <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

          <div class="field">
            <label>Hallazgo relacionado</label>
            <select v-model="form.hallazgo" required>
              <option value="" disabled>Seleccione un hallazgo</option>
              <option v-for="h in hallazgos" :key="h.id" :value="h.id">
                #{{ h.numero_hallazgo }} — {{ h.titulo }}
              </option>
            </select>
          </div>

          <div class="field">
            <label>Descripción de la acción</label>
            <textarea v-model="form.descripcion" rows="2" required></textarea>
          </div>

          <div class="field">
            <label>Responsable</label>
            <input v-model="form.responsable" type="text" required />
          </div>

          <div class="grid-2">
            <div class="field">
              <label>Fecha de inicio</label>
              <input v-model="form.fecha_inicio" type="date" required />
            </div>
            <div class="field">
              <label>Fecha límite</label>
              <input v-model="form.fecha_limite" type="date" required />
            </div>
          </div>

          <div class="grid-2">
            <div class="field">
              <label>% de avance</label>
              <input v-model.number="form.porcentaje_avance" type="number" min="0" max="100" required />
            </div>
            <div class="field">
              <label>Estado</label>
              <select v-model="form.estado" required>
                <option v-for="e in ESTADOS_ACCION" :key="e" :value="e">{{ e }}</option>
              </select>
            </div>
          </div>

          <div class="field">
            <label>Observaciones</label>
            <textarea v-model="form.observaciones" rows="2"></textarea>
          </div>

          <button type="submit" class="btn-primary" :disabled="guardando">
            {{ guardando ? 'Guardando...' : esEdicion ? 'Guardar cambios' : 'Crear acción' }}
          </button>
        </form>

        <template v-if="esEdicion">
          <div class="table-title">Seguimientos registrados</div>

          <p v-if="seguimientos.length === 0" class="empty-note">Aún no hay seguimientos para esta acción.</p>
          <ul v-else class="seguimiento-list">
            <li v-for="s in seguimientos" :key="s.id">
              <div class="seg-top">
                <span class="code">{{ s.fecha_seguimiento }}</span>
                <span class="seg-pct">{{ s.porcentaje_avance }}%</span>
                <span class="seg-estado">{{ s.estado }}</span>
              </div>
              <div class="seg-desc">{{ s.descripcion }}</div>
            </li>
          </ul>

          <form class="form-card seg-form" @submit.prevent="agregarSeguimiento">
            <div class="grid-2">
              <div class="field">
                <label>Fecha de seguimiento</label>
                <input v-model="nuevoSeguimiento.fecha_seguimiento" type="date" required />
              </div>
              <div class="field">
                <label>% de avance</label>
                <input v-model.number="nuevoSeguimiento.porcentaje_avance" type="number" min="0" max="100" required />
              </div>
            </div>
            <div class="field">
              <label>Descripción del avance</label>
              <textarea v-model="nuevoSeguimiento.descripcion" rows="2" required></textarea>
            </div>
            <div class="field">
              <label>Estado</label>
              <select v-model="nuevoSeguimiento.estado" required>
                <option v-for="e in ESTADOS_SEGUIMIENTO" :key="e" :value="e">{{ e }}</option>
              </select>
            </div>
            <div class="field">
              <label>Evidencias (nombre de archivo o referencia)</label>
              <input v-model="nuevoSeguimiento.evidencias" type="text" placeholder="checklist_v1.pdf" />
            </div>
            <button type="submit" class="btn-secondary" :disabled="guardandoSeguimiento">
              {{ guardandoSeguimiento ? 'Guardando...' : '+ Registrar seguimiento' }}
            </button>
          </form>
        </template>
      </template>
    </main>
  </div>
</template>

<style scoped>
.shell { display: flex; min-height: 100vh; }
.main { flex: 1; padding: 28px 36px; min-width: 0; max-width: 640px; }
.main h1 { font-size: 20px; font-weight: 600; margin: 4px 0 20px; }
.btn-back { background: none; border: none; color: var(--ink-soft); font-size: 12px; cursor: pointer; padding: 0; }
.form-card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px; margin-bottom: 24px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.field { margin-bottom: 16px; }
.field label { display: block; font-size: 13px; color: var(--ink-soft); margin-bottom: 6px; }
.field input, .field select, .field textarea { width: 100%; padding: 9px 11px; border: 1px solid var(--line); border-radius: var(--radius); font-size: 13px; font-family: inherit; background: var(--bg); color: var(--ink); }
.field textarea { resize: vertical; }
.field input:focus, .field select:focus, .field textarea:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
.error-msg { color: var(--warn); font-size: 13px; margin: 0 0 16px; }
.btn-primary { background: var(--ink); color: #F6F5F2; border: none; border-radius: var(--radius); padding: 10px 18px; font-size: 13px; font-weight: 500; cursor: pointer; }
.btn-primary:disabled { opacity: 0.6; cursor: default; }
.btn-secondary { background: var(--accent-soft); color: #6B4E1F; border: none; border-radius: var(--radius); padding: 9px 16px; font-size: 13px; font-weight: 500; cursor: pointer; }
.btn-secondary:disabled { opacity: 0.6; cursor: default; }
.table-title { font-size: 13px; font-weight: 600; margin: 0 0 10px; color: var(--ink-soft); }
.seguimiento-list { list-style: none; margin: 0 0 20px; padding: 0; display: flex; flex-direction: column; gap: 8px; }
.seguimiento-list li { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 10px 14px; }
.seg-top { display: flex; gap: 12px; align-items: center; margin-bottom: 4px; }
.seg-pct { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: var(--ok); font-weight: 500; }
.seg-estado { font-size: 11px; background: var(--accent-soft); color: #6B4E1F; padding: 2px 7px; border-radius: 2px; }
.seg-desc { font-size: 13px; }
.code { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: var(--ink-soft); }
.empty-note { font-size: 12px; color: var(--ink-soft); padding: 18px 14px; background: var(--surface); border: 1px dashed var(--line); border-radius: var(--radius); margin-bottom: 20px; }
</style>
