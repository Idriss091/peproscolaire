<template>
  <div class="messaging-view h-full flex flex-col">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <h1 class="text-2xl font-bold text-gray-900">Messagerie</h1>
          <div v-if="unreadCount > 0" class="bg-red-500 text-white px-2 py-1 rounded-full text-xs">
            {{ unreadCount }}
          </div>
        </div>
        
        <div class="flex items-center space-x-3">
          <!-- Recherche -->
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Rechercher des conversations..."
              class="w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              @input="searchConversations"
            />
            <MagnifyingGlassIcon class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
          </div>
          
          <!-- Nouvelle conversation -->
          <button
            @click="showNewConversationModal = true"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
          >
            <PlusIcon class="h-5 w-5" />
            <span>Nouvelle conversation</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Corps principal -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Liste des conversations -->
      <div class="w-1/3 bg-gray-50 border-r border-gray-200 flex flex-col">
        <!-- Filtres -->
        <div class="p-4 border-b border-gray-200">
          <div class="flex space-x-2">
            <button
              v-for="filter in conversationFilters"
              :key="filter.key"
              @click="activeFilter = filter.key"
              :class="[
                'px-3 py-1 rounded-full text-sm transition-colors',
                activeFilter === filter.key
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100'
              ]"
            >
              {{ filter.label }}
              <span v-if="filter.count > 0" class="ml-1 text-xs">
                ({{ filter.count }})
              </span>
            </button>
          </div>
        </div>

        <!-- Liste -->
        <div class="flex-1 overflow-y-auto">
          <div v-if="loading.conversations" class="p-4 text-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          </div>
          
          <div v-else-if="filteredConversations.length === 0" class="p-4 text-center text-gray-500">
            <ChatBubbleLeftRightIcon class="h-12 w-12 mx-auto mb-2 text-gray-300" />
            <p>Aucune conversation trouvée</p>
          </div>
          
          <div v-else>
            <div
              v-for="conversation in filteredConversations"
              :key="conversation.id"
              @click="selectConversation(conversation)"
              :class="[
                'p-4 border-b border-gray-200 cursor-pointer hover:bg-white transition-colors',
                currentConversation?.id === conversation.id ? 'bg-white border-l-4 border-l-blue-600' : ''
              ]"
            >
              <div class="flex items-start space-x-3">
                <!-- Avatar -->
                <div class="flex-shrink-0">
                  <div v-if="conversation.is_group" class="h-10 w-10 bg-gray-300 rounded-full flex items-center justify-center">
                    <UsersIcon class="h-6 w-6 text-gray-600" />
                  </div>
                  <div v-else class="h-10 w-10 bg-blue-500 rounded-full flex items-center justify-center">
                    <span class="text-white font-medium">
                      {{ getInitials(getConversationTitle(conversation, currentUser?.id || '')) }}
                    </span>
                  </div>
                </div>
                
                <!-- Contenu -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-center justify-between">
                    <h3 class="text-sm font-medium text-gray-900 truncate">
                      {{ getConversationTitle(conversation, currentUser?.id || '') }}
                    </h3>
                    <span class="text-xs text-gray-500">
                      {{ formatTime(conversation.last_message?.created_at || conversation.updated_at) }}
                    </span>
                  </div>
                  
                  <div class="flex items-center justify-between mt-1">
                    <p class="text-sm text-gray-600 truncate">
                      {{ conversation.last_message?.content || 'Aucun message' }}
                    </p>
                    <div v-if="conversation.unread_count > 0" 
                         class="bg-blue-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center ml-2">
                      {{ conversation.unread_count }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Zone de chat -->
      <div class="flex-1 flex flex-col">
        <div v-if="!currentConversation" class="flex-1 flex items-center justify-center bg-gray-50">
          <div class="text-center">
            <ChatBubbleLeftRightIcon class="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-gray-900 mb-2">Sélectionnez une conversation</h3>
            <p class="text-gray-500">Choisissez une conversation pour commencer à discuter</p>
          </div>
        </div>
        
        <div v-else class="flex-1 flex flex-col">
          <!-- Header de conversation -->
          <div class="bg-white border-b border-gray-200 px-6 py-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div v-if="currentConversation.is_group" class="h-8 w-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <UsersIcon class="h-5 w-5 text-gray-600" />
                </div>
                <div v-else class="h-8 w-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <span class="text-white text-sm">
                    {{ getInitials(getConversationTitle(currentConversation, currentUser?.id || '')) }}
                  </span>
                </div>
                
                <div>
                  <h2 class="text-lg font-medium text-gray-900">
                    {{ getConversationTitle(currentConversation, currentUser?.id || '') }}
                  </h2>
                  <p class="text-sm text-gray-500">
                    {{ currentConversation.participants.length }} participant{{ currentConversation.participants.length > 1 ? 's' : '' }}
                  </p>
                </div>
              </div>
              
              <div class="flex items-center space-x-2">
                <button
                  @click="markAsRead(currentConversation.id)"
                  class="p-2 text-gray-400 hover:text-gray-600"
                  title="Marquer comme lu"
                >
                  <CheckIcon class="h-5 w-5" />
                </button>
                
                <button
                  @click="showConversationSettings = true"
                  class="p-2 text-gray-400 hover:text-gray-600"
                  title="Paramètres"
                >
                  <Cog6ToothIcon class="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>

          <!-- Messages -->
          <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
            <div v-if="loading.messages" class="text-center">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>
            
            <div v-for="message in currentMessages" :key="message.id" class="flex space-x-3">
              <!-- Avatar de l'expéditeur -->
              <div class="flex-shrink-0">
                <div class="h-8 w-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <span class="text-white text-xs">
                    {{ getInitials(`${message.sender.first_name} ${message.sender.last_name}`) }}
                  </span>
                </div>
              </div>
              
              <!-- Contenu du message -->
              <div class="flex-1">
                <div class="flex items-center space-x-2 mb-1">
                  <span class="text-sm font-medium text-gray-900">
                    {{ message.sender.first_name }} {{ message.sender.last_name }}
                  </span>
                  <span class="text-xs text-gray-500">
                    {{ formatDateTime(message.created_at) }}
                  </span>
                </div>
                
                <div class="bg-white rounded-lg border border-gray-200 p-3">
                  <p class="text-gray-900">{{ message.content }}</p>
                  
                  <!-- Pièces jointes -->
                  <div v-if="message.attachments && message.attachments.length > 0" class="mt-2 space-y-2">
                    <div
                      v-for="attachment in message.attachments"
                      :key="attachment.id"
                      class="flex items-center space-x-2 text-sm text-blue-600 hover:text-blue-800"
                    >
                      <PaperClipIcon class="h-4 w-4" />
                      <a :href="attachment.file_url" target="_blank">{{ attachment.filename }}</a>
                    </div>
                  </div>
                  
                  <!-- Réactions -->
                  <div v-if="message.reactions && message.reactions.length > 0" class="mt-2 flex space-x-1">
                    <button
                      v-for="reaction in message.reactions"
                      :key="reaction.id"
                      @click="reactToMessage(message.id, reaction.emoji)"
                      class="bg-gray-100 hover:bg-gray-200 rounded-full px-2 py-1 text-xs"
                    >
                      {{ reaction.emoji }} {{ reaction.count }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Zone de saisie -->
          <div class="bg-white border-t border-gray-200 px-4 py-4">
            <form @submit.prevent="sendMessage" class="flex space-x-3">
              <div class="flex-1">
                <textarea
                  v-model="newMessage"
                  placeholder="Tapez votre message..."
                  rows="3"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  @keydown.ctrl.enter="sendMessage"
                ></textarea>
              </div>
              
              <div class="flex flex-col space-y-2">
                <button
                  type="button"
                  @click="$refs.fileInput.click()"
                  class="p-2 text-gray-400 hover:text-gray-600"
                  title="Joindre un fichier"
                >
                  <PaperClipIcon class="h-5 w-5" />
                </button>
                
                <button
                  type="submit"
                  :disabled="!newMessage.trim() || loading.sending"
                  class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white p-2 rounded-lg"
                >
                  <PaperAirplaneIcon class="h-5 w-5" />
                </button>
              </div>
            </form>
            
            <input
              ref="fileInput"
              type="file"
              multiple
              class="hidden"
              @change="handleFileSelection"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Modal nouvelle conversation -->
    <div v-if="showNewConversationModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-medium mb-4">Nouvelle conversation</h3>
        
        <form @submit.prevent="createNewConversation">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Titre</label>
            <input
              v-model="newConversationForm.title"
              type="text"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Type</label>
            <select
              v-model="newConversationForm.is_group"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option :value="false">Conversation privée</option>
              <option :value="true">Groupe</option>
            </select>
          </div>
          
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">Participants</label>
            <!-- Ici on pourrait ajouter un sélecteur d'utilisateurs -->
            <p class="text-sm text-gray-500">Fonctionnalité à implémenter</p>
          </div>
          
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="showNewConversationModal = false"
              class="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Créer
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useMessagingStore } from '@/stores/messaging'
import { useAuthStore } from '@/stores/auth'
import {
  ChatBubbleLeftRightIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  UsersIcon,
  CheckIcon,
  Cog6ToothIcon,
  PaperClipIcon,
  PaperAirplaneIcon
} from '@heroicons/vue/24/outline'
import type { Conversation } from '@/types'

// Stores
const messagingStore = useMessagingStore()
const authStore = useAuthStore()

// Réactivité
const {
  conversations,
  currentConversation,
  messages,
  unreadCount,
  loading,
  error,
  sortedConversations,
  currentMessages,
  totalUnreadConversations
} = messagingStore

const { currentUser } = authStore

// État local
const searchQuery = ref('')
const activeFilter = ref('all')
const newMessage = ref('')
const showNewConversationModal = ref(false)
const showConversationSettings = ref(false)
const messagesContainer = ref<HTMLElement>()

const newConversationForm = ref({
  title: '',
  is_group: false,
  participants: [] as string[]
})

// Filtres de conversation
const conversationFilters = computed(() => [
  {
    key: 'all',
    label: 'Toutes',
    count: conversations.length
  },
  {
    key: 'unread',
    label: 'Non lues',
    count: totalUnreadConversations
  },
  {
    key: 'groups',
    label: 'Groupes',
    count: conversations.filter(c => c.is_group).length
  }
])

// Conversations filtrées
const filteredConversations = computed(() => {
  let filtered = sortedConversations

  // Filtre par type
  if (activeFilter.value === 'unread') {
    filtered = filtered.filter(c => c.unread_count > 0)
  } else if (activeFilter.value === 'groups') {
    filtered = filtered.filter(c => c.is_group)
  }

  // Filtre par recherche
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(c => 
      messagingStore.getConversationTitle(c, currentUser?.id || '').toLowerCase().includes(query) ||
      c.last_message?.content.toLowerCase().includes(query)
    )
  }

  return filtered
})

