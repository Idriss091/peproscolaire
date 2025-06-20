import api from './api'
import type { 
  ChatbotConversation, 
  ChatbotMessage, 
  ChatbotResponse,
  QuickReply,
  ChatbotFeedback,
  ChatbotSearch,
  ChatbotAction 
} from '@/types/chatbot'

export const chatbotApi = {
  // Conversations
  async getConversations(params?: any) {
    const response = await api.get('/chatbot/conversations/', { params })
    return response.data
  },

  async getConversation(conversationId: string) {
    const response = await api.get(`/chatbot/conversations/${conversationId}/`)
    return response.data
  },

  async createConversation(data: { conversation_type: string }) {
    const response = await api.post('/chatbot/conversations/', data)
    return response.data
  },

  async sendMessage(conversationId: string, data: { content: string; message_type?: string }) {
    const response = await api.post(`/chatbot/conversations/${conversationId}/send_message/`, data)
    return response.data
  },

  async closeConversation(conversationId: string) {
    const response = await api.post(`/chatbot/conversations/${conversationId}/close_conversation/`)
    return response.data
  },

  async rateConversation(conversationId: string, data: ChatbotFeedback) {
    const response = await api.post(`/chatbot/conversations/${conversationId}/rate_conversation/`, data)
    return response.data
  },

  async getConversationSummary(conversationId: string) {
    const response = await api.get(`/chatbot/conversations/${conversationId}/summary/`)
    return response.data
  },

  // Messages
  async getMessages(params?: any) {
    const response = await api.get('/chatbot/messages/', { params })
    return response.data
  },

  async markMessageAsRead(messageId: string) {
    const response = await api.post(`/chatbot/messages/${messageId}/mark_read/`)
    return response.data
  },

  // Base de connaissances
  async getKnowledgeBase(params?: any) {
    const response = await api.get('/chatbot/knowledge-base/', { params })
    return response.data
  },

  async searchKnowledge(data: ChatbotSearch) {
    const response = await api.post('/chatbot/knowledge-base/search/', data)
    return response.data
  },

  // Actions rapides
  async quickStart(type: string, message?: string) {
    const response = await api.post('/chatbot/actions/quick_start/', {
      type,
      message
    })
    return response.data
  },

  async getSuggestions() {
    const response = await api.get('/chatbot/actions/suggestions/')
    return response.data
  },

  async handleAction(data: ChatbotAction) {
    const response = await api.post('/chatbot/actions/handle_action/', data)
    return response.data
  },

  // Analytiques (admin)
  async getAnalytics(params?: any) {
    const response = await api.get('/chatbot/analytics/', { params })
    return response.data
  },

  async getDashboard() {
    const response = await api.get('/chatbot/analytics/dashboard/')
    return response.data
  }
}