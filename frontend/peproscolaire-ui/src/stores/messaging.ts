import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import type { 
  Message, 
  MessageRecipient,
  MessageAttachment,
  PaginatedResponse,
  User
} from '@/types'

interface MessageFilters {
  folder?: 'inbox' | 'sent' | 'draft' | 'trash' | 'archive'
  isRead?: boolean
  isStarred?: boolean
  priority?: 'low' | 'normal' | 'high'
  sender?: number
  recipient?: number
  search?: string
  startDate?: string
  endDate?: string
  hasAttachments?: boolean
  limit?: number
}

interface MessageGroup {
  id: number
  name: string
  description?: string
  members: number[]
  is_dynamic: boolean
  query?: string
}

interface MessageTemplate {
  id: number
  name: string
  subject: string
  body: string
  category: string
}

export const useMessagingStore = defineStore('messaging', () => {
  // State
  const messages = ref<Message[]>([])
  const currentMessage = ref<Message | null>(null)
  const messageGroups = ref<MessageGroup[]>([])
  const messageTemplates = ref<MessageTemplate[]>([])
  const draftMessage = ref<Partial<Message> | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const currentFilters = ref<MessageFilters>({ folder: 'inbox' })
  const totalCount = ref(0)

  // Getters
  const unreadCount = computed(() => 
    messages.value.filter(m => {
      if (!m.recipients) return false
      const recipient = m.recipients.find(r => r.recipient === currentUserId.value)
      return recipient && !recipient.is_read
    }).length
  )

  const starredMessages = computed(() =>
    messages.value.filter(m => {
      if (!m.recipients) return false
      const recipient = m.recipients.find(r => r.recipient === currentUserId.value)
      return recipient && recipient.is_starred
    })
  )

  const messagesByFolder = computed(() => {
    const grouped: Record<string, Message[]> = {
      inbox: [],
      sent: [],
      draft: [],
      trash: [],
      archive: []
    }

    messages.value.forEach(message => {
      if (message.is_draft) {
        grouped.draft.push(message)
      } else if (message.sender === currentUserId.value) {
        grouped.sent.push(message)
      } else if (message.recipients) {
        const recipient = message.recipients.find(r => r.recipient === currentUserId.value)
        if (recipient) {
          grouped[recipient.folder].push(message)
        }
      }
    })

    return grouped
  })

  // Current user ID (should come from auth store)
  const currentUserId = computed(() => {
    // TODO: Get from auth store
    return 1
  })

  // Actions
  async function fetchMessages(filters: MessageFilters = {}) {
    loading.value = true
    error.value = null
    currentFilters.value = { ...currentFilters.value, ...filters }

    try {
      const params = new URLSearchParams()
      
      if (filters.folder) params.append('folder', filters.folder)
      if (filters.isRead !== undefined) params.append('is_read', filters.isRead.toString())
      if (filters.isStarred !== undefined) params.append('is_starred', filters.isStarred.toString())
      if (filters.priority) params.append('priority', filters.priority)
      if (filters.sender) params.append('sender', filters.sender.toString())
      if (filters.recipient) params.append('recipient', filters.recipient.toString())
      if (filters.search) params.append('search', filters.search)
      if (filters.startDate) params.append('start_date', filters.startDate)
      if (filters.endDate) params.append('end_date', filters.endDate)
      if (filters.hasAttachments !== undefined) params.append('has_attachments', filters.hasAttachments.toString())
      if (filters.limit) params.append('limit', filters.limit.toString())

      const response = await apiClient.get<{ results: any[] }>(
        `/messaging/messages/?${params.toString()}`
      )
      
      messages.value = response.data.results
      totalCount.value = response.data.results?.length || 0
    } catch (err) {
      error.value = 'Erreur lors du chargement des messages'
      console.error('Failed to fetch messages:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchMessage(id: number) {
    try {
      const response = await apiClient.get<Message>(`/messaging/messages/${id}/`)
      currentMessage.value = response.data
      
      // Mark as read automatically
      await markAsRead(id)
      
      return response.data
    } catch (err) {
      error.value = 'Erreur lors du chargement du message'
      throw err
    }
  }

  async function sendMessage(data: {
    recipients: number[]
    recipientGroups?: number[]
    subject: string
    body: string
    priority?: 'low' | 'normal' | 'high'
    attachments?: File[]
    replyTo?: number
  }) {
    loading.value = true
    error.value = null

    try {
      const formData = new FormData()
      
      // Add recipients
      data.recipients.forEach(r => formData.append('recipients', r.toString()))
      if (data.recipientGroups) {
        data.recipientGroups.forEach(g => formData.append('recipient_groups', g.toString()))
      }
      
      // Add message data
      formData.append('subject', data.subject)
      formData.append('body', data.body)
      formData.append('priority', data.priority || 'normal')
      
      if (data.replyTo) {
        formData.append('thread', data.replyTo.toString())
      }

      // Add attachments
      if (data.attachments) {
        data.attachments.forEach((file, index) => {
          formData.append(`attachment_${index}`, file)
        })
      }

      const response = await apiClient.post<Message>(
        '/messaging/messages/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      
      messages.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de l\'envoi du message'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function saveDraft(data: Partial<Message>) {
    try {
      const response = await apiClient.post<Message>(
        '/messaging/messages/draft/',
        { ...data, is_draft: true }
      )
      
      draftMessage.value = null
      messages.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de l\'enregistrement du brouillon'
      throw err
    }
  }

  async function updateDraft(id: number, data: Partial<Message>) {
    try {
      const response = await apiClient.patch<Message>(
        `/messaging/messages/${id}/`,
        data
      )
      
      const index = messages.value.findIndex(m => m.id === id)
      if (index !== -1) {
        messages.value[index] = response.data
      }
      
      return response.data
    } catch (err) {
      error.value = 'Erreur lors de la mise à jour du brouillon'
      throw err
    }
  }

  async function deleteMessage(id: number, permanent: boolean = false) {
    try {
      if (permanent) {
        await apiClient.delete(`/messaging/messages/${id}/`)
        messages.value = messages.value.filter(m => m.id !== id)
      } else {
        // Move to trash
        await moveToFolder(id, 'trash')
      }
    } catch (err) {
      error.value = 'Erreur lors de la suppression du message'
      throw err
    }
  }

  async function markAsRead(id: number) {
    try {
      await apiClient.post(`/messaging/messages/${id}/mark-read/`)
      
      const message = messages.value.find(m => m.id === id)
      if (message) {
        const recipient = message.recipients.find(r => r.recipient === currentUserId.value)
        if (recipient) {
          recipient.is_read = true
        }
      }
    } catch (err) {
      console.error('Failed to mark as read:', err)
    }
  }

  async function markAsUnread(id: number) {
    try {
      await apiClient.post(`/messaging/messages/${id}/mark-unread/`)
      
      const message = messages.value.find(m => m.id === id)
      if (message) {
        const recipient = message.recipients.find(r => r.recipient === currentUserId.value)
        if (recipient) {
          recipient.is_read = false
        }
      }
    } catch (err) {
      error.value = 'Erreur lors du marquage comme non lu'
      throw err
    }
  }

  async function toggleStar(id: number) {
    try {
      const message = messages.value.find(m => m.id === id)
      if (!message) return
      
      const recipient = message.recipients.find(r => r.recipient === currentUserId.value)
      if (!recipient) return
      
      const newStarred = !recipient.is_starred
      
      await apiClient.post(`/messaging/messages/${id}/toggle-star/`)
      recipient.is_starred = newStarred
    } catch (err) {
      error.value = 'Erreur lors du marquage'
      throw err
    }
  }

  async function moveToFolder(id: number, folder: MessageRecipient['folder']) {
    try {
      await apiClient.post(`/messaging/messages/${id}/move/`, { folder })
      
      const message = messages.value.find(m => m.id === id)
      if (message) {
        const recipient = message.recipients.find(r => r.recipient === currentUserId.value)
        if (recipient) {
          recipient.folder = folder
        }
      }
    } catch (err) {
      error.value = 'Erreur lors du déplacement du message'
      throw err
    }
  }

  async function bulkAction(messageIds: number[], action: {
    type: 'read' | 'unread' | 'star' | 'unstar' | 'move' | 'delete'
    folder?: MessageRecipient['folder']
  }) {
    try {
      await apiClient.post('/messaging/messages/bulk-action/', {
        message_ids: messageIds,
        action: action.type,
        folder: action.folder
      })
      
      // Update local state based on action
      switch (action.type) {
        case 'delete':
          messages.value = messages.value.filter(m => !messageIds.includes(m.id))
          break
        // Handle other actions...
      }
    } catch (err) {
      error.value = 'Erreur lors de l\'action groupée'
      throw err
    }
  }

  async function fetchMessageGroups() {
    try {
      const response = await apiClient.get<PaginatedResponse<MessageGroup>>(
        '/messaging/groups/'
      )
      messageGroups.value = response.data.results
    } catch (err) {
      console.error('Failed to fetch message groups:', err)
    }
  }

  async function fetchMessageTemplates() {
    try {
      const response = await apiClient.get<PaginatedResponse<MessageTemplate>>(
        '/messaging/templates/'
      )
      messageTemplates.value = response.data.results
    } catch (err) {
      console.error('Failed to fetch message templates:', err)
    }
  }

  async function searchRecipients(query: string) {
    try {
      const response = await apiClient.get<PaginatedResponse<User>>(
        `/users/search/?q=${encodeURIComponent(query)}`
      )
      return response.data.results
    } catch (err) {
      console.error('Failed to search recipients:', err)
      return []
    }
  }

  return {
    // State
    messages,
    currentMessage,
    messageGroups,
    messageTemplates,
    draftMessage,
    loading,
    error,
    currentFilters,
    totalCount,
    // Getters
    unreadCount,
    starredMessages,
    messagesByFolder,
    // Actions
    fetchMessages,
    fetchMessage,
    sendMessage,
    saveDraft,
    updateDraft,
    deleteMessage,
    markAsRead,
    markAsUnread,
    toggleStar,
    moveToFolder,
    bulkAction,
    fetchMessageGroups,
    fetchMessageTemplates,
    searchRecipients
  }
})