<template>
  <div ref="dropdownRef" class="dropdown-container">
    <!-- Trigger -->
    <div
      @click="toggle"
      @keydown.enter="toggle"
      @keydown.space.prevent="toggle"
      @keydown.escape="close"
      :class="triggerClasses"
      class="dropdown-trigger"
      role="button"
      :aria-expanded="isOpen"
      :aria-haspopup="true"
      tabindex="0"
    >
      <slot name="trigger" :isOpen="isOpen" :toggle="toggle">
        <div class="flex items-center justify-between gap-2">
          <span>{{ triggerText }}</span>
          <ChevronDownIcon
            :class="[
              'h-4 w-4 transition-transform duration-200',
              { 'rotate-180': isOpen }
            ]"
          />
        </div>
      </slot>
    </div>

    <!-- Dropdown Menu -->
    <Teleport to="body">
      <Transition
        enter-active-class="animate-fade-in-scale"
        leave-active-class="animate-fade-out"
      >
        <div
          v-if="isOpen"
          ref="menuRef"
          :style="menuPosition"
          :class="menuClasses"
          class="dropdown-menu"
          role="menu"
          @keydown.escape="close"
          @keydown.arrow-down.prevent="navigateDown"
          @keydown.arrow-up.prevent="navigateUp"
          @keydown.enter="selectFocused"
        >
          <!-- Header -->
          <div v-if="$slots.header" class="dropdown-header">
            <slot name="header" />
          </div>

          <!-- Menu Items -->
          <div class="dropdown-items">
            <slot :close="close" :isOpen="isOpen" />
          </div>

          <!-- Footer -->
          <div v-if="$slots.footer" class="dropdown-footer">
            <slot name="footer" />
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ChevronDownIcon } from '@heroicons/vue/24/outline'

interface Props {
  modelValue?: boolean
  placement?: 'bottom-start' | 'bottom-end' | 'top-start' | 'top-end' | 'bottom' | 'top'
  offset?: number
  triggerText?: string
  disabled?: boolean
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'ghost' | 'outline'
  width?: 'auto' | 'trigger' | 'screen'
  maxHeight?: string
  closeOnSelect?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placement: 'bottom-start',
  offset: 8,
  triggerText: 'Options',
  disabled: false,
  size: 'md',
  variant: 'default',
  width: 'auto',
  maxHeight: '20rem',
  closeOnSelect: true
})

interface Emits {
  'update:modelValue': [value: boolean]
  open: []
  close: []
}

const emit = defineEmits<Emits>()

const dropdownRef = ref<HTMLElement>()
const menuRef = ref<HTMLElement>()
const isOpen = ref(props.modelValue || false)
const menuPosition = ref({})
const focusedIndex = ref(-1)

// Watch modelValue changes
watch(() => props.modelValue, (newValue) => {
  isOpen.value = newValue || false
})

// Watch isOpen changes
watch(isOpen, (newValue) => {
  emit('update:modelValue', newValue)
  if (newValue) {
    emit('open')
    nextTick(() => {
      calculatePosition()
      focusFirstItem()
    })
  } else {
    emit('close')
    focusedIndex.value = -1
  }
})

// Computed classes
const triggerClasses = computed(() => [
  'dropdown-trigger',
  `dropdown-trigger-${props.size}`,
  `dropdown-trigger-${props.variant}`,
  {
    'dropdown-trigger-disabled': props.disabled,
    'dropdown-trigger-open': isOpen.value
  }
])

const menuClasses = computed(() => [
  'dropdown-menu',
  `dropdown-menu-${props.size}`,
  {
    [`w-${props.width}`]: props.width !== 'auto'
  }
])

// Methods
const toggle = () => {
  if (props.disabled) return
  isOpen.value = !isOpen.value
}

const open = () => {
  if (props.disabled) return
  isOpen.value = true
}

const close = () => {
  isOpen.value = false
}

const calculatePosition = () => {
  if (!dropdownRef.value || !menuRef.value) return

  const trigger = dropdownRef.value.getBoundingClientRect()
  const menu = menuRef.value.getBoundingClientRect()
  const viewport = {
    width: window.innerWidth,
    height: window.innerHeight
  }

  let top = 0
  let left = 0

  // Calculate position based on placement
  switch (props.placement) {
    case 'bottom-start':
      top = trigger.bottom + props.offset
      left = trigger.left
      break
    case 'bottom-end':
      top = trigger.bottom + props.offset
      left = trigger.right - menu.width
      break
    case 'bottom':
      top = trigger.bottom + props.offset
      left = trigger.left + (trigger.width - menu.width) / 2
      break
    case 'top-start':
      top = trigger.top - menu.height - props.offset
      left = trigger.left
      break
    case 'top-end':
      top = trigger.top - menu.height - props.offset
      left = trigger.right - menu.width
      break
    case 'top':
      top = trigger.top - menu.height - props.offset
      left = trigger.left + (trigger.width - menu.width) / 2
      break
  }

  // Adjust for viewport boundaries
  if (left + menu.width > viewport.width) {
    left = viewport.width - menu.width - 16
  }
  if (left < 16) {
    left = 16
  }
  if (top + menu.height > viewport.height) {
    top = trigger.top - menu.height - props.offset
  }
  if (top < 16) {
    top = trigger.bottom + props.offset
  }

  // Set width if needed
  let width = ''
  if (props.width === 'trigger') {
    width = `${trigger.width}px`
  } else if (props.width === 'screen') {
    width = `${viewport.width - 32}px`
    left = 16
  }

  menuPosition.value = {
    position: 'fixed',
    top: `${top}px`,
    left: `${left}px`,
    width,
    maxHeight: props.maxHeight,
    zIndex: 'var(--z-dropdown)'
  }
}

