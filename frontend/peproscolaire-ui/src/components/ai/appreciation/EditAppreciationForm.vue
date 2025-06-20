<template>
  <div class="space-y-6">
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Contenu de l'appréciation
      </label>
      <textarea
        v-model="content"
        rows="6"
        class="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
      />
    </div>

    <div class="flex justify-end space-x-3">
      <BaseButton
        type="button"
        variant="secondary"
        @click="$emit('close')"
      >
        Annuler
      </BaseButton>
      
      <BaseButton
        variant="primary"
        @click="save"
      >
        Sauvegarder
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import BaseButton from '@/components/ui/BaseButton.vue'

interface Props {
  appreciationId: string
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const content = ref('Contenu de l\'appréciation à éditer...')

const save = () => {
  // TODO: Sauvegarder via l'API
  emit('saved')
}
</script>