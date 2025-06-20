<template>
  <router-link
    :to="to"
    :class="linkClasses"
    class="nav-link"
    @click="$emit('click')"
  >
    <div class="nav-link-content">
      <div class="nav-icon">
        <component :is="icon" class="h-5 w-5" />
      </div>
      
      <span v-if="!collapsed" class="nav-label">{{ label }}</span>
      
      <div v-if="badge && !collapsed" class="nav-badge-container">
        <span :class="badgeClasses" class="nav-badge">
          {{ badge > 99 ? '99+' : badge }}
        </span>
      </div>
    </div>
    
    <!-- Tooltip pour mode collapsed -->
    <div v-if="collapsed" class="nav-tooltip">
      {{ label }}
      <span v-if="badge" class="tooltip-badge">
        {{ badge > 99 ? '99+' : badge }}
      </span>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import type { Component } from 'vue'

interface Props {
  to: string
  icon: Component
  label: string
  badge?: number | null
  collapsed?: boolean
  ai?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  badge: null,
  collapsed: false,
  ai: false
})

interface Emits {
  click: []
}

defineEmits<Emits>()

const route = useRoute()

const isActive = computed(() => {
  return route.path === props.to || route.path.startsWith(`${props.to}/`)
})

const linkClasses = computed(() => [
  'nav-link',
  {
    'nav-link-active': isActive.value,
    'nav-link-collapsed': props.collapsed,
    'nav-link-ai': props.ai
  }
])

const badgeClasses = computed(() => [
  'nav-badge',
  {
    'nav-badge-primary': !props.ai,
    'nav-badge-ai': props.ai
  }
])
</script>

<style scoped>
.nav-link {
  @apply relative flex items-center w-full px-3 py-2 text-sm font-medium text-neutral-600 rounded-lg hover:bg-neutral-100 hover:text-neutral-900 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 group;
}

.nav-link-active {
  @apply bg-primary-50 text-primary-700 hover:bg-primary-100 hover:text-primary-800;
}

.nav-link-ai.nav-link-active {
  @apply bg-ai-50 text-ai-700 hover:bg-ai-100 hover:text-ai-800;
}

.nav-link-collapsed {
  @apply justify-center px-2;
}

.nav-link-content {
  @apply flex items-center gap-3 w-full;
}

.nav-link-collapsed .nav-link-content {
  @apply justify-center;
}

.nav-icon {
  @apply flex-shrink-0;
}

.nav-label {
  @apply flex-1 truncate;
}

.nav-badge-container {
  @apply flex-shrink-0;
}

.nav-badge {
  @apply px-2 py-1 text-xs font-semibold rounded-full;
}

.nav-badge-primary {
  @apply bg-primary-100 text-primary-800;
}

.nav-badge-ai {
  @apply bg-ai-100 text-ai-800;
}

/* Tooltip pour mode collapsed */
.nav-tooltip {
  @apply absolute left-full ml-2 px-2 py-1 bg-neutral-900 text-white text-xs rounded-md whitespace-nowrap opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50;
}

.tooltip-badge {
  @apply ml-2 px-1.5 py-0.5 bg-white/20 rounded-full text-xs;
}

/* Responsive */
@media (max-width: 1024px) {
  .nav-tooltip {
    @apply hidden;
  }
}
</style>