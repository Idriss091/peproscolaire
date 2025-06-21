<template>
  <div :class="messageClasses" class="chat-message">
    <div class="message-content">
      <!-- Avatar -->
      <div v-if="!isUser" class="message-avatar">
        <SparklesIcon class="h-4 w-4 text-ai-600" />
      </div>

      <!-- Bulle de message -->
      <div :class="bubbleClasses" class="message-bubble">
        <!-- Contenu du message -->
        <div v-if="message.message_type === 'text'" class="message-text">
          <div v-html="formattedContent" />
        </div>

        <!-- Actions système -->
        <div v-else-if="message.message_type === 'action'" class="message-action">
          <div class="flex items-center gap-2 text-gray-600">
            <InformationCircleIcon class="h-4 w-4" />
            <span class="text-sm italic">{{ message.content }}</span>
          </div>
        </div>

        <!-- Pièce jointe -->
        <div v-else-if="message.message_type === 'attachment'" class="message-attachment">
          <div class="attachment-preview">
            <DocumentIcon class="h-8 w-8 text-gray-500" />
            <div class="attachment-info">
              <p class="attachment-name">{{ getAttachmentName() }}</p>
              <p class="attachment-size">{{ getAttachmentSize() }}</p>
            </div>
          </div>
        </div>

        <!-- Métadonnées du message -->
        <div v-if="showMetadata" class="message-metadata">
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <span>{{ formatTime(message.timestamp) }}</span>
            
            <!-- Intention détectée -->
            <span v-if="message.intent && !isUser" class="intent-badge">
              {{ message.intent }}
            </span>
            
            <!-- Score de confiance -->
            <span
              v-if="message.confidence_score && !isUser"
              :class="confidenceClasses"
              class="confidence-score"
            >
              {{ Math.round(message.confidence_score * 100) }}%
            </span>
            
            <!-- Temps de réponse -->
            <span v-if="message.response_time_ms && !isUser" class="response-time">
              {{ message.response_time_ms }}ms
            </span>
          </div>
        </div>
      </div>

      <!-- Avatar utilisateur -->
      <div v-if="isUser" class="message-avatar user-avatar">
        <UserIcon class="h-4 w-4 text-gray-600" />
      </div>
    </div>

    <!-- Actions sur le message -->
    <div v-if="!isUser && showActions" class="message-actions">
      <button
        @click="copyMessage"
        class="message-action-btn"
        title="Copier"
      >
        <ClipboardDocumentIcon class="h-3 w-3" />
      </button>
      
      <button
        @click="likeMessage"
        :class="{ 'text-green-600': isLiked }"
        class="message-action-btn"
        title="Utile"
      >
        <HandThumbUpIcon class="h-3 w-3" />
      </button>
      
      <button
        @click="dislikeMessage"
        :class="{ 'text-red-600': isDisliked }"
        class="message-action-btn"
        title="Pas utile"
      >
        <HandThumbDownIcon class="h-3 w-3" />
      </button>
      
      <button
        @click="reportMessage"
        class="message-action-btn"
        title="Signaler"
      >
        <ExclamationTriangleIcon class="h-3 w-3" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  SparklesIcon,
  UserIcon,
  InformationCircleIcon,
  DocumentIcon,
  ClipboardDocumentIcon,
  HandThumbUpIcon,
  HandThumbDownIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'
import type { ChatbotMessage } from '@/types/chatbot'

interface Props {
  message: ChatbotMessage
  showMetadata?: boolean
  showActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showMetadata: false,
  showActions: true
})

interface Emits {
  action: [action: string, payload?: any]
}

const emit = defineEmits<Emits>()

const isLiked = ref(false)
const isDisliked = ref(false)

// Computed
const isUser = computed(() => props.message.sender === 'user')
const isSystem = computed(() => props.message.sender === 'system')

const messageClasses = computed(() => [
  'chat-message',
  {
    'message-user': isUser.value,
    'message-bot': !isUser.value && !isSystem.value,
    'message-system': isSystem.value
  }
])

const bubbleClasses = computed(() => [
  'message-bubble',
  {
    'bubble-user': isUser.value,
    'bubble-bot': !isUser.value && !isSystem.value,
    'bubble-system': isSystem.value
  }
])

const confidenceClasses = computed(() => {
  const score = props.message.confidence_score || 0
  if (score >= 0.8) return 'text-green-600'
  if (score >= 0.6) return 'text-warning-600'
  return 'text-red-600'
})

