import axios from 'axios'
import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'

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
    // Get token from localStorage directly
    const token = localStorage.getItem('token')
    
    // Add auth token if available
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
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
    if (error.response?.status === 401) {
      // Clear tokens and redirect to login
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      
      // Redirect to login page
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
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