<template>
  <div :class="cardClasses" class="stat-card">
    <div class="stat-content">
      <div class="stat-header">
        <div class="stat-icon-container">
          <component :is="icon" :class="iconClasses" class="stat-icon" />
        </div>
        
        <BaseDropdown v-if="hasActions" placement="bottom-end" size="sm">
          <template #trigger>
            <button class="stat-action-btn">
              <EllipsisVerticalIcon class="h-4 w-4" />
            </button>
          </template>
          <div class="py-1">
            <slot name="actions" />
          </div>
        </BaseDropdown>
      </div>
      
      <div class="stat-body">
        <div class="stat-value-container">
          <div v-if="loading" class="stat-skeleton">
            <div class="skeleton-line skeleton-value" />
          </div>
          <div v-else class="stat-value">{{ formattedValue }}</div>
          
          <div v-if="change && !loading" :class="changeClasses" class="stat-change">
            <component :is="trendIcon" class="h-3 w-3" />
            {{ formattedChange }}
          </div>
        </div>
        
        <div class="stat-title-container">
          <div v-if="loading" class="stat-skeleton">
            <div class="skeleton-line skeleton-title" />
          </div>
          <h3 v-else class="stat-title">{{ title }}</h3>
        </div>
        
        <p v-if="description && !loading" class="stat-description">
          {{ description }}
        </p>
      </div>
    </div>
    
    <!-- Mini graphique (optionnel) -->
    <div v-if="chartData && !loading" class="stat-chart">
      <svg
        viewBox="0 0 100 20"
        class="w-full h-5"
        preserveAspectRatio="none"
      >
        <polyline
          :points="chartPoints"
          :class="chartLineClasses"
          class="chart-line"
          fill="none"
          stroke-width="2"
        />
      </svg>
    </div>
    
    <!-- Link vers les détails -->
    <div v-if="link && !loading" class="stat-footer">
      <router-link :to="link" class="stat-link">
        Voir les détails
        <ArrowRightIcon class="h-4 w-4" />
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, useSlots } from 'vue'
import {
  EllipsisVerticalIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ArrowRightIcon,
  MinusIcon
} from '@heroicons/vue/24/outline'
import BaseDropdown from '@/components/ui/BaseDropdown.vue'
import type { Component } from 'vue'

interface Props {
  title: string
  value: string | number
  change?: string | number
  trend?: 'up' | 'down' | 'neutral'
  icon?: Component
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'education' | 'ai'
  description?: string
  loading?: boolean
  chartData?: number[]
  size?: 'sm' | 'md' | 'lg'
  link?: string
  format?: 'number' | 'currency' | 'percentage'
}

const props = withDefaults(defineProps<Props>(), {
  color: 'primary',
  loading: false,
  size: 'md',
  trend: 'neutral',
  format: 'number'
})

const slots = useSlots()

const hasActions = computed(() => !!slots.actions)

const formattedValue = computed(() => {
  if (typeof props.value === 'string') return props.value
  
  let numValue = props.value
  
  switch (props.format) {
    case 'currency':
      return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'EUR'
      }).format(numValue)
    case 'percentage':
      return `${numValue}%`
    default:
      if (numValue >= 1000000) {
        return `${(numValue / 1000000).toFixed(1)}M`
      }
      if (numValue >= 1000) {
        return `${(numValue / 1000).toFixed(1)}k`
      }
      return new Intl.NumberFormat('fr-FR').format(numValue)
  }
})

const cardClasses = computed(() => [
  'stat-card',
  `stat-card-${props.size}`,
  `stat-card-${props.color}`,
  {
    'stat-card-loading': props.loading
  }
])

const iconClasses = computed(() => [
  'stat-icon',
  `stat-icon-${props.color}`
])

const formattedChange = computed(() => {
  if (props.change === undefined || props.change === null) return ''
  if (typeof props.change === 'string') return props.change
  return props.change.toString()
})

const changeClasses = computed(() => [
  'stat-change',
  {
    'stat-change-up': props.trend === 'up',
    'stat-change-down': props.trend === 'down',
    'stat-change-neutral': props.trend === 'neutral'
  }
])

