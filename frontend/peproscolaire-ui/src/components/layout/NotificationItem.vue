<template>
  <div
    @click="$emit('click', notification)"
    :class="itemClasses"
    class="notification-item"
  >
    <div class="notification-content">
      <!-- Icône -->
      <div :class="iconContainerClasses" class="notification-icon">
        <component :is="notificationIcon" class="h-5 w-5" />
      </div>
      
      <!-- Contenu principal -->
      <div class="notification-body">
        <div class="notification-header">
          <h4 class="notification-title">{{ notification.title }}</h4>
          <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
        </div>
        
        <p class="notification-message">{{ notification.message }}</p>
        
        <!-- Métadonnées -->
        <div v-if="hasMetadata" class="notification-meta">
          <span v-if="notification.category" class="meta-category">
            {{ getCategoryLabel(notification.category) }}
          </span>
          <span v-if="notification.sender" class="meta-sender">
            par {{ notification.sender }}
          </span>
        </div>
        
        <!-- Actions -->
        <div v-if="notification.actions && notification.actions.length > 0" class="notification-actions">
          <button
            v-for="action in notification.actions"
            :key="action.id"
            @click.stop="handleAction(action)"
            :class="getActionClasses(action.type)"
            class="action-btn"
          >
            {{ action.label }}
          </button>
        </div>
      </div>
      
      <!-- Badge de priorité -->
      <div v-if="notification.priority === 'high'" class="priority-badge">
        <ExclamationTriangleIcon class="h-3 w-3" />
      </div>
    </div>
    
    <!-- Menu d'actions -->
    <BaseDropdown placement="bottom-end" size="sm">
      <template #trigger>
        <button
          @click.stop
          class="notification-menu-btn"
          aria-label="Actions"
        >
          <EllipsisVerticalIcon class="h-4 w-4" />
        </button>
      </template>
      
      <div class="py-1">
        <button
          v-if="!notification.read"
          @click="$emit('mark-read', notification.id)"
          class="dropdown-item"
          role="menuitem"
        >
          <CheckIcon class="h-4 w-4" />
          Marquer comme lu
        </button>
        <button
          v-else
          @click="$emit('mark-unread', notification.id)"
          class="dropdown-item"
          role="menuitem"
        >
          <XCircleIcon class="h-4 w-4" />
          Marquer comme non lu
        </button>
        
        <button
          @click="$emit('archive', notification.id)"
          class="dropdown-item"
          role="menuitem"
        >
          <ArchiveBoxIcon class="h-4 w-4" />
          Archiver
        </button>
        
        <div class="dropdown-divider" />
        
        <button
          @click="$emit('delete', notification.id)"
          class="dropdown-item dropdown-item-danger"
          role="menuitem"
        >
          <TrashIcon class="h-4 w-4" />
          Supprimer
        </button>
      </div>
    </BaseDropdown>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  BellIcon,
  InformationCircleIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  UserIcon,
  AcademicCapIcon,
  CalendarIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
  EllipsisVerticalIcon,
  CheckIcon,
  ArchiveBoxIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import BaseDropdown from '@/components/ui/BaseDropdown.vue'
import type { Notification, NotificationAction } from '@/types/notifications'

interface Props {
  notification: Notification
}

const props = defineProps<Props>()

interface Emits {
  click: [notification: Notification]
  'mark-read': [id: string]
  'mark-unread': [id: string]
  archive: [id: string]
  delete: [id: string]
}

defineEmits<Emits>()

const itemClasses = computed(() => [
  'notification-item',
  {
    'notification-unread': !props.notification.read,
    'notification-read': props.notification.read,
    'notification-high-priority': props.notification.priority === 'high'
  }
])

const iconContainerClasses = computed(() => [
  'notification-icon',
  `icon-${props.notification.type || 'info'}`,
  {
    'icon-high-priority': props.notification.priority === 'high'
  }
])

const notificationIcon = computed(() => {
  const icons = {
    info: InformationCircleIcon,
    success: CheckCircleIcon,
    warning: ExclamationTriangleIcon,
    error: XCircleIcon,
    message: ChatBubbleLeftRightIcon,
    grade: AcademicCapIcon,
    schedule: CalendarIcon,
    document: DocumentTextIcon,
    user: UserIcon
  }
  
  return icons[props.notification.type] || BellIcon
})

