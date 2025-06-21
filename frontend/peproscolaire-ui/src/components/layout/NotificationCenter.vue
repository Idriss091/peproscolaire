<template>
  <BaseDropdown placement="bottom-end" :width="400">
    <template #trigger>
      <button
        :class="triggerClasses"
        class="notification-trigger"
        aria-label="Notifications"
      >
        <BellIcon class="h-5 w-5" />
        
        <!-- Badge de notifications -->
        <Transition name="bounce">
          <div
            v-if="unreadCount > 0"
            class="notification-badge"
          >
            {{ unreadCount > 99 ? '99+' : unreadCount }}
          </div>
        </Transition>
      </button>
    </template>
    
    <div class="notification-panel">
      <!-- Header -->
      <div class="panel-header">
        <h3 class="panel-title">Notifications</h3>
        <div class="header-actions">
          <button
            v-if="unreadCount > 0"
            @click="markAllAsRead"
            class="action-btn"
            title="Marquer tout comme lu"
          >
            <CheckIcon class="h-4 w-4" />
          </button>
          <button
            @click="openSettings"
            class="action-btn"
            title="Paramètres"
          >
            <Cog6ToothIcon class="h-4 w-4" />
          </button>
        </div>
      </div>
      
      <!-- Filtres -->
      <div class="notification-filters">
        <button
          v-for="filter in filters"
          :key="filter.id"
          @click="activeFilter = filter.id"
          :class="[
            'filter-btn',
            { 'filter-active': activeFilter === filter.id }
          ]"
        >
          {{ filter.label }}
          <span v-if="filter.count > 0" class="filter-count">
            {{ filter.count }}
          </span>
        </button>
      </div>
      
      <!-- Liste des notifications -->
      <div class="notifications-list">
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner" />
          <span>Chargement des notifications...</span>
        </div>
        
        <div v-else-if="filteredNotifications.length === 0" class="empty-state">
          <BellSlashIcon class="h-12 w-12 text-gray-400" />
          <p class="empty-text">Aucune notification</p>
          <p class="empty-subtitle">
            {{ activeFilter === 'unread' ? 'Toutes vos notifications sont lues' : 'Vous êtes à jour !' }}
          </p>
        </div>
        
        <div v-else class="notifications-container">
          <NotificationItem
            v-for="notification in filteredNotifications"
            :key="notification.id"
            :notification="notification"
            @click="handleNotificationClick"
            @mark-read="markAsRead"
            @mark-unread="markAsUnread"
            @archive="archiveNotification"
            @delete="deleteNotification"
          />
        </div>
      </div>
      
      <!-- Footer -->
      <div class="panel-footer">
        <router-link to="/notifications" class="view-all-link">
          Voir toutes les notifications
          <ArrowRightIcon class="h-4 w-4" />
        </router-link>
      </div>
    </div>
  </BaseDropdown>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  BellIcon,
  BellSlashIcon,
  CheckIcon,
  Cog6ToothIcon,
  ArrowRightIcon
} from '@heroicons/vue/24/outline'
import BaseDropdown from '@/components/ui/BaseDropdown.vue'
import NotificationItem from './NotificationItem.vue'
import { useNotificationsStore } from '@/stores/notifications'
import type { Notification } from '@/types/notifications'

const notificationsStore = useNotificationsStore()

const activeFilter = ref('all')
const isLoading = ref(false)

const filters = computed(() => [
  {
    id: 'all',
    label: 'Toutes',
    count: notificationsStore.notifications.length
  },
  {
    id: 'unread',
    label: 'Non lues',
    count: notificationsStore.unreadCount
  },
  {
    id: 'important',
    label: 'Importantes',
    count: notificationsStore.notifications.filter(n => n.priority === 'high').length
  }
])

const unreadCount = computed(() => notificationsStore.unreadCount)

const triggerClasses = computed(() => [
  'notification-trigger',
  {
    'trigger-has-notifications': unreadCount.value > 0
  }
])

