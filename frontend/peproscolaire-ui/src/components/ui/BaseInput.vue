<template>
  <div class="space-y-1">
    <label
      v-if="label"
      :for="inputId"
      class="block text-sm font-medium text-gray-700"
    >
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>
    
    <div class="relative">
      <div
        v-if="$slots.prefix"
        class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
      >
        <slot name="prefix" />
      </div>
      
      <input
        :id="inputId"
        v-model="inputValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :class="inputClasses"
        v-bind="$attrs"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
        @input="$emit('input', $event)"
        @change="$emit('change', $event)"
      />
      
      <div
        v-if="$slots.suffix"
        class="absolute inset-y-0 right-0 pr-3 flex items-center"
      >
        <slot name="suffix" />
      </div>
    </div>
    
    <div v-if="error || hint" class="text-sm">
      <p v-if="error" class="text-red-600">
        {{ error }}
      </p>
      <p v-else-if="hint" class="text-gray-500">
        {{ hint }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, useAttrs } from 'vue'

interface Props {
  modelValue?: string | number
  label?: string
  type?: string
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  error?: string
  hint?: string
  size?: 'sm' | 'md' | 'lg'
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  size: 'md'
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  blur: [event: Event]
  focus: [event: Event]
  input: [event: Event]
  change: [event: Event]
}>()

const attrs = useAttrs()

const inputId = computed(() => {
  return props.id || `input-${Math.random().toString(36).substr(2, 9)}`
})

const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const baseClasses = 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-primary-500 disabled:bg-gray-50 disabled:text-gray-500'

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'px-3 py-2 text-sm'
    case 'md':
      return 'px-3 py-2 text-sm'
    case 'lg':
      return 'px-4 py-3 text-base'
    default:
      return 'px-3 py-2 text-sm'
  }
})

const errorClasses = computed(() => {
  return props.error ? 'border-red-300 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500' : ''
})

const prefixClasses = computed(() => {
  return props.$slots?.prefix ? 'pl-10' : ''
})

const suffixClasses = computed(() => {
  return props.$slots?.suffix ? 'pr-10' : ''
})

const inputClasses = computed(() => {
  return [
    baseClasses,
    sizeClasses.value,
    errorClasses.value,
    prefixClasses.value,
    suffixClasses.value
  ].filter(Boolean).join(' ')
})
</script>