import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials, UserType } from '@/types'
import { authApi } from '@/api/auth'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userType = computed(() => user.value?.user_type as UserType | null)
  const userFullName = computed(() => {
    if (!user.value) return ''
    return `${user.value.first_name} ${user.value.last_name}`
  })

  // Actions
  async function login(credentials: LoginCredentials) {
    loading.value = true
    error.value = null
    
    try {
      const response = await authApi.login(credentials)
      
      // Store tokens
      token.value = response.access
      refreshToken.value = response.refresh
      localStorage.setItem('token', response.access)
      localStorage.setItem('refreshToken', response.refresh)
      
      // Get user info
      await fetchCurrentUser()
      
      return { success: true, userType: user.value?.user_type }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Erreur de connexion'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      // Clear local data
      user.value = null
      token.value = null
      refreshToken.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('currentUser')
      
      // Redirect to login using window.location to avoid inject() error
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }
  }

  async function fetchCurrentUser() {
    if (!token.value) return
    
    try {
      user.value = await authApi.getCurrentUser()
    } catch (err) {
      console.error('Failed to fetch user:', err)
      // If token is invalid, logout
      if ((err as any).response?.status === 401) {
        await logout()
      }
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) {
      await logout()
      return null
    }
    
    try {
      const response = await authApi.refreshToken(refreshToken.value)
      token.value = response.access
      localStorage.setItem('token', response.access)
      return response.access
    } catch (err) {
      await logout()
      return null
    }
  }

  // Check user permissions
  function hasPermission(permission: string): boolean {
    if (!user.value) return false
    
    const userType = user.value.user_type
    
    // Define permission mappings
    const permissions = {
      'teacher_access': ['teacher', 'admin', 'superadmin'],
      'student_access': ['student', 'admin', 'superadmin'],
      'parent_access': ['parent', 'admin', 'superadmin'],
      'admin_access': ['admin', 'superadmin'],
      'superadmin_access': ['superadmin'],
      'read_own_data': ['student', 'parent', 'teacher', 'admin', 'superadmin']
    }
    
    return permissions[permission as keyof typeof permissions]?.includes(userType) || false
  }

  // Initialize user if token exists
  if (token.value) {
    fetchCurrentUser()
  }

  return {
    // State
    user,
    token,
    loading,
    error,
    // Getters
    isAuthenticated,
    userType,
    userFullName,
    // Actions
    login,
    logout,
    fetchCurrentUser,
    refreshAccessToken,
    hasPermission
  }
})