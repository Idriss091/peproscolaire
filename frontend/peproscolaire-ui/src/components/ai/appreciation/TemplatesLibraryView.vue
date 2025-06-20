<template>
  <div class="space-y-6">
    <div class="text-center py-8">
      <h3 class="text-lg font-medium text-gray-900 mb-2">Bibliothèque de modèles</h3>
      <p class="text-gray-600">Sélection de modèles d'appréciations prédéfinis</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  close: []
  templateSelected: []
}>()
</script>