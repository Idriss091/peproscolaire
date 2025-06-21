<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transform transition ease-in-out duration-500"
      enter-from-class="translate-x-full"
      enter-to-class="translate-x-0"
      leave-active-class="transform transition ease-in-out duration-500"
      leave-from-class="translate-x-0"
      leave-to-class="translate-x-full"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-50 overflow-hidden"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black bg-opacity-50"
          @click="$emit('close')"
        />
        
        <!-- Panel -->
        <div class="absolute right-0 top-0 h-full w-full max-w-md">
          <div class="h-full bg-white shadow-xl">
            <!-- Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-medium text-gray-900">
                Notifications
              </h2>
              <button
                type="button"
                class="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md p-1"
                @click="$emit('close')"
              >
                <XMarkIcon class="h-6 w-6" />
              </button>
            </div>
            
            <!-- Content -->
            <div class="flex-1 overflow-y-auto">
              <div v-if="notifications.length === 0" class="p-6 text-center">
                <BellIcon class="mx-auto h-12 w-12 text-gray-400" />
                <p class="mt-2 text-sm text-gray-500">
                  Aucune notification
                </p>
              </div>
              
              <div v-else class="divide-y divide-gray-200">
                <div
                  v-for="notification in notifications"
                  :key="notification.id"
                  :class="[
                    'p-4 hover:bg-gray-50 cursor-pointer',
                    !notification.read ? 'bg-blue-50' : ''
                  ]"
                  @click="markAsRead(notification.id)"
                >
                  <div class="flex items-start space-x-3">
                    <div :class="getNotificationIconClasses(notification.type)">
                      <component :is="getNotificationIcon(notification.type)" class="h-5 w-5" />
                    </div>
                    
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900">
                        {{ notification.title }}
                      </p>
                      <p class="text-sm text-gray-500 mt-1">
                        {{ notification.message }}
                      </p>
                      <p class="text-xs text-gray-400 mt-2">
                        {{ formatDate(notification.created_at) }}
                      </p>
                    </div>
                    
                    <div v-if="!notification.read" class="flex-shrink-0">
                      <div class="h-2 w-2 bg-blue-500 rounded-full" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Footer -->
            <div class="border-t border-gray-200 px-6 py-4">
              <button
                v-if="hasUnreadNotifications"
                type="button"
                class="w-full text-center text-sm text-blue-600 hover:text-blue-500"
                @click="markAllAsRead"
              >
                Marquer tout comme lu
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'
import {
  XMarkIcon,
  BellIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon
} from '@heroicons/vue/24/outline'
import type { Notification } from '@/types'

interface Props {
  open: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

// Mock data - À remplacer par des données réelles
const notifications = computed<Notification[]>(() => [
  {
    id: '1',
    title: 'Nouvel élève à risque',
    message: 'Jean Dupont présente un niveau de risque élevé',
    type: 'warning',
    read: false,
    created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString() // 30 min ago
  },
  {
    id: '2',
    title: 'Plan d\'intervention complété',
    message: 'Le plan pour Marie Martin a été marqué comme terminé',
    type: 'success',
    read: true,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString() // 2h ago
  },
  {
    id: '3',
    title: 'Alerte critique',
    message: 'Pierre Durand nécessite une intervention immédiate',
    type: 'error',
    read: false,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString() // 4h ago
  }
])

const hasUnreadNotifications = computed(() => {
  return notifications.value.some(n => !n.read)
})

const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'success':
      return CheckCircleIcon
    case 'warning':
      return ExclamationTriangleIcon
    case 'error':
      return XCircleIcon
    default:
      return InformationCircleIcon
  }
}

const getNotificationIconClasses = (type: string) => {
  const baseClasses = 'flex-shrink-0 rounded-full p-1'
  
  switch (type) {
    case 'success':
      return `${baseClasses} bg-green-100 text-green-600`
    case 'warning':
      return `${baseClasses} bg-yellow-100 text-yellow-600`
    case 'error':
      return `${baseClasses} bg-red-100 text-red-600`
    default:
      return `${baseClasses} bg-blue-100 text-blue-600`
  }
}

const formatDate = (dateString: string) => {
  return formatDistanceToNow(new Date(dateString), {
    addSuffix: true,
    locale: fr
  })
}

const markAsRead = (id: string) => {
  // À implémenter avec l'API
  console.log('Mark as read:', id)
}

const markAllAsRead = () => {
  // À implémenter avec l'API
  console.log('Mark all as read')
}
</script>