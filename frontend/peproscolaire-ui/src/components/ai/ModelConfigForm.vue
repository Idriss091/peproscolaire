<template>
  <div class="space-y-6">
    <div class="text-center py-8">
      <h3 class="text-lg font-medium text-gray-900 mb-2">Configuration du modèle</h3>
      <p class="text-gray-600">Paramètres avancés du modèle prédictif</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  close: []
  saved: []
}>()
</script>