const formattedContent = computed(() => {
  let content = props.message.content

  // Remplacer les liens
  content = content.replace(
    /(https?:\/\/[^\s]+)/g,
    '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-ai-600 hover:text-ai-700 underline">$1</a>'
  )

  // Remplacer les mentions d'email
  content = content.replace(
    /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g,
    '<a href="mailto:$1" class="text-ai-600 hover:text-ai-700 underline">$1</a>'
  )

  // Remplacer les sauts de ligne
  content = content.replace(/\n/g, '<br>')

  // Formatage markdown simple
  content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  content = content.replace(/\*(.*?)\*/g, '<em>$1</em>')
  content = content.replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 py-0.5 rounded text-sm">$1</code>')

  return content
})

// Methods
const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))

  if (diffInMinutes < 1) return 'À l\'instant'
  if (diffInMinutes < 60) return `Il y a ${diffInMinutes}min`
  if (diffInMinutes < 1440) return `Il y a ${Math.floor(diffInMinutes / 60)}h`
  
  return date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getAttachmentName = () => {
  // Extract filename from attachment data
  return 'document.pdf' // Placeholder
}

const getAttachmentSize = () => {
  // Extract file size from attachment data
  return '1.2 MB' // Placeholder
}

const copyMessage = async () => {
  try {
    await navigator.clipboard.writeText(props.message.content)
    // Show success toast
    emit('action', 'copy_success')
  } catch (error) {
    console.error('Erreur copie:', error)
  }
}

const likeMessage = () => {
  isLiked.value = !isLiked.value
  if (isLiked.value) {
    isDisliked.value = false
  }
  emit('action', 'like_message', { messageId: props.message.id, liked: isLiked.value })
}

const dislikeMessage = () => {
  isDisliked.value = !isDisliked.value
  if (isDisliked.value) {
    isLiked.value = false
  }
  emit('action', 'dislike_message', { messageId: props.message.id, disliked: isDisliked.value })
}

const reportMessage = () => {
  emit('action', 'report_message', { messageId: props.message.id })
}
</script>

<style scoped>
.chat-message {
  @apply relative group;
}

.message-content {
  @apply flex items-end gap-2;
}

.message-user .message-content {
  @apply flex-row-reverse;
}

.message-avatar {
  @apply w-6 h-6 rounded-full bg-ai-100 flex items-center justify-center flex-shrink-0;
}

.user-avatar {
  @apply bg-gray-100;
}

.message-bubble {
  @apply max-w-xs lg:max-w-md px-3 py-2 rounded-2xl relative;
  word-wrap: break-word;
}

.bubble-user {
  @apply bg-ai-600 text-white;
}

.bubble-bot {
  @apply bg-gray-100 text-gray-900;
}

.bubble-system {
  @apply bg-gray-50 border border-gray-200 text-gray-600 italic;
}

.message-text {
  @apply leading-relaxed;
}

.message-text :deep(strong) {
  @apply font-semibold;
}

.message-text :deep(em) {
  @apply italic;
}

.message-text :deep(code) {
  @apply bg-gray-200 text-gray-800;
}

.bubble-user .message-text :deep(code) {
  @apply bg-ai-500 text-white;
}

.message-action {
  @apply p-1;
}

.message-attachment {
  @apply space-y-2;
}

.attachment-preview {
  @apply flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-200;
}

.attachment-info {
  @apply flex-1 min-w-0;
}

.attachment-name {
  @apply font-medium text-gray-900 truncate;
}

.attachment-size {
  @apply text-sm text-gray-500;
}

.message-metadata {
  @apply mt-1 pt-1 border-t border-gray-200;
}

.bubble-user .message-metadata {
  @apply border-ai-500;
}

.intent-badge {
  @apply bg-ai-100 text-ai-700 px-1.5 py-0.5 rounded text-xs font-medium;
}

.confidence-score {
  @apply font-medium;
}

.response-time {
  @apply text-gray-400;
}

.message-actions {
  @apply absolute -bottom-6 left-8 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity bg-white rounded-lg border border-gray-200 px-2 py-1;
}

.message-user + .message-actions {
  @apply right-8 left-auto;
}

.message-action-btn {
  @apply w-6 h-6 rounded flex items-center justify-center text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-ai-500;
}

/* Animations */
.chat-message {
  animation: slideInUp 0.3s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>