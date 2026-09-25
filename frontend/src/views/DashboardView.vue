<script setup>
import { computed, onMounted, ref } from 'vue'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import AppSidebar from '@/components/AppSidebar.vue'

const auth = useAuthStore()

const resumen = ref(null)
const loading = ref(true)
const errorMsg = ref('')

const titulo = computed(() => {
  if (auth.isAdmin) return 'Panel general'
  if (auth.isAuditor) return 'Mis auditorías asignadas'
  return 'Auditorías'
})

const subtitulo = computed(() => {
  if (auth.isAdmin) {
    return 'Vista consolidada del estado de las auditorías.'
  }

  if (auth.isAuditor) {
    return 'Resumen de las auditorías donde usted está asignado como auditor activo.'
  }

  return 'Puede consultar el estado global de las auditorías.'
})

const misAuditorias = computed(() => {
  return resumen.value?.mis_auditorias ?? []
})

const estadosAuditoria = computed(() => {
  return Object.entries(resumen.value?.auditorias_por_estado ?? {})
})

const totalEstados = computed(() => {
  return estadosAuditoria.value.reduce((total, [, cantidad]) => {
    return total + cantidad
  }, 0)
})

function porcentajeEstado(cantidad) {
  if (!totalEstados.value) return 0

  return Math.round((cantidad / totalEstados.value) * 100)
}

