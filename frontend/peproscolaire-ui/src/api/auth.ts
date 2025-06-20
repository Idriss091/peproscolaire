import { apiClient } from './client'
import type { User, LoginCredentials, AuthResponse } from '@/types'

// Données mockées pour la démonstration
const MOCK_USERS: Record<string, User> = {
  'demo': {
    id: '1',
    username: 'demo',
    first_name: 'Jean',
    last_name: 'Professeur',
    email: 'jean.professeur@demo.fr',
    user_type: 'teacher',
    profile_picture: null,
    is_active: true,
    last_login: new Date().toISOString(),
    date_joined: new Date().toISOString()
  },
  'admin': {
    id: '2',
    username: 'admin',
    first_name: 'Admin',
    last_name: 'Principal',
    email: 'admin@demo.fr',
    user_type: 'admin',
    profile_picture: null,
    is_active: true,
    last_login: new Date().toISOString(),
    date_joined: new Date().toISOString()
  },
  'eleve': {
    id: '3',
    username: 'eleve',
    first_name: 'Marie',
    last_name: 'Élève',
    email: 'marie.eleve@demo.fr',
    user_type: 'student',
    profile_picture: null,
    is_active: true,
    last_login: new Date().toISOString(),
    date_joined: new Date().toISOString()
  },
  'parent': {
    id: '4',
    username: 'parent',
    first_name: 'Pierre',
    last_name: 'Parent',
    email: 'pierre.parent@demo.fr',
    user_type: 'parent',
    profile_picture: null,
    is_active: true,
    last_login: new Date().toISOString(),
    date_joined: new Date().toISOString()
  }
}

export const authApi = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // Vérifier si on utilise l'API mockée ou la vraie API
    const useMockApi = import.meta.env.VITE_USE_MOCK_API === 'true'
    
    if (useMockApi) {
      // Mode mockée (ancien comportement)
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const user = MOCK_USERS[credentials.username] || MOCK_USERS['demo']
      
      if (credentials.password !== 'demo123' && credentials.password !== 'password' && credentials.password !== 'demo') {
        throw new Error('Identifiants incorrects')
      }
      
      // Adapter le type d'utilisateur selon la sélection
      if (credentials.user_type && credentials.user_type !== user.user_type) {
        user.user_type = credentials.user_type
        user.first_name = user.user_type === 'student' ? 'Marie' :
                          user.user_type === 'parent' ? 'Pierre' :
                          user.user_type === 'teacher' ? 'Jean' : 'Admin'
        user.last_name = user.user_type === 'student' ? 'Élève' :
                         user.user_type === 'parent' ? 'Parent' :
                         user.user_type === 'teacher' ? 'Professeur' : 'Principal'
      }
      
      return {
        access: 'mock-jwt-token-access',
        refresh: 'mock-jwt-token-refresh',
        user
      }
    } else {
      // Mode API réelle
      const response = await apiClient.post<AuthResponse>('/auth/login/', credentials)
      return response.data
    }
  },

  async logout(): Promise<void> {
    // Simulation logout
    await new Promise(resolve => setTimeout(resolve, 500))
  },

  async getCurrentUser(): Promise<User> {
    const useMockApi = import.meta.env.VITE_USE_MOCK_API === 'true'
    
    if (useMockApi) {
      await new Promise(resolve => setTimeout(resolve, 500))
      return MOCK_USERS['demo']
    } else {
      const response = await apiClient.get<User>('/auth/me/')
      return response.data
    }
  },

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    await new Promise(resolve => setTimeout(resolve, 500))
    return { access: 'mock-new-jwt-token' }
  },

  async changePassword(data: {
    old_password: string
    new_password: string
    new_password_confirm: string
  }): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 1000))
    // Simulation réussie
  },

  async resetPasswordRequest(email: string): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log('Reset password requested for:', email)
  },

  async resetPasswordConfirm(data: {
    uid: string
    token: string
    new_password: string
    new_password_confirm: string
  }): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 1000))
    // Simulation réussie
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    await new Promise(resolve => setTimeout(resolve, 1000))
    return { ...MOCK_USERS['demo'], ...data }
  }
}

// Re-export for backward compatibility
export const authAPI = authApi