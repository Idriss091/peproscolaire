<template>
  <Teleport to="body">
    <div
      v-if="visible"
      :class="toastContainerClasses"
      class="toast-container"
    >
      <Transition
        enter-active-class="animate-slide-in-up"
        leave-active-class="animate-slide-out-down"
      >
        <div
          v-if="visible"
          :class="toastClasses"
          class="toast"
          @click="handleClick"
        >
          <div class="flex items-start gap-3">
            <!-- Icône -->
            <div class="flex-shrink-0">
              <component
                :is="iconComponent"
                :class="iconClasses"
                class="h-5 w-5"
              />
            </div>

            <!-- Contenu -->
            <div class="flex-1 min-w-0">
              <h4 v-if="title" class="toast-title">
                {{ title }}
              </h4>
              <p class="toast-message">
                {{ message }}
              </p>
              
              <!-- Actions -->
              <div v-if="actions.length > 0" class="mt-2 flex gap-2">
                <button
                  v-for="action in actions"
                  :key="action.label"
                  @click="handleAction(action)"
                  :class="action.variant ? `btn-${action.variant}` : 'btn-ghost'"
                  class="btn btn-xs"
                >
                  {{ action.label }}
                </button>
              </div>
            </div>

            <!-- Bouton de fermeture -->
            <button
              v-if="closable"
              @click="close"
              class="close-button"
              aria-label="Fermer"
            >
              <XMarkIcon class="h-4 w-4" />
            </button>
          </div>

          <!-- Barre de progression pour auto-close -->
          <div
            v-if="autoClose && showProgress"
            class="progress-bar"
            :style="{ animationDuration: `${duration}ms` }"
          />
        </div>
      </Transition>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  XMarkIcon,
  SparklesIcon
} from '@heroicons/vue/24/outline'

interface ToastAction {
  label: string
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger'
  handler: () => void
}

interface Props {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'ai'
  title?: string
  message: string
  position?: 'top-right' | 'top-left' | 'top-center' | 'bottom-right' | 'bottom-left' | 'bottom-center'
  closable?: boolean
  autoClose?: boolean
  duration?: number
  showProgress?: boolean
  clickable?: boolean
  actions?: ToastAction[]
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'info',
  position: 'top-right',
  closable: true,
  autoClose: true,
  duration: 5000,
  showProgress: false,
  clickable: false,
  actions: () => []
})

interface Emits {
  close: []
  click: []
}

const emit = defineEmits<Emits>()

const visible = ref(true)
let autoCloseTimer: number | null = null

// Auto-close logic
onMounted(() => {
  if (props.autoClose) {
    autoCloseTimer = window.setTimeout(() => {
      close()
    }, props.duration)
  }
})

onUnmounted(() => {
  if (autoCloseTimer) {
    clearTimeout(autoCloseTimer)
  }
})

// Computed classes
const toastContainerClasses = computed(() => [
  'toast-container',
  `toast-${props.position}`
])

const toastClasses = computed(() => [
  'toast',
  `toast-${props.variant}`,
  {
    'cursor-pointer': props.clickable
  }
])

const iconComponent = computed(() => {
  const icons = {
    success: CheckCircleIcon,
    warning: ExclamationTriangleIcon,
    danger: ExclamationCircleIcon,
    info: InformationCircleIcon,
    ai: SparklesIcon
  }
  return icons[props.variant] || InformationCircleIcon
})

const iconClasses = computed(() => {
  const classes = {
    success: 'text-success-600',
    warning: 'text-warning-600',
    danger: 'text-danger-600',
    info: 'text-info-600',
    ai: 'text-ai-600'
  }
  return classes[props.variant] || 'text-neutral-600'
})

// Methods
const close = () => {
  visible.value = false
  if (autoCloseTimer) {
    clearTimeout(autoCloseTimer)
  }
  emit('close')
}

const handleClick = () => {
  if (props.clickable) {
    emit('click')
  }
}

const handleAction = (action: ToastAction) => {
  action.handler()
  close()
}
</script>

<style scoped>
.toast-container {
  @apply fixed z-50 p-4 pointer-events-none;
}

.toast-top-right {
  @apply top-0 right-0;
}

.toast-top-left {
  @apply top-0 left-0;
}

.toast-top-center {
  @apply top-0 left-1/2 -translate-x-1/2;
}

.toast-bottom-right {
  @apply bottom-0 right-0;
}

.toast-bottom-left {
  @apply bottom-0 left-0;
}

.toast-bottom-center {
  @apply bottom-0 left-1/2 -translate-x-1/2;
}

.toast {
  @apply relative bg-white rounded-lg border border-neutral-200 p-4 max-w-sm pointer-events-auto transition-all duration-200;
  box-shadow: var(--shadow-lg);
}

.toast-success {
  @apply border-success-200 bg-success-50;
}

.toast-warning {
  @apply border-warning-200 bg-warning-50;
}

.toast-danger {
  @apply border-danger-200 bg-danger-50;
}

.toast-info {
  @apply border-info-200 bg-info-50;
}

.toast-ai {
  @apply border-ai-200 bg-ai-50;
}

.toast-title {
  @apply font-semibold text-sm text-neutral-900 mb-1;
}

.toast-message {
  @apply text-sm text-neutral-700 leading-relaxed;
}

.close-button {
  @apply flex-shrink-0 text-neutral-400 hover:text-neutral-600 focus:outline-none focus:text-neutral-600 transition-colors rounded p-1;
}

.progress-bar {
  @apply absolute bottom-0 left-0 h-1 bg-current opacity-30 rounded-b-lg;
  width: 100%;
  animation: progress linear forwards;
}

@keyframes progress {
  from {
    width: 100%;
  }
  to {
    width: 0%;
  }
}

@keyframes slideInUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.animate-slide-in-up {
  animation: slideInUp 0.3s ease-out;
}

.animate-slide-out-down {
  animation: slideInUp 0.2s ease-in reverse;
}
</style>