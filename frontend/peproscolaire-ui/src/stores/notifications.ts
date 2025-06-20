import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'

export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: Date
  read: boolean
  actionUrl?: string
  actionLabel?: string
  metadata?: Record<string, any>
}

export const useNotificationsStore = defineStore('notifications', () => {
  // State
  const notifications = ref<Notification[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // WebSocket connection for real-time notifications
  let ws: WebSocket | null = null

  // Getters
  const unreadCount = computed(() => 
    notifications.value.filter(n => !n.read).length
  )

  const unreadNotifications = computed(() => 
    notifications.value.filter(n => !n.read)
  )

  const allNotifications = computed(() => 
    [...notifications.value].sort((a, b) => 
      b.timestamp.getTime() - a.timestamp.getTime()
    )
  )

  // Actions
  async function fetchNotifications() {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.get('/notifications/')
      notifications.value = response.data.results.map((n: any) => ({
        ...n,
        timestamp: new Date(n.timestamp)
      }))
    } catch (err) {
      error.value = 'Erreur lors du chargement des notifications'
      console.error('Failed to fetch notifications:', err)
    } finally {
      loading.value = false
    }
  }

  function addNotification(notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false
    }
    
    notifications.value.unshift(newNotification)
    
    // Show browser notification if permitted
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/favicon.ico'
      })
    }
  }

  async function markAsRead(notificationId: string) {
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification) {
      notification.read = true
      
      try {
        await apiClient.patch(`/notifications/${notificationId}/`, { read: true })
      } catch (err) {
        // Revert on error
        notification.read = false
        console.error('Failed to mark notification as read:', err)
      }
    }
  }

  async function markAllAsRead() {
    const unread = notifications.value.filter(n => !n.read)
    
    // Optimistically update
    unread.forEach(n => n.read = true)
    
    try {
      await apiClient.post('/notifications/mark-all-read/')
    } catch (err) {
      // Revert on error
      unread.forEach(n => n.read = false)
      console.error('Failed to mark all as read:', err)
    }
  }

  async function deleteNotification(notificationId: string) {
    const index = notifications.value.findIndex(n => n.id === notificationId)
    if (index !== -1) {
      const [removed] = notifications.value.splice(index, 1)
      
      try {
        await apiClient.delete(`/notifications/${notificationId}/`)
      } catch (err) {
        // Restore on error
        notifications.value.splice(index, 0, removed)
        console.error('Failed to delete notification:', err)
      }
    }
  }

  function connectWebSocket() {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/notifications/'
    
    ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('WebSocket connected')
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'notification') {
        addNotification({
          type: data.notification_type || 'info',
          title: data.title,
          message: data.message,
          actionUrl: data.action_url,
          actionLabel: data.action_label,
          metadata: data.metadata
        })
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    ws.onclose = () => {
      console.log('WebSocket disconnected')
      // Reconnect after 5 seconds
      setTimeout(connectWebSocket, 5000)
    }
  }

  function disconnectWebSocket() {
    if (ws) {
      ws.close()
      ws = null
    }
  }

  // Request browser notification permission
  async function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      const permission = await Notification.requestPermission()
      return permission === 'granted'
    }
    return false
  }

  return {
    // State
    notifications,
    loading,
    error,
    // Getters
    unreadCount,
    unreadNotifications,
    allNotifications,
    // Actions
    fetchNotifications,
    addNotification,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    connectWebSocket,
    disconnectWebSocket,
    requestNotificationPermission
  }
})