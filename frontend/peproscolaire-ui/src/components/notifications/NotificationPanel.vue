<template>
  <div class="relative">
    <!-- Notification Bell Button -->
    <button
      @click="togglePanel"
      class="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 rounded-md"
      :class="{ 'text-blue-600': showPanel }"
    >
      <BellIcon class="h-6 w-6" />
      
      <!-- Unread count badge -->
      <span
        v-if="unreadCount > 0"
        class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center"
      >
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
      
      <!-- Pulse animation for new notifications -->
      <span
        v-if="unreadCount > 0"
        class="absolute -top-1 -right-1 bg-red-500 rounded-full h-5 w-5 animate-ping"
      ></span>
    </button>

    <!-- Notification Panel -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="showPanel"
        v-click-outside="() => showPanel = false"
        class="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 z-50"
      >
        <!-- Panel Header -->
        <div class="px-4 py-3 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">
              Notifications
            </h3>
            <div class="flex items-center space-x-2">
              <!-- Mark all as read -->
              <button
                v-if="unreadCount > 0"
                @click="markAllAsRead"
                class="text-sm text-blue-600 hover:text-blue-800"
              >
                Tout marquer comme lu
              </button>
              
              <!-- Settings -->
              <button
                @click="openSettings"
                class="p-1 text-gray-400 hover:text-gray-600 rounded-md"
              >
                <CogIcon class="h-4 w-4" />
              </button>
              
              <!-- Close -->
              <button
                @click="showPanel = false"
                class="p-1 text-gray-400 hover:text-gray-600 rounded-md"
              >
                <XMarkIcon class="h-4 w-4" />
              </button>
            </div>
          </div>
          
          <!-- Unread count -->
          <p v-if="unreadCount > 0" class="text-sm text-gray-500 mt-1">
            {{ unreadCount }} notification{{ unreadCount > 1 ? 's' : '' }} non lue{{ unreadCount > 1 ? 's' : '' }}
          </p>
        </div>

        <!-- Notifications List -->
        <div class="max-h-96 overflow-y-auto">
          <div v-if="recentNotifications.length === 0" class="px-4 py-8 text-center">
            <BellIcon class="mx-auto h-8 w-8 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">Aucune notification</h3>
            <p class="mt-1 text-sm text-gray-500">
              Vous serez notifié ici des événements importants.
            </p>
          </div>
          
          <div v-else class="divide-y divide-gray-200">
            <TransitionGroup
              name="notification"
              tag="div"
            >
              <NotificationItem
                v-for="notification in recentNotifications"
                :key="notification.id"
                :notification="notification"
                @click="handleNotificationClick"
                @mark-read="markAsRead"
                @remove="removeNotification"
              />
            </TransitionGroup>
          </div>
        </div>

        <!-- Panel Footer -->
        <div class="px-4 py-3 border-t border-gray-200 bg-gray-50">
          <div class="flex items-center justify-between">
            <router-link
              to="/notifications"
              class="text-sm text-blue-600 hover:text-blue-800"
              @click="showPanel = false"
            >
              Voir toutes les notifications
            </router-link>
            
            <button
              v-if="recentNotifications.length > 0"
              @click="clearRead"
              class="text-sm text-gray-500 hover:text-gray-700"
            >
              Effacer les lues
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notifications'
import NotificationItem from './NotificationItem.vue'
import {
  BellIcon,
  CogIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'
import type { Notification } from '@/types'

const router = useRouter()
const notificationStore = useNotificationsStore()

// State
const showPanel = ref(false)

// Computed
const unreadCount = computed(() => notificationStore.unreadCount)
const recentNotifications = computed(() => notificationStore.recentNotifications)

// Methods
const togglePanel = () => {
  showPanel.value = !showPanel.value
}

const markAllAsRead = () => {
  notificationStore.markAllAsRead()
}

const markAsRead = (id: string) => {
  notificationStore.markAsRead(id)
}

const removeNotification = (id: string) => {
  notificationStore.removeNotification(id)
}

const clearRead = () => {
  notificationStore.clearRead()
}

const handleNotificationClick = (notification: Notification) => {
  // Mark as read
  if (!notification.read) {
    markAsRead(notification.id)
  }
  
  // Navigate if link is provided
  if (notification.link) {
    router.push(notification.link)
    showPanel.value = false
  }
}

const openSettings = () => {
  router.push('/settings/notifications')
  showPanel.value = false
}

// Click outside directive
const vClickOutside = {
  mounted(el: HTMLElement, binding: any) {
    el.clickOutsideEvent = (event: Event) => {
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value()
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el: HTMLElement) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}
</script>

<style scoped>
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.notification-move {
  transition: transform 0.3s ease;
}
</style>