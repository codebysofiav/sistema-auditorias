import axios from 'axios'

// AJUSTAR: crea un archivo .env en la raíz de frontend/ con:
//   VITE_API_URL=http://localhost:8000/api
// Así no dejas la URL fija en el código, y es fácil cambiarla cuando
// tengas el servidor con PostgreSQL configurado.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_URL,
})

let refreshInProgress = false
let waitingRequests = []

function resolverPeticionesPendientes(error, token = null) {
  waitingRequests.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve(token)
  })
  waitingRequests = []
}

function limpiarSesion() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

// Agrega el token JWT a cada petición automáticamente, si existe
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Si el token expiró (401), limpia la sesión y manda al login.
// NOTA: esto es una versión simple. Más adelante se puede mejorar
// para que intente refrescar el token automáticamente con
// POST /auth/refresh/ antes de cerrar sesión.
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const refreshToken = localStorage.getItem('refresh_token')

    if (
      error.response?.status !== 401 ||
      originalRequest?._retry ||
      originalRequest?.url?.includes('/auth/refresh/') ||
      !refreshToken
    ) {
      if (error.response?.status === 401) {
        limpiarSesion()
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }

    if (refreshInProgress) {
      return new Promise((resolve, reject) => {
        waitingRequests.push({ resolve, reject })
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`
        return apiClient(originalRequest)
      })
    }

    originalRequest._retry = true
    refreshInProgress = true

    try {
      const { data } = await apiClient.post('/auth/refresh/', { refresh: refreshToken })
      localStorage.setItem('access_token', data.access)
      resolverPeticionesPendientes(null, data.access)
      originalRequest.headers.Authorization = `Bearer ${data.access}`
      return apiClient(originalRequest)
    } catch (refreshError) {
      resolverPeticionesPendientes(refreshError)
      limpiarSesion()
      window.location.href = '/login'
      return Promise.reject(refreshError)
    } finally {
      refreshInProgress = false
    }
  }
)

export default apiClient