// Méthodes
const selectConversation = async (conversation: Conversation) => {
  await messagingStore.fetchConversation(conversation.id)
  await messagingStore.fetchMessages(conversation.id)
  await messagingStore.markAsRead(conversation.id)
  
  // Scroll vers le bas
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || !currentConversation) return

  try {
    await messagingStore.sendMessage(currentConversation.id, {
      content: newMessage.value.trim()
    })
    
    newMessage.value = ''
    
    // Scroll vers le bas
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    })
  } catch (error) {
    console.error('Erreur lors de l\'envoi du message:', error)
  }
}

const createNewConversation = async () => {
  try {
    await messagingStore.createConversation({
      title: newConversationForm.value.title,
      is_group: newConversationForm.value.is_group,
      participants: newConversationForm.value.participants
    })
    
    showNewConversationModal.value = false
    newConversationForm.value = {
      title: '',
      is_group: false,
      participants: []
    }
  } catch (error) {
    console.error('Erreur lors de la création de la conversation:', error)
  }
}

const searchConversations = () => {
  // La recherche est gérée par le computed filteredConversations
}

const handleFileSelection = (event: Event) => {
  const files = (event.target as HTMLInputElement).files
  if (files && files.length > 0) {
    // TODO: Implémenter l'upload de fichiers
    console.log('Fichiers sélectionnés:', files)
  }
}

const reactToMessage = async (messageId: string, emoji: string) => {
  try {
    await messagingStore.reactToMessage(messageId, emoji)
  } catch (error) {
    console.error('Erreur lors de la réaction:', error)
  }
}

const markAsRead = async (conversationId: string) => {
  await messagingStore.markAsRead(conversationId)
}

// Utilitaires
const getInitials = (name: string) => {
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const getConversationTitle = (conversation: Conversation, currentUserId: string) => {
  return messagingStore.getConversationTitle(conversation, currentUserId)
}

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
  } else {
    return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
  }
}

const formatDateTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('fr-FR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Cycle de vie
onMounted(async () => {
  await messagingStore.fetchConversations()
  await messagingStore.fetchUnreadCount()
})

// Watchers
watch(currentMessages, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
})
</script>

<style scoped>
.messaging-view {
  height: calc(100vh - 64px); /* Ajuster selon la hauteur du header */
}
</style>