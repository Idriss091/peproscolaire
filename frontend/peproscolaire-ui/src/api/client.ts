import axios from 'axios'
import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    
    // Add auth token if available
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    
    // Add tenant header based on subdomain
    const hostname = window.location.hostname
    const subdomain = hostname.split('.')[0]
    if (subdomain && subdomain !== 'www' && subdomain !== 'localhost') {
      config.headers['X-Tenant-Subdomain'] = subdomain
    }
    
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const authStore = useAuthStore()
    const router = useRouter()
    
    if (error.response?.status === 401) {
      // Try to refresh token
      const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
      
      if (!originalRequest._retry) {
        originalRequest._retry = true
        
        try {
          const newToken = await authStore.refreshAccessToken()
          if (newToken && originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            return apiClient(originalRequest)
          }
        } catch (refreshError) {
          // Refresh failed, logout
          await authStore.logout()
          router.push('/login')
        }
      } else {
        // No refresh token or already retried, logout
        await authStore.logout()
        router.push('/login')
      }
    }
    
    return Promise.reject(error)
  }
)

// Helper functions for common HTTP methods
export const api = {
  get: <T = any>(url: string, config?: any) => apiClient.get<T>(url, config),
  post: <T = any>(url: string, data?: any, config?: any) => apiClient.post<T>(url, data, config),
  put: <T = any>(url: string, data?: any, config?: any) => apiClient.put<T>(url, data, config),
  patch: <T = any>(url: string, data?: any, config?: any) => apiClient.patch<T>(url, data, config),
  delete: <T = any>(url: string, config?: any) => apiClient.delete<T>(url, config),
}

// Export both named and default
export const client = apiClient
export default apiClient