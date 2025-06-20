<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Seuil de confiance minimum
        </label>
        <input
          v-model="form.confidenceThreshold"
          type="number"
          min="50"
          max="100"
          step="5"
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
        <p class="text-xs text-gray-500 mt-1">Seuil minimum pour déclencher une alerte (50-100%)</p>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Fréquence d'analyse
        </label>
        <select
          v-model="form.analysisFrequency"
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="daily">Quotidienne</option>
          <option value="weekly">Hebdomadaire</option>
          <option value="monthly">Mensuelle</option>
        </select>
      </div>
    </div>

    <div class="border-t pt-6">
      <h4 class="text-sm font-medium text-gray-900 mb-4">Facteurs de risque à analyser</h4>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="space-y-3">
          <div class="flex items-center">
            <input
              id="factor-absences"
              v-model="form.factors.absences"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            >
            <label for="factor-absences" class="ml-2 block text-sm text-gray-900">
              Absentéisme
            </label>
          </div>
          <div class="flex items-center">
            <input
              id="factor-grades"
              v-model="form.factors.grades"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            >
            <label for="factor-grades" class="ml-2 block text-sm text-gray-900">
              Évolution des notes
            </label>
          </div>
        </div>
        <div class="space-y-3">
          <div class="flex items-center">
            <input
              id="factor-behavior"
              v-model="form.factors.behavior"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            >
            <label for="factor-behavior" class="ml-2 block text-sm text-gray-900">
              Comportement
            </label>
          </div>
          <div class="flex items-center">
            <input
              id="factor-participation"
              v-model="form.factors.participation"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            >
            <label for="factor-participation" class="ml-2 block text-sm text-gray-900">
              Participation en classe
            </label>
          </div>
        </div>
      </div>
    </div>

    <div class="flex justify-end space-x-3 pt-6 border-t">
      <BaseButton
        type="button"
        variant="secondary"
        @click="$emit('close')"
      >
        Annuler
      </BaseButton>
      
      <BaseButton
        type="submit"
        variant="primary"
        :loading="saving"
      >
        Sauvegarder la configuration
      </BaseButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const emit = defineEmits<{
  close: []
  saved: []
}>()

const saving = ref(false)

const form = reactive({
  confidenceThreshold: 80,
  analysisFrequency: 'weekly',
  factors: {
    absences: true,
    grades: true,
    behavior: true,
    participation: false
  }
})

const handleSubmit = async () => {
  saving.value = true
  try {
    // TODO: Sauvegarder la configuration via l'API
    await new Promise(resolve => setTimeout(resolve, 1000))
    emit('saved')
  } catch (error) {
    console.error('Erreur lors de la sauvegarde:', error)
  } finally {
    saving.value = false
  }
}
</script>