onMounted(async () => {
  try {
    const { data } = await apiClient.get('/dashboard/resumen/')
    resumen.value = data
  } catch (error) {
    console.error(error)
    errorMsg.value = 'No se pudo cargar el resumen del dashboard.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="shell">
    <AppSidebar />

    <main class="main dashboard-main">
      <!-- Encabezado -->
      <header class="page-header">
        <div>
          <span class="eyebrow">Sistema de Gestión de Auditorías</span>
          <h1>{{ titulo }}</h1>
          <p class="sub">{{ subtitulo }}</p>
        </div>

        <div v-if="resumen && !loading" class="header-date">
          <span>Estado del sistema</span>
          <strong>Actualizado</strong>
        </div>
      </header>

      <!-- Carga / error -->
      <div v-if="loading" class="status-card">
        <div class="loading-dot"></div>
        <span>Cargando información del dashboard...</span>
      </div>

      <div v-else-if="errorMsg" class="status-card error-card">
        <strong>No fue posible cargar el dashboard</strong>
        <span>{{ errorMsg }}</span>
      </div>

      <template v-else>
        <!-- ========================================= -->
        <!-- FILA 1 - AUDITORÍAS -->
        <!-- ========================================= -->
        <section class="dashboard-section">
          <div class="section-heading">
            <div>
              <span class="section-number">01</span>
              <h2>Auditorías</h2>
            </div>

            <span class="section-description">
              Estado general del proceso
            </span>
          </div>

          <div class="kpi-grid four-columns">
            <article class="kpi-card">
              <div class="kpi-icon">A</div>

              <div class="kpi-content">
                <span class="kpi-label">Auditorías activas</span>
                <strong class="kpi-value">
                  {{ resumen.total_auditorias_activas }}
                </strong>
              </div>
            </article>

            <article class="kpi-card">
              <div class="kpi-icon">E</div>

              <div class="kpi-content">
                <span class="kpi-label">Estados registrados</span>
                <strong class="kpi-value">
                  {{ estadosAuditoria.length }}
                </strong>
              </div>
            </article>

            <article class="kpi-card">
              <div class="kpi-icon accent">P</div>

              <div class="kpi-content">
                <span class="kpi-label">Preliminares sin definitivo</span>
                <strong class="kpi-value">
                  {{ resumen.auditorias_preliminar_sin_definitivo }}
                </strong>
              </div>
            </article>

            <article class="kpi-card">
              <div class="kpi-icon">
                U
              </div>

              <div class="kpi-content">
                <span class="kpi-label">Unidades activas</span>
                <strong class="kpi-value">
                  {{ resumen.unidades_activas }}
                </strong>
              </div>
            </article>
          </div>
        </section>

        <!-- ========================================= -->
        <!-- FILA 2 - ACCIONES -->
        <!-- ========================================= -->
        <section class="dashboard-section">
          <div class="section-heading">
            <div>
              <span class="section-number">02</span>
              <h2>Acciones de mejoramiento</h2>
            </div>

            <span class="section-description">
              Seguimiento y cumplimiento
            </span>
          </div>

          <div class="kpi-grid three-columns">
            <article
              class="kpi-card large-number"
              :class="{ danger: resumen.acciones_vencidas > 0 }"
            >
              <div class="kpi-icon danger-icon">!</div>

              <div class="kpi-content">
                <span class="kpi-label">Acciones vencidas</span>
                <strong class="kpi-value">
                  {{ resumen.acciones_vencidas }}
                </strong>
                <small v-if="resumen.acciones_vencidas > 0">
                  Requieren atención
                </small>
                <small v-else>
                  Sin acciones vencidas
                </small>
              </div>
            </article>

            <article class="kpi-card large-number">
              <div class="kpi-icon accent">→</div>

              <div class="kpi-content">
                <span class="kpi-label">Próximas a vencer</span>
                <strong class="kpi-value">
                  {{ resumen.acciones_proximas_vencer }}
                </strong>
                <small>Revisar fechas límite</small>
              </div>
            </article>

            <article class="kpi-card large-number">
              <div class="kpi-icon">—</div>

              <div class="kpi-content">
                <span class="kpi-label">Sin seguimiento</span>
                <strong class="kpi-value">
                  {{ resumen.acciones_sin_seguimiento }}
                </strong>
                <small>Acciones pendientes de seguimiento</small>
              </div>
            </article>
          </div>
        </section>

        <!-- ========================================= -->
        <!-- FILA 3 - HALLAZGOS -->
        <!-- ========================================= -->
        <section class="dashboard-section">
          <div class="section-heading">
            <div>
              <span class="section-number">03</span>
              <h2>Hallazgos</h2>
            </div>

            <span class="section-description">
              Resultados de las auditorías
            </span>
          </div>

          <div class="kpi-grid two-columns">
            <article
              class="kpi-card large-number"
              :class="{ danger: resumen.hallazgos_abiertos > 0 }"
            >
              <div class="kpi-icon danger-icon">H</div>

              <div class="kpi-content">
                <span class="kpi-label">Hallazgos abiertos</span>
                <strong class="kpi-value">
                  {{ resumen.hallazgos_abiertos }}
                </strong>
                <small>Hallazgos que requieren gestión</small>
              </div>
            </article>

            <article class="kpi-card large-number">
              <div class="kpi-icon accent">A</div>

              <div class="kpi-content">
                <span class="kpi-label">Hallazgos sin acción</span>
                <strong class="kpi-value">
                  {{ resumen.hallazgos_sin_accion }}
                </strong>
                <small>Sin acción de mejoramiento asociada</small>
              </div>
            </article>
          </div>
        </section>

        <!-- ========================================= -->
        <!-- FILA 4 - ALERTAS -->
        <!-- ========================================= -->
        <section class="dashboard-section">
          <div class="section-heading">
            <div>
              <span class="section-number">04</span>
              <h2>Alertas</h2>
            </div>

            <span class="section-description">
              Situaciones pendientes
            </span>
          </div>

          <div class="alert-summary">
            <div class="alert-main">
              <div
                class="alert-circle"
                :class="{ 'has-alerts': resumen.alertas_pendientes > 0 }"
              >
                {{ resumen.alertas_pendientes }}
              </div>

              <div>
                <strong>Alertas pendientes</strong>

                <p v-if="resumen.alertas_pendientes > 0">
                  Existen situaciones que requieren revisión.
                </p>

                <p v-else>
                  No hay alertas pendientes en este momento.
                </p>
              </div>
            </div>

            <div class="alert-status">
              <span
                class="status-dot"
                :class="{ active: resumen.alertas_pendientes > 0 }"
              ></span>

              {{
                resumen.alertas_pendientes > 0
                  ? 'Requiere atención'
                  : 'Sin novedades'
              }}
            </div>
          </div>
        </section>

        <!-- ========================================= -->
        <!-- ESTADOS DE AUDITORÍA -->
        <!-- ========================================= -->
        <section class="bottom-grid">
          <div class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">DISTRIBUCIÓN</span>
                <h2>Auditorías por estado</h2>
              </div>
            </div>

            <div
              v-if="estadosAuditoria.length"
              class="state-chart"
            >
              <div
                v-for="([estado, total]) in estadosAuditoria"
                :key="estado"
                class="state-row"
              >
                <div class="state-info">
                  <span>{{ estado }}</span>
                  <strong>{{ total }}</strong>
                </div>

                <div class="state-bar">
                  <div
                    class="state-progress"
                    :style="{ width: `${porcentajeEstado(total)}%` }"
                  ></div>
                </div>

                <span class="state-percent">
                  {{ porcentajeEstado(total) }}%
                </span>
              </div>
            </div>

            <div v-else class="empty-note">
              No hay auditorías registradas.
            </div>
          </div>

          <!-- ADMINISTRACIÓN -->
          <div v-if="auth.isAdmin" class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">ADMINISTRACIÓN</span>
                <h2>Resumen institucional</h2>
              </div>
            </div>

            <div class="admin-stats">
              <div
                v-for="(total, rol) in resumen.usuarios_por_rol"
                :key="rol"
                class="admin-stat"
              >
                <span>{{ rol }}</span>
                <strong>{{ total }}</strong>
              </div>

              <div class="admin-stat">
                <span>Unidades activas</span>
                <strong>{{ resumen.unidades_activas }}</strong>
              </div>

              <div class="admin-stat">
                <span>Unidades inactivas</span>
                <strong>{{ resumen.unidades_inactivas }}</strong>
              </div>
            </div>
          </div>
        </section>

        <!-- ========================================= -->
        <!-- MIS AUDITORÍAS -->
        <!-- ========================================= -->
        <section
          v-if="auth.isAuditor && !auth.isAdmin"
          class="panel my-audits"
        >
          <div class="panel-header">
            <div>
              <span class="eyebrow">SEGUIMIENTO</span>
              <h2>Mis auditorías</h2>
            </div>
          </div>

          <p
            v-if="misAuditorias.length === 0"
            class="empty-note"
          >
            No tiene auditorías asignadas activas.
          </p>

          <div v-else class="audit-list">
            <div
              v-for="auditoria in misAuditorias"
              :key="auditoria.id"
              class="audit-item"
            >
              <span class="audit-code">
                {{ auditoria.codigo }}
              </span>

              <span class="audit-status">
                {{ auditoria.estado }}
              </span>
            </div>
          </div>
        </section>
      </template>
    </main>
  </div>
</template>

<style scoped>
.shell {
  display: flex;
  min-height: 100vh;
  background: var(--bg);
}

.main {
  flex: 1;
  min-width: 0;
  padding: 34px 42px 50px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 34px;
}

.eyebrow {
  display: block;
  color: var(--accent);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.08em;
  margin-bottom: 7px;
}

.page-header h1 {
  margin: 0;
  color: var(--ink);
  font-size: 28px;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.sub {
  margin: 7px 0 0;
  color: var(--ink-soft);
  font-size: 13px;
}

.header-date {
  min-width: 130px;
  padding: 10px 14px;
  border-left: 2px solid var(--accent);
  background: var(--surface);
}

.header-date span,
.header-date strong {
  display: block;
}

.header-date span {
  color: var(--ink-soft);
  font-size: 10px;
  margin-bottom: 3px;
}

.header-date strong {
  font-size: 12px;
}

.dashboard-section {
  margin-bottom: 32px;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 12px;
}

.section-heading > div {
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-number {
  color: var(--accent);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
}

.section-heading h2 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}

.section-description {
  color: var(--ink-soft);
  font-size: 11px;
}

.kpi-grid {
  display: grid;
  gap: 12px;
}

.four-columns {
  grid-template-columns: repeat(4, 1fr);
}

.three-columns {
  grid-template-columns: repeat(3, 1fr);
}

.two-columns {
  grid-template-columns: repeat(2, 1fr);
}

.kpi-card {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 13px;
  min-height: 110px;
  padding: 17px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(29, 43, 58, 0.06);
}

.kpi-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 31px;
  height: 31px;
  flex-shrink: 0;
  border: 1px solid var(--line);
  color: var(--ink-soft);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  align-self: center;
}

.kpi-icon.accent {
  border-color: var(--accent-soft);
  background: var(--accent-soft);
  color: #6B4E1F;
}

.kpi-icon.danger-icon {
  border-color: var(--warn-soft);
  background: var(--warn-soft);
  color: var(--warn);
}

.kpi-content {
  min-width: 0;
}

.kpi-label {
  display: block;
  color: var(--ink-soft);
  font-size: 11px;
  line-height: 1.35;
}

.kpi-value {
  display: block;
  margin-top: 5px;
  color: var(--ink);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 27px;
  font-weight: 500;
}

.kpi-content small {
  display: block;
  margin-top: 4px;
  color: var(--ink-soft);
  font-size: 10px;
}

.kpi-card.danger {
  border-color: var(--warn-soft);
  background: #FCF8F8;
}

.kpi-card.danger .kpi-value {
  color: var(--warn);
}

.alert-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 19px 20px;
  border: 1px solid var(--line);
  background: var(--surface);
}

.alert-main {
  display: flex;
  align-items: center;
  gap: 14px;
}

.alert-circle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--ok-soft);
  color: var(--ok);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 17px;
}

