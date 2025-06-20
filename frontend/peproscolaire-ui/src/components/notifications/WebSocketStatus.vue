<template>
  <div class="flex items-center space-x-2">
    <!-- Status Indicator -->
    <div class="relative">
      <div
        :class="[
          'w-3 h-3 rounded-full transition-colors duration-300',
          getStatusColor()
        ]"
      >
        <!-- Pulse animation for connecting states -->
        <div
          v-if="status.reconnecting"
          class="absolute inset-0 w-3 h-3 rounded-full bg-yellow-400 animate-ping"
        ></div>
      </div>
    </div>
    
    <!-- Status Text -->
    <span :class="getTextColor()" class="text-sm font-medium">
      {{ getStatusText() }}
    </span>
    
    <!-- Reconnect Button -->
    <button
      v-if="!status.connected && !status.reconnecting"
      @click="reconnect"
      class="text-xs bg-primary-600 text-white px-2 py-1 rounded hover:bg-primary-700 transition-colors"
    >
      Reconnecter
    </button>
    
    <!-- Error Tooltip -->
    <div
      v-if="status.error"
      class="relative group"
    >
      <ExclamationTriangleIcon class="h-4 w-4 text-red-500 cursor-help" />
      
      <!-- Tooltip -->
      <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
        {{ status.error }}
        <div class="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWebSocket } from '@/services/websocket'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

const { status, reconnect } = useWebSocket()

// Computed
const getStatusColor = () => {
  if (status.connected) {
    return 'bg-green-400'
  } else if (status.reconnecting) {
    return 'bg-yellow-400'
  } else {
    return 'bg-red-400'
  }
}

const getTextColor = () => {
  if (status.connected) {
    return 'text-green-700'
  } else if (status.reconnecting) {
    return 'text-yellow-700'
  } else {
    return 'text-red-700'
  }
}

const getStatusText = () => {
  if (status.connected) {
    return 'Temps réel'
  } else if (status.reconnecting) {
    return `Reconnexion... (${status.reconnectAttempts}/5)`
  } else if (status.error) {
    return 'Déconnecté'
  } else {
    return 'Hors ligne'
  }
}
</script>