import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { webSocketService, useWebSocket } from '../websocket'

// Mock dependencies
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    isAuthenticated: true,
    token: 'test-token'
  }))
}))

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: vi.fn(() => ({
    addNotification: vi.fn()
  }))
}))

vi.mock('@/stores/risk-detection', () => ({
  useRiskDetectionStore: vi.fn(() => ({
    alerts: [],
    riskProfiles: [],
    interventionPlans: []
  }))
}))

vi.mock('vue-sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  }
}))

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  readyState = MockWebSocket.CONNECTING
  onopen: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null

  constructor(public url: string) {
    // Simulate connection opening
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN
      if (this.onopen) {
        this.onopen(new Event('open'))
      }
    }, 10)
  }

  send = vi.fn()
  close = vi.fn((code?: number, reason?: string) => {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close', { code: code || 1000, reason }))
    }
  })

  // Helper methods for testing
  simulateMessage(data: any) {
    if (this.onmessage) {
      this.onmessage(new MessageEvent('message', { data: JSON.stringify(data) }))
    }
  }

  simulateError() {
    if (this.onerror) {
      this.onerror(new Event('error'))
    }
  }

  simulateClose(code = 1000, reason = '') {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close', { code, reason }))
    }
  }
}

global.WebSocket = MockWebSocket as any

