<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Page header -->
      <div>
        <h1 class="text-2xl font-bold text-gray-900">
          Paramètres
        </h1>
        <p class="text-gray-600">
          Configuration et outils de développement
        </p>
      </div>

      <!-- Settings sections -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Notifications Settings -->
        <BaseCard title="Notifications">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-sm font-medium text-gray-900">
                  Notifications temps réel
                </h4>
                <p class="text-sm text-gray-500">
                  Recevoir les notifications en temps réel via WebSocket
                </p>
              </div>
              <button
                @click="toggleNotifications"
                :class="[
                  'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                  notificationsEnabled ? 'bg-primary-600' : 'bg-gray-200'
                ]"
              >
                <span
                  :class="[
                    'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                    notificationsEnabled ? 'translate-x-5' : 'translate-x-0'
                  ]"
                />
              </button>
            </div>

            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-sm font-medium text-gray-900">
                  Notifications par email
                </h4>
                <p class="text-sm text-gray-500">
                  Recevoir un résumé quotidien par email
                </p>
              </div>
              <button
                @click="toggleEmailNotifications"
                :class="[
                  'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                  emailNotificationsEnabled ? 'bg-primary-600' : 'bg-gray-200'
                ]"
              >
                <span
                  :class="[
                    'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                    emailNotificationsEnabled ? 'translate-x-5' : 'translate-x-0'
                  ]"
                />
              </button>
            </div>
          </div>
        </BaseCard>

        <!-- WebSocket Status -->
        <BaseCard title="Connexion temps réel">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-700">Statut actuel:</span>
              <WebSocketStatus />
            </div>
            
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-700">Dernière connexion:</span>
              <span class="text-sm text-gray-500">
                {{ status.lastConnected ? formatDate(status.lastConnected.toISOString()) : 'Jamais' }}
              </span>
            </div>
            
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-700">Tentatives de reconnexion:</span>
              <span class="text-sm text-gray-500">
                {{ status.reconnectAttempts }}/5
              </span>
            </div>
            
            <div class="pt-4 border-t">
              <BaseButton
                @click="reconnectWebSocket"
                variant="secondary"
                size="sm"
                :disabled="status.connected"
              >
                Reconnecter manuellement
              </BaseButton>
            </div>
          </div>
        </BaseCard>

        <!-- User Preferences -->
        <BaseCard title="Préférences utilisateur">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Langue de l'interface
              </label>
              <select
                v-model="userPreferences.language"
                class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-primary-500 sm:text-sm"
              >
                <option value="fr">Français</option>
                <option value="en">English</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Thème
              </label>
              <select
                v-model="userPreferences.theme"
                class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-primary-500 sm:text-sm"
              >
                <option value="light">Clair</option>
                <option value="dark">Sombre</option>
                <option value="system">Système</option>
              </select>
            </div>

            <div class="pt-4 border-t">
              <BaseButton
                @click="savePreferences"
                variant="primary"
                size="sm"
              >
                Sauvegarder les préférences
              </BaseButton>
            </div>
          </div>
        </BaseCard>

        <!-- WebSocket Tester (Admin only) -->
        <div v-if="authStore.canAccessAdminPanel" class="lg:col-span-2">
          <WebSocketTester />
        </div>
      </div>

      <!-- Statistics -->
      <BaseCard title="Statistiques d'utilisation">
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-3">
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-600">
              {{ notificationStore.notifications.length }}
            </div>
            <div class="text-sm text-gray-500">
              Notifications reçues
            </div>
          </div>
          
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">
              {{ notificationStore.unreadCount }}
            </div>
            <div class="text-sm text-gray-500">
              Non lues
            </div>
          </div>
          
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-600">
              {{ status.connected ? 'Connecté' : 'Déconnecté' }}
            </div>
            <div class="text-sm text-gray-500">
              Statut WebSocket
            </div>
          </div>
        </div>
      </BaseCard>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import { useWebSocket } from '@/services/websocket'
import AppLayout from '@/layouts/AppLayout.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import WebSocketStatus from '@/components/notifications/WebSocketStatus.vue'
import WebSocketTester from '@/components/admin/WebSocketTester.vue'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'
import { toast } from 'vue-sonner'

const authStore = useAuthStore()
const notificationStore = useNotificationsStore()
const { status, reconnect } = useWebSocket()

// State
const notificationsEnabled = ref(true)
const emailNotificationsEnabled = ref(false)

const userPreferences = ref({
  language: 'fr',
  theme: 'light'
})

// Methods
const formatDate = (dateString: string) => {
  return formatDistanceToNow(new Date(dateString), {
    addSuffix: true,
    locale: fr
  })
}

const toggleNotifications = () => {
  notificationsEnabled.value = !notificationsEnabled.value
  toast.success(
    notificationsEnabled.value 
      ? 'Notifications temps réel activées' 
      : 'Notifications temps réel désactivées'
  )
}

const toggleEmailNotifications = () => {
  emailNotificationsEnabled.value = !emailNotificationsEnabled.value
  toast.success(
    emailNotificationsEnabled.value 
      ? 'Notifications email activées' 
      : 'Notifications email désactivées'
  )
}

const reconnectWebSocket = () => {
  reconnect()
  toast.info('Reconnexion WebSocket en cours...')
}

const savePreferences = () => {
  // Save preferences logic here
  localStorage.setItem('userPreferences', JSON.stringify(userPreferences.value))
  toast.success('Préférences sauvegardées')
}

// Load preferences on mount
const savedPreferences = localStorage.getItem('userPreferences')
if (savedPreferences) {
  try {
    Object.assign(userPreferences.value, JSON.parse(savedPreferences))
  } catch (error) {
    console.error('Error loading preferences:', error)
  }
}
</script>