.alert-circle.has-alerts {
  background: var(--warn-soft);
  color: var(--warn);
}

.alert-main strong {
  font-size: 13px;
}

.alert-main p {
  margin: 4px 0 0;
  color: var(--ink-soft);
  font-size: 11px;
}

.alert-status {
  display: flex;
  align-items: center;
  gap: 7px;
  color: var(--ink-soft);
  font-size: 11px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--ok);
}

.status-dot.active {
  background: var(--warn);
}

.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.panel {
  border: 1px solid var(--line);
  background: var(--surface);
  padding: 19px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.panel-header h2 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}

.state-chart {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.state-row {
  display: grid;
  grid-template-columns: 135px 1fr 40px;
  align-items: center;
  gap: 10px;
}

.state-info {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 11px;
}

.state-info strong {
  font-family: 'IBM Plex Mono', monospace;
}

.state-bar {
  height: 7px;
  overflow: hidden;
  background: var(--bg);
}

.state-progress {
  height: 100%;
  min-width: 3px;
  background: var(--accent);
}

.state-percent {
  color: var(--ink-soft);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  text-align: right;
}

.admin-stats {
  display: flex;
  flex-direction: column;
}

.admin-stat {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 11px 0;
  border-bottom: 1px solid var(--line);
}

.admin-stat:last-child {
  border-bottom: 0;
}

.admin-stat span {
  color: var(--ink-soft);
  font-size: 11px;
}

.admin-stat strong {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 16px;
}

.my-audits {
  margin-top: 24px;
}

.audit-list {
  display: flex;
  flex-direction: column;
}

.audit-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
}

