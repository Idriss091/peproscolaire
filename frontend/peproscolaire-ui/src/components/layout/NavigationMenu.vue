<template>
  <div class="space-y-1">
    <router-link
      v-for="item in items"
      :key="item.name"
      :to="item.href"
      @click="$emit('navigate')"
      class="group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors duration-150"
      :class="[
        isActive(item.href)
          ? 'bg-indigo-100 text-indigo-700'
          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
      ]"
    >
      <component
        :is="item.icon"
        class="mr-3 h-5 w-5 flex-shrink-0 transition-colors duration-150"
        :class="[
          isActive(item.href)
            ? 'text-indigo-500'
            : 'text-gray-400 group-hover:text-gray-500'
        ]"
      />
      {{ item.name }}
      <span
        v-if="item.badge"
        class="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
        :class="[
          item.badgeType === 'danger'
            ? 'bg-red-100 text-red-800'
            : 'bg-gray-100 text-gray-600'
        ]"
      >
        {{ item.badge }}
      </span>
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import type { Component } from 'vue'

interface MenuItem {
  name: string
  href: string
  icon: Component
  badge?: string | number
  badgeType?: 'default' | 'danger'
}

interface Props {
  items: MenuItem[]
}

defineProps<Props>()
defineEmits<{
  navigate: []
}>()

const route = useRoute()

const isActive = (href: string) => {
  return route.path === href || route.path.startsWith(href + '/')
}
</script>