const hasMetadata = computed(() => {
  return props.notification.category || props.notification.sender
})

// Méthodes
const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
  
  if (diffInMinutes < 1) return 'À l\'instant'
  if (diffInMinutes < 60) return `${diffInMinutes}min`
  if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h`
  if (diffInMinutes < 10080) return `${Math.floor(diffInMinutes / 1440)}j`
  
  return date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short'
  })
}

const getCategoryLabel = (category: string) => {
  const labels = {
    academic: 'Académique',
    administrative: 'Administratif',
    social: 'Social',
    system: 'Système',
    announcement: 'Annonce'
  }
  return labels[category] || category
}

const handleAction = (action: NotificationAction) => {
  if (action.url) {
    window.location.href = action.url
  }
  
  // Émettre un événement personnalisé si nécessaire
  if (action.callback) {
    action.callback()
  }
}

const getActionClasses = (type: string) => {
  const classes = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    success: 'btn-success',
    warning: 'btn-warning',
    danger: 'btn-danger'
  }
  return classes[type] || 'btn-secondary'
}
</script>

<style scoped>
.notification-item {
  @apply relative flex items-start gap-3 p-4 hover:bg-gray-50 transition-colors border-l-4 border-transparent cursor-pointer group;
}

.notification-unread {
  @apply bg-primary-50/50 border-l-primary-500;
}

.notification-read {
  @apply border-l-neutral-200;
}

.notification-high-priority {
  @apply border-l-danger-500;
}

.notification-content {
  @apply flex-1 flex items-start gap-3;
}

.notification-icon {
  @apply w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0;
}

.icon-info {
  @apply bg-info-100 text-info-600;
}

.icon-success {
  @apply bg-green-100 text-green-600;
}

.icon-warning {
  @apply bg-warning-100 text-warning-600;
}

.icon-error {
  @apply bg-red-100 text-red-600;
}

.icon-message {
  @apply bg-primary-100 text-blue-600;
}

.icon-grade {
  @apply bg-education-100 text-education-600;
}

.icon-schedule {
  @apply bg-secondary-100 text-secondary-600;
}

.icon-document {
  @apply bg-gray-100 text-gray-600;
}

.icon-user {
  @apply bg-gray-100 text-gray-600;
}

.icon-high-priority {
  @apply ring-2 ring-danger-200;
}

.notification-body {
  @apply flex-1 min-w-0 space-y-2;
}

.notification-header {
  @apply flex items-start justify-between gap-2;
}

.notification-title {
  @apply font-semibold text-gray-900 text-sm leading-tight;
}

.notification-unread .notification-title {
  @apply font-bold;
}

.notification-time {
  @apply text-xs text-gray-500 flex-shrink-0;
}

.notification-message {
  @apply text-sm text-gray-700 leading-relaxed;
}

.notification-meta {
  @apply flex items-center gap-2 text-xs text-gray-500;
}

.meta-category {
  @apply px-2 py-1 bg-gray-100 rounded-full font-medium;
}

.meta-sender {
  @apply italic;
}

.notification-actions {
  @apply flex items-center gap-2 mt-3;
}

.action-btn {
  @apply px-3 py-1.5 text-xs font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2;
}

.btn-primary {
  @apply bg-primary-600 text-white hover:bg-primary-700 focus:ring-blue-500;
}

.btn-secondary {
  @apply bg-gray-200 text-gray-700 hover:bg-gray-300 focus:ring-neutral-500;
}

.btn-success {
  @apply bg-green-600 text-white hover:bg-green-700 focus:ring-success-500;
}

.btn-warning {
  @apply bg-warning-600 text-white hover:bg-warning-700 focus:ring-warning-500;
}

.btn-danger {
  @apply bg-red-600 text-white hover:bg-red-700 focus:ring-danger-500;
}

.priority-badge {
  @apply w-6 h-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center flex-shrink-0;
}

.notification-menu-btn {
  @apply w-8 h-8 rounded-lg bg-transparent hover:bg-gray-200 flex items-center justify-center text-gray-400 hover:text-gray-600 transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100 focus:outline-none focus:ring-2 focus:ring-blue-500;
}

/* États de lecture */
.notification-read {
  @apply opacity-75;
}

.notification-unread::before {
  @apply content-[''] absolute top-4 left-1 w-2 h-2 bg-primary-500 rounded-full;
}
</style>