.audit-item:last-child {
  border-bottom: 0;
}

.audit-code {
  color: var(--ink);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
}

.audit-status {
  padding: 4px 8px;
  background: var(--accent-soft);
  color: #6B4E1F;
  font-size: 10px;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px;
  border: 1px solid var(--line);
  background: var(--surface);
  color: var(--ink-soft);
  font-size: 12px;
}

.status-card.error-card {
  flex-direction: column;
  align-items: flex-start;
  color: var(--warn);
  background: var(--warn-soft);
}

.loading-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.35;
  }

  50% {
    opacity: 1;
  }
}

.empty-note {
  padding: 15px;
  border: 1px dashed var(--line);
  color: var(--ink-soft);
  font-size: 11px;
  text-align: center;
}

@media (max-width: 1100px) {
  .four-columns {
    grid-template-columns: repeat(2, 1fr);
  }

  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 750px) {
  .main {
    padding: 25px 20px 40px;
  }

  .page-header {
    flex-direction: column;
  }

  .three-columns,
  .two-columns,
  .four-columns {
    grid-template-columns: 1fr;
  }

  .section-heading {
    align-items: flex-start;
    flex-direction: column;
    gap: 5px;
  }

  .alert-summary {
    align-items: flex-start;
    flex-direction: column;
  }

  .state-row {
    grid-template-columns: 110px 1fr 35px;
  }
}
</style>
