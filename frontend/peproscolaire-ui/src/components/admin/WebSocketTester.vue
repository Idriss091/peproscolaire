<template>
  <BaseCard>
    <div class="space-y-4">
      <h3 class="text-lg font-medium text-gray-900">
        Testeur WebSocket
      </h3>
      
      <!-- Connection Status -->
      <div class="flex items-center justify-between p-3 bg-gray-50 rounded-md">
        <span class="text-sm font-medium">Statut de connexion:</span>
        <WebSocketStatus />
      </div>
      
      <!-- Message Controls -->
      <div class="space-y-3">
        <h4 class="text-sm font-medium text-gray-700">
          Simuler des événements:
        </h4>
        
        <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <BaseButton
            @click="sendTestNotification"
            variant="secondary"
            size="sm"
          >
            📨 Notification
          </BaseButton>
          
          <BaseButton
            @click="sendTestAlert"
            variant="warning"
            size="sm"
          >
            🚨 Alerte urgente
          </BaseButton>
          
          <BaseButton
            @click="sendUserConnection"
            variant="success"
            size="sm"
          >
            👤 Connexion utilisateur
          </BaseButton>
          
          <BaseButton
            @click="sendRiskUpdate"
            variant="info"
            size="sm"
          >
            📊 Mise à jour risque
          </BaseButton>
        </div>
      </div>
      
      <!-- Custom Message -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700">
          Message personnalisé:
        </label>
        <div class="flex space-x-2">
          <select
            v-model="customMessage.type"
            class="block w-32 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          >
            <option value="info">Info</option>
            <option value="success">Succès</option>
            <option value="warning">Avertissement</option>
            <option value="error">Erreur</option>
          </select>
          <input
            v-model="customMessage.title"
            placeholder="Titre..."
            class="block flex-1 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          />
          <BaseButton
            @click="sendCustomMessage"
            variant="primary"
            size="sm"
          >
            Envoyer
          </BaseButton>
        </div>
      </div>
      
      <!-- Message History -->
      <div class="border-t pt-4">
        <div class="flex items-center justify-between mb-2">
          <h4 class="text-sm font-medium text-gray-700">
            Messages envoyés:
          </h4>
          <BaseButton
            @click="clearHistory"
            variant="ghost"
            size="xs"
          >
            Effacer
          </BaseButton>
        </div>
        
        <div class="max-h-32 overflow-y-auto space-y-1">
          <div
            v-for="(message, index) in messageHistory"
            :key="index"
            class="text-xs p-2 bg-gray-100 rounded text-gray-600"
          >
            <strong>{{ message.type }}:</strong> {{ message.data.title || 'Message' }}
            <span class="float-right">{{ formatTime(message.timestamp) }}</span>
          </div>
          
          <div v-if="messageHistory.length === 0" class="text-center text-xs text-gray-500 py-4">
            Aucun message envoyé
          </div>
        </div>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useWebSocket } from '@/services/websocket'
import { useNotificationsStore } from '@/stores/notifications'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import WebSocketStatus from '@/components/notifications/WebSocketStatus.vue'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'

const { send } = useWebSocket()
const notificationStore = useNotificationsStore()

// State
const customMessage = ref({
  type: 'info',
  title: ''
})

const messageHistory = ref<any[]>([])

// Methods
const sendTestNotification = () => {
  const message = {
    type: 'notification',
    data: {
      title: 'Test de notification',
      message: 'Ceci est un test de notification en temps réel',
      type: 'info'
    },
    timestamp: new Date().toISOString()
  }
  
  // Simulate receiving the message locally for demo purposes
  notificationStore.addNotification({
    title: message.data.title,
    message: message.data.message,
    type: message.data.type as any,
    created_at: message.timestamp
  })
  
  messageHistory.value.unshift(message)
}

const sendTestAlert = () => {
  const students = ['Jean Dupont', 'Marie Martin', 'Pierre Durand', 'Sophie Leroy']
  const randomStudent = students[Math.floor(Math.random() * students.length)]
  
  const message = {
    type: 'alert_created',
    data: {
      alert: {
        id: Date.now().toString(),
        title: 'Risque critique détecté',
        message: `L'élève ${randomStudent} présente un risque critique de décrochage`,
        priority: 'urgent',
        risk_profile: {
          student: {
            first_name: randomStudent.split(' ')[0],
            last_name: randomStudent.split(' ')[1]
          }
        }
      }
    },
    timestamp: new Date().toISOString()
  }
  
  // Simulate receiving the message locally
  notificationStore.addNotification({
    title: message.data.alert.title,
    message: message.data.alert.message,
    type: 'error',
    created_at: message.timestamp,
    link: '/risk-detection/alerts'
  })
  
  messageHistory.value.unshift(message)
}

const sendUserConnection = () => {
  const users = [
    { first_name: 'Marie', last_name: 'Dubois' },
    { first_name: 'Jean', last_name: 'Martin' },
    { first_name: 'Sophie', last_name: 'Leroy' }
  ]
  const randomUser = users[Math.floor(Math.random() * users.length)]
  
  const message = {
    type: 'user_connected',
    data: {
      user: randomUser
    },
    timestamp: new Date().toISOString()
  }
  
  notificationStore.addNotification({
    title: 'Nouvelle connexion',
    message: `${randomUser.first_name} ${randomUser.last_name} s'est connecté`,
    type: 'success',
    created_at: message.timestamp
  })
  
  messageHistory.value.unshift(message)
}

const sendRiskUpdate = () => {
  const students = ['Jean Dupont', 'Marie Martin', 'Pierre Durand']
  const randomStudent = students[Math.floor(Math.random() * students.length)]
  const riskLevels = ['low', 'moderate', 'high', 'critical']
  const randomLevel = riskLevels[Math.floor(Math.random() * riskLevels.length)]
  
  const message = {
    type: 'risk_profile_updated',
    data: {
      profile: {
        student: {
          first_name: randomStudent.split(' ')[0],
          last_name: randomStudent.split(' ')[1]
        },
        risk_level: randomLevel
      },
      risk_change: {
        significant: true,
        message: `Niveau de risque passé à ${randomLevel}`
      }
    },
    timestamp: new Date().toISOString()
  }
  
  notificationStore.addNotification({
    title: 'Profil de risque mis à jour',
    message: `${randomStudent}: niveau ${randomLevel}`,
    type: randomLevel === 'critical' || randomLevel === 'high' ? 'warning' : 'info',
    created_at: message.timestamp,
    link: '/risk-detection/profiles'
  })
  
  messageHistory.value.unshift(message)
}

const sendCustomMessage = () => {
  if (!customMessage.value.title.trim()) return
  
  const message = {
    type: 'notification',
    data: {
      title: customMessage.value.title,
      message: 'Message personnalisé envoyé depuis le testeur',
      type: customMessage.value.type
    },
    timestamp: new Date().toISOString()
  }
  
  notificationStore.addNotification({
    title: message.data.title,
    message: message.data.message,
    type: message.data.type as any,
    created_at: message.timestamp
  })
  
  messageHistory.value.unshift(message)
  customMessage.value.title = ''
}

const clearHistory = () => {
  messageHistory.value = []
}

const formatTime = (timestamp: string) => {
  return formatDistanceToNow(new Date(timestamp), {
    addSuffix: true,
    locale: fr
  })
}
</script>