<template>
  <div
    :class="[
      'px-4 py-3 cursor-pointer transition-colors duration-200',
      !notification.read ? 'bg-blue-50 hover:bg-blue-100' : 'hover:bg-gray-50',
      'border-l-4',
      !notification.read ? getBorderColor(notification.type) : 'border-transparent'
    ]"
    @click="$emit('click', notification)"
  >
    <div class="flex items-start space-x-3">
      <!-- Notification Icon -->
      <div :class="getIconClasses(notification.type)">
        <component :is="getIcon(notification.type)" class="h-5 w-5" />
      </div>
      
      <!-- Notification Content -->
      <div class="flex-1 min-w-0">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <p class="text-sm font-medium text-gray-900">
              {{ notification.title }}
            </p>
            <p class="text-sm text-gray-600 mt-1 line-clamp-2">
              {{ notification.message }}
            </p>
            
            <!-- Timestamp -->
            <p class="text-xs text-gray-400 mt-2 flex items-center">
              <ClockIcon class="h-3 w-3 mr-1" />
              {{ formatTime(notification.created_at) }}
            </p>
          </div>
          
          <!-- Actions -->
          <div class="flex items-center space-x-1 ml-2">
            <!-- Mark as read/unread -->
            <button
              @click.stop="toggleRead"
              :title="notification.read ? 'Marquer comme non lu' : 'Marquer comme lu'"
              class="p-1 text-gray-400 hover:text-gray-600 rounded"
            >
              <component
                :is="notification.read ? EyeSlashIcon : EyeIcon"
                class="h-4 w-4"
              />
            </button>
            
            <!-- Remove -->
            <button
              @click.stop="$emit('remove', notification.id)"
              title="Supprimer"
              class="p-1 text-gray-400 hover:text-red-600 rounded"
            >
              <XMarkIcon class="h-4 w-4" />
            </button>
          </div>
        </div>
        
        <!-- Link indicator -->
        <div v-if="notification.link" class="mt-2">
          <span class="inline-flex items-center text-xs text-primary-600">
            <ArrowTopRightOnSquareIcon class="h-3 w-3 mr-1" />
            Cliquer pour ouvrir
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  ClockIcon,
  EyeIcon,
  EyeSlashIcon,
  XMarkIcon,
  ArrowTopRightOnSquareIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/vue/24/outline'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'
import type { Notification } from '@/types'

interface Props {
  notification: Notification
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: [notification: Notification]
  'mark-read': [id: string]
  remove: [id: string]
}>()

// Methods
const formatTime = (dateString: string) => {
  return formatDistanceToNow(new Date(dateString), {
    addSuffix: true,
    locale: fr
  })
}

const getIcon = (type: string) => {
  switch (type) {
    case 'success':
      return CheckCircleIcon
    case 'error':
      return XCircleIcon
    case 'warning':
      return ExclamationTriangleIcon
    case 'info':
    default:
      return InformationCircleIcon
  }
}

const getIconClasses = (type: string) => {
  const baseClasses = 'flex-shrink-0 rounded-full p-1'
  
  switch (type) {
    case 'success':
      return `${baseClasses} bg-green-100 text-green-600`
    case 'error':
      return `${baseClasses} bg-red-100 text-red-600`
    case 'warning':
      return `${baseClasses} bg-yellow-100 text-yellow-600`
    case 'info':
    default:
      return `${baseClasses} bg-blue-100 text-blue-600`
  }
}

const getBorderColor = (type: string) => {
  switch (type) {
    case 'success':
      return 'border-green-400'
    case 'error':
      return 'border-red-400'
    case 'warning':
      return 'border-yellow-400'
    case 'info':
    default:
      return 'border-blue-400'
  }
}

const toggleRead = () => {
  emit('mark-read', props.notification.id)
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>