describe.skip('WebSocket Service', () => {
  let wsService: typeof webSocketService
  let mockWS: MockWebSocket

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    
    // Use the singleton instance
    wsService = webSocketService
    
    // Clear any existing status
    wsService.status.connected = false
    wsService.status.reconnecting = false
    wsService.status.error = null
    wsService.status.reconnectAttempts = 0
  })

  afterEach(() => {
    vi.useRealTimers()
    if (wsService) {
      wsService.disconnect()
    }
  })

  describe('Connection Management', () => {
    it('should connect to WebSocket server', async () => {
      wsService.connect('test-token')

      // Fast-forward timers to simulate connection
      vi.advanceTimersByTime(50)

      expect(wsService.status.connected).toBe(true)
      expect(wsService.status.error).toBeNull()
    })

    it('should handle connection error', () => {
      wsService.connect('test-token')
      
      // Get the mock WebSocket instance
      const ws = (global.WebSocket as any).mock.instances[0]
      ws.simulateError()

      expect(wsService.status.connected).toBe(false)
      expect(wsService.status.error).toBe('Connection error')
    })

    it('should disconnect properly', () => {
      wsService.connect('test-token')
      vi.advanceTimersByTime(50)

      expect(wsService.status.connected).toBe(true)

      wsService.disconnect()

      expect(wsService.status.connected).toBe(false)
    })

    it('should not connect if already connected', () => {
      wsService.connect('test-token')
      vi.advanceTimersByTime(50)

      const firstConnection = (global.WebSocket as any).mock.instances.length

      // Try to connect again
      wsService.connect('test-token')

      expect((global.WebSocket as any).mock.instances.length).toBe(firstConnection)
    })
  })

  describe('Reconnection Logic', () => {
    it('should attempt to reconnect on unexpected disconnect', () => {
      wsService.connect('test-token')
      vi.advanceTimersByTime(50)

      const ws = (global.WebSocket as any).mock.instances[0]
      
      // Simulate unexpected disconnect
      ws.simulateClose(1006, 'Connection lost')

      expect(wsService.status.reconnecting).toBe(true)
      expect(wsService.status.reconnectAttempts).toBe(1)

      // Fast-forward to trigger reconnection
      vi.advanceTimersByTime(5000)

      expect((global.WebSocket as any).mock.instances.length).toBe(2)
    })

    it('should stop reconnecting after max attempts', () => {
      wsService.connect('test-token')
      vi.advanceTimersByTime(50)

      const ws = (global.WebSocket as any).mock.instances[0]

      // Simulate multiple failed reconnections
      for (let i = 0; i < 5; i++) {
        ws.simulateClose(1006, 'Connection lost')
        vi.advanceTimersByTime(5000 * (i + 1))
      }

      expect(wsService.status.reconnectAttempts).toBe(5)
      expect(wsService.status.error).toBe('Max reconnection attempts reached')
    })

    it('should reset reconnect attempts on successful connection', () => {
      wsService.connect('test-token')
      vi.advanceTimersByTime(50)

      wsService.status.reconnectAttempts = 3

      const ws = (global.WebSocket as any).mock.instances[0]
      ws.simulateMessage({ type: 'heartbeat', data: {}, timestamp: new Date().toISOString() })

      // Simulate successful reconnection
      wsService.status.connected = true

      expect(wsService.status.reconnectAttempts).toBe(0)
    })
  })

  describe('Message Handling', () => {
    beforeEach(() => {
      wsService.connect('test-token')
      vi.advanceTimersByTime(50)
    })

    it('should handle notification messages', () => {
      const ws = (global.WebSocket as any).mock.instances[0]
      // const { toast } = require('vue-sonner')

      const notificationData = {
        type: 'notification',
        data: {
          title: 'Test Notification',
          message: 'Test message',
          type: 'info'
        },
        timestamp: new Date().toISOString()
      }

      ws.simulateMessage(notificationData)

      expect(toast.info).toHaveBeenCalledWith(
        'Test Notification',
        { description: 'Test message' }
      )
    })

    it('should handle alert created messages', () => {
      const ws = (global.WebSocket as any).mock.instances[0]
      // const { toast } = require('vue-sonner')

      const alertData = {
        type: 'alert_created',
        data: {
          alert: {
            id: '1',
            title: 'Urgent Alert',
            priority: 'urgent',
            risk_profile: {
              student: {
                first_name: 'John',
                last_name: 'Doe'
              }
            }
          }
        },
        timestamp: new Date().toISOString()
      }

      ws.simulateMessage(alertData)

      expect(toast.error).toHaveBeenCalledWith(
        'Nouvelle alerte urgente',
        {
          description: 'Urgent Alert - John Doe',
          duration: 10000
        }
      )
    })

    it('should handle heartbeat messages', () => {
      const ws = (global.WebSocket as any).mock.instances[0]

      const heartbeatData = {
        type: 'heartbeat',
        data: {},
        timestamp: new Date().toISOString()
      }

      ws.simulateMessage(heartbeatData)

      expect(ws.send).toHaveBeenCalledWith(
        JSON.stringify({
          type: 'heartbeat_response',
          data: {},
          timestamp: expect.any(String)
        })
      )
    })

    it('should call registered message handlers', () => {
      const handler = vi.fn()
      const unsubscribe = wsService.subscribe('test_message', handler)

      const ws = (global.WebSocket as any).mock.instances[0]
      const testData = {
        type: 'test_message',
        data: { test: 'data' },
        timestamp: new Date().toISOString()
      }

      ws.simulateMessage(testData)

      expect(handler).toHaveBeenCalledWith({ test: 'data' })

      // Test unsubscribe
      unsubscribe()
      ws.simulateMessage(testData)

      expect(handler).toHaveBeenCalledTimes(1)
    })

    it('should handle invalid JSON messages gracefully', () => {
      const ws = (global.WebSocket as any).mock.instances[0]
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      // Simulate invalid JSON
      if (ws.onmessage) {
        ws.onmessage(new MessageEvent('message', { data: 'invalid json' }))
      }

      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to parse WebSocket message:',
        expect.any(Error)
      )

      consoleSpy.mockRestore()
    })
  })

  describe('Message Sending', () => {
    beforeEach(() => {
      wsService.connect('test-token')
      vi.advanceTimersByTime(50)
    })

    it('should send messages when connected', () => {
      const ws = (global.WebSocket as any).mock.instances[0]
      
      const message = {
        type: 'test',
        data: { test: 'data' },
        timestamp: new Date().toISOString()
      }

      wsService.send(message)

      expect(ws.send).toHaveBeenCalledWith(JSON.stringify(message))
    })

    it('should queue messages when not connected', () => {
      wsService.disconnect()

      const message = {
        type: 'test',
        data: { test: 'data' },
        timestamp: new Date().toISOString()
      }

      wsService.send(message)

      // Reconnect and check if queued message is sent
      wsService.connect('test-token')
      vi.advanceTimersByTime(50)

      const ws = (global.WebSocket as any).mock.instances[1]
      expect(ws.send).toHaveBeenCalledWith(JSON.stringify(message))
    })
  })

  describe('Heartbeat Mechanism', () => {
    beforeEach(() => {
      wsService.connect('test-token')
      vi.advanceTimersByTime(50)
    })

    it('should send heartbeat messages periodically', () => {
      const ws = (global.WebSocket as any).mock.instances[0]

      // Fast-forward 30 seconds (heartbeat interval)
      vi.advanceTimersByTime(30000)

      expect(ws.send).toHaveBeenCalledWith(
        JSON.stringify({
          type: 'heartbeat',
          data: {},
          timestamp: expect.any(String)
        })
      )
    })

    it('should stop heartbeat on disconnect', () => {
      const ws = (global.WebSocket as any).mock.instances[0]

      wsService.disconnect()

      // Fast-forward and ensure no heartbeat is sent
      vi.advanceTimersByTime(30000)

      expect(ws.send).not.toHaveBeenCalled()
    })
  })

  describe('Event Subscription', () => {
    it('should allow subscribing to specific message types', () => {
      const handler1 = vi.fn()
      const handler2 = vi.fn()

      wsService.subscribe('test_event', handler1)
      wsService.subscribe('test_event', handler2)
      wsService.subscribe('other_event', vi.fn())

      wsService.connect('test-token')
      vi.advanceTimersByTime(50)

      const ws = (global.WebSocket as any).mock.instances[0]
      ws.simulateMessage({
        type: 'test_event',
        data: { test: 'data' },
        timestamp: new Date().toISOString()
      })

      expect(handler1).toHaveBeenCalledWith({ test: 'data' })
      expect(handler2).toHaveBeenCalledWith({ test: 'data' })
    })

    it('should return unsubscribe function', () => {
      const handler = vi.fn()
      const unsubscribe = wsService.subscribe('test_event', handler)

      wsService.connect('test-token')
      vi.advanceTimersByTime(50)

      const ws = (global.WebSocket as any).mock.instances[0]

      // Send message before unsubscribe
      ws.simulateMessage({
        type: 'test_event',
        data: { test: 'data' },
        timestamp: new Date().toISOString()
      })

      expect(handler).toHaveBeenCalledTimes(1)

      // Unsubscribe and send another message
      unsubscribe()

      ws.simulateMessage({
        type: 'test_event',
        data: { test: 'data2' },
        timestamp: new Date().toISOString()
      })

      expect(handler).toHaveBeenCalledTimes(1)
    })
  })
})