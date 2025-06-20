<template>
  <span :class="badgeClasses">
    <component
      v-if="icon"
      :is="icon"
      :class="iconClasses"
    />
    <slot />
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'sm' | 'md' | 'lg'
  icon?: any
  dot?: boolean
  removable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  dot: false,
  removable: false
})

const emit = defineEmits<{
  remove: []
}>()

const baseClasses = 'inline-flex items-center font-medium rounded-full'

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'primary':
      return 'bg-primary-100 text-primary-800'
    case 'secondary':
      return 'bg-gray-100 text-gray-800'
    case 'success':
      return 'bg-success-100 text-success-800'
    case 'warning':
      return 'bg-warning-100 text-warning-800'
    case 'danger':
      return 'bg-danger-100 text-danger-800'
    case 'info':
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-primary-100 text-primary-800'
  }
})

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'px-2 py-0.5 text-xs'
    case 'md':
      return 'px-2.5 py-0.5 text-sm'
    case 'lg':
      return 'px-3 py-1 text-sm'
    default:
      return 'px-2.5 py-0.5 text-sm'
  }
})

const badgeClasses = computed(() => {
  return [
    baseClasses,
    variantClasses.value,
    sizeClasses.value
  ].join(' ')
})

const iconClasses = computed(() => {
  const baseIconClasses = 'flex-shrink-0'
  
  if (props.size === 'sm') {
    return `${baseIconClasses} h-3 w-3 ${props.$slots.default ? 'mr-1' : ''}`
  } else if (props.size === 'lg') {
    return `${baseIconClasses} h-4 w-4 ${props.$slots.default ? 'mr-1.5' : ''}`
  } else {
    return `${baseIconClasses} h-3.5 w-3.5 ${props.$slots.default ? 'mr-1' : ''}`
  }
})
</script>