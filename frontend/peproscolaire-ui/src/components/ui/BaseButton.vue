<template>
  <component
    :is="to ? 'router-link' : href ? 'a' : 'button'"
    :to="to"
    :href="href"
    :type="!to && !href ? type : undefined"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="handleClick"
  >
    <span v-if="loading" class="absolute inset-0 flex items-center justify-center">
      <svg 
        class="animate-spin h-5 w-5" 
        :class="loadingColorClass"
        xmlns="http://www.w3.org/2000/svg" 
        fill="none" 
        viewBox="0 0 24 24"
      >
        <circle 
          class="opacity-25" 
          cx="12" 
          cy="12" 
          r="10" 
          stroke="currentColor" 
          stroke-width="4"
        />
        <path 
          class="opacity-75" 
          fill="currentColor" 
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </span>
    <span 
      class="flex items-center justify-center"
      :class="{ 'opacity-0': loading }"
    >
      <component 
        v-if="icon && iconPosition === 'left'" 
        :is="icon" 
        class="flex-shrink-0 -ml-1 mr-2"
        :class="iconSizeClass"
      />
      <slot>{{ label }}</slot>
      <component 
        v-if="icon && iconPosition === 'right'" 
        :is="icon" 
        class="flex-shrink-0 ml-2 -mr-1"
        :class="iconSizeClass"
      />
    </span>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'
import type { RouteLocationRaw } from 'vue-router'

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'success' | 'warning' | 'ghost' | 'link'
type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

interface Props {
  variant?: ButtonVariant
  size?: ButtonSize
  type?: 'button' | 'submit' | 'reset'
  disabled?: boolean
  loading?: boolean
  fullWidth?: boolean
  rounded?: boolean
  icon?: Component
  iconPosition?: 'left' | 'right'
  label?: string
  to?: RouteLocationRaw
  href?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  type: 'button',
  disabled: false,
  loading: false,
  fullWidth: false,
  rounded: false,
  iconPosition: 'left'
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const baseClasses = 'relative inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'

const variantClasses = computed(() => {
  const variants = {
    primary: 'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-500 shadow-sm',
    secondary: 'bg-white text-gray-700 hover:bg-gray-50 focus:ring-indigo-500 border border-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 shadow-sm',
    success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500 shadow-sm',
    warning: 'bg-yellow-500 text-white hover:bg-yellow-600 focus:ring-yellow-500 shadow-sm',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
    link: 'text-indigo-600 hover:text-indigo-500 focus:ring-indigo-500 underline-offset-4 hover:underline'
  }
  return variants[props.variant]
})

const sizeClasses = computed(() => {
  const sizes = {
    xs: 'px-2.5 py-1.5 text-xs',
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-4 py-2 text-base',
    xl: 'px-6 py-3 text-base'
  }
  return sizes[props.size]
})

const roundedClass = computed(() => {
  return props.rounded ? 'rounded-full' : 'rounded-md'
})

const widthClass = computed(() => {
  return props.fullWidth ? 'w-full' : ''
})

const buttonClasses = computed(() => {
  return [
    baseClasses,
    variantClasses.value,
    sizeClasses.value,
    roundedClass.value,
    widthClass.value
  ].join(' ')
})

const iconSizeClass = computed(() => {
  const sizes = {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-5 w-5',
    xl: 'h-6 w-6'
  }
  return sizes[props.size]
})

const loadingColorClass = computed(() => {
  return ['primary', 'danger', 'success', 'warning'].includes(props.variant) 
    ? 'text-white' 
    : 'text-gray-700'
})

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading && !props.to && !props.href) {
    emit('click', event)
  }
}
</script>