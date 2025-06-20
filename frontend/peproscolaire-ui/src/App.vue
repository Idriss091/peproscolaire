<template>
  <component :is="layoutComponent">
    <router-view />
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'

const route = useRoute()

// Détermine le layout à utiliser selon la route
const layoutComponent = computed(() => {
  const layoutName = route.meta.layout
  
  if (layoutName === 'AppLayout') {
    return AppLayout
  }
  
  // Pour les pages sans layout spécifique (comme login)
  return 'div'
})
</script>