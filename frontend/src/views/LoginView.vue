<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import logoUis from '@/assets/logo-uis.png'

const email = ref('')
const password = ref('')
const errorMsg = ref('')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()

async function handleSubmit() {
  errorMsg.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push({ name: 'dashboard' })
  } catch (err) {
    errorMsg.value = 'Correo o contraseña incorrectos.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-view">
    <div class="login-card">
      <div class="brand-lockup">
        <img :src="logoUis" alt="Universidad Industrial de Santander" />
        <div class="uni-name">
          <strong>Universidad Industrial de Santander</strong>
          Sistema de Gesión de Auditorias
        </div>
      </div>

      <h1>Iniciar sesión</h1>

      <form @submit.prevent="handleSubmit">
        <div class="field">
          <label for="email">Correo institucional</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="nombre@universidad.edu.co"
            required
          />
        </div>

        <div class="field">
          <label for="password">Contraseña</label>
          <input id="password" v-model="password" type="password" placeholder="••••••••" required />
        </div>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <button type="submit" class="login-submit" :disabled="loading">
          {{ loading ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>

      <div class="login-foot">
        Acceso exclusivo para personal autorizado. Si olvidó su contraseña, contacte a la
        administración del sistema.
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
}
.login-card {
  width: 100%;
  max-width: 380px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 42px 38px 34px;
  box-shadow: var(--shadow-subtle);
}
.brand-lockup {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 28px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--line);
}
.brand-lockup img { height: 43px; width: auto; display: block; }
.uni-name {
  font-size: 12.5px;
  line-height: 1.3;
  color: var(--ink-soft);
  font-weight: 500;
}
.uni-name strong { display: block; color: var(--ink); font-weight: 600; font-size: 13px; }
h1 { font-size: 23px; font-weight: 600; margin: 0 0 28px; line-height: 1.3; letter-spacing: 0; }
.field { margin-bottom: 18px; }
.field label { display: block; font-size: 13px; color: var(--ink-soft); margin-bottom: 6px; }
.field input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  font-size: 14px;
  background: var(--bg);
  color: var(--ink);
}
.field input:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
.field input:hover { border-color: #C8C1B5; }
.error-msg { color: var(--warn); font-size: 13px; margin: -6px 0 14px; background: var(--warn-soft); border-left: 2px solid var(--warn); padding: 8px 10px; }
.login-submit {
  width: 100%;
  padding: 11px;
  margin-top: 8px;
  background: var(--ink);
  color: #F6F5F2;
  border: none;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 2px 0 rgba(10, 20, 31, 0.18);
  transition: background-color 150ms ease, transform 150ms ease, box-shadow 150ms ease;
}
.login-submit:hover:not(:disabled) { background: #26394D; box-shadow: 0 4px 10px rgba(29, 43, 58, 0.14); transform: translateY(-1px); }
.login-submit:disabled { opacity: 0.6; cursor: default; }
.login-foot {
  margin-top: 20px;
  font-size: 12px;
  color: var(--ink-soft);
  line-height: 1.6;
  border-top: 1px solid var(--line);
  padding-top: 16px;
}
</style>
