<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'
import AppSidebar from '@/components/AppSidebar.vue'
import { useAuthStore } from '@/stores/auth'

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
const auth = useAuthStore()

const esEdicion = computed(() => !!route.params.id)
const puedeEditarAuditoria = computed(() => auth.isAdmin || auth.isAuditor)
const puedeDefinirEquipoAlCrear = computed(() => !esEdicion.value && puedeEditarAuditoria.value)
const puedeGestionarEquipo = computed(() => esEdicion.value && auth.isAdmin)

const unidades = ref([])
const loading = ref(true)
const guardando = ref(false)
const guardandoEquipo = ref(false)
const errorMsg = ref('')
const usuariosAuditores = ref([])
const auditoresSeleccionados = ref([])
const equipo = ref([])
const eliminacionesEquipo = ref([])
const auditorNuevo = ref('')
const busquedaAuditor = ref('')

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
  const { data } = await apiClient.get('/unidades/')
  unidades.value = data.results ?? data
}

async function cargarAuditores() {
  const { data } = await apiClient.get('/auth/usuarios/auditores/')
  usuariosAuditores.value = data.results ?? data
}

async function cargarEquipo() {
  const { data } = await apiClient.get('/auditoria-auditores/')
  const asignaciones = data.results ?? data
  equipo.value = asignaciones
    .filter((asignacion) => asignacion.auditoria === Number(route.params.id))
    .map((asignacion) => ({ ...asignacion, activoOriginal: asignacion.activo }))
  eliminacionesEquipo.value = []
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
    await Promise.all([cargarUnidades(), cargarAuditores()])
    if (esEdicion.value) {
      await Promise.all([cargarAuditoria(), cargarEquipo()])
    }
  } catch (err) {
    errorMsg.value = 'No se pudo cargar la información necesaria.'
  } finally {
    loading.value = false
  }
})

const auditoresFiltrados = computed(() => {
  const termino = busquedaAuditor.value.trim().toLocaleLowerCase()
  if (!termino) return usuariosAuditores.value
  return usuariosAuditores.value.filter((usuario) => nombreAuditor(usuario).toLocaleLowerCase().includes(termino))
})

const auditoresDisponibles = computed(() => {
  const asignados = new Set(equipo.value.map((asignacion) => asignacion.auditor))
  return usuariosAuditores.value.filter((usuario) => !asignados.has(usuario.id))
})

function nombreAuditor(usuario) {
  const nombre = `${usuario.first_name ?? ''} ${usuario.last_name ?? ''}`.trim()
  return nombre || usuario.email
}

function nombreAuditorPorId(id) {
  const usuario = usuariosAuditores.value.find((item) => item.id === id)
  return usuario ? nombreAuditor(usuario) : `Usuario #${id}`
}

function agregarAuditor() {
  const auditorId = Number(auditorNuevo.value)
  if (!auditorId || equipo.value.some((asignacion) => asignacion.auditor === auditorId)) return
  equipo.value.push({ id: null, auditor: auditorId, activo: true, activoOriginal: true })
  auditorNuevo.value = ''
}

function alternarActivo(asignacion) {
  asignacion.activo = !asignacion.activo
}

function eliminarAsignacion(asignacion) {
  if (asignacion.id) eliminacionesEquipo.value.push(asignacion.id)
  equipo.value = equipo.value.filter((item) => item !== asignacion)
}

async function guardarEquipo() {
  guardandoEquipo.value = true
  errorMsg.value = ''
  try {
    const nuevas = equipo.value.filter((asignacion) => !asignacion.id)
    const modificadas = equipo.value.filter(
      (asignacion) => asignacion.id && asignacion.activo !== asignacion.activoOriginal,
    )

    await Promise.all([
      ...nuevas.map((asignacion) => apiClient.post('/auditoria-auditores/', {
        auditoria: Number(route.params.id),
        auditor: asignacion.auditor,
        activo: asignacion.activo,
      })),
      ...modificadas.map((asignacion) => apiClient.patch(
        `/auditoria-auditores/${asignacion.id}/`,
        { activo: asignacion.activo },
      )),
      ...eliminacionesEquipo.value.map((id) => apiClient.delete(`/auditoria-auditores/${id}/`)),
    ])
    await cargarEquipo()
  } catch (err) {
    errorMsg.value = err.response?.status === 403
      ? 'No tiene permiso para administrar el equipo auditor.'
      : 'No se pudieron guardar los cambios del equipo auditor.'
  } finally {
    guardandoEquipo.value = false
  }
}

