<template>
  <div class="space-y-6">
    <div class="text-center py-8">
      <h3 class="text-lg font-medium text-gray-900 mb-2">Détail de l'intervention</h3>
      <p class="text-gray-600">Suivi détaillé du plan d'intervention</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  interventionId: string
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
  updated: []
}>()
</script>