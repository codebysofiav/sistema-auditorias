<script setup>
import { useAuthStore } from '@/stores/auth'
import logoUis from '@/assets/logo-uis.png'

const auth = useAuthStore()
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
      <router-link to="/planeacion">Planeación</router-link>
      <router-link to="/informes">Informes</router-link>
      <router-link to="/hallazgos">Hallazgos</router-link>
      <router-link to="/plan-mejoramiento">Plan de mejoramiento</router-link>
      <router-link to="/documentos">Documentos</router-link>
    </nav>

    <div class="user-chip">
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