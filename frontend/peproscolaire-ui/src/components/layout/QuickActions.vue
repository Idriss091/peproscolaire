<template>
  <BaseDropdown placement="bottom-end" :width="320">
    <template #trigger>
      <button
        class="quick-actions-trigger"
        aria-label="Actions rapides"
      >
        <PlusIcon class="h-5 w-5" />
      </button>
    </template>
    
    <div class="quick-actions-panel">
      <!-- Header -->
      <div class="panel-header">
        <h3 class="panel-title">Actions rapides</h3>
        <span class="panel-subtitle">Accès rapide aux fonctionnalités principales</span>
      </div>
      
      <!-- Actions grid -->
      <div class="actions-grid">
        <button
          v-for="action in quickActions"
          :key="action.id"
          @click="handleAction(action)"
          :class="actionClasses(action)"
          class="action-item"
        >
          <div class="action-icon">
            <component :is="action.icon" class="h-5 w-5" />
          </div>
          <div class="action-content">
            <span class="action-title">{{ action.title }}</span>
            <span class="action-description">{{ action.description }}</span>
          </div>
          <div v-if="action.badge" class="action-badge">
            {{ action.badge }}
          </div>
        </button>
      </div>
      
      <!-- Divider -->
      <div class="divider" />
      
      <!-- Raccourcis clavier -->
      <div class="shortcuts-section">
        <h4 class="shortcuts-title">Raccourcis clavier</h4>
        <div class="shortcuts-list">
          <div
            v-for="shortcut in keyboardShortcuts"
            :key="shortcut.id"
            class="shortcut-item"
          >
            <span class="shortcut-action">{{ shortcut.action }}</span>
            <div class="shortcut-keys">
              <kbd
                v-for="key in shortcut.keys"
                :key="key"
                class="shortcut-key"
              >
                {{ key }}
              </kbd>
            </div>
          </div>
        </div>
      </div>
    </div>
  </BaseDropdown>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  PlusIcon,
  PencilIcon,
  DocumentPlusIcon,
  CalendarPlusIcon,
  UserPlusIcon,
  ChatBubbleLeftRightIcon,
  ClipboardDocumentListIcon,
  AcademicCapIcon,
  PhotoIcon,
  MegaphoneIcon
} from '@heroicons/vue/24/outline'
import BaseDropdown from '@/components/ui/BaseDropdown.vue'
import { useAuthStore } from '@/stores/auth'

interface QuickAction {
  id: string
  title: string
  description: string
  icon: any
  action: string
  url?: string
  color: string
  roles?: string[]
  badge?: string | number
}

interface KeyboardShortcut {
  id: string
  action: string
  keys: string[]
}

const router = useRouter()
const authStore = useAuthStore()

const quickActions = computed(() => {
  const actions: QuickAction[] = [
    {
      id: 'new-note',
      title: 'Nouvelle note',
      description: 'Créer une note rapide',
      icon: PencilIcon,
      action: 'create_note',
      url: '/notes/nouvelle',
      color: 'primary'
    },
    {
      id: 'new-assignment',
      title: 'Nouveau devoir',
      description: 'Créer un devoir',
      icon: ClipboardDocumentListIcon,
      action: 'create_assignment',
      url: '/devoirs/nouveau',
      color: 'education',
      roles: ['teacher']
    },
    {
      id: 'new-event',
      title: 'Nouvel événement',
      description: 'Ajouter un événement au calendrier',
      icon: CalendarPlusIcon,
      action: 'create_event',
      url: '/calendrier/nouveau',
      color: 'secondary'
    },
    {
      id: 'send-message',
      title: 'Envoyer un message',
      description: 'Contacter un utilisateur',
      icon: ChatBubbleLeftRightIcon,
      action: 'send_message',
      url: '/messages/nouveau',
      color: 'info'
    },
    {
      id: 'add-student',
      title: 'Ajouter un élève',
      description: 'Inscrire un nouvel élève',
      icon: UserPlusIcon,
      action: 'add_student',
      url: '/eleves/nouveau',
      color: 'success',
      roles: ['admin', 'teacher']
    },
    {
      id: 'upload-document',
      title: 'Téléverser un document',
      description: 'Ajouter un fichier',
      icon: DocumentPlusIcon,
      action: 'upload_document',
      color: 'warning'
    },
    {
      id: 'grade-assignment',
      title: 'Noter un devoir',
      description: 'Évaluer les devoirs',
      icon: AcademicCapIcon,
      action: 'grade_assignment',
      url: '/notation',
      color: 'education',
      roles: ['teacher'],
      badge: '5' // Exemple: 5 devoirs en attente
    },
    {
      id: 'share-photo',
      title: 'Partager une photo',
      description: 'Galerie de classe',
      icon: PhotoIcon,
      action: 'share_photo',
      color: 'purple'
    },
    {
      id: 'make-announcement',
      title: 'Faire une annonce',
      description: 'Communiquer avec la classe',
      icon: MegaphoneIcon,
      action: 'make_announcement',
      url: '/annonces/nouvelle',
      color: 'danger',
      roles: ['teacher', 'admin']
    }
  ]
  
  // Filtrer par rôle utilisateur
  const userRole = authStore.currentUser?.role
  return actions.filter(action => 
    !action.roles || action.roles.includes(userRole)
  )
})

