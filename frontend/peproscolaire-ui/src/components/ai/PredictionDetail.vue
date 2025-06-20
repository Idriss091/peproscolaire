<template>
  <div class="space-y-6">
    <div class="text-center py-8">
      <h3 class="text-lg font-medium text-gray-900 mb-2">Détail de la prédiction</h3>
      <p class="text-gray-600">Analyse détaillée de la prédiction IA</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  predictionId: string
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()
</script>