import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import { useRiskDetectionStore } from '@/stores/risk-detection'
import { toast } from 'vue-sonner'

export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
  id?: string
}

export interface ConnectionStatus {
  connected: boolean
  reconnecting: boolean
  error: string | null
  lastConnected: Date | null
  reconnectAttempts: number
}

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectTimer: number | null = null
  private heartbeatTimer: number | null = null
  private maxReconnectAttempts = 5
  private reconnectInterval = 5000 // 5 seconds
  private heartbeatInterval = 30000 // 30 seconds
  
  public status = reactive<ConnectionStatus>({
    connected: false,
    reconnecting: false,
    error: null,
    lastConnected: null,
    reconnectAttempts: 0
  })

  private messageHandlers = new Map<string, Array<(data: any) => void>>()
  private messageQueue: WebSocketMessage[] = []

  constructor() {
    // Defer initialization until Pinia is ready
  }

  public initialize() {
    // Initialize auth watcher after Pinia is ready
    this.setupAuthWatcher()
  }

  private setupAuthWatcher() {
    // Watch for authentication changes
    const authStore = useAuthStore()
    if (authStore.isAuthenticated && authStore.token) {
      this.connect()
    }
  }

  public connect(token?: string): void {
    const authStore = useAuthStore()
    const wsToken = token || authStore.token

    if (!wsToken) {
      console.warn('No token available for WebSocket connection')
      return
    }

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected')
      return
    }

    try {
      // Construct WebSocket URL
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsHost = import.meta.env.VITE_WS_HOST || window.location.host
      const wsUrl = `${wsProtocol}//${wsHost}/ws/notifications/?token=${wsToken}`

      console.log('Connecting to WebSocket:', wsUrl.replace(wsToken, '***'))

      this.ws = new WebSocket(wsUrl)
      this.setupEventHandlers()
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      this.handleError('Connection failed')
    }
  }

  private setupEventHandlers(): void {
    if (!this.ws) return

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.status.connected = true
      this.status.reconnecting = false
      this.status.error = null
      this.status.lastConnected = new Date()
      this.status.reconnectAttempts = 0

      // Send queued messages
      this.flushMessageQueue()
      
      // Start heartbeat
      this.startHeartbeat()

      // Notify UI
      toast.success('Connexion temps réel établie')
    }

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data)
        this.handleMessage(message)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    this.ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason)
      this.status.connected = false
      this.stopHeartbeat()

      if (event.code !== 1000) { // Not a normal closure
        this.handleDisconnection()
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.handleError('Connection error')
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    console.log('Received WebSocket message:', message.type)

    // Handle different message types
    switch (message.type) {
      case 'notification':
        this.handleNotification(message.data)
        break
      case 'alert_created':
        this.handleAlertCreated(message.data)
        break
      case 'alert_updated':
        this.handleAlertUpdated(message.data)
        break
      case 'risk_profile_updated':
        this.handleRiskProfileUpdated(message.data)
        break
      case 'intervention_plan_updated':
        this.handleInterventionPlanUpdated(message.data)
        break
      case 'system_announcement':
        this.handleSystemAnnouncement(message.data)
        break
      case 'heartbeat':
        // Respond to heartbeat
        this.send({ type: 'heartbeat_response', data: {}, timestamp: new Date().toISOString() })
        break
      default:
        console.warn('Unknown message type:', message.type)
    }

    // Call registered handlers
    const handlers = this.messageHandlers.get(message.type) || []
    handlers.forEach(handler => {
      try {
        handler(message.data)
      } catch (error) {
        console.error('Error in message handler:', error)
      }
    })
  }

  private handleNotification(data: any): void {
    const notificationStore = useNotificationsStore()
    notificationStore.addNotification({
      id: data.id || Date.now().toString(),
      title: data.title,
      message: data.message,
      type: data.type || 'info',
      read: false,
      created_at: data.timestamp || new Date().toISOString(),
      link: data.link
    })

    // Show toast notification
    switch (data.type) {
      case 'error':
        toast.error(data.title, { description: data.message })
        break
      case 'warning':
        toast.warning(data.title, { description: data.message })
        break
      case 'success':
        toast.success(data.title, { description: data.message })
        break
      default:
        toast(data.title, { description: data.message })
    }
  }

  private handleAlertCreated(data: any): void {
    const riskStore = useRiskDetectionStore()
    
    // Add alert to store
    riskStore.alerts.unshift(data.alert)
    
    // Show urgent notification for high priority alerts
    if (['urgent', 'high'].includes(data.alert.priority)) {
      toast.error('Nouvelle alerte urgente', {
        description: `${data.alert.title} - ${data.alert.risk_profile.student.first_name} ${data.alert.risk_profile.student.last_name}`,
        duration: 10000
      })
    }
  }

  private handleAlertUpdated(data: any): void {
    const riskStore = useRiskDetectionStore()
    
    // Update alert in store
    const index = riskStore.alerts.findIndex(a => a.id === data.alert.id)
    if (index !== -1) {
      riskStore.alerts[index] = data.alert
    }
  }

  private handleRiskProfileUpdated(data: any): void {
    const riskStore = useRiskDetectionStore()
    
    // Update risk profile in store
    const index = riskStore.riskProfiles.findIndex(p => p.id === data.profile.id)
    if (index !== -1) {
      riskStore.riskProfiles[index] = data.profile
    }

    // Show notification for significant risk changes
    if (data.risk_change && data.risk_change.significant) {
      toast.warning('Évolution du risque détectée', {
        description: `${data.profile.student.first_name} ${data.profile.student.last_name}: ${data.risk_change.message}`
      })
    }
  }

  private handleInterventionPlanUpdated(data: any): void {
    const riskStore = useRiskDetectionStore()
    
    // Update intervention plan in store
    const index = riskStore.interventionPlans.findIndex(p => p.id === data.plan.id)
    if (index !== -1) {
      riskStore.interventionPlans[index] = data.plan
    }
  }

  private handleSystemAnnouncement(data: any): void {
    toast.info('Annonce système', {
      description: data.message,
      duration: 15000
    })
  }

  private handleDisconnection(): void {
    if (this.status.reconnectAttempts < this.maxReconnectAttempts) {
      this.status.reconnecting = true
      this.status.reconnectAttempts++
      
      console.log(`Attempting to reconnect (${this.status.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      this.reconnectTimer = window.setTimeout(() => {
        this.connect()
      }, this.reconnectInterval * this.status.reconnectAttempts) // Exponential backoff
    } else {
      this.handleError('Max reconnection attempts reached')
      toast.error('Connexion temps réel perdue', {
        description: 'Impossible de rétablir la connexion automatiquement'
      })
    }
  }

  private handleError(error: string): void {
    this.status.error = error
    this.status.connected = false
    this.status.reconnecting = false
    console.error('WebSocket error:', error)
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = window.setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({
          type: 'heartbeat',
          data: {},
          timestamp: new Date().toISOString()
        })
      }
    }, this.heartbeatInterval)
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift()
      if (message) {
        this.send(message)
      }
    }
  }

  public send(message: WebSocketMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      // Queue message for later
      this.messageQueue.push(message)
      console.warn('WebSocket not connected, message queued')
    }
  }

  public subscribe(messageType: string, handler: (data: any) => void): () => void {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, [])
    }
    
    const handlers = this.messageHandlers.get(messageType)!
    handlers.push(handler)

    // Return unsubscribe function
    return () => {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  public disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    
    this.stopHeartbeat()
    
    if (this.ws) {
      this.ws.close(1000, 'User disconnected')
      this.ws = null
    }
    
    this.status.connected = false
    this.status.reconnecting = false
    this.messageQueue.length = 0
  }

  public reconnect(): void {
    this.disconnect()
    this.status.reconnectAttempts = 0
    this.connect()
  }
}

// Create singleton instance
export const webSocketService = new WebSocketService()

// Vue composable for easier use in components
export function useWebSocket() {
  return {
    status: webSocketService.status,
    connect: webSocketService.connect.bind(webSocketService),
    disconnect: webSocketService.disconnect.bind(webSocketService),
    reconnect: webSocketService.reconnect.bind(webSocketService),
    send: webSocketService.send.bind(webSocketService),
    subscribe: webSocketService.subscribe.bind(webSocketService)
  }
}