const chartLineClasses = computed(() => [
  'chart-line',
  `chart-line-${props.color}`
])

const trendIcon = computed(() => {
  switch (props.trend) {
    case 'up': return ArrowUpIcon
    case 'down': return ArrowDownIcon
    default: return MinusIcon
  }
})

const chartPoints = computed(() => {
  if (!props.chartData || props.chartData.length === 0) return ''
  
  const data = props.chartData
  const max = Math.max(...data)
  const min = Math.min(...data)
  const range = max - min || 1
  
  return data
    .map((value, index) => {
      const x = (index / (data.length - 1)) * 100
      const y = 20 - ((value - min) / range) * 20
      return `${x},${y}`
    })
    .join(' ')
})
</script>

<style scoped>
.stat-card {
  @apply bg-white rounded-xl border border-gray-200 overflow-hidden transition-all duration-200 hover:shadow-md;
}

.stat-card-sm {
  @apply p-4;
}

.stat-card-md {
  @apply p-6;
}

.stat-card-lg {
  @apply p-8;
}

.stat-content {
  @apply space-y-4;
}

.stat-header {
  @apply flex items-start justify-between;
}

.stat-icon-container {
  @apply w-12 h-12 rounded-lg flex items-center justify-center;
}

.stat-card-primary .stat-icon-container {
  @apply bg-blue-100;
}

.stat-card-success .stat-icon-container {
  @apply bg-green-100;
}

.stat-card-warning .stat-icon-container {
  @apply bg-yellow-100;
}

.stat-card-danger .stat-icon-container {
  @apply bg-red-100;
}

.stat-card-info .stat-icon-container {
  @apply bg-cyan-100;
}

.stat-card-education .stat-icon-container {
  @apply bg-indigo-100;
}

.stat-card-ai .stat-icon-container {
  @apply bg-purple-100;
}

.stat-icon {
  @apply h-6 w-6;
}

.stat-icon-primary {
  @apply text-blue-600;
}

.stat-icon-success {
  @apply text-green-600;
}

.stat-icon-warning {
  @apply text-yellow-600;
}

.stat-icon-danger {
  @apply text-red-600;
}

.stat-icon-info {
  @apply text-cyan-600;
}

.stat-icon-education {
  @apply text-indigo-600;
}

.stat-icon-ai {
  @apply text-purple-600;
}

.stat-action-btn {
  @apply w-8 h-8 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500 hover:text-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.stat-body {
  @apply space-y-2;
}

.stat-value-container {
  @apply flex items-center gap-2;
}

.stat-value {
  @apply text-2xl font-bold text-gray-900;
}

.stat-card-sm .stat-value {
  @apply text-xl;
}

.stat-card-lg .stat-value {
  @apply text-3xl;
}

.stat-change {
  @apply inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium;
}

.stat-change-up {
  @apply bg-green-100 text-green-800;
}

.stat-change-down {
  @apply bg-red-100 text-red-800;
}

.stat-change-neutral {
  @apply bg-gray-100 text-gray-600;
}

.stat-title {
  @apply text-sm font-medium text-gray-600;
}

.stat-description {
  @apply text-xs text-gray-500;
}

.stat-chart {
  @apply mt-4 pt-4 border-t border-gray-100;
}

.chart-line {
  @apply transition-all duration-300;
}

.chart-line-primary {
  @apply stroke-blue-500;
}

.chart-line-success {
  @apply stroke-green-500;
}

.chart-line-warning {
  @apply stroke-yellow-500;
}

.chart-line-danger {
  @apply stroke-red-500;
}

.chart-line-info {
  @apply stroke-cyan-500;
}

.chart-line-education {
  @apply stroke-indigo-500;
}

.chart-line-ai {
  @apply stroke-purple-500;
}

.stat-footer {
  @apply mt-4 pt-4 border-t border-gray-100;
}

.stat-link {
  @apply inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors;
}

/* Loading states */
.stat-skeleton {
  @apply animate-pulse;
}

.skeleton-line {
  @apply bg-gray-200 rounded;
}

.skeleton-value {
  @apply h-8 w-16;
}

.skeleton-title {
  @apply h-4 w-24;
}

.stat-card-loading {
  @apply pointer-events-none;
}
</style>