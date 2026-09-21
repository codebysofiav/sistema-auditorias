<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'
import AppSidebar from '@/components/AppSidebar.vue'

// AJUSTAR: como 'estado' es texto libre en el backend, esta lista es
// solo una convención del frontend para mantener los valores consistentes.
// Si luego se agregan choices reales en el modelo Django, reemplazar esto
// por los valores exactos que el backend espere.
const ESTADOS = [
  'En planeación',
  'En desarrollo',
  'En elaboración de informe',
  'En plan de mejoramiento',
  'Cerrada',
]

const route = useRoute()
const router = useRouter()

const esEdicion = computed(() => !!route.params.id)

const unidades = ref([])
const loading = ref(true)
const guardando = ref(false)
const errorMsg = ref('')

const form = ref({
  codigo: '',
  unidad_auditada: '',
  responsable_unidad: '',
  tipo_auditoria: '',
  fecha_inicio: '',
  fecha_fin: '',
  objetivo: '',
  alcance: '',
  estado: ESTADOS[0],
})

async function cargarUnidades() {
  const { data } = await apiClient.get('/unidades-auditadas/')
  unidades.value = data.results ?? data
}

async function cargarAuditoria() {
  const { data } = await apiClient.get(`/auditorias/${route.params.id}/`)
  form.value = {
    codigo: data.codigo,
    unidad_auditada: data.unidad_auditada,
    responsable_unidad: data.responsable_unidad,
    tipo_auditoria: data.tipo_auditoria,
    fecha_inicio: data.fecha_inicio,
    fecha_fin: data.fecha_fin,
    objetivo: data.objetivo,
    alcance: data.alcance,
    estado: data.estado,
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await cargarUnidades()
    if (esEdicion.value) {
      await cargarAuditoria()
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
      await apiClient.patch(`/auditorias/${route.params.id}/`, form.value)
    } else {
      await apiClient.post('/auditorias/', form.value)
    }
    router.push({ name: 'auditorias' })
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
      <button class="btn-back" @click="router.push({ name: 'auditorias' })">← Volver al listado</button>
      <h1>{{ esEdicion ? 'Editar auditoría' : 'Nueva auditoría' }}</h1>

      <p v-if="loading" class="empty-note">Cargando...</p>

      <form v-else class="form-card" @submit.prevent="guardar">
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <div class="grid-2">
          <div class="field">
            <label>Código</label>
            <input v-model="form.codigo" type="text" required placeholder="AUD-2026-001" />
          </div>
          <div class="field">
            <label>Tipo de auditoría</label>
            <input v-model="form.tipo_auditoria" type="text" required placeholder="Interna" />
          </div>
        </div>

        <div class="field">
          <label>Unidad auditada</label>
          <select v-model="form.unidad_auditada" required>
            <option value="" disabled>Seleccione una unidad</option>
            <option v-for="u in unidades" :key="u.id" :value="u.id">{{ u.nombre_unidad }}</option>
          </select>
        </div>

        <div class="field">
          <label>Responsable de la unidad</label>
          <input v-model="form.responsable_unidad" type="text" required />
        </div>

        <div class="grid-2">
          <div class="field">
            <label>Fecha de inicio</label>
            <input v-model="form.fecha_inicio" type="date" required />
          </div>
          <div class="field">
            <label>Fecha de fin</label>
            <input v-model="form.fecha_fin" type="date" required />
          </div>
        </div>

        <div class="field">
          <label>Objetivo</label>
          <textarea v-model="form.objetivo" rows="3" required></textarea>
        </div>

        <div class="field">
          <label>Alcance</label>
          <textarea v-model="form.alcance" rows="3" required></textarea>
        </div>

        <div class="field">
          <label>Estado</label>
          <select v-model="form.estado" required>
            <option v-for="e in ESTADOS" :key="e" :value="e">{{ e }}</option>
          </select>
        </div>

        <button type="submit" class="btn-primary" :disabled="guardando">
          {{ guardando ? 'Guardando...' : esEdicion ? 'Guardar cambios' : 'Crear auditoría' }}
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