<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'
import AppSidebar from '@/components/AppSidebar.vue'

// Según la documentación del proyecto, solo existen estos dos tipos.
const TIPOS_INFORME = ['Preliminar', 'Definitivo']

const route = useRoute()
const router = useRouter()

const esEdicion = computed(() => !!route.params.id)

const auditorias = ref([])
const loading = ref(true)
const guardando = ref(false)
const errorMsg = ref('')

const form = ref({
  auditoria: '',
  tipo_informe: TIPOS_INFORME[0],
  fecha_informe: '',
  actividades_realizadas: '',
  conclusiones: '',
  observaciones: '',
  evidencias: '',
})

async function cargarAuditorias() {
  const { data } = await apiClient.get('/auditorias/')
  auditorias.value = data.results ?? data
}

async function cargarInforme() {
  const { data } = await apiClient.get(`/informes/${route.params.id}/`)
  form.value = {
    auditoria: data.auditoria,
    tipo_informe: data.tipo_informe,
    fecha_informe: data.fecha_informe,
    actividades_realizadas: data.actividades_realizadas,
    conclusiones: data.conclusiones,
    observaciones: data.observaciones,
    evidencias: data.evidencias,
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await cargarAuditorias()
    if (esEdicion.value) {
      await cargarInforme()
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
    if (esEdicion.value) {
      await apiClient.patch(`/informes/${route.params.id}/`, form.value)
    } else {
      await apiClient.post('/informes/', form.value)
    }
    router.push({ name: 'informes' })
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
      <button class="btn-back" @click="router.push({ name: 'informes' })">← Volver al listado</button>
      <h1>{{ esEdicion ? 'Editar informe' : 'Nuevo informe' }}</h1>

      <p v-if="loading" class="empty-note">Cargando...</p>

      <form v-else class="form-card" @submit.prevent="guardar">
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <div class="grid-2">
          <div class="field">
            <label>Auditoría</label>
            <select v-model="form.auditoria" required :disabled="esEdicion">
              <option value="" disabled>Seleccione una auditoría</option>
              <option v-for="a in auditorias" :key="a.id" :value="a.id">{{ a.codigo }}</option>
            </select>
          </div>
          <div class="field">
            <label>Tipo de informe</label>
            <select v-model="form.tipo_informe" required>
              <option v-for="t in TIPOS_INFORME" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
        </div>

        <div class="field">
          <label>Fecha del informe</label>
          <input v-model="form.fecha_informe" type="date" required />
        </div>

        <div class="field">
          <label>Actividades realizadas</label>
          <textarea v-model="form.actividades_realizadas" rows="3" required></textarea>
        </div>

        <div class="field">
          <label>Conclusiones</label>
          <textarea v-model="form.conclusiones" rows="3" required></textarea>
        </div>

        <div class="field">
          <label>Observaciones</label>
          <textarea v-model="form.observaciones" rows="2"></textarea>
        </div>

        <div class="field">
          <label>Evidencias (ubicación o referencia)</label>
          <input v-model="form.evidencias" type="text" placeholder="Carpeta compartida / enlace" />
        </div>

        <button type="submit" class="btn-primary" :disabled="guardando">
          {{ guardando ? 'Guardando...' : esEdicion ? 'Guardar cambios' : 'Crear informe' }}
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
.field input, .field select, .field textarea { width: 100%; padding: 9px 11px; border: 1px solid var(--line); border-radius: var(--radius); font-size: 13px; font-family: inherit; background: var(--bg); color: var(--ink); }
.field textarea { resize: vertical; }
.field input:focus, .field select:focus, .field textarea:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
.error-msg { color: var(--warn); font-size: 13px; margin: 0 0 16px; }
.btn-primary { background: var(--ink); color: #F6F5F2; border: none; border-radius: var(--radius); padding: 10px 18px; font-size: 13px; font-weight: 500; cursor: pointer; }
.btn-primary:disabled { opacity: 0.6; cursor: default; }
.empty-note { font-size: 12px; color: var(--ink-soft); padding: 18px 14px; background: var(--surface); border: 1px dashed var(--line); border-radius: var(--radius); }
</style>