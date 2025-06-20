<template>
  <div class="space-y-6">
    <div class="text-center py-8">
      <h3 class="text-lg font-medium text-gray-900 mb-2">Détail élève à risque</h3>
      <p class="text-gray-600">Analyse détaillée du profil de risque</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  studentId: string
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
  interventionCreated: []
}>()
</script>