// Keyboard navigation
const focusFirstItem = () => {
  const items = menuRef.value?.querySelectorAll('[role="menuitem"]')
  if (items && items.length > 0) {
    focusedIndex.value = 0
    ;(items[0] as HTMLElement).focus()
  }
}

const navigateDown = () => {
  const items = menuRef.value?.querySelectorAll('[role="menuitem"]')
  if (!items) return
  
  focusedIndex.value = Math.min(focusedIndex.value + 1, items.length - 1)
  ;(items[focusedIndex.value] as HTMLElement).focus()
}

const navigateUp = () => {
  const items = menuRef.value?.querySelectorAll('[role="menuitem"]')
  if (!items) return
  
  focusedIndex.value = Math.max(focusedIndex.value - 1, 0)
  ;(items[focusedIndex.value] as HTMLElement).focus()
}

const selectFocused = () => {
  const items = menuRef.value?.querySelectorAll('[role="menuitem"]')
  if (items && focusedIndex.value >= 0) {
    ;(items[focusedIndex.value] as HTMLElement).click()
  }
}

// Outside click handler
const handleOutsideClick = (event: MouseEvent) => {
  if (!dropdownRef.value?.contains(event.target as Node) && 
      !menuRef.value?.contains(event.target as Node)) {
    close()
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
  window.addEventListener('resize', calculatePosition)
  window.addEventListener('scroll', calculatePosition)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
  window.removeEventListener('resize', calculatePosition)
  window.removeEventListener('scroll', calculatePosition)
})

// Expose methods
defineExpose({
  open,
  close,
  toggle
})
</script>

<style scoped>
.dropdown-container {
  @apply relative inline-block;
}

.dropdown-trigger {
  @apply inline-flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 cursor-pointer;
}

.dropdown-trigger-sm {
  @apply px-2 py-1 text-xs rounded-md;
}

.dropdown-trigger-md {
  @apply px-3 py-2 text-sm rounded-lg;
}

.dropdown-trigger-lg {
  @apply px-4 py-3 text-base rounded-lg;
}

.dropdown-trigger-default {
  @apply bg-white border border-neutral-300 text-neutral-700 hover:bg-neutral-50;
}

.dropdown-trigger-ghost {
  @apply bg-transparent text-neutral-700 hover:bg-neutral-100;
}

.dropdown-trigger-outline {
  @apply bg-transparent border-2 border-neutral-300 text-neutral-700 hover:border-neutral-400;
}

.dropdown-trigger-disabled {
  @apply opacity-50 cursor-not-allowed;
}

.dropdown-trigger-open {
  @apply ring-2 ring-primary-500 ring-offset-2;
}

.dropdown-menu {
  @apply bg-white rounded-lg border border-neutral-200 py-1 overflow-auto;
  box-shadow: var(--shadow-xl);
}

.dropdown-menu-sm {
  @apply text-xs;
}

.dropdown-menu-md {
  @apply text-sm;
}

.dropdown-menu-lg {
  @apply text-base;
}

.dropdown-header {
  @apply px-3 py-2 border-b border-neutral-200 bg-neutral-50;
}

.dropdown-items {
  @apply py-1;
}

.dropdown-footer {
  @apply px-3 py-2 border-t border-neutral-200 bg-neutral-50;
}

/* Menu item styles (for slotted content) */
:deep(.dropdown-item) {
  @apply block w-full px-3 py-2 text-left text-neutral-700 hover:bg-neutral-100 hover:text-neutral-900 focus:bg-neutral-100 focus:text-neutral-900 focus:outline-none transition-colors duration-150 cursor-pointer;
}

:deep(.dropdown-item[disabled]) {
  @apply opacity-50 cursor-not-allowed hover:bg-transparent hover:text-neutral-700;
}

:deep(.dropdown-item-danger) {
  @apply text-danger-700 hover:bg-danger-50 hover:text-danger-900 focus:bg-danger-50 focus:text-danger-900;
}

:deep(.dropdown-divider) {
  @apply border-t border-neutral-200 my-1;
}
</style>