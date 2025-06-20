import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { chatbotApi } from '@/services/chatbot'
import type { 
  ChatbotConversation, 
  ChatbotMessage, 
  ChatbotResponse,
  QuickReply 
} from '@/types/chatbot'

export const useChatbotStore = defineStore('chatbot', () => {
  // État
  const conversations = ref<ChatbotConversation[]>([])
  const currentConversation = ref<ChatbotConversation | null>(null)
  const loading = ref(false)
  const isTyping = ref(false)
  const suggestions = ref<string[]>([])
  const quickReplies = ref<QuickReply[]>([])
  const isConnected = ref(true)

  // État de l'interface
  const isMinimized = ref(true)
  const showSuggestions = ref(true)
  const soundEnabled = ref(true)

  // Getters
  const currentMessages = computed(() => 
    currentConversation.value?.messages || []
  )

  const unreadMessagesCount = computed(() => {
    return conversations.value.reduce((count, conv) => {
      return count + conv.messages.filter(msg => 
        msg.sender === 'bot' && !msg.is_read
      ).length
    }, 0)
  })

  const hasActiveConversation = computed(() => 
    currentConversation.value !== null
  )

  const canSendMessage = computed(() => 
    hasActiveConversation.value && !loading.value && !isTyping.value
  )

  // Actions
  const loadConversations = async () => {
    try {
      loading.value = true
      const data = await chatbotApi.getConversations()
      conversations.value = data.results || data
    } catch (error) {
      console.error('Erreur lors du chargement des conversations:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const loadConversation = async (conversationId: string) => {
    try {
      loading.value = true
      const conversation = await chatbotApi.getConversation(conversationId)
      currentConversation.value = conversation
      
      // Marquer les messages comme lus
      await markMessagesAsRead(conversationId)
    } catch (error) {
      console.error('Erreur lors du chargement de la conversation:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const startNewConversation = async (type: string = 'general', initialMessage?: string) => {
    try {
      loading.value = true
      
      if (initialMessage) {
        // Démarrage rapide avec message initial
        const response = await chatbotApi.quickStart(type, initialMessage)
        const conversation = await chatbotApi.getConversation(response.conversation_id)
        currentConversation.value = conversation
        quickReplies.value = response.quick_replies || []
      } else {
        // Créer une conversation vide
        const conversation = await chatbotApi.createConversation({
          conversation_type: type
        })
        currentConversation.value = conversation
        
        // Charger les suggestions de démarrage
        await loadSuggestions()
      }
      
      // Ajouter à la liste des conversations
      if (currentConversation.value) {
        const existingIndex = conversations.value.findIndex(
          conv => conv.id === currentConversation.value!.id
        )
        if (existingIndex >= 0) {
          conversations.value[existingIndex] = currentConversation.value
        } else {
          conversations.value.unshift(currentConversation.value)
        }
      }

      isMinimized.value = false
    } catch (error) {
      console.error('Erreur lors de la création de la conversation:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const sendMessage = async (content: string, messageType: string = 'text') => {
    if (!currentConversation.value || !canSendMessage.value) {
      throw new Error('Impossible d\'envoyer le message')
    }

    try {
      isTyping.value = true
      
      const response = await chatbotApi.sendMessage(currentConversation.value.id, {
        content,
        message_type: messageType
      })

      // Ajouter les nouveaux messages à la conversation
      if (response.user_message) {
        currentConversation.value.messages.push(response.user_message)
      }
      if (response.bot_response) {
        currentConversation.value.messages.push(response.bot_response)
      }

      // Mettre à jour les suggestions et réponses rapides
      quickReplies.value = response.quick_replies || []
      suggestions.value = response.suggestions || []

      // Jouer un son de notification si activé
      if (soundEnabled.value && response.bot_response) {
        playNotificationSound()
      }

      // Vérifier si une assistance humaine est nécessaire
      if (response.needs_human) {
        await handleHumanAssistanceRequest()
      }

      return response
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error)
      throw error
    } finally {
      isTyping.value = false
    }
  }

  const handleQuickReply = async (quickReply: QuickReply) => {
    if (quickReply.action) {
      // Gérer les actions spéciales
      await handleAction(quickReply.action, quickReply.payload)
    } else {
      // Envoyer comme message normal
      await sendMessage(quickReply.text, 'quick_reply')
    }
  }

  const handleAction = async (action: string, payload?: any) => {
    try {
      loading.value = true
      
      const response = await chatbotApi.handleAction({
        action,
        payload: payload || {}
      })

      // Traiter la réponse selon le type d'action
      if (response.action_type === 'redirect') {
        // Redirection vers une autre page
        window.location.href = response.redirect_url
      } else if (response.action_type === 'form') {
        // Afficher un formulaire
        // TODO: Implémenter l'affichage de formulaires
        console.log('Formulaire à afficher:', response.form_fields)
      } else {
        // Ajouter la réponse comme message
        if (currentConversation.value) {
          const botMessage: ChatbotMessage = {
            id: `action_${Date.now()}`,
            sender: 'bot',
            content: response.message,
            message_type: 'text',
            timestamp: new Date().toISOString(),
            is_read: false
          }
          currentConversation.value.messages.push(botMessage)
          quickReplies.value = response.quick_replies || []
        }
      }
    } catch (error) {
      console.error('Erreur lors de l\'action:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const loadSuggestions = async () => {
    try {
      const response = await chatbotApi.getSuggestions()
      suggestions.value = response.suggestions
    } catch (error) {
      console.error('Erreur lors du chargement des suggestions:', error)
    }
  }

  const searchKnowledge = async (query: string) => {
    try {
      const response = await chatbotApi.searchKnowledge({
        query,
        limit: 5
      })
      return response.results
    } catch (error) {
      console.error('Erreur lors de la recherche:', error)
      throw error
    }
  }

  const markMessagesAsRead = async (conversationId: string) => {
    try {
      const conversation = conversations.value.find(conv => conv.id === conversationId)
      if (conversation) {
        const unreadMessages = conversation.messages.filter(
          msg => msg.sender === 'bot' && !msg.is_read
        )
        
        for (const message of unreadMessages) {
          await chatbotApi.markMessageAsRead(message.id)
          message.is_read = true
        }
      }
    } catch (error) {
      console.error('Erreur lors du marquage des messages:', error)
    }
  }

  const closeConversation = async () => {
    if (!currentConversation.value) return

    try {
      await chatbotApi.closeConversation(currentConversation.value.id)
      currentConversation.value.status = 'closed'
      currentConversation.value = null
      quickReplies.value = []
      suggestions.value = []
    } catch (error) {
      console.error('Erreur lors de la fermeture:', error)
      throw error
    }
  }

  const rateConversation = async (rating: number, feedback?: string) => {
    if (!currentConversation.value) return

    try {
      await chatbotApi.rateConversation(currentConversation.value.id, {
        satisfaction_rating: rating,
        feedback_text: feedback
      })
      currentConversation.value.satisfaction_rating = rating
    } catch (error) {
      console.error('Erreur lors de l\'évaluation:', error)
      throw error
    }
  }

  const handleHumanAssistanceRequest = async () => {
    // Créer un ticket de support ou rediriger vers le support
    console.log('Demande d\'assistance humaine')
    // TODO: Implémenter la logique de support humain
  }

  const playNotificationSound = () => {
    if (!soundEnabled.value) return
    
    try {
      const audio = new Audio('/sounds/notification.mp3')
      audio.volume = 0.3
      audio.play().catch(() => {
        // Ignore les erreurs de lecture audio
      })
    } catch (error) {
      // Ignore les erreurs
    }
  }

  // Interface utilisateur
  const minimizeChat = () => {
    isMinimized.value = true
  }

  const maximizeChat = () => {
    isMinimized.value = false
  }

  const toggleChat = () => {
    isMinimized.value = !isMinimized.value
  }

  const toggleSuggestions = () => {
    showSuggestions.value = !showSuggestions.value
  }

  const toggleSound = () => {
    soundEnabled.value = !soundEnabled.value
  }

  const clearConversations = () => {
    conversations.value = []
    currentConversation.value = null
    quickReplies.value = []
    suggestions.value = []
  }

  return {
    // État
    conversations,
    currentConversation,
    loading,
    isTyping,
    suggestions,
    quickReplies,
    isConnected,
    isMinimized,
    showSuggestions,
    soundEnabled,

    // Getters
    currentMessages,
    unreadMessagesCount,
    hasActiveConversation,
    canSendMessage,

    // Actions
    loadConversations,
    loadConversation,
    startNewConversation,
    sendMessage,
    handleQuickReply,
    handleAction,
    loadSuggestions,
    searchKnowledge,
    markMessagesAsRead,
    closeConversation,
    rateConversation,
    
    // Interface
    minimizeChat,
    maximizeChat,
    toggleChat,
    toggleSuggestions,
    toggleSound,
    clearConversations
  }
})