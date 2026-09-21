<script setup>
// El layout (sidebar, etc.) vive dentro de cada vista protegida
// (ej. DashboardView), no aquí, porque LoginView no debe mostrar sidebar.
</script>

<template>
  <router-view />
</template>