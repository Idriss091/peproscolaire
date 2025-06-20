<template>
  <BaseCard>
    <div class="space-y-4">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">
          Statut temps réel
        </h3>
        <WebSocketStatus />
      </div>

      <!-- Live Statistics -->
      <div class="grid grid-cols-2 gap-4">
        <div class="text-center p-3 bg-green-50 rounded-lg">
          <div class="text-2xl font-bold text-green-600">
            {{ liveStats.activeUsers }}
          </div>
          <div class="text-sm text-green-700">
            Utilisateurs connectés
          </div>
        </div>
        
        <div class="text-center p-3 bg-blue-50 rounded-lg">
          <div class="text-2xl font-bold text-blue-600">
            {{ liveStats.pendingAlerts }}
          </div>
          <div class="text-sm text-blue-700">
            Alertes en attente
          </div>
        </div>
      </div>

      <!-- Recent Activity Feed -->
      <div class="border-t pt-4">
        <h4 class="text-sm font-medium text-gray-900 mb-3">
          Activité récente
        </h4>
        
        <div class="space-y-2 max-h-48 overflow-y-auto">
          <div
            v-for="activity in recentActivity"
            :key="activity.id"
            class="flex items-start space-x-2 text-sm"
          >
            <div :class="getActivityIconClasses(activity.type)">
              <component :is="getActivityIcon(activity.type)" class="h-3 w-3" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-gray-900">{{ activity.message }}</p>
              <p class="text-gray-500 text-xs">
                {{ formatTime(activity.timestamp) }}
              </p>
            </div>
          </div>
          
          <div v-if="recentActivity.length === 0" class="text-center py-4">
            <p class="text-sm text-gray-500">
              Aucune activité récente
            </p>
          </div>
        </div>
      </div>

      <!-- Connection Quality -->
      <div class="border-t pt-4">
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-600">Qualité de connexion:</span>
          <div class="flex items-center space-x-1">
            <div
              v-for="bar in 4"
              :key="bar"
              :class="[
                'w-2 h-4 rounded-sm',
                getConnectionQualityBar(bar)
              ]"
            ></div>
            <span class="ml-2 text-gray-700">{{ connectionQuality }}</span>
          </div>
        </div>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useWebSocket } from '@/services/websocket'
import { useNotificationsStore } from '@/stores/notifications'
import BaseCard from '@/components/ui/BaseCard.vue'
import WebSocketStatus from '@/components/notifications/WebSocketStatus.vue'
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  UserIcon,
  DocumentTextIcon
} from '@heroicons/vue/24/outline'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'

const { status, subscribe } = useWebSocket()
const notificationStore = useNotificationsStore()

// State
const liveStats = ref({
  activeUsers: 0,
  pendingAlerts: 0
})

const recentActivity = ref<Array<{
  id: string
  type: string
  message: string
  timestamp: string
}>>([])

const connectionLatency = ref(0)

// Computed
const connectionQuality = computed(() => {
  if (!status.connected) return 'Déconnecté'
  if (connectionLatency.value < 100) return 'Excellent'
  if (connectionLatency.value < 300) return 'Bon'
  if (connectionLatency.value < 500) return 'Moyen'
  return 'Faible'
})

// Methods
const formatTime = (timestamp: string) => {
  return formatDistanceToNow(new Date(timestamp), {
    addSuffix: true,
    locale: fr
  })
}

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'alert':
      return ExclamationTriangleIcon
    case 'login':
    case 'logout':
      return UserIcon
    case 'update':
      return CheckCircleIcon
    case 'plan':
      return DocumentTextIcon
    default:
      return InformationCircleIcon
  }
}

const getActivityIconClasses = (type: string) => {
  const baseClasses = 'flex-shrink-0 rounded-full p-1'
  
  switch (type) {
    case 'alert':
      return `${baseClasses} bg-red-100 text-red-600`
    case 'login':
      return `${baseClasses} bg-green-100 text-green-600`
    case 'logout':
      return `${baseClasses} bg-gray-100 text-gray-600`
    case 'update':
      return `${baseClasses} bg-blue-100 text-blue-600`
    case 'plan':
      return `${baseClasses} bg-purple-100 text-purple-600`
    default:
      return `${baseClasses} bg-gray-100 text-gray-600`
  }
}

const getConnectionQualityBar = (barIndex: number) => {
  if (!status.connected) {
    return 'bg-gray-300'
  }
  
  const qualityLevel = connectionLatency.value < 100 ? 4 :
                      connectionLatency.value < 300 ? 3 :
                      connectionLatency.value < 500 ? 2 : 1
  
  if (barIndex <= qualityLevel) {
    return qualityLevel >= 3 ? 'bg-green-500' :
           qualityLevel >= 2 ? 'bg-yellow-500' : 'bg-red-500'
  }
  
  return 'bg-gray-300'
}

const addActivity = (type: string, message: string) => {
  const activity = {
    id: Date.now().toString(),
    type,
    message,
    timestamp: new Date().toISOString()
  }
  
  recentActivity.value.unshift(activity)
  
  // Keep only last 10 activities
  if (recentActivity.value.length > 10) {
    recentActivity.value = recentActivity.value.slice(0, 10)
  }
}

const measureLatency = () => {
  const start = Date.now()
  
  // This would be replaced with actual ping/pong in a real WebSocket implementation
  connectionLatency.value = Math.random() * 200 + 50 // Mock latency
}

// WebSocket event handlers
let unsubscribeHandlers: Array<() => void> = []

onMounted(() => {
  // Subscribe to WebSocket events
  unsubscribeHandlers.push(
    subscribe('alert_created', (data) => {
      liveStats.value.pendingAlerts++
      addActivity('alert', `Nouvelle alerte: ${data.alert.title}`)
    }),
    
    subscribe('user_connected', (data) => {
      liveStats.value.activeUsers++
      addActivity('login', `${data.user.first_name} ${data.user.last_name} s'est connecté`)
    }),
    
    subscribe('user_disconnected', (data) => {
      liveStats.value.activeUsers = Math.max(0, liveStats.value.activeUsers - 1)
      addActivity('logout', `${data.user.first_name} ${data.user.last_name} s'est déconnecté`)
    }),
    
    subscribe('risk_profile_updated', (data) => {
      addActivity('update', `Profil de risque mis à jour: ${data.profile.student.first_name} ${data.profile.student.last_name}`)
    }),
    
    subscribe('intervention_plan_updated', (data) => {
      addActivity('plan', `Plan d'intervention modifié: ${data.plan.title}`)
    })
  )
  
  // Mock initial data
  liveStats.value.activeUsers = Math.floor(Math.random() * 20) + 5
  liveStats.value.pendingAlerts = Math.floor(Math.random() * 10) + 2
  
  // Add some initial activity
  const mockActivities = [
    { type: 'login', message: 'Marie Dubois s\'est connectée' },
    { type: 'alert', message: 'Nouvelle alerte: Risque de décrochage détecté' },
    { type: 'update', message: 'Profil de risque mis à jour: Jean Martin' },
    { type: 'plan', message: 'Plan d\'intervention créé pour Sophie Leroy' }
  ]
  
  mockActivities.forEach((activity, index) => {
    setTimeout(() => {
      addActivity(activity.type, activity.message)
    }, index * 2000)
  })
  
  // Start latency monitoring
  const latencyInterval = setInterval(measureLatency, 5000)
  
  onUnmounted(() => {
    clearInterval(latencyInterval)
  })
})

onUnmounted(() => {
  // Unsubscribe from all WebSocket events
  unsubscribeHandlers.forEach(unsubscribe => unsubscribe())
})
</script>