async function guardar() {
  guardando.value = true
  errorMsg.value = ''
  try {
    const payload = { ...form.value }
    if (esEdicion.value) {
      await apiClient.patch(`/auditorias/${route.params.id}/`, payload)
    } else {
      if (puedeDefinirEquipoAlCrear.value && auditoresSeleccionados.value.length === 0) {
        errorMsg.value = 'Seleccione al menos un auditor para conformar el equipo.'
        return
      }
      payload.equipo_auditor = auditoresSeleccionados.value
      await apiClient.post('/auditorias/', payload)
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
            <input v-model="form.codigo" type="text" required placeholder="AUD-2026-001" :disabled="esEdicion && !puedeEditarAuditoria" />
          </div>
          <div class="field">
            <label>Tipo de auditoría</label>
            <input v-model="form.tipo_auditoria" type="text" required placeholder="Interna" :disabled="esEdicion && !puedeEditarAuditoria" />
          </div>
        </div>

        <div class="field">
          <label>Unidad auditada</label>
          <select v-model="form.unidad_auditada" required :disabled="esEdicion && !puedeEditarAuditoria">
            <option value="" disabled>Seleccione una unidad</option>
            <option v-for="u in unidades" :key="u.id" :value="u.id">{{ u.nombre_unidad }}</option>
          </select>
        </div>

        <div class="field">
          <label>Responsable de la unidad</label>
          <input v-model="form.responsable_unidad" type="text" required :disabled="esEdicion && !puedeEditarAuditoria" />
        </div>

        <div class="grid-2">
          <div class="field">
            <label>Fecha de inicio</label>
            <input v-model="form.fecha_inicio" type="date" required :disabled="esEdicion && !puedeEditarAuditoria" />
          </div>
          <div class="field">
            <label>Fecha de fin</label>
            <input v-model="form.fecha_fin" type="date" required :disabled="esEdicion && !puedeEditarAuditoria" />
          </div>
        </div>

        <div class="field">
          <label>Objetivo</label>
          <textarea v-model="form.objetivo" rows="3" required :disabled="esEdicion && !puedeEditarAuditoria"></textarea>
        </div>

        <div class="field">
          <label>Alcance</label>
          <textarea v-model="form.alcance" rows="3" required :disabled="esEdicion && !puedeEditarAuditoria"></textarea>
        </div>

        <div class="field">
          <label>Estado</label>
          <select v-model="form.estado" required :disabled="esEdicion && !puedeEditarAuditoria">
            <option v-for="e in ESTADOS" :key="e" :value="e">{{ e }}</option>
          </select>
        </div>

        <section v-if="puedeDefinirEquipoAlCrear" class="team-section">
          <div class="section-heading"><div><h2>Equipo auditor</h2><p>Seleccione los usuarios con rol Auditor que participarán en esta auditoría.</p></div><span class="team-count">{{ auditoresSeleccionados.length }} seleccionados</span></div>
          <input v-model="busquedaAuditor" class="auditor-search" type="search" placeholder="Buscar por nombre o correo" />
          <p v-if="auditoresFiltrados.length === 0" class="empty-team">No se encontraron auditores disponibles.</p>
          <div v-else class="auditor-picker">
            <label v-for="usuario in auditoresFiltrados" :key="usuario.id" class="auditor-option">
              <input v-model="auditoresSeleccionados" type="checkbox" :value="usuario.id" />
              <span>{{ nombreAuditor(usuario) }}</span><small>{{ usuario.email }}</small>
            </label>
          </div>
        </section>

        <section v-if="esEdicion" class="team-section">
          <div class="section-heading"><div><h2>Equipo auditor</h2><p v-if="puedeGestionarEquipo">Administre las asignaciones activas e históricas de esta auditoría.</p><p v-else>Auditores asignados a esta auditoría.</p></div><span class="team-count">{{ equipo.length }} asignados</span></div>
          <p v-if="equipo.length === 0" class="empty-team">No hay auditores asignados.</p>
          <ul v-else class="team-list">
            <li v-for="asignacion in equipo" :key="asignacion.id ?? `nuevo-${asignacion.auditor}`">
              <div><strong>{{ nombreAuditorPorId(asignacion.auditor) }}</strong><small>{{ asignacion.activo ? 'Activo' : 'Inactivo' }}</small></div>
              <div v-if="puedeGestionarEquipo" class="team-actions"><button type="button" class="btn-link" @click="alternarActivo(asignacion)">{{ asignacion.activo ? 'Desactivar' : 'Reactivar' }}</button><button type="button" class="btn-danger-link" @click="eliminarAsignacion(asignacion)">Eliminar</button></div>
            </li>
          </ul>
          <template v-if="puedeGestionarEquipo">
            <div class="add-auditor"><select v-model="auditorNuevo"><option value="">Seleccione un auditor para agregar</option><option v-for="usuario in auditoresDisponibles" :key="usuario.id" :value="usuario.id">{{ nombreAuditor(usuario) }} · {{ usuario.email }}</option></select><button type="button" class="btn-link" :disabled="!auditorNuevo" @click="agregarAuditor">Agregar auditor</button></div>
            <button type="button" class="btn-secondary" :disabled="guardandoEquipo" @click="guardarEquipo">{{ guardandoEquipo ? 'Guardando equipo...' : 'Guardar equipo auditor' }}</button>
          </template>
        </section>

        <button v-if="puedeEditarAuditoria" type="submit" class="btn-primary" :disabled="guardando">
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
.team-section { border-top: 1px solid var(--line); margin: 24px 0; padding-top: 20px; }.section-heading { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 12px; }.section-heading h2 { font-size: 15px; margin: 0 0 3px; }.section-heading p { color: var(--ink-soft); font-size: 12px; margin: 0; }.team-count { background: var(--accent-soft); color: var(--ink); font-size: 11px; padding: 4px 7px; white-space: nowrap; }.auditor-search, .add-auditor select { width: 100%; box-sizing: border-box; padding: 9px 11px; border: 1px solid var(--line); border-radius: var(--radius); font: inherit; background: var(--bg); }.auditor-picker { border: 1px solid var(--line); max-height: 210px; margin-top: 8px; overflow-y: auto; }.auditor-option { align-items: center; border-bottom: 1px solid var(--line); cursor: pointer; display: grid; gap: 3px 9px; grid-template-columns: auto 1fr; padding: 9px 11px; }.auditor-option:last-child { border-bottom: 0; }.auditor-option small { color: var(--ink-soft); grid-column: 2; }.empty-team { color: var(--ink-soft); font-size: 12px; margin: 0; padding: 12px 0; }.team-list { border: 1px solid var(--line); list-style: none; margin: 0 0 12px; padding: 0; }.team-list li { align-items: center; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; gap: 12px; padding: 10px 11px; }.team-list li:last-child { border-bottom: 0; }.team-list strong, .team-list small { display: block; }.team-list strong { font-size: 13px; }.team-list small { color: var(--ink-soft); font-size: 11px; margin-top: 2px; }.team-actions, .add-auditor { display: flex; gap: 8px; align-items: center; }.add-auditor { margin-bottom: 12px; }.btn-link, .btn-danger-link, .btn-secondary { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); cursor: pointer; font-size: 12px; padding: 7px 10px; white-space: nowrap; }.btn-danger-link { color: var(--warn); }.btn-secondary { background: var(--accent-soft); border-color: var(--accent); color: var(--ink); }.btn-link:disabled, .btn-secondary:disabled { cursor: default; opacity: .6; }
</style>
