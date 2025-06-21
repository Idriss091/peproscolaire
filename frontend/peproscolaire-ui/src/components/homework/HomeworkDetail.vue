<template>
  <div class="homework-detail">
    <div class="bg-white rounded-lg shadow-md border border-gray-200">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900">Détail du devoir</h3>
      </div>
      <div class="px-6 py-4">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Titre</label>
            <p class="mt-1 text-sm text-gray-900">{{ homework?.title || 'Titre du devoir' }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Description</label>
            <p class="mt-1 text-sm text-gray-600">{{ homework?.description || 'Description du devoir...' }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Date d'échéance</label>
            <p class="mt-1 text-sm text-gray-900">{{ homework?.due_date || 'À définir' }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  homework?: {
    id: string
    title: string
    description: string
    due_date: string
  } | null
}

const props = withDefaults(defineProps<Props>(), {
  homework: null
})
</script>

<style scoped>
.homework-detail {
  /* Styles pour le composant de détail des devoirs */
}
</style>