import { apiClient } from './client'
import type { 
  Conversation, 
  Message,
  MessageAttachment,
  APIResponse,
  PaginatedResponse 
} from '@/types'

export const messagingApi = {
  // Conversations
  async getConversations(params?: {
    participant?: string
    search?: string
    limit?: number
    offset?: number
  }): Promise<PaginatedResponse<Conversation>> {
    const response = await apiClient.get('/messaging/conversations/', { params })
    return response.data
  },

  async getConversation(id: string): Promise<Conversation> {
    const response = await apiClient.get(`/messaging/conversations/${id}/`)
    return response.data
  },

  async createConversation(data: {
    title: string
    participants: string[]
    is_group?: boolean
    description?: string
  }): Promise<Conversation> {
    const response = await apiClient.post('/messaging/conversations/', data)
    return response.data
  },

  async updateConversation(id: string, data: Partial<Conversation>): Promise<Conversation> {
    const response = await apiClient.patch(`/messaging/conversations/${id}/`, data)
    return response.data
  },

  async deleteConversation(id: string): Promise<void> {
    await apiClient.delete(`/messaging/conversations/${id}/`)
  },

  async addParticipant(conversationId: string, userId: string): Promise<void> {
    await apiClient.post(`/messaging/conversations/${conversationId}/add_participant/`, {
      user_id: userId
    })
  },

  async removeParticipant(conversationId: string, userId: string): Promise<void> {
    await apiClient.post(`/messaging/conversations/${conversationId}/remove_participant/`, {
      user_id: userId
    })
  },

  async leaveConversation(conversationId: string): Promise<void> {
    await apiClient.post(`/messaging/conversations/${conversationId}/leave/`)
  },

  async markAsRead(conversationId: string): Promise<void> {
    await apiClient.post(`/messaging/conversations/${conversationId}/mark_as_read/`)
  },

  // Messages
  async getMessages(conversationId: string, params?: {
    limit?: number
    offset?: number
    before?: string
    after?: string
  }): Promise<PaginatedResponse<Message>> {
    const response = await apiClient.get(`/messaging/conversations/${conversationId}/messages/`, { params })
    return response.data
  },

  async getMessage(id: string): Promise<Message> {
    const response = await apiClient.get(`/messaging/messages/${id}/`)
    return response.data
  },

  async sendMessage(conversationId: string, data: {
    content: string
    message_type?: 'text' | 'file' | 'image' | 'announcement'
    reply_to?: string
    attachments?: File[]
  }): Promise<Message> {
    const formData = new FormData()
    formData.append('conversation', conversationId)
    formData.append('content', data.content)
    
    if (data.message_type) {
      formData.append('message_type', data.message_type)
    }
    
    if (data.reply_to) {
      formData.append('reply_to', data.reply_to)
    }
    
    if (data.attachments) {
      data.attachments.forEach((file, index) => {
        formData.append(`attachments[${index}]`, file)
      })
    }

    const response = await apiClient.post('/messaging/messages/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async updateMessage(id: string, data: {
    content: string
  }): Promise<Message> {
    const response = await apiClient.patch(`/messaging/messages/${id}/`, data)
    return response.data
  },

  async deleteMessage(id: string): Promise<void> {
    await apiClient.delete(`/messaging/messages/${id}/`)
  },

  async reactToMessage(messageId: string, emoji: string): Promise<void> {
    await apiClient.post(`/messaging/messages/${messageId}/react/`, {
      emoji
    })
  },

  async removeReaction(messageId: string, emoji: string): Promise<void> {
    await apiClient.delete(`/messaging/messages/${messageId}/react/`, {
      data: { emoji }
    })
  },

  // Attachments
  async downloadAttachment(attachmentId: string): Promise<Blob> {
    const response = await apiClient.get(`/messaging/attachments/${attachmentId}/download/`, {
      responseType: 'blob'
    })
    return response.data
  },

  async deleteAttachment(attachmentId: string): Promise<void> {
    await apiClient.delete(`/messaging/attachments/${attachmentId}/`)
  },

  // Search
  async searchMessages(query: string, params?: {
    conversation?: string
    message_type?: string
    date_from?: string
    date_to?: string
    limit?: number
    offset?: number
  }): Promise<PaginatedResponse<Message>> {
    const response = await apiClient.get('/messaging/search/', {
      params: { q: query, ...params }
    })
    return response.data
  },

  // Statistics
  async getMessagingStats(): Promise<{
    total_conversations: number
    total_messages: number
    unread_messages: number
    active_conversations: number
  }> {
    const response = await apiClient.get('/messaging/stats/')
    return response.data
  },

  // Notifications
  async getUnreadCount(): Promise<{ count: number }> {
    const response = await apiClient.get('/messaging/unread-count/')
    return response.data
  },

  async markAllAsRead(): Promise<void> {
    await apiClient.post('/messaging/mark-all-read/')
  },

  // Export
  async exportConversation(conversationId: string, format: 'pdf' | 'csv' = 'pdf'): Promise<Blob> {
    const response = await apiClient.get(`/messaging/conversations/${conversationId}/export/`, {
      params: { format },
      responseType: 'blob'
    })
    return response.data
  }
}