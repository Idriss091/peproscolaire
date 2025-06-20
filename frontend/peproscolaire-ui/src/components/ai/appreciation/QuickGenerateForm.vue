<template>
  <div class="space-y-6">
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Élève
      </label>
      <select
        v-model="form.studentId"
        class="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
      >
        <option value="">Sélectionner un élève</option>
        <option v-for="student in students" :key="student.id" :value="student.id">
          {{ student.name }}
        </option>
      </select>
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
        :disabled="!form.studentId"
        @click="generate"
      >
        Générer
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const emit = defineEmits<{
  close: []
  generated: []
}>()

const students = ref([
  { id: '1', name: 'Marie Dubois' },
  { id: '2', name: 'Pierre Martin' }
])

const form = reactive({
  studentId: ''
})

const generate = () => {
  // TODO: Génération rapide
  emit('generated')
}
</script>