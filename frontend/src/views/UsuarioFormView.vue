<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/api/client'
import AppSidebar from '@/components/AppSidebar.vue'

// Valores exactos que acepta el backend (UsuarioCreateSerializer.rol)
const ROLES = ['Administrador', 'Auditor', 'Usuario consulta']

const router = useRouter()
const route = useRoute()
const esEdicion = computed(() => Boolean(route.params.id))

const guardando = ref(false)
const loading = ref(false)
const errorMsg = ref('')

const form = ref({
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  rol: '',
})
const confirmarPassword = ref('')

const ETIQUETAS = {
  email: 'Correo',
  first_name: 'Nombre',
  last_name: 'Apellido',
  password: 'Contraseña',
  rol: 'Rol',
}

// Convierte el error 400 de DRF ({ campo: ["mensaje"] }) en texto legible
function formatearErrores(data) {
  if (!data || typeof data !== 'object') return ''
  return Object.entries(data)
    .map(([campo, msgs]) => {
      const texto = Array.isArray(msgs) ? msgs.join(' ') : String(msgs)
      return `${ETIQUETAS[campo] ?? campo}: ${texto}`
    })
    .join(' ')
}

async function guardar() {
  errorMsg.value = ''

  if (form.value.password && form.value.password.length < 8) {
    errorMsg.value = 'La contraseña debe tener al menos 8 caracteres.'
    return
  }
  if (form.value.password !== confirmarPassword.value) {
    errorMsg.value = 'Las contraseñas no coinciden.'
    return
  }

  guardando.value = true
  try {
    const payload = { ...form.value }
    if (!payload.password) delete payload.password

    if (esEdicion.value) {
      await apiClient.patch(`/auth/usuarios/${route.params.id}/`, payload)
    } else {
      await apiClient.post('/auth/usuarios/crear/', payload)
    }
    router.push({ name: 'usuarios' })
  } catch (err) {
    if (err.response?.status === 403) {
      errorMsg.value = 'No tiene permiso para realizar esta acción.'
    } else if (err.response?.status === 400) {
      errorMsg.value =
        formatearErrores(err.response.data) || 'Revise los datos e intente de nuevo.'
    } else {
      errorMsg.value = 'Ocurrió un error al guardar. Revise los datos e intente de nuevo.'
    }
  } finally {
    guardando.value = false
  }
}

async function cargarUsuario() {
  if (!esEdicion.value) return

  loading.value = true
  try {
    const { data } = await apiClient.get(`/auth/usuarios/${route.params.id}/`)
    form.value = {
      email: data.email,
      first_name: data.first_name,
      last_name: data.last_name,
      password: '',
      rol: data.roles?.[0] ?? '',
    }
  } catch (err) {
    errorMsg.value =
      err.response?.status === 403
        ? 'No tiene permiso para ver este usuario.'
        : 'No se pudo cargar la información del usuario.'
  } finally {
    loading.value = false
  }
}

onMounted(cargarUsuario)
</script>

<template>
  <div class="shell">
    <AppSidebar />

    <main class="main">
      <button class="btn-back" @click="router.push({ name: 'usuarios' })">← Volver al listado</button>
      <h1>{{ esEdicion ? 'Editar usuario' : 'Nuevo usuario' }}</h1>

      <p v-if="loading" class="hint">Cargando...</p>

      <form v-else class="form-card" @submit.prevent="guardar">
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <div class="grid-2">
          <div class="field">
            <label>Nombre</label>
            <input v-model="form.first_name" type="text" required />
          </div>
          <div class="field">
            <label>Apellido</label>
            <input v-model="form.last_name" type="text" required />
          </div>
        </div>

        <div class="field">
          <label>Correo</label>
          <input v-model="form.email" type="email" required placeholder="usuario@uis.edu.co" />
        </div>

        <div class="field">
          <label>Rol</label>
          <select v-model="form.rol" required>
            <option value="" disabled>Seleccione un rol</option>
            <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>

        <div class="grid-2">
          <div class="field">
            <label>Contraseña</label>
            <input v-model="form.password" type="password" :required="!esEdicion" minlength="8" autocomplete="new-password" />
          </div>
          <div class="field">
            <label>Confirmar contraseña</label>
            <input v-model="confirmarPassword" type="password" :required="!esEdicion" minlength="8" autocomplete="new-password" />
          </div>
        </div>
        <p class="hint">{{ esEdicion ? 'Deje la contraseña vacía para conservarla. Mínimo 8 caracteres si la cambia.' : 'Mínimo 8 caracteres.' }}</p>

        <button type="submit" class="btn-primary" :disabled="guardando">
          {{ guardando ? 'Guardando...' : esEdicion ? 'Guardar cambios' : 'Crear usuario' }}
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
.field input, .field select {
  width: 100%;
  padding: 9px 11px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  font-size: 13px;
  font-family: inherit;
  background: var(--bg);
  color: var(--ink);
}
.field input:focus, .field select:focus { outline: 2px solid var(--accent); outline-offset: 1px; }

.hint { font-size: 12px; color: var(--ink-soft); margin: -6px 0 16px; }
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
</style>
