<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg">
      <!-- Logo et titre -->
      <div class="text-center">
        <img 
          v-if="tenantLogo" 
          :src="tenantLogo" 
          alt="Logo établissement" 
          class="mx-auto h-20 w-auto mb-4"
        >
        <h2 class="text-3xl font-bold text-gray-900">
          {{ tenantName || 'PeproScolaire' }}
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          Connectez-vous à votre espace
        </p>
      </div>

      <!-- Sélection du profil -->
      <div class="grid grid-cols-2 gap-3">
        <button
          v-for="profile in profiles"
          :key="profile.value"
          @click="selectedProfile = profile.value"
          :class="[
            'relative rounded-lg p-4 text-center transition-all duration-200',
            selectedProfile === profile.value
              ? 'bg-indigo-600 text-white shadow-lg transform scale-105'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          <component :is="profile.icon" class="w-8 h-8 mx-auto mb-2" />
          <span class="text-sm font-medium">{{ profile.label }}</span>
        </button>
      </div>

      <!-- Formulaire de connexion -->
      <form @submit.prevent="handleLogin" class="mt-8 space-y-6">
        <div class="space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700">
              Identifiant
            </label>
            <input
              id="username"
              v-model="credentials.username"
              type="text"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              :class="{ 'border-red-500': errors.username }"
              placeholder="Votre identifiant"
            >
            <p v-if="errors.username" class="mt-1 text-sm text-red-600">
              {{ errors.username }}
            </p>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              Mot de passe
            </label>
            <div class="mt-1 relative">
              <input
                id="password"
                v-model="credentials.password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                :class="{ 'border-red-500': errors.password }"
                placeholder="Votre mot de passe"
              >
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <EyeIcon v-if="!showPassword" class="h-5 w-5 text-gray-400" />
                <EyeSlashIcon v-else class="h-5 w-5 text-gray-400" />
              </button>
            </div>
            <p v-if="errors.password" class="mt-1 text-sm text-red-600">
              {{ errors.password }}
            </p>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember-me"
              v-model="rememberMe"
              type="checkbox"
              class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            >
            <label for="remember-me" class="ml-2 block text-sm text-gray-900">
              Se souvenir de moi
            </label>
          </div>

          <div class="text-sm">
            <a href="#" class="font-medium text-indigo-600 hover:text-indigo-500">
              Mot de passe oublié ?
            </a>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!loading">Se connecter</span>
            <span v-else class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Connexion en cours...
            </span>
          </button>
        </div>

        <div v-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <ExclamationCircleIcon class="h-5 w-5 text-red-400" />
            </div>
            <div class="ml-3">
              <p class="text-sm text-red-800">{{ error }}</p>
            </div>
          </div>
        </div>
      </form>

      <!-- Footer -->
      <div class="text-center text-sm text-gray-500">
        <p>© 2025 PeproScolaire. Tous droits réservés.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { UserType } from '@/types'
import { 
  AcademicCapIcon, 
  UserGroupIcon, 
  UserIcon, 
  CogIcon 
} from '@heroicons/vue/24/outline'
import { 
  EyeIcon, 
  EyeSlashIcon, 
  ExclamationCircleIcon 
} from '@heroicons/vue/24/solid'

const router = useRouter()
const authStore = useAuthStore()

// Profile options
const profiles = [
  { value: 'student' as UserType, label: 'Élève', icon: AcademicCapIcon },
  { value: 'parent' as UserType, label: 'Parent', icon: UserGroupIcon },
  { value: 'teacher' as UserType, label: 'Professeur', icon: UserIcon },
  { value: 'admin' as UserType, label: 'Administration', icon: CogIcon },
]

// Form state
const selectedProfile = ref<UserType>('student')
const credentials = reactive({
  username: '',
  password: '',
})
const rememberMe = ref(false)
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')
const errors = reactive({
  username: '',
  password: '',
})

// Tenant customization
const tenantName = ref('')
const tenantLogo = ref('')

// Get tenant info from subdomain
onMounted(async () => {
  const hostname = window.location.hostname
  const subdomain = hostname.split('.')[0]
  
  if (subdomain && subdomain !== 'www' && subdomain !== 'localhost') {
    // TODO: Fetch tenant info from API
    // For now, use placeholder
    tenantName.value = `Lycée ${subdomain.charAt(0).toUpperCase() + subdomain.slice(1)}`
  }
})

// Form validation
const validateForm = () => {
  errors.username = ''
  errors.password = ''
  
  if (!credentials.username) {
    errors.username = 'L\'identifiant est requis'
    return false
  }
  
  if (!credentials.password) {
    errors.password = 'Le mot de passe est requis'
    return false
  }
  
  return true
}

// Handle login
const handleLogin = async () => {
  if (!validateForm()) return
  
  loading.value = true
  error.value = ''
  
  try {
    const result = await authStore.login({
      username: credentials.username,
      password: credentials.password,
      user_type: selectedProfile.value,
    })
    
    if (result.success) {
      // Redirect based on user type
      const redirectPath = getRedirectPath(authStore.userType)
      router.push(redirectPath)
    } else {
      error.value = result.error || 'Erreur de connexion'
    }
  } catch (err) {
    error.value = 'Une erreur est survenue. Veuillez réessayer.'
  } finally {
    loading.value = false
  }
}

// Get redirect path based on user type
const getRedirectPath = (userType: UserType | null): string => {
  // Tous les utilisateurs utilisent le même dashboard
  // Le contenu sera adapté selon le type d'utilisateur
  return '/dashboard'
}
</script>

<style scoped>
/* Add any custom styles here */
</style>