<template>
  <div :class="widgetClasses" class="chatbot-widget">
    <!-- Bouton flottant -->
    <Transition name="scale">
      <button
        v-if="chatbotStore.isMinimized"
        @click="openChat"
        :class="fabClasses"
        class="chatbot-fab"
        aria-label="Ouvrir le chat"
      >
        <div class="relative">
          <ChatBubbleLeftRightIcon class="h-6 w-6" />
          
          <!-- Badge de notifications -->
          <Transition name="bounce">
            <div
              v-if="chatbotStore.unreadMessagesCount > 0"
              class="notification-badge"
            >
              {{ chatbotStore.unreadMessagesCount > 9 ? '9+' : chatbotStore.unreadMessagesCount }}
            </div>
          </Transition>
        </div>
      </button>
    </Transition>

    <!-- Interface de chat -->
    <Transition name="slide-up">
      <div
        v-if="!chatbotStore.isMinimized"
        :class="chatContainerClasses"
        class="chat-container"
      >
        <!-- Header -->
        <div class="chat-header">
          <div class="flex items-center gap-3">
            <div class="flex items-center gap-2">
              <div :class="avatarClasses" class="chatbot-avatar">
                <SparklesIcon class="h-5 w-5" />
              </div>
              <div>
                <h3 class="font-semibold text-white">Assistant PeproScolaire</h3>
                <div class="flex items-center gap-1 text-xs text-blue-100">
                  <div
                    :class="[
                      'w-2 h-2 rounded-full',
                      chatbotStore.isConnected ? 'bg-green-400' : 'bg-red-400'
                    ]"
                  />
                  {{ chatbotStore.isConnected ? 'En ligne' : 'Hors ligne' }}
                </div>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <!-- Options -->
            <BaseDropdown placement="bottom-end" size="sm">
              <template #trigger>
                <button class="chat-action-btn" aria-label="Options">
                  <Cog6ToothIcon class="h-4 w-4" />
                </button>
              </template>
              
              <div class="py-1">
                <button
                  @click="chatbotStore.toggleSound()"
                  class="dropdown-item flex items-center gap-2"
                  role="menuitem"
                >
                  <component
                    :is="chatbotStore.soundEnabled ? SpeakerWaveIcon : SpeakerXMarkIcon"
                    class="h-4 w-4"
                  />
                  {{ chatbotStore.soundEnabled ? 'Désactiver le son' : 'Activer le son' }}
                </button>
                
                <button
                  @click="chatbotStore.toggleSuggestions()"
                  class="dropdown-item flex items-center gap-2"
                  role="menuitem"
                >
                  <LightBulbIcon class="h-4 w-4" />
                  {{ chatbotStore.showSuggestions ? 'Masquer suggestions' : 'Afficher suggestions' }}
                </button>
                
                <div class="dropdown-divider" />
                
                <button
                  @click="openConversationHistory"
                  class="dropdown-item flex items-center gap-2"
                  role="menuitem"
                >
                  <ClockIcon class="h-4 w-4" />
                  Historique
                </button>
              </div>
            </BaseDropdown>

            <!-- Fermer -->
            <button
              @click="minimizeChat"
              class="chat-action-btn"
              aria-label="Réduire"
            >
              <MinusIcon class="h-4 w-4" />
            </button>
          </div>
        </div>

        <!-- Messages -->
        <div ref="messagesContainer" class="messages-container">
          <div v-if="!chatbotStore.hasActiveConversation" class="welcome-screen">
            <div class="welcome-content">
              <div class="welcome-avatar">
                <SparklesIcon class="h-8 w-8 text-ai-500" />
              </div>
              <h4 class="welcome-title">Bonjour ! 👋</h4>
              <p class="welcome-message">
                Je suis votre assistant virtuel PeproScolaire. Comment puis-je vous aider aujourd'hui ?
              </p>
              
              <!-- Suggestions de démarrage -->
              <div v-if="chatbotStore.showSuggestions && suggestions.length > 0" class="suggestions-grid">
                <button
                  v-for="suggestion in suggestions"
                  :key="suggestion.action"
                  @click="handleSuggestion(suggestion)"
                  class="suggestion-card"
                >
                  <div class="suggestion-icon">
                    <component :is="getSuggestionIcon(suggestion.type)" class="h-5 w-5" />
                  </div>
                  <div class="suggestion-content">
                    <h5 class="suggestion-title">{{ suggestion.title }}</h5>
                    <p class="suggestion-description">{{ suggestion.description }}</p>
                  </div>
                </button>
              </div>
            </div>
          </div>

          <!-- Messages de conversation -->
          <div v-else class="messages-list">
            <ChatMessage
              v-for="message in chatbotStore.currentMessages"
              :key="message.id"
              :message="message"
              @action="handleMessageAction"
            />
            
            <!-- Indicateur de frappe -->
            <div v-if="chatbotStore.isTyping" class="typing-indicator">
              <div class="typing-avatar">
                <SparklesIcon class="h-4 w-4 text-ai-500" />
              </div>
              <div class="typing-dots">
                <div class="typing-dot" />
                <div class="typing-dot" />
                <div class="typing-dot" />
              </div>
            </div>
          </div>
        </div>

        <!-- Réponses rapides -->
        <div v-if="chatbotStore.quickReplies.length > 0" class="quick-replies">
          <button
            v-for="reply in chatbotStore.quickReplies"
            :key="reply.text"
            @click="handleQuickReply(reply)"
            class="quick-reply-btn"
          >
            {{ reply.text }}
          </button>
        </div>

        <!-- Zone de saisie -->
        <div class="input-area">
          <form @submit.prevent="sendMessage" class="message-form">
            <div class="input-container">
              <textarea
                ref="messageInput"
                v-model="messageText"
                :disabled="!chatbotStore.canSendMessage"
                placeholder="Tapez votre message..."
                class="message-input"
                rows="1"
                @keydown.enter.exact.prevent="sendMessage"
                @keydown.enter.shift.exact="addNewLine"
                @input="adjustTextareaHeight"
              />
              
              <!-- Actions d'input -->
              <div class="input-actions">
                <button
                  type="button"
                  @click="toggleEmojiPicker"
                  class="input-action-btn"
                  aria-label="Émojis"
                >
                  <FaceSmileIcon class="h-5 w-5" />
                </button>
                
                <button
                  type="submit"
                  :disabled="!canSend"
                  :class="sendButtonClasses"
                  class="send-btn"
                  aria-label="Envoyer"
                >
                  <PaperAirplaneIcon class="h-5 w-5" />
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useChatbotStore } from '@/stores/chatbot'
import {
  ChatBubbleLeftRightIcon,
  SparklesIcon,
  MinusIcon,
  Cog6ToothIcon,
  PaperAirplaneIcon,
  FaceSmileIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  LightBulbIcon,
  ClockIcon,
  AcademicCapIcon,
  QuestionMarkCircleIcon,
  DocumentTextIcon,
  UserGroupIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/vue/24/outline'
import BaseDropdown from '@/components/ui/BaseDropdown.vue'
import ChatMessage from './ChatMessage.vue'
import type { QuickReply, ChatbotSuggestion } from '@/types/chatbot'

interface Props {
  position?: 'bottom-right' | 'bottom-left'
  theme?: 'primary' | 'ai' | 'education'
}

const props = withDefaults(defineProps<Props>(), {
  position: 'bottom-right',
  theme: 'ai'
})

const chatbotStore = useChatbotStore()

// Refs
const messagesContainer = ref<HTMLElement>()
const messageInput = ref<HTMLTextAreaElement>()
const messageText = ref('')
const showEmojiPicker = ref(false)

// Suggestions par défaut
const suggestions = ref([
  {
    title: 'Voir mes notes',
    description: 'Consulter mes dernières évaluations',
    action: 'view_grades',
    type: 'academic'
  },
  {
    title: 'Planning',
    description: 'Mon emploi du temps de la semaine',
    action: 'view_schedule',
    type: 'academic'
  },
  {
    title: 'Aide technique',
    description: 'Résoudre un problème',
    action: 'report_issue',
    type: 'support'
  },
  {
    title: 'Questions',
    description: 'Poser une question générale',
    action: 'general_help',
    type: 'general'
  }
])

// Computed
const widgetClasses = computed(() => [
  'chatbot-widget',
  `chatbot-${props.position}`,
  `chatbot-${props.theme}`
])

const fabClasses = computed(() => [
  'chatbot-fab',
  `chatbot-fab-${props.theme}`
])

const chatContainerClasses = computed(() => [
  'chat-container',
  `chat-${props.theme}`
])

const avatarClasses = computed(() => [
  'chatbot-avatar',
  `avatar-${props.theme}`
])

const canSend = computed(() => 
  messageText.value.trim().length > 0 && chatbotStore.canSendMessage
)

const sendButtonClasses = computed(() => [
  'send-btn',
  {
    'send-btn-active': canSend.value,
    'send-btn-disabled': !canSend.value
  }
])

// Methods
const openChat = async () => {
  if (!chatbotStore.hasActiveConversation) {
    await chatbotStore.startNewConversation()
  }
  chatbotStore.maximizeChat()
  await nextTick()
  scrollToBottom()
  focusInput()
}

const minimizeChat = () => {
  chatbotStore.minimizeChat()
}

const sendMessage = async () => {
  if (!canSend.value) return
  
  const text = messageText.value.trim()
  messageText.value = ''
  adjustTextareaHeight()
  
  try {
    await chatbotStore.sendMessage(text)
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('Erreur envoi message:', error)
    messageText.value = text // Restore message on error
  }
}

const addNewLine = () => {
  messageText.value += '\n'
  adjustTextareaHeight()
}

const handleQuickReply = async (reply: QuickReply) => {
  try {
    await chatbotStore.handleQuickReply(reply)
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('Erreur réponse rapide:', error)
  }
}

const handleSuggestion = async (suggestion: any) => {
  try {
    await chatbotStore.startNewConversation('general', suggestion.title)
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('Erreur suggestion:', error)
  }
}

const handleMessageAction = async (action: string, payload?: any) => {
  try {
    await chatbotStore.handleAction(action, payload)
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('Erreur action message:', error)
  }
}

const openConversationHistory = () => {
  // TODO: Ouvrir un modal avec l'historique des conversations
  console.log('Ouvrir historique')
}

const toggleEmojiPicker = () => {
  showEmojiPicker.value = !showEmojiPicker.value
}

const adjustTextareaHeight = () => {
  if (!messageInput.value) return
  
  messageInput.value.style.height = 'auto'
  const maxHeight = 120 // 5 lignes environ
  const newHeight = Math.min(messageInput.value.scrollHeight, maxHeight)
  messageInput.value.style.height = `${newHeight}px`
}

const scrollToBottom = () => {
  if (!messagesContainer.value) return
  
  messagesContainer.value.scrollTo({
    top: messagesContainer.value.scrollHeight,
    behavior: 'smooth'
  })
}

const focusInput = () => {
  nextTick(() => {
    messageInput.value?.focus()
  })
}

const getSuggestionIcon = (type: string) => {
  const icons = {
    academic: AcademicCapIcon,
    support: QuestionMarkCircleIcon,
    administrative: DocumentTextIcon,
    orientation: UserGroupIcon,
    emergency: ExclamationTriangleIcon,
    general: InformationCircleIcon
  }
  return icons[type] || InformationCircleIcon
}

// Watchers
watch(() => chatbotStore.currentMessages, () => {
  nextTick(() => scrollToBottom())
}, { deep: true })

// Lifecycle
onMounted(() => {
  // Charger les conversations si pas encore fait
  if (chatbotStore.conversations.length === 0) {
    chatbotStore.loadConversations()
  }
})
</script>

<style scoped>
.chatbot-widget {
  @apply fixed z-50 pointer-events-none;
}

.chatbot-bottom-right {
  @apply bottom-4 right-4;
}

.chatbot-bottom-left {
  @apply bottom-4 left-4;
}

/* FAB Button */
.chatbot-fab {
  @apply w-14 h-14 rounded-full shadow-xl hover:shadow-2xl transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-offset-2 pointer-events-auto;
  animation: pulse-gentle 2s infinite;
}

.chatbot-fab-primary {
  @apply bg-primary-600 hover:bg-primary-700 text-white focus:ring-primary-500;
}

.chatbot-fab-ai {
  @apply bg-ai-600 hover:bg-ai-700 text-white focus:ring-ai-500;
}

.chatbot-fab-education {
  @apply bg-education-600 hover:bg-education-700 text-white focus:ring-education-500;
}

.notification-badge {
  @apply absolute -top-1 -right-1 bg-danger-500 text-white text-xs font-bold rounded-full min-w-[1.25rem] h-5 flex items-center justify-center px-1;
}

/* Chat Container */
.chat-container {
  @apply w-96 h-[32rem] bg-white rounded-2xl shadow-2xl border border-neutral-200 flex flex-col overflow-hidden pointer-events-auto;
  max-height: calc(100vh - 2rem);
}

@media (max-width: 640px) {
  .chat-container {
    @apply w-screen h-screen rounded-none;
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
  }
}

/* Header */
.chat-header {
  @apply flex items-center justify-between p-4 text-white;
}

.chat-primary .chat-header {
  @apply bg-gradient-to-r from-primary-600 to-primary-700;
}

.chat-ai .chat-header {
  @apply bg-gradient-to-r from-ai-600 to-ai-700;
}

.chat-education .chat-header {
  @apply bg-gradient-to-r from-education-600 to-education-700;
}

.chatbot-avatar {
  @apply w-10 h-10 rounded-full flex items-center justify-center;
}

.avatar-primary {
  @apply bg-primary-500;
}

.avatar-ai {
  @apply bg-ai-500;
}

.avatar-education {
  @apply bg-education-500;
}

.chat-action-btn {
  @apply w-8 h-8 rounded-lg bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors focus:outline-none focus:ring-2 focus:ring-white/50;
}

/* Messages */
.messages-container {
  @apply flex-1 overflow-y-auto p-4 space-y-4;
  scrollbar-width: thin;
}

.messages-container::-webkit-scrollbar {
  @apply w-1;
}

.messages-container::-webkit-scrollbar-track {
  @apply bg-neutral-100;
}

.messages-container::-webkit-scrollbar-thumb {
  @apply bg-neutral-300 rounded-full;
}

/* Welcome Screen */
.welcome-screen {
  @apply h-full flex items-center justify-center;
}

.welcome-content {
  @apply text-center space-y-4 max-w-xs;
}

.welcome-avatar {
  @apply w-16 h-16 rounded-full bg-ai-100 flex items-center justify-center mx-auto;
}

.welcome-title {
  @apply text-xl font-bold text-neutral-900;
}

.welcome-message {
  @apply text-neutral-600 leading-relaxed;
}

.suggestions-grid {
  @apply grid grid-cols-1 gap-2 mt-6;
}

.suggestion-card {
  @apply flex items-start gap-3 p-3 rounded-lg border border-neutral-200 hover:border-ai-300 hover:bg-ai-50 transition-all duration-200 text-left focus:outline-none focus:ring-2 focus:ring-ai-500;
}

.suggestion-icon {
  @apply w-8 h-8 rounded-lg bg-ai-100 flex items-center justify-center flex-shrink-0 text-ai-600;
}

.suggestion-content {
  @apply flex-1 min-w-0;
}

.suggestion-title {
  @apply font-semibold text-neutral-900 text-sm;
}

.suggestion-description {
  @apply text-neutral-600 text-xs mt-1;
}

/* Typing Indicator */
.typing-indicator {
  @apply flex items-end gap-2;
}

.typing-avatar {
  @apply w-6 h-6 rounded-full bg-ai-100 flex items-center justify-center;
}

.typing-dots {
  @apply flex items-center gap-1 bg-neutral-100 rounded-2xl px-3 py-2;
}

.typing-dot {
  @apply w-2 h-2 bg-neutral-400 rounded-full;
  animation: typing-bounce 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dot:nth-child(2) {
  animation-delay: -0.16s;
}

/* Quick Replies */
.quick-replies {
  @apply p-4 border-t border-neutral-200 bg-neutral-50;
}

.quick-reply-btn {
  @apply inline-block bg-white border border-neutral-300 text-neutral-700 px-3 py-1.5 rounded-full text-sm hover:bg-neutral-100 hover:border-neutral-400 transition-colors mr-2 mb-2 focus:outline-none focus:ring-2 focus:ring-primary-500;
}

/* Input Area */
.input-area {
  @apply p-4 border-t border-neutral-200 bg-white;
}

.message-form {
  @apply space-y-2;
}

.input-container {
  @apply relative flex items-end gap-2;
}

.message-input {
  @apply flex-1 px-3 py-2 border border-neutral-300 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-ai-500 focus:border-transparent transition-all duration-200 max-h-32;
  line-height: 1.5;
}

.input-actions {
  @apply flex items-end gap-2;
}

.input-action-btn {
  @apply w-8 h-8 rounded-full bg-neutral-100 hover:bg-neutral-200 flex items-center justify-center text-neutral-600 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500;
}

.send-btn {
  @apply w-8 h-8 rounded-full flex items-center justify-center transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2;
}

.send-btn-active {
  @apply bg-ai-600 hover:bg-ai-700 text-white focus:ring-ai-500;
}

.send-btn-disabled {
  @apply bg-neutral-200 text-neutral-400 cursor-not-allowed;
}

/* Animations */
@keyframes pulse-gentle {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

@keyframes typing-bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* Transitions */
.scale-enter-active,
.scale-leave-active {
  transition: all 0.3s ease;
}

.scale-enter-from,
.scale-leave-to {
  transform: scale(0);
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

.bounce-enter-active {
  animation: bounce 0.5s ease;
}

@keyframes bounce {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}
</style>