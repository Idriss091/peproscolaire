<template>
  <Transition
    enter-active-class="animate-fade-in-scale"
    leave-active-class="animate-fade-out"
  >
    <div
      v-if="visible"
      :class="alertClasses"
      class="alert"
      role="alert"
    >
      <div class="flex items-start gap-3">
        <!-- Icône -->
        <div class="flex-shrink-0 pt-0.5">
          <component
            :is="iconComponent"
            :class="iconClasses"
            class="h-5 w-5"
          />
        </div>

        <!-- Contenu -->
        <div class="flex-1 min-w-0">
          <h4 v-if="title" :class="titleClasses" class="alert-title">
            {{ title }}
          </h4>
          <div :class="messageClasses" class="alert-message">
            <slot>{{ message }}</slot>
          </div>
          
          <!-- Actions -->
          <div v-if="$slots.actions || showDefaultActions" class="mt-3 flex gap-2">
            <slot name="actions">
              <button
                v-if="dismissible"
                @click="dismiss"
                class="btn btn-sm btn-ghost"
              >
                Fermer
              </button>
            </slot>
          </div>
        </div>

        <!-- Bouton de fermeture -->
        <button
          v-if="closable"
          @click="dismiss"
          :class="closeButtonClasses"
          class="close-button"
          aria-label="Fermer"
        >
          <XMarkIcon class="h-4 w-4" />
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  XMarkIcon,
  SparklesIcon
} from '@heroicons/vue/24/outline'

interface Props {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'ai' | 'neutral'
  title?: string
  message?: string
  closable?: boolean
  dismissible?: boolean
  showDefaultActions?: boolean
  autoClose?: boolean
  autoCloseDelay?: number
  size?: 'sm' | 'md' | 'lg'
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  shadow?: boolean
  border?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'info',
  closable: true,
  dismissible: false,
  showDefaultActions: false,
  autoClose: false,
  autoCloseDelay: 5000,
  size: 'md',
  rounded: 'lg',
  shadow: true,
  border: true
})

interface Emits {
  dismiss: []
  close: []
}

const emit = defineEmits<Emits>()

const visible = ref(true)

// Auto-close logic
onMounted(() => {
  if (props.autoClose) {
    setTimeout(() => {
      dismiss()
    }, props.autoCloseDelay)
  }
})

// Computed classes
const alertClasses = computed(() => [
  'alert',
  `alert-${props.variant}`,
  `alert-${props.size}`,
  {
    'alert-shadow': props.shadow,
    'alert-border': props.border,
    [`rounded-${props.rounded}`]: props.rounded !== 'none'
  }
])

const iconComponent = computed(() => {
  const icons = {
    success: CheckCircleIcon,
    warning: ExclamationTriangleIcon,
    danger: ExclamationCircleIcon,
    info: InformationCircleIcon,
    ai: SparklesIcon,
    neutral: InformationCircleIcon
  }
  return icons[props.variant] || InformationCircleIcon
})

const iconClasses = computed(() => {
  const classes = {
    success: 'text-success-600',
    warning: 'text-warning-600',
    danger: 'text-danger-600',
    info: 'text-info-600',
    ai: 'text-ai-600',
    neutral: 'text-neutral-600'
  }
  return classes[props.variant] || 'text-neutral-600'
})

const titleClasses = computed(() => {
  const classes = {
    success: 'text-success-800',
    warning: 'text-warning-800',
    danger: 'text-danger-800',
    info: 'text-info-800',
    ai: 'text-ai-800',
    neutral: 'text-neutral-800'
  }
  return `font-semibold ${classes[props.variant] || 'text-neutral-800'}`
})

const messageClasses = computed(() => {
  const classes = {
    success: 'text-success-700',
    warning: 'text-warning-700',
    danger: 'text-danger-700',
    info: 'text-info-700',
    ai: 'text-ai-700',
    neutral: 'text-neutral-700'
  }
  return `text-sm ${classes[props.variant] || 'text-neutral-700'}`
})

const closeButtonClasses = computed(() => {
  const classes = {
    success: 'text-success-600 hover:text-success-800',
    warning: 'text-warning-600 hover:text-warning-800',
    danger: 'text-danger-600 hover:text-danger-800',
    info: 'text-info-600 hover:text-info-800',
    ai: 'text-ai-600 hover:text-ai-800',
    neutral: 'text-neutral-600 hover:text-neutral-800'
  }
  return `focus-ring rounded-md p-1 transition-colors ${classes[props.variant] || 'text-neutral-600 hover:text-neutral-800'}`
})

// Methods
const dismiss = () => {
  visible.value = false
  emit('dismiss')
  emit('close')
}
</script>

<style scoped>
.alert {
  @apply p-4 transition-all duration-200;
}

.alert-sm {
  @apply p-3;
}

.alert-lg {
  @apply p-6;
}

.alert-shadow {
  box-shadow: var(--shadow-md);
}

.alert-border {
  @apply border;
}

/* Variantes */
.alert-success {
  @apply bg-success-50 border-success-200;
}

.alert-warning {
  @apply bg-warning-50 border-warning-200;
}

.alert-danger {
  @apply bg-danger-50 border-danger-200;
}

.alert-info {
  @apply bg-info-50 border-info-200;
}

.alert-ai {
  @apply bg-ai-50 border-ai-200;
}

.alert-neutral {
  @apply bg-neutral-50 border-neutral-200;
}

.alert-title {
  @apply mb-1 text-sm;
}

.alert-message {
  @apply leading-relaxed;
}

.close-button {
  @apply flex-shrink-0;
}

/* Animations */
.animate-fade-out {
  @apply transition-all duration-200 ease-in;
  transform: scale(0.95);
  opacity: 0;
}
</style>