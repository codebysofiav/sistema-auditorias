<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/api/client'
import logoUis from '@/assets/logo-uis.png'

const auth = useAuthStore()
const alertas = ref([])
const mostrarAlertas = ref(false)

async function cargarAlertas() {
  if (!auth.isAuthenticated) return
  try {
    const { data } = await apiClient.get('/notificaciones/no-leidas/')
    alertas.value = data.results ?? data
  } catch {
    alertas.value = []
  }
}

async function marcarLeida(alerta) {
  try {
    await apiClient.post(`/notificaciones/${alerta.id}/marcar-leida/`)
    alertas.value = alertas.value.filter((item) => item.id !== alerta.id)
  } catch {
    // Mantiene la alerta visible para que el usuario pueda intentarlo de nuevo.
  }
}

onMounted(cargarAlertas)
</script>

<template>
  <aside class="sidebar">
    <div class="brand">
      <img :src="logoUis" alt="UIS" />
      <div class="txt">
        <strong>UIS Auditorías</strong>
        Univ. Industrial de Santander
      </div>
    </div>

    <nav>
      <router-link to="/dashboard">Dashboard</router-link>
      <router-link v-if="auth.isAdmin" to="/usuarios">Usuarios</router-link>
      <router-link to="/auditorias">Auditorías</router-link>
      <router-link to="/unidades">Unidades auditadas</router-link>
      <router-link to="/planeacion">Planeación</router-link>
      <router-link to="/informes">Informes</router-link>
      <router-link to="/hallazgos">Hallazgos</router-link>
      <router-link to="/plan-mejoramiento">Plan de mejoramiento</router-link>
      <router-link to="/documentos">Documentos</router-link>
    </nav>

    <div class="user-chip">
      <div class="alertas">
        <button class="alerts-button" type="button" @click="mostrarAlertas = !mostrarAlertas">
          Alertas <span v-if="alertas.length" class="alerts-count">{{ alertas.length }}</span>
        </button>
        <div v-if="mostrarAlertas" class="alerts-panel">
          <p v-if="alertas.length === 0" class="alerts-empty">No hay alertas pendientes.</p>
          <article v-for="alerta in alertas" :key="alerta.id" class="alert-item">
            <strong>{{ alerta.tipo_alerta }}</strong>
            <span>{{ alerta.mensaje }}</span>
            <button type="button" @click="marcarLeida(alerta)">Marcar leída</button>
          </article>
        </div>
      </div>
      <div>{{ auth.user?.first_name }} {{ auth.user?.last_name }}</div>
      <span class="role-tag">{{ auth.rol?.toUpperCase() }}</span>
      <button class="logout-link" @click="auth.logout()">Cerrar sesión</button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 210px;
  flex-shrink: 0;
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
  padding: 24px 16px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-bottom: 24px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--sidebar-line);
}
.brand img { height: 26px; width: auto; flex-shrink: 0; }
.brand .txt { font-family: 'IBM Plex Mono', monospace; font-size: 10.5px; line-height: 1.35; color: #8494A5; }
.brand .txt strong { display: block; color: #DCE3EA; font-family: 'IBM Plex Sans', sans-serif; font-size: 12px; font-weight: 600; }

nav { display: flex; flex-direction: column; }
nav a {
  display: block;
  padding: 9px 10px;
  font-size: 13px;
  color: var(--sidebar-text);
  text-decoration: none;
  border-radius: var(--radius);
  margin-bottom: 2px;
}
nav a.router-link-active { background: var(--sidebar-hover); color: #fff; font-weight: 500; }

.user-chip {
  margin-top: 28px;
  padding-top: 16px;
  border-top: 1px solid var(--sidebar-line);
  font-size: 12px;
}
.alertas { position: relative; margin-bottom: 16px; }
.alerts-button { width: 100%; display: flex; justify-content: space-between; align-items: center; border: 1px solid var(--sidebar-line); background: transparent; color: var(--sidebar-text); cursor: pointer; font-size: 12px; padding: 7px 8px; }
.alerts-count { min-width: 18px; border-radius: 9px; background: var(--warn); color: #fff; font-size: 11px; line-height: 18px; text-align: center; }
.alerts-panel { position: absolute; z-index: 2; bottom: calc(100% + 6px); left: 0; width: 260px; max-height: 280px; overflow-y: auto; border: 1px solid var(--sidebar-line); background: var(--sidebar-bg); padding: 8px; }
.alerts-empty { margin: 6px; color: #8494A5; font-size: 12px; }.alert-item { display: flex; flex-direction: column; gap: 5px; border-bottom: 1px solid var(--sidebar-line); padding: 9px 4px; font-size: 12px; }.alert-item:last-child { border-bottom: 0; }.alert-item strong { color: #F1E4CC; }.alert-item span { color: var(--sidebar-text); line-height: 1.35; }.alert-item button { align-self: flex-start; border: 0; background: none; color: #9FC6AE; cursor: pointer; font-size: 11px; padding: 0; }
.role-tag {
  display: inline-block;
  margin-top: 6px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  background: var(--accent-soft);
  color: #6B4E1F;
  padding: 2px 7px;
  border-radius: 2px;
}
.logout-link {
  display: block;
  margin-top: 12px;
  background: none;
  border: none;
  color: #8494A5;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
}
</style>
