<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/client'
import AppSidebar from '@/components/AppSidebar.vue'

// AJUSTAR según las plantillas .docx reales que entregue la universidad.
const TIPOS_DOCUMENTO = [
  'Informe preliminar',
  'Informe definitivo',
  'Plan de mejoramiento',
  'Acta de cierre',
]
const FORMATOS = ['Word (.docx)', 'PDF']

const router = useRouter()

const auditorias = ref([])
const loading = ref(true)
const generando = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const form = ref({
  auditoria: '',
  tipo_documento: TIPOS_DOCUMENTO[0],
  formato: FORMATOS[0],
})

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await apiClient.get('/auditorias/')
    auditorias.value = data.results ?? data
  } catch (err) {
    errorMsg.value = 'No se pudo cargar el listado de auditorías.'
  } finally {
    loading.value = false
  }
})

// --- CONTRATO CON EL BACKEND (pendiente de construir) ---
// Endpoint esperado:  POST /api/auditorias/{id}/generar-documento/
// Body:               { tipo_documento, formato }
// Respuesta esperada: el archivo binario (.docx o .pdf) como descarga,
//                      y el backend debe registrar automáticamente una
//                      fila en DocumentoGenerado (tipo, formato, fecha,
//                      generado_por = usuario autenticado).
// Mientras el backend no exista, este botón mostrará un aviso claro
// en vez de fallar en silencio.
async function generar() {
  generando.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const response = await apiClient.post(
      `/auditorias/${form.value.auditoria}/generar-documento/`,
      { tipo_documento: form.value.tipo_documento, formato: form.value.formato },
      { responseType: 'blob' }
    )

    const extension = form.value.formato.includes('PDF') ? 'pdf' : 'docx'
    const nombreArchivo = `${form.value.tipo_documento.replace(/\s+/g, '_')}.${extension}`

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', nombreArchivo)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    successMsg.value = 'Documento generado y descargado correctamente.'
  } catch (err) {
    if (err.response?.status === 404) {
      errorMsg.value =
        'La generación automática de documentos todavía no está implementada en el backend. Este flujo del frontend ya está listo — falta construir el endpoint correspondiente.'
    } else if (err.response?.status === 403) {
      errorMsg.value = 'No tiene permiso para generar documentos de esta auditoría.'
    } else {
      errorMsg.value = 'Ocurrió un error al generar el documento.'
    }
  } finally {
    generando.value = false
  }
}
</script>

<template>
  <div class="shell">
    <AppSidebar />

    <main class="main">
      <button class="btn-back" @click="router.push({ name: 'documentos' })">← Volver al listado</button>
      <h1>Generar documento</h1>
      <p class="sub">Selecciona la auditoría y la plantilla oficial de la universidad que quieres generar con los datos ya registrados.</p>

      <p v-if="loading" class="empty-note">Cargando...</p>

      <form v-else class="form-card" @submit.prevent="generar">
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
        <p v-if="successMsg" class="success-msg">{{ successMsg }}</p>

        <div class="field">
          <label>Auditoría</label>
          <select v-model="form.auditoria" required>
            <option value="" disabled>Seleccione una auditoría</option>
            <option v-for="a in auditorias" :key="a.id" :value="a.id">{{ a.codigo }}</option>
          </select>
        </div>

        <div class="field">
          <label>Tipo de documento</label>
          <select v-model="form.tipo_documento" required>
            <option v-for="t in TIPOS_DOCUMENTO" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>

        <div class="field">
          <label>Formato</label>
          <select v-model="form.formato" required>
            <option v-for="f in FORMATOS" :key="f" :value="f">{{ f }}</option>
          </select>
        </div>

        <button type="submit" class="btn-primary" :disabled="generando || !form.auditoria">
          {{ generando ? 'Generando...' : 'Generar y descargar' }}
        </button>
      </form>
    </main>
  </div>
</template>

<style scoped>
.shell { display: flex; min-height: 100vh; }
.main { flex: 1; padding: 28px 36px; min-width: 0; max-width: 560px; }
.main h1 { font-size: 20px; font-weight: 600; margin: 4px 0 4px; }
.sub { font-size: 13px; color: var(--ink-soft); margin: 0 0 20px; }
.btn-back { background: none; border: none; color: var(--ink-soft); font-size: 12px; cursor: pointer; padding: 0; }
.form-card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px; }
.field { margin-bottom: 16px; }
.field label { display: block; font-size: 13px; color: var(--ink-soft); margin-bottom: 6px; }
.field select { width: 100%; padding: 9px 11px; border: 1px solid var(--line); border-radius: var(--radius); font-size: 13px; font-family: inherit; background: var(--bg); color: var(--ink); }
.field select:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
.error-msg { color: var(--warn); font-size: 13px; margin: 0 0 16px; background: var(--warn-soft); padding: 10px 12px; border-radius: var(--radius); }
.success-msg { color: var(--ok); font-size: 13px; margin: 0 0 16px; background: var(--ok-soft); padding: 10px 12px; border-radius: var(--radius); }
.btn-primary { background: var(--ink); color: #F6F5F2; border: none; border-radius: var(--radius); padding: 10px 18px; font-size: 13px; font-weight: 500; cursor: pointer; }
.btn-primary:disabled { opacity: 0.6; cursor: default; }
.empty-note { font-size: 12px; color: var(--ink-soft); padding: 18px 14px; background: var(--surface); border: 1px dashed var(--line); border-radius: var(--radius); }
</style>