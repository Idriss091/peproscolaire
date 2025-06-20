import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'
import { createMockUser, createMockApiResponse, createMockApiError } from '@/test/utils'

// Mock the auth API
vi.mock('@/api/auth', () => ({
  authAPI: {
    login: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
    getStoredToken: vi.fn(),
    getStoredUser: vi.fn()
  }
}))

// Mock WebSocket service
vi.mock('@/services/websocket', () => ({
  webSocketService: {
    connect: vi.fn(),
    disconnect: vi.fn()
  }
}))

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const authStore = useAuthStore()

      expect(authStore.user).toBeNull()
      expect(authStore.token).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
      expect(authStore.isLoading).toBe(false)
      expect(authStore.error).toBeNull()
    })
  })

  describe('Getters', () => {
    it('should compute isAuthenticated correctly', () => {
      const authStore = useAuthStore()

      expect(authStore.isAuthenticated).toBe(false)

      authStore.user = createMockUser()
      authStore.token = 'test-token'

      expect(authStore.isAuthenticated).toBe(true)
    })

    it('should compute fullName correctly', () => {
      const authStore = useAuthStore()

      expect(authStore.fullName).toBe('')

      authStore.user = createMockUser({
        first_name: 'John',
        last_name: 'Doe'
      })

      expect(authStore.fullName).toBe('John Doe')
    })

    it('should compute canAccessAdminPanel correctly', () => {
      const authStore = useAuthStore()

      expect(authStore.canAccessAdminPanel).toBe(false)

      authStore.user = createMockUser({ user_type: 'admin' })
      expect(authStore.canAccessAdminPanel).toBe(true)

      authStore.user = createMockUser({ user_type: 'superadmin' })
      expect(authStore.canAccessAdminPanel).toBe(true)

      authStore.user = createMockUser({ user_type: 'teacher' })
      expect(authStore.canAccessAdminPanel).toBe(false)
    })

    it('should compute canManageStudents correctly', () => {
      const authStore = useAuthStore()

      expect(authStore.canManageStudents).toBe(false)

      authStore.user = createMockUser({ user_type: 'teacher' })
      expect(authStore.canManageStudents).toBe(true)

      authStore.user = createMockUser({ user_type: 'admin' })
      expect(authStore.canManageStudents).toBe(true)

      authStore.user = createMockUser({ user_type: 'student' })
      expect(authStore.canManageStudents).toBe(false)
    })
  })

  describe('Actions', () => {
    describe('login', () => {
      it('should login successfully', async () => {
        const { authAPI } = await import('@/api/auth')
        const { webSocketService } = await import('@/services/websocket')
        
        const mockUser = createMockUser()
        const mockResponse = createMockApiResponse({
          user: mockUser,
          access: 'test-token'
        })

        authAPI.login = vi.fn().mockResolvedValue(mockResponse)

        const authStore = useAuthStore()
        const result = await authStore.login({
          email: 'test@example.com',
          password: 'password'
        })

        expect(result).toBe(true)
        expect(authStore.user).toEqual(mockUser)
        expect(authStore.token).toBe('test-token')
        expect(authStore.error).toBeNull()
        expect(webSocketService.connect).toHaveBeenCalledWith('test-token')
      })

      it('should handle login error', async () => {
        const { authAPI } = await import('@/api/auth')
        
        const mockError = createMockApiError('Invalid credentials')
        authAPI.login = vi.fn().mockResolvedValue(mockError)

        const authStore = useAuthStore()
        const result = await authStore.login({
          email: 'test@example.com',
          password: 'wrong-password'
        })

        expect(result).toBe(false)
        expect(authStore.user).toBeNull()
        expect(authStore.token).toBeNull()
        expect(authStore.error).toBe('Invalid credentials')
      })

      it('should handle network error during login', async () => {
        const { authAPI } = await import('@/api/auth')
        
        authAPI.login = vi.fn().mockRejectedValue(new Error('Network error'))

        const authStore = useAuthStore()
        const result = await authStore.login({
          email: 'test@example.com',
          password: 'password'
        })

        expect(result).toBe(false)
        expect(authStore.error).toBe('Erreur de connexion')
      })
    })

    describe('logout', () => {
      it('should logout successfully', async () => {
        const { authAPI } = await import('@/api/auth')
        const { webSocketService } = await import('@/services/websocket')
        
        authAPI.logout = vi.fn().mockResolvedValue({})

        const authStore = useAuthStore()
        // Set initial state
        authStore.user = createMockUser()
        authStore.token = 'test-token'

        await authStore.logout()

        expect(authStore.user).toBeNull()
        expect(authStore.token).toBeNull()
        expect(authStore.error).toBeNull()
        expect(webSocketService.disconnect).toHaveBeenCalled()
      })

      it('should clear state even if API call fails', async () => {
        const { authAPI } = await import('@/api/auth')
        const { webSocketService } = await import('@/services/websocket')
        
        authAPI.logout = vi.fn().mockRejectedValue(new Error('API error'))

        const authStore = useAuthStore()
        // Set initial state
        authStore.user = createMockUser()
        authStore.token = 'test-token'

        await authStore.logout()

        expect(authStore.user).toBeNull()
        expect(authStore.token).toBeNull()
        expect(authStore.error).toBeNull()
        expect(webSocketService.disconnect).toHaveBeenCalled()
      })
    })

    describe('refreshUser', () => {
      it('should refresh user data successfully', async () => {
        const { authAPI } = await import('@/api/auth')
        
        const mockUser = createMockUser()
        const mockResponse = createMockApiResponse(mockUser)
        authAPI.getCurrentUser = vi.fn().mockResolvedValue(mockResponse)

        const authStore = useAuthStore()
        const result = await authStore.refreshUser()

        expect(result).toBe(true)
        expect(authStore.user).toEqual(mockUser)
      })

      it('should handle 401 error by logging out', async () => {
        const { authAPI } = await import('@/api/auth')
        
        const mockError = createMockApiError('Unauthorized', 401)
        authAPI.getCurrentUser = vi.fn().mockResolvedValue(mockError)
        authAPI.logout = vi.fn().mockResolvedValue({})

        const authStore = useAuthStore()
        authStore.user = createMockUser()
        authStore.token = 'expired-token'

        const result = await authStore.refreshUser()

        expect(result).toBe(false)
        expect(authStore.user).toBeNull()
        expect(authStore.token).toBeNull()
      })
    })

    describe('initializeAuth', () => {
      it('should initialize auth from stored data', async () => {
        const { authAPI } = await import('@/api/auth')
        const { webSocketService } = await import('@/services/websocket')
        
        const mockUser = createMockUser()
        const mockToken = 'stored-token'

        authAPI.getStoredToken = vi.fn().mockReturnValue(mockToken)
        authAPI.getStoredUser = vi.fn().mockReturnValue(mockUser)

        const authStore = useAuthStore()
        await authStore.initializeAuth()

        expect(authStore.user).toEqual(mockUser)
        expect(authStore.token).toBe(mockToken)
        expect(webSocketService.connect).toHaveBeenCalledWith(mockToken)
      })

      it('should not initialize auth if no stored data', async () => {
        const { authAPI } = await import('@/api/auth')
        const { webSocketService } = await import('@/services/websocket')
        
        authAPI.getStoredToken = vi.fn().mockReturnValue(null)
        authAPI.getStoredUser = vi.fn().mockReturnValue(null)

        const authStore = useAuthStore()
        await authStore.initializeAuth()

        expect(authStore.user).toBeNull()
        expect(authStore.token).toBeNull()
        expect(webSocketService.connect).not.toHaveBeenCalled()
      })
    })
  })

  describe('Loading States', () => {
    it('should set loading state during login', async () => {
      const { authAPI } = await import('@/api/auth')
      
      let resolvePromise: (value: any) => void
      const loginPromise = new Promise(resolve => {
        resolvePromise = resolve
      })

      authAPI.login = vi.fn().mockReturnValue(loginPromise)

      const authStore = useAuthStore()
      const loginCall = authStore.login({
        email: 'test@example.com',
        password: 'password'
      })

      expect(authStore.isLoading).toBe(true)

      resolvePromise!(createMockApiResponse({
        user: createMockUser(),
        access: 'token'
      }))

      await loginCall

      expect(authStore.isLoading).toBe(false)
    })
  })

  describe('Error Handling', () => {
    it('should clear error when starting new action', async () => {
      const { authAPI } = await import('@/api/auth')
      
      const authStore = useAuthStore()
      authStore.error = 'Previous error'

      authAPI.login = vi.fn().mockResolvedValue(createMockApiResponse({
        user: createMockUser(),
        access: 'token'
      }))

      await authStore.login({
        email: 'test@example.com',
        password: 'password'
      })

      expect(authStore.error).toBeNull()
    })
  })
})