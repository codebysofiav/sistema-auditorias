import axios from 'axios'

// AJUSTAR: crea un archivo .env en la raíz de frontend/ con:
//   VITE_API_URL=http://localhost:8000/api
// Así no dejas la URL fija en el código, y es fácil cambiarla cuando
// tengas el servidor con PostgreSQL configurado.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_URL,
})

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
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient