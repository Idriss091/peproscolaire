<template>
  <div :class="containerClasses" class="progress-container">
    <!-- Label et valeur -->
    <div v-if="showLabel || showValue" class="flex justify-between items-center mb-2">
      <span v-if="showLabel" :class="labelClasses" class="progress-label">
        {{ label }}
      </span>
      <span v-if="showValue" :class="valueClasses" class="progress-value">
        {{ formattedValue }}
      </span>
    </div>

    <!-- Barre de progression -->
    <div :class="trackClasses" class="progress-track">
      <div
        :class="barClasses"
        class="progress-bar"
        :style="barStyles"
        role="progressbar"
        :aria-valuenow="value"
        :aria-valuemin="min"
        :aria-valuemax="max"
        :aria-valuetext="`${value}%`"
      >
        <!-- Animation de progression -->
        <div
          v-if="animated"
          class="progress-animation"
        />
        
        <!-- Texte dans la barre -->
        <span
          v-if="showValueInBar"
          class="progress-bar-text"
        >
          {{ formattedValue }}
        </span>
      </div>
    </div>

    <!-- Description ou message de statut -->
    <div v-if="$slots.default || statusMessage" class="mt-2">
      <slot>
        <p :class="statusClasses" class="progress-status">
          {{ statusMessage }}
        </p>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  value: number
  min?: number
  max?: number
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'ai' | 'neutral'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  label?: string
  showLabel?: boolean
  showValue?: boolean
  showValueInBar?: boolean
  valueFormat?: 'percentage' | 'fraction' | 'custom'
  customUnit?: string
  animated?: boolean
  striped?: boolean
  rounded?: boolean
  statusMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  min: 0,
  max: 100,
  variant: 'primary',
  size: 'md',
  showLabel: false,
  showValue: false,
  showValueInBar: false,
  valueFormat: 'percentage',
  animated: false,
  striped: false,
  rounded: true
})

// Computed properties
const normalizedValue = computed(() => {
  const range = props.max - props.min
  const adjustedValue = Math.max(props.min, Math.min(props.max, props.value))
  return ((adjustedValue - props.min) / range) * 100
})

const formattedValue = computed(() => {
  switch (props.valueFormat) {
    case 'percentage':
      return `${Math.round(normalizedValue.value)}%`
    case 'fraction':
      return `${props.value}/${props.max}`
    case 'custom':
      return `${props.value}${props.customUnit || ''}`
    default:
      return `${Math.round(normalizedValue.value)}%`
  }
})

const containerClasses = computed(() => [
  'progress-container',
  `progress-${props.size}`
])

const trackClasses = computed(() => [
  'progress-track',
  {
    'rounded-full': props.rounded,
    'rounded-sm': !props.rounded
  }
])

const barClasses = computed(() => [
  'progress-bar',
  `progress-bar-${props.variant}`,
  {
    'progress-bar-striped': props.striped,
    'progress-bar-animated': props.animated,
    'rounded-full': props.rounded,
    'rounded-sm': !props.rounded
  }
])

const barStyles = computed(() => ({
  width: `${normalizedValue.value}%`,
  transition: props.animated ? 'width 0.3s ease-in-out' : 'none'
}))

const labelClasses = computed(() => [
  'text-sm font-medium text-neutral-700'
])

const valueClasses = computed(() => [
  'text-sm font-semibold',
  {
    'text-primary-600': props.variant === 'primary',
    'text-success-600': props.variant === 'success',
    'text-warning-600': props.variant === 'warning',
    'text-danger-600': props.variant === 'danger',
    'text-ai-600': props.variant === 'ai',
    'text-neutral-600': props.variant === 'neutral'
  }
])

const statusClasses = computed(() => [
  'text-xs text-neutral-500'
])
</script>

<style scoped>
.progress-container {
  @apply w-full;
}

.progress-xs {
  @apply text-xs;
}

.progress-xs .progress-track {
  @apply h-1;
}

.progress-sm {
  @apply text-sm;
}

.progress-sm .progress-track {
  @apply h-2;
}

.progress-md .progress-track {
  @apply h-3;
}

.progress-lg .progress-track {
  @apply h-4;
}

.progress-xl .progress-track {
  @apply h-6;
}

.progress-track {
  @apply w-full bg-neutral-200 overflow-hidden;
}

.progress-bar {
  @apply h-full transition-all duration-300 ease-in-out relative overflow-hidden;
}

.progress-bar-primary {
  @apply bg-primary-600;
}

.progress-bar-success {
  @apply bg-success-600;
}

.progress-bar-warning {
  @apply bg-warning-600;
}

.progress-bar-danger {
  @apply bg-danger-600;
}

.progress-bar-ai {
  @apply bg-ai-600;
}

.progress-bar-neutral {
  @apply bg-neutral-600;
}

.progress-bar-striped {
  background-image: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.15) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0.15) 75%,
    transparent 75%,
    transparent
  );
  background-size: 1rem 1rem;
}

.progress-bar-animated .progress-animation {
  @apply absolute inset-0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  animation: progress-shine 1.5s infinite;
}

.progress-bar-striped.progress-bar-animated {
  animation: progress-stripes 1s linear infinite;
}

.progress-bar-text {
  @apply absolute inset-0 flex items-center justify-center text-xs font-medium text-white mix-blend-difference;
}

@keyframes progress-shine {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes progress-stripes {
  0% {
    background-position: 1rem 0;
  }
  100% {
    background-position: 0 0;
  }
}
</style>