const filteredNotifications = computed(() => {
  let notifications = notificationsStore.notifications
  
  switch (activeFilter.value) {
    case 'unread':
      notifications = notifications.filter(n => !n.read)
      break
    case 'important':
      notifications = notifications.filter(n => n.priority === 'high')
      break
  }
  
  return notifications.slice(0, 10) // Limiter à 10 pour le dropdown
})

// Méthodes
const markAllAsRead = async () => {
  try {
    await notificationsStore.markAllAsRead()
  } catch (error) {
    console.error('Erreur marquage notifications:', error)
  }
}

const markAsRead = async (notificationId: string) => {
  try {
    await notificationsStore.markAsRead(notificationId)
  } catch (error) {
    console.error('Erreur marquage lecture:', error)
  }
}

const markAsUnread = async (notificationId: string) => {
  try {
    await notificationsStore.markAsUnread(notificationId)
  } catch (error) {
    console.error('Erreur marquage non lu:', error)
  }
}

const archiveNotification = async (notificationId: string) => {
  try {
    await notificationsStore.archiveNotification(notificationId)
  } catch (error) {
    console.error('Erreur archivage:', error)
  }
}

const deleteNotification = async (notificationId: string) => {
  try {
    await notificationsStore.deleteNotification(notificationId)
  } catch (error) {
    console.error('Erreur suppression:', error)
  }
}

const handleNotificationClick = async (notification: Notification) => {
  // Marquer comme lu si pas déjà lu
  if (!notification.read) {
    await markAsRead(notification.id)
  }
  
  // Naviguer vers l'action si définie
  if (notification.action_url) {
    window.location.href = notification.action_url
  }
}

const openSettings = () => {
  // TODO: Ouvrir les paramètres de notifications
  console.log('Ouvrir paramètres notifications')
}

// Lifecycle
onMounted(async () => {
  if (notificationsStore.notifications.length === 0) {
    isLoading.value = true
    try {
      await notificationsStore.loadNotifications()
    } catch (error) {
      console.error('Erreur chargement notifications:', error)
    } finally {
      isLoading.value = false
    }
  }
})
</script>

<style scoped>
.notification-trigger {
  @apply relative w-10 h-10 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-600 hover:text-gray-900 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.trigger-has-notifications {
  @apply text-blue-600 hover:text-blue-700;
}

.notification-badge {
  @apply absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full min-w-[1.25rem] h-5 flex items-center justify-center px-1;
}

.notification-panel {
  @apply flex flex-col max-h-96;
}

.panel-header {
  @apply flex items-center justify-between p-4 border-b border-gray-200;
}

.panel-title {
  @apply font-semibold text-gray-900;
}

.header-actions {
  @apply flex items-center gap-2;
}

.action-btn {
  @apply w-8 h-8 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500 hover:text-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.notification-filters {
  @apply flex p-3 border-b border-gray-200 bg-gray-50;
}

.filter-btn {
  @apply flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-lg hover:bg-white transition-colors;
}

.filter-active {
  @apply bg-white text-blue-700 shadow-sm;
}

.filter-count {
  @apply px-1.5 py-0.5 text-xs font-semibold bg-gray-200 text-gray-600 rounded-full;
}

.filter-active .filter-count {
  @apply bg-primary-100 text-blue-700;
}

.notifications-list {
  @apply flex-1 overflow-hidden;
}

.loading-state {
  @apply flex items-center gap-3 p-4 text-gray-600;
}

.loading-spinner {
  @apply w-5 h-5 border-2 border-gray-300 border-t-primary-600 rounded-full animate-spin;
}

.empty-state {
  @apply flex flex-col items-center justify-center p-8 text-center;
}

.empty-text {
  @apply text-gray-900 font-medium mt-3;
}

.empty-subtitle {
  @apply text-gray-600 text-sm mt-1;
}

.notifications-container {
  @apply overflow-y-auto;
}

.panel-footer {
  @apply p-3 border-t border-gray-200 bg-gray-50;
}

.view-all-link {
  @apply inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors;
}

/* Transitions */
.bounce-enter-active {
  animation: bounce 0.5s ease;
}

@keyframes bounce {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}
</style>