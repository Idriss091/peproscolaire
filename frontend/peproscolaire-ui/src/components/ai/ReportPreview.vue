<template>
  <div class="space-y-6">
    <div class="text-center py-8">
      <h3 class="text-lg font-medium text-gray-900 mb-2">Aperçu du rapport</h3>
      <p class="text-gray-600">Prévisualisation avant génération finale</p>
    </div>
    
    <div class="flex justify-end space-x-3">
      <BaseButton
        variant="secondary"
        @click="$emit('close')"
      >
        Fermer
      </BaseButton>
      
      <BaseButton
        variant="primary"
        @click="$emit('generate')"
      >
        Générer le rapport
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/ui/BaseButton.vue'

interface Props {
  reportType: string
  config: any
  data: any
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
  generate: []
}>()
</script>