const keyboardShortcuts = computed(() => [
  {
    id: 'search',
    action: 'Recherche globale',
    keys: ['⌘', 'K']
  },
  {
    id: 'new-note',
    action: 'Nouvelle note',
    keys: ['⌘', 'N']
  },
  {
    id: 'messages',
    action: 'Messages',
    keys: ['⌘', 'M']
  },
  {
    id: 'calendar',
    action: 'Calendrier',
    keys: ['⌘', 'C']
  }
])

const actionClasses = (action: QuickAction) => [
  'action-item',
  `action-${action.color}`
]

const handleAction = async (action: QuickAction) => {
  try {
    switch (action.action) {
      case 'upload_document':
        // Déclencher l'upload de fichier
        const input = document.createElement('input')
        input.type = 'file'
        input.multiple = true
        input.onchange = handleFileUpload
        input.click()
        break
        
      case 'share_photo':
        // Déclencher l'upload de photo
        const photoInput = document.createElement('input')
        photoInput.type = 'file'
        photoInput.accept = 'image/*'
        photoInput.multiple = true
        photoInput.onchange = handlePhotoUpload
        photoInput.click()
        break
        
      default:
        // Navigation standard
        if (action.url) {
          router.push(action.url)
        }
    }
  } catch (error) {
    console.error('Erreur action rapide:', error)
  }
}

const handleFileUpload = (event: Event) => {
  const files = (event.target as HTMLInputElement).files
  if (files) {
    // TODO: Implémenter l'upload de fichiers
    console.log('Upload fichiers:', files)
  }
}

const handlePhotoUpload = (event: Event) => {
  const files = (event.target as HTMLInputElement).files
  if (files) {
    // TODO: Implémenter l'upload de photos
    console.log('Upload photos:', files)
  }
}
</script>

<style scoped>
.quick-actions-trigger {
  @apply w-10 h-10 rounded-lg bg-primary-600 hover:bg-primary-700 flex items-center justify-center text-white transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2;
}

.quick-actions-panel {
  @apply max-h-96 overflow-y-auto;
}

.panel-header {
  @apply p-4 border-b border-gray-200;
}

.panel-title {
  @apply font-semibold text-gray-900;
}

.panel-subtitle {
  @apply text-sm text-gray-600 mt-1;
}

.actions-grid {
  @apply p-2;
}

.action-item {
  @apply flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors text-left w-full focus:outline-none focus:ring-2 focus:ring-blue-500 group;
}

.action-icon {
  @apply w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0;
}

.action-primary .action-icon {
  @apply bg-primary-100 text-blue-600 group-hover:bg-primary-200;
}

.action-education .action-icon {
  @apply bg-education-100 text-education-600 group-hover:bg-education-200;
}

.action-secondary .action-icon {
  @apply bg-secondary-100 text-secondary-600 group-hover:bg-secondary-200;
}

.action-info .action-icon {
  @apply bg-info-100 text-info-600 group-hover:bg-info-200;
}

.action-success .action-icon {
  @apply bg-green-100 text-green-600 group-hover:bg-green-200;
}

.action-warning .action-icon {
  @apply bg-warning-100 text-warning-600 group-hover:bg-warning-200;
}

.action-danger .action-icon {
  @apply bg-red-100 text-red-600 group-hover:bg-red-200;
}

.action-purple .action-icon {
  @apply bg-purple-100 text-purple-600 group-hover:bg-purple-200;
}

.action-content {
  @apply flex-1 min-w-0;
}

.action-title {
  @apply block font-medium text-gray-900 text-sm;
}

.action-description {
  @apply block text-gray-600 text-xs mt-0.5;
}

.action-badge {
  @apply px-2 py-1 bg-red-100 text-red-800 text-xs font-semibold rounded-full;
}

.divider {
  @apply border-t border-gray-200 my-2;
}

.shortcuts-section {
  @apply p-4 bg-gray-50;
}

.shortcuts-title {
  @apply font-medium text-gray-900 text-sm mb-3;
}

.shortcuts-list {
  @apply space-y-2;
}

.shortcut-item {
  @apply flex items-center justify-between;
}

.shortcut-action {
  @apply text-sm text-gray-700;
}

.shortcut-keys {
  @apply flex items-center gap-1;
}

.shortcut-key {
  @apply px-1.5 py-0.5 text-xs font-mono bg-white border border-gray-300 rounded text-gray-600;
}
</style>