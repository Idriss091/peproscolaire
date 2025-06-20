import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import { setActivePinia, createPinia } from 'pinia'
import { renderWithProviders, createMockNotification } from '@/test/utils'
import NotificationPanel from '../NotificationPanel.vue'
import { useNotificationStore } from '@/stores/notifications'

// Mock the router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  })
}))

describe('NotificationPanel', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('renders notification bell with unread count', () => {
    const notificationStore = useNotificationStore()
    notificationStore.addNotification(createMockNotification({ read: false }))
    notificationStore.addNotification(createMockNotification({ read: false }))
    notificationStore.addNotification(createMockNotification({ read: true }))

    renderWithProviders(NotificationPanel)

    const bellButton = screen.getByRole('button')
    expect(bellButton).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument() // Unread count
  })

  it('shows 99+ when unread count exceeds 99', () => {
    const notificationStore = useNotificationStore()
    
    // Add 105 unread notifications
    for (let i = 0; i < 105; i++) {
      notificationStore.addNotification(createMockNotification({ 
        id: i.toString(),
        read: false 
      }))
    }

    renderWithProviders(NotificationPanel)

    expect(screen.getByText('99+')).toBeInTheDocument()
  })

  it('opens and closes notification panel', async () => {
    const user = userEvent.setup()
    renderWithProviders(NotificationPanel)

    const bellButton = screen.getByRole('button')
    
    // Panel should be closed initially
    expect(screen.queryByText('Notifications')).not.toBeInTheDocument()

    // Open panel
    await user.click(bellButton)
    expect(screen.getByText('Notifications')).toBeInTheDocument()

    // Close panel with close button
    const closeButton = screen.getByRole('button', { name: /close/i })
    await user.click(closeButton)
    expect(screen.queryByText('Notifications')).not.toBeInTheDocument()
  })

  it('displays recent notifications', async () => {
    const user = userEvent.setup()
    const notificationStore = useNotificationStore()
    
    notificationStore.addNotification(createMockNotification({
      id: '1',
      title: 'Test Notification 1',
      message: 'First notification',
      read: false
    }))
    
    notificationStore.addNotification(createMockNotification({
      id: '2',
      title: 'Test Notification 2',
      message: 'Second notification',
      read: true
    }))

    renderWithProviders(NotificationPanel)

    // Open panel
    await user.click(screen.getByRole('button'))

    expect(screen.getByText('Test Notification 1')).toBeInTheDocument()
    expect(screen.getByText('Test Notification 2')).toBeInTheDocument()
  })

  it('shows empty state when no notifications', async () => {
    const user = userEvent.setup()
    renderWithProviders(NotificationPanel)

    await user.click(screen.getByRole('button'))

    expect(screen.getByText('Aucune notification')).toBeInTheDocument()
    expect(screen.getByText('Vous serez notifié ici des événements importants.')).toBeInTheDocument()
  })

  it('marks all notifications as read', async () => {
    const user = userEvent.setup()
    const notificationStore = useNotificationStore()
    
    notificationStore.addNotification(createMockNotification({ read: false }))
    notificationStore.addNotification(createMockNotification({ read: false }))

    expect(notificationStore.unreadCount).toBe(2)

    renderWithProviders(NotificationPanel)

    await user.click(screen.getByRole('button'))
    
    const markAllButton = screen.getByText('Tout marquer comme lu')
    await user.click(markAllButton)

    expect(notificationStore.unreadCount).toBe(0)
  })

  it('does not show mark all as read when no unread notifications', async () => {
    const user = userEvent.setup()
    const notificationStore = useNotificationStore()
    
    notificationStore.addNotification(createMockNotification({ read: true }))

    renderWithProviders(NotificationPanel)

    await user.click(screen.getByRole('button'))
    
    expect(screen.queryByText('Tout marquer comme lu')).not.toBeInTheDocument()
  })

  it('navigates to settings when clicking settings button', async () => {
    const user = userEvent.setup()
    renderWithProviders(NotificationPanel)

    await user.click(screen.getByRole('button'))
    
    const settingsButton = screen.getByRole('button', { name: /settings/i })
    await user.click(settingsButton)

    expect(mockPush).toHaveBeenCalledWith('/settings/notifications')
  })

  it('navigates to full notifications page', async () => {
    const user = userEvent.setup()
    renderWithProviders(NotificationPanel)

    await user.click(screen.getByRole('button'))
    
    const viewAllLink = screen.getByText('Voir toutes les notifications')
    await user.click(viewAllLink)

    expect(mockPush).toHaveBeenCalledWith('/notifications')
  })

  it('clears read notifications', async () => {
    const user = userEvent.setup()
    const notificationStore = useNotificationStore()
    
    const id1 = notificationStore.addNotification(createMockNotification({ read: false }))
    const id2 = notificationStore.addNotification(createMockNotification({ read: true }))
    
    notificationStore.markAsRead(id1)
    
    expect(notificationStore.notifications).toHaveLength(2)

    renderWithProviders(NotificationPanel)

    await user.click(screen.getByRole('button'))
    
    const clearButton = screen.getByText('Effacer les lues')
    await user.click(clearButton)

    expect(notificationStore.notifications).toHaveLength(0)
  })

  it('handles notification click with navigation', async () => {
    const user = userEvent.setup()
    const notificationStore = useNotificationStore()
    
    notificationStore.addNotification(createMockNotification({
      id: '1',
      title: 'Clickable Notification',
      read: false,
      link: '/test-route'
    }))

    renderWithProviders(NotificationPanel)

    await user.click(screen.getByRole('button'))
    
    const notificationItem = screen.getByText('Clickable Notification')
    await user.click(notificationItem)

    expect(mockPush).toHaveBeenCalledWith('/test-route')
    
    // Should mark as read when clicked
    const notification = notificationStore.notifications.find(n => n.id === '1')
    expect(notification?.read).toBe(true)
  })

  it('closes panel when clicking outside', async () => {
    const user = userEvent.setup()
    renderWithProviders(NotificationPanel)

    // Open panel
    await user.click(screen.getByRole('button'))
    expect(screen.getByText('Notifications')).toBeInTheDocument()

    // Click outside (on document body)
    await user.click(document.body)
    expect(screen.queryByText('Notifications')).not.toBeInTheDocument()
  })

  it('shows correct unread count in header', async () => {
    const user = userEvent.setup()
    const notificationStore = useNotificationStore()
    
    notificationStore.addNotification(createMockNotification({ read: false }))
    notificationStore.addNotification(createMockNotification({ read: false }))
    notificationStore.addNotification(createMockNotification({ read: true }))

    renderWithProviders(NotificationPanel)

    await user.click(screen.getByRole('button'))
    
    expect(screen.getByText('2 notifications non lues')).toBeInTheDocument()
  })

  it('handles pulse animation for new notifications', () => {
    const notificationStore = useNotificationStore()
    notificationStore.addNotification(createMockNotification({ read: false }))

    renderWithProviders(NotificationPanel)

    const pulseElement = document.querySelector('.animate-ping')
    expect(pulseElement).toBeInTheDocument()
  })

  it('applies correct CSS classes based on panel state', async () => {
    const user = userEvent.setup()
    renderWithProviders(NotificationPanel)

    const bellButton = screen.getByRole('button')
    
    // Initially should not have active state
    expect(bellButton).toHaveClass('text-gray-600')

    // Should have active state when panel is open
    await user.click(bellButton)
    expect(bellButton).toHaveClass('text-primary-600')
  })
})