import { defineStore } from 'pinia'
import apiClient from '@/api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null, // { id, email, first_name, last_name, roles: [...] }
    accessToken: localStorage.getItem('access_token') || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,

    // AJUSTAR si un usuario pudiera tener más de un rol a la vez;
    // por ahora asumimos un solo rol principal por usuario.
    rol: (state) => state.user?.roles?.[0] || null,

    isAdmin: (state) => state.user?.roles?.includes('Administrador') ?? false,
    isAuditor: (state) => state.user?.roles?.includes('Auditor') ?? false,
    isConsulta: (state) => state.user?.roles?.includes('Usuario consulta') ?? false,
  },

  actions: {
    async login(email, password) {
      const { data } = await apiClient.post('/auth/login/', { email, password })

      this.accessToken = data.access
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)

      await this.fetchUser()
    },

    async fetchUser() {
      const { data } = await apiClient.get('/auth/me/')
      this.user = data
    },

    async logout() {
      try {
        await apiClient.post('/auth/logout/')
      } catch {
        // si falla la llamada al backend, igual limpiamos la sesión local
      }
      this.user = null
      this.accessToken = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    },
  },
})