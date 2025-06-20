<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click="handleBackdropClick"
      >
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black bg-opacity-50" />
        
        <!-- Modal container -->
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <Transition
            enter-active-class="transition ease-out duration-300"
            enter-from-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to-class="opacity-100 translate-y-0 sm:scale-100"
            leave-active-class="transition ease-in duration-200"
            leave-from-class="opacity-100 translate-y-0 sm:scale-100"
            leave-to-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <div
              v-if="modelValue"
              ref="modalRef"
              :class="modalClasses"
              @click.stop
            >
              <!-- Header -->
              <div v-if="$slots.header || title || showCloseButton" class="flex items-center justify-between p-6 border-b border-gray-200">
                <div>
                  <slot name="header">
                    <h3 v-if="title" class="text-lg font-medium text-gray-900">
                      {{ title }}
                    </h3>
                  </slot>
                </div>
                
                <button
                  v-if="showCloseButton"
                  type="button"
                  class="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-md p-1"
                  @click="close"
                >
                  <XMarkIcon class="h-6 w-6" />
                </button>
              </div>
              
              <!-- Body -->
              <div :class="bodyClasses">
                <slot />
              </div>
              
              <!-- Footer -->
              <div v-if="$slots.footer" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
                <slot name="footer" />
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

interface Props {
  modelValue: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full'
  showCloseButton?: boolean
  closeOnBackdrop?: boolean
  persistent?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  showCloseButton: true,
  closeOnBackdrop: true,
  persistent: false
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  close: []
  open: []
}>()

const modalRef = ref<HTMLElement>()

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'max-w-md'
    case 'md':
      return 'max-w-lg'
    case 'lg':
      return 'max-w-2xl'
    case 'xl':
      return 'max-w-4xl'
    case '2xl':
      return 'max-w-6xl'
    case 'full':
      return 'max-w-none mx-4'
    default:
      return 'max-w-lg'
  }
})

const modalClasses = computed(() => {
  return [
    'relative w-full bg-white rounded-lg shadow-xl transform transition-all',
    sizeClasses.value
  ].join(' ')
})

const bodyClasses = computed(() => {
  return props.$slots?.footer ? 'p-6' : 'p-6'
})

const close = () => {
  if (!props.persistent) {
    emit('update:modelValue', false)
    emit('close')
  }
}

const handleBackdropClick = () => {
  if (props.closeOnBackdrop) {
    close()
  }
}

// Focus management
watch(() => props.modelValue, async (isOpen) => {
  if (isOpen) {
    emit('open')
    await nextTick()
    // Focus the modal for accessibility
    modalRef.value?.focus()
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden'
  } else {
    // Restore body scroll
    document.body.style.overflow = ''
  }
})

// Keyboard event handling
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.modelValue) {
    close()
  }
}

// Add keyboard event listener when modal is open
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    document.addEventListener('keydown', handleKeydown)
  } else {
    document.removeEventListener('keydown', handleKeydown)
  }
})
</script>