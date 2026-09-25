<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/client'
import AppSidebar from '@/components/AppSidebar.vue'

const router = useRouter()

const usuarios = ref([])
const loading = ref(true)
const errorMsg = ref('')
const eliminandoId = ref(null)

async function cargarUsuarios() {
  loading.value = true
  errorMsg.value = ''
  try {
    const { data } = await apiClient.get('/auth/usuarios/')
    usuarios.value = data.results ?? data
  } catch (err) {
    errorMsg.value =
      err.response?.status === 403
        ? 'No tiene permiso para ver los usuarios.'
        : 'No se pudo cargar el listado de usuarios.'
  } finally {
    loading.value = false
  }
}

function nombreCompleto(u) {
  return `${u.first_name} ${u.last_name}`.trim() || '—'
}

onMounted(cargarUsuarios)

async function eliminarUsuario(usuario) {
  const confirmado = window.confirm(
    `¿Eliminar el usuario ${usuario.email}? Esta acción no se puede deshacer.`
  )

  if (!confirmado) return

  eliminandoId.value = usuario.id
  errorMsg.value = ''
  try {
    await apiClient.delete(`/auth/usuarios/${usuario.id}/`)
    usuarios.value = usuarios.value.filter((item) => item.id !== usuario.id)
  } catch (err) {
    errorMsg.value =
      err.response?.status === 403
        ? 'No tiene permiso para eliminar usuarios.'
        : 'No se pudo eliminar el usuario. Intente nuevamente.'
  } finally {
    eliminandoId.value = null
  }
}
</script>

<template>
  <div class="shell">
    <AppSidebar />

    <main class="main">
      <div class="head">
        <h1>Usuarios</h1>
        <button class="btn-primary" @click="router.push({ name: 'usuario-nuevo' })">
          + Nuevo usuario
        </button>
      </div>

      <p v-if="loading" class="empty-note">Cargando...</p>
      <p v-else-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
      <p v-else-if="usuarios.length === 0" class="empty-note">
        Aún no hay usuarios registrados. Cree el primero con “Nuevo usuario”.
      </p>

      <div v-else class="table-card">
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Rol</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in usuarios" :key="u.id">
              <td>{{ nombreCompleto(u) }}</td>
              <td>{{ u.email }}</td>
              <td>
                <span v-for="r in u.roles" :key="r" class="role-tag">{{ r }}</span>
                <span v-if="!u.roles.length" class="sin-rol">Sin rol</span>
              </td>
              <td class="actions-cell">
                <button class="btn-link" @click="router.push({ name: 'usuario-editar', params: { id: u.id } })">
                  Editar
                </button>
                <button
                  class="btn-danger"
                  :disabled="eliminandoId === u.id"
                  @click="eliminarUsuario(u)"
                >
                  {{ eliminandoId === u.id ? 'Eliminando...' : 'Eliminar' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<style scoped>
.shell { display: flex; min-height: 100vh; }
.main { flex: 1; padding: 28px 36px; min-width: 0; }
.head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.head h1 { font-size: 20px; font-weight: 600; margin: 0; }

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

.table-card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { text-align: left; font-weight: 500; color: var(--ink-soft); padding: 12px 16px; border-bottom: 1px solid var(--line); }
td { padding: 12px 16px; border-bottom: 1px solid var(--line); color: var(--ink); }
tbody tr:last-child td { border-bottom: none; }

.role-tag {
  display: inline-block;
  margin-right: 6px;
  font-size: 12px;
  background: var(--accent-soft);
  color: #6B4E1F;
  padding: 2px 8px;
  border-radius: 2px;
}
.sin-rol { color: var(--ink-soft); font-size: 12px; }
.actions-cell { display: flex; justify-content: flex-end; gap: 8px; white-space: nowrap; }
.btn-link, .btn-danger { border: 1px solid var(--line); border-radius: var(--radius); padding: 5px 10px; font-size: 12px; cursor: pointer; background: var(--surface); }
.btn-link { color: var(--ink); }
.btn-danger { color: var(--warn); }
.btn-danger:disabled { opacity: 0.6; cursor: default; }

.error-msg { color: var(--warn); font-size: 13px; margin: 0; }
.empty-note { font-size: 12px; color: var(--ink-soft); padding: 18px 14px; background: var(--surface); border: 1px dashed var(--line); border-radius: var(--radius); }
</style>
