import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useNotificationStore } from '../notifications'
import { createMockNotification } from '@/test/utils'

describe('Notifications Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const notificationStore = useNotificationStore()

      expect(notificationStore.notifications).toEqual([])
      expect(notificationStore.unreadCount).toBe(0)
    })
  })

  describe('Getters', () => {
    it('should compute unreadCount correctly', () => {
      const notificationStore = useNotificationStore()

      // Add some notifications
      notificationStore.addNotification(createMockNotification({ read: false }))
      notificationStore.addNotification(createMockNotification({ read: true }))
      notificationStore.addNotification(createMockNotification({ read: false }))

      expect(notificationStore.unreadCount).toBe(2)
    })

    it('should return unreadNotifications correctly', () => {
      const notificationStore = useNotificationStore()

      const unreadNotif1 = createMockNotification({ id: '1', read: false })
      const readNotif = createMockNotification({ id: '2', read: true })
      const unreadNotif2 = createMockNotification({ id: '3', read: false })

      notificationStore.addNotification(unreadNotif1)
      notificationStore.addNotification(readNotif)
      notificationStore.addNotification(unreadNotif2)

      const unreadNotifications = notificationStore.unreadNotifications
      expect(unreadNotifications).toHaveLength(2)
      expect(unreadNotifications.map(n => n.id)).toEqual(['3', '1'])
    })

    it('should return recentNotifications limited to 10', () => {
      const notificationStore = useNotificationStore()

      // Add 15 notifications
      for (let i = 0; i < 15; i++) {
        notificationStore.addNotification(
          createMockNotification({
            id: i.toString(),
            created_at: new Date(Date.now() + i * 1000).toISOString()
          })
        )
      }

      const recentNotifications = notificationStore.recentNotifications
      expect(recentNotifications).toHaveLength(10)
      
      // Should be sorted by created_at desc (most recent first)
      expect(recentNotifications[0].id).toBe('14')
      expect(recentNotifications[9].id).toBe('5')
    })

    it('should group notificationsByType correctly', () => {
      const notificationStore = useNotificationStore()

      notificationStore.addNotification(createMockNotification({ type: 'info' }))
      notificationStore.addNotification(createMockNotification({ type: 'error' }))
      notificationStore.addNotification(createMockNotification({ type: 'info' }))
      notificationStore.addNotification(createMockNotification({ type: 'success' }))

      const groupedNotifications = notificationStore.notificationsByType
      expect(groupedNotifications.info).toHaveLength(2)
      expect(groupedNotifications.error).toHaveLength(1)
      expect(groupedNotifications.success).toHaveLength(1)
    })
  })

  describe('Actions', () => {
    describe('addNotification', () => {
      it('should add notification with generated ID', () => {
        const notificationStore = useNotificationStore()

        const notification = {
          title: 'Test Notification',
          message: 'Test message',
          type: 'info' as const
        }

        const id = notificationStore.addNotification(notification)

        expect(notificationStore.notifications).toHaveLength(1)
        expect(notificationStore.notifications[0]).toMatchObject({
          title: 'Test Notification',
          message: 'Test message',
          type: 'info',
          read: false
        })
        expect(notificationStore.notifications[0].id).toBe(id)
        expect(notificationStore.notifications[0].created_at).toBeDefined()
      })

      it('should add notification with custom ID', () => {
        const notificationStore = useNotificationStore()

        const notification = {
          id: 'custom-id',
          title: 'Custom ID Notification',
          message: 'Test message',
          type: 'success' as const
        }

        const id = notificationStore.addNotification(notification)

        expect(id).toBe('custom-id')
        expect(notificationStore.notifications[0].id).toBe('custom-id')
      })

      it('should add notification to beginning of array', () => {
        const notificationStore = useNotificationStore()

        notificationStore.addNotification({ title: 'First', message: 'First', type: 'info' })
        notificationStore.addNotification({ title: 'Second', message: 'Second', type: 'info' })

        expect(notificationStore.notifications[0].title).toBe('Second')
        expect(notificationStore.notifications[1].title).toBe('First')
      })

      it('should limit notifications to maxNotifications', () => {
        const notificationStore = useNotificationStore()

        // Add 55 notifications (max is 50)
        for (let i = 0; i < 55; i++) {
          notificationStore.addNotification({
            title: `Notification ${i}`,
            message: 'Test',
            type: 'info'
          })
        }

        expect(notificationStore.notifications).toHaveLength(50)
        expect(notificationStore.notifications[0].title).toBe('Notification 54')
        expect(notificationStore.notifications[49].title).toBe('Notification 5')
      })
    })

    describe('markAsRead', () => {
      it('should mark notification as read', () => {
        const notificationStore = useNotificationStore()

        const id = notificationStore.addNotification({
          title: 'Test',
          message: 'Test',
          type: 'info'
        })

        expect(notificationStore.notifications[0].read).toBe(false)

        notificationStore.markAsRead(id)

        expect(notificationStore.notifications[0].read).toBe(true)
      })

      it('should not error if notification ID not found', () => {
        const notificationStore = useNotificationStore()

        expect(() => {
          notificationStore.markAsRead('non-existent-id')
        }).not.toThrow()
      })
    })

    describe('markAllAsRead', () => {
      it('should mark all notifications as read', () => {
        const notificationStore = useNotificationStore()

        notificationStore.addNotification({ title: '1', message: 'Test', type: 'info' })
        notificationStore.addNotification({ title: '2', message: 'Test', type: 'info' })
        notificationStore.addNotification({ title: '3', message: 'Test', type: 'info' })

        expect(notificationStore.unreadCount).toBe(3)

        notificationStore.markAllAsRead()

        expect(notificationStore.unreadCount).toBe(0)
        expect(notificationStore.notifications.every(n => n.read)).toBe(true)
      })
    })

    describe('removeNotification', () => {
      it('should remove notification by ID', () => {
        const notificationStore = useNotificationStore()

        const id1 = notificationStore.addNotification({ title: '1', message: 'Test', type: 'info' })
        const id2 = notificationStore.addNotification({ title: '2', message: 'Test', type: 'info' })

        expect(notificationStore.notifications).toHaveLength(2)

        notificationStore.removeNotification(id1)

        expect(notificationStore.notifications).toHaveLength(1)
        expect(notificationStore.notifications[0].id).toBe(id2)
      })

      it('should not error if notification ID not found', () => {
        const notificationStore = useNotificationStore()

        expect(() => {
          notificationStore.removeNotification('non-existent-id')
        }).not.toThrow()
      })
    })

    describe('clearAll', () => {
      it('should clear all notifications', () => {
        const notificationStore = useNotificationStore()

        notificationStore.addNotification({ title: '1', message: 'Test', type: 'info' })
        notificationStore.addNotification({ title: '2', message: 'Test', type: 'info' })

        expect(notificationStore.notifications).toHaveLength(2)

        notificationStore.clearAll()

        expect(notificationStore.notifications).toHaveLength(0)
      })
    })

    describe('clearRead', () => {
      it('should clear only read notifications', () => {
        const notificationStore = useNotificationStore()

        const id1 = notificationStore.addNotification({ title: '1', message: 'Test', type: 'info' })
        const id2 = notificationStore.addNotification({ title: '2', message: 'Test', type: 'info' })
        const id3 = notificationStore.addNotification({ title: '3', message: 'Test', type: 'info' })

        // Mark some as read
        notificationStore.markAsRead(id1)
        notificationStore.markAsRead(id3)

        expect(notificationStore.notifications).toHaveLength(3)
        expect(notificationStore.unreadCount).toBe(1)

        notificationStore.clearRead()

        expect(notificationStore.notifications).toHaveLength(1)
        expect(notificationStore.notifications[0].id).toBe(id2)
        expect(notificationStore.unreadCount).toBe(1)
      })
    })
  })

  describe('Utility Functions', () => {
    it('should return correct icon for notification type', () => {
      const notificationStore = useNotificationStore()

      expect(notificationStore.getNotificationIcon('success')).toBe('CheckCircleIcon')
      expect(notificationStore.getNotificationIcon('error')).toBe('XCircleIcon')
      expect(notificationStore.getNotificationIcon('warning')).toBe('ExclamationTriangleIcon')
      expect(notificationStore.getNotificationIcon('info')).toBe('InformationCircleIcon')
      expect(notificationStore.getNotificationIcon('unknown')).toBe('InformationCircleIcon')
    })

    it('should return correct color for notification type', () => {
      const notificationStore = useNotificationStore()

      expect(notificationStore.getNotificationColor('success')).toBe('green')
      expect(notificationStore.getNotificationColor('error')).toBe('red')
      expect(notificationStore.getNotificationColor('warning')).toBe('yellow')
      expect(notificationStore.getNotificationColor('info')).toBe('blue')
      expect(notificationStore.getNotificationColor('unknown')).toBe('blue')
    })
  })
})