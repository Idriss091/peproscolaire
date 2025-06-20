<template>
  <div :class="cardClasses">
    <div v-if="$slots.header || title" :class="headerClasses">
      <slot name="header">
        <h3 v-if="title" class="text-lg font-medium text-gray-900">
          {{ title }}
        </h3>
      </slot>
    </div>
    
    <div :class="bodyClasses">
      <slot />
    </div>
    
    <div v-if="$slots.footer" :class="footerClasses">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
  shadow?: 'none' | 'sm' | 'md' | 'lg'
  border?: boolean
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
}

const props = withDefaults(defineProps<Props>(), {
  padding: 'md',
  shadow: 'md',
  border: true,
  rounded: 'md'
})

const baseClasses = 'bg-white'

const paddingClasses = computed(() => {
  switch (props.padding) {
    case 'none':
      return ''
    case 'sm':
      return 'p-4'
    case 'md':
      return 'p-6'
    case 'lg':
      return 'p-8'
    default:
      return 'p-6'
  }
})

const shadowClasses = computed(() => {
  switch (props.shadow) {
    case 'none':
      return ''
    case 'sm':
      return 'shadow-sm'
    case 'md':
      return 'shadow-md'
    case 'lg':
      return 'shadow-lg'
    default:
      return 'shadow-md'
  }
})

const borderClasses = computed(() => {
  return props.border ? 'border border-gray-200' : ''
})

const roundedClasses = computed(() => {
  switch (props.rounded) {
    case 'none':
      return ''
    case 'sm':
      return 'rounded'
    case 'md':
      return 'rounded-lg'
    case 'lg':
      return 'rounded-xl'
    case 'xl':
      return 'rounded-2xl'
    default:
      return 'rounded-lg'
  }
})

const cardClasses = computed(() => {
  return [
    baseClasses,
    shadowClasses.value,
    borderClasses.value,
    roundedClasses.value,
    props.padding === 'none' ? '' : ''
  ].filter(Boolean).join(' ')
})

const headerClasses = computed(() => {
  const classes = ['border-b border-gray-200']
  
  switch (props.padding) {
    case 'none':
      classes.push('px-6 py-4')
      break
    case 'sm':
      classes.push('px-4 py-3')
      break
    case 'md':
      classes.push('px-6 py-4')
      break
    case 'lg':
      classes.push('px-8 py-5')
      break
    default:
      classes.push('px-6 py-4')
  }
  
  return classes.join(' ')
})

const bodyClasses = computed(() => {
  if (props.padding === 'none') {
    return 'p-0'
  }
  return paddingClasses.value
})

const footerClasses = computed(() => {
  const classes = ['border-t border-gray-200']
  
  switch (props.padding) {
    case 'none':
      classes.push('px-6 py-4')
      break
    case 'sm':
      classes.push('px-4 py-3')
      break
    case 'md':
      classes.push('px-6 py-4')
      break
    case 'lg':
      classes.push('px-8 py-5')
      break
    default:
      classes.push('px-6 py-4')
  }
  
  return classes.join(' ')
})
</script>