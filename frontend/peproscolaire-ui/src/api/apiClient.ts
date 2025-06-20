import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios'

// Configuration de base de l'API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// Instance Axios principale
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Intercepteur pour ajouter le token d'authentification
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Intercepteur pour gérer les réponses et les erreurs
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expiré, essayer de le rafraîchir
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken
          })
          const newToken = response.data.access
          localStorage.setItem('access_token', newToken)
          
          // Retenter la requête originale
          if (error.config) {
            error.config.headers.Authorization = `Bearer ${newToken}`
            return apiClient.request(error.config)
          }
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient