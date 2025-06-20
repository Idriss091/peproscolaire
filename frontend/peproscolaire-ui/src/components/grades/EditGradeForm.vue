<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Élève
        </label>
        <BaseInput
          :model-value="grade.student_name"
          readonly
          disabled
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Matière
        </label>
        <BaseInput
          :model-value="grade.subject_name"
          readonly
          disabled
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Évaluation
        </label>
        <BaseInput
          :model-value="grade.evaluation_name"
          readonly
          disabled
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Période
        </label>
        <BaseInput
          :model-value="grade.period"
          readonly
          disabled
        />
      </div>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Note *
        </label>
        <BaseInput
          v-model="form.value"
          type="number"
          step="0.5"
          min="0"
          :max="form.maxValue"
          required
          placeholder="Ex: 15.5"
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Note maximum
        </label>
        <BaseInput
          v-model="form.maxValue"
          type="number"
          min="1"
          readonly
          disabled
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Coefficient
        </label>
        <BaseInput
          v-model="form.coefficient"
          type="number"
          min="0.5"
          step="0.5"
          readonly
          disabled
        />
      </div>
    </div>
    
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Date
      </label>
      <BaseInput
        v-model="form.date"
        type="date"
        readonly
        disabled
      />
    </div>
    
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Commentaire
      </label>
      <textarea
        v-model="form.comment"
        rows="3"
        class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        placeholder="Commentaire optionnel sur cette note..."
      />
    </div>
    
    <!-- Comparaison avant/après -->
    <div class="bg-gray-50 rounded-lg p-4">
      <h4 class="text-sm font-medium text-gray-900 mb-3">Comparaison</h4>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <h5 class="text-xs font-medium text-gray-700 mb-2">Note actuelle</h5>
          <div class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
               :class="getGradeColorClass(grade.value, grade.max_value)">
            {{ grade.value }}/{{ grade.max_value }}
          </div>
          <div class="text-xs text-gray-600 mt-1">
            {{ getPercentage(grade.value, grade.max_value) }}% - {{ getMention(grade.value, grade.max_value) }}
          </div>
        </div>
        
        <div v-if="form.value">
          <h5 class="text-xs font-medium text-gray-700 mb-2">Nouvelle note</h5>
          <div class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
               :class="getGradeColorClass(parseFloat(form.value), parseFloat(form.maxValue))">
            {{ form.value }}/{{ form.maxValue }}
          </div>
          <div class="text-xs text-gray-600 mt-1">
            {{ getPercentage(parseFloat(form.value), parseFloat(form.maxValue)) }}% - {{ getMention(parseFloat(form.value), parseFloat(form.maxValue)) }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Zone de danger -->
    <div class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">
            Attention
          </h3>
          <div class="mt-2 text-sm text-red-700">
            <p>
              La modification d'une note peut avoir des conséquences sur les moyennes et les bulletins.
              Assurez-vous que cette modification est justifiée.
            </p>
          </div>
          
          <div class="mt-3">
            <label class="block text-sm font-medium text-red-800 mb-1">
              Motif de la modification *
            </label>
            <textarea
              v-model="form.modificationReason"
              rows="2"
              required
              class="w-full rounded-md border-red-300 shadow-sm focus:border-red-500 focus:ring-red-500"
              placeholder="Expliquer pourquoi cette note est modifiée..."
            />
          </div>
        </div>
      </div>
    </div>
    
    <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200">
      <BaseButton
        type="button"
        variant="secondary"
        @click="$emit('close')"
      >
        Annuler
      </BaseButton>
      
      <BaseButton
        type="button"
        variant="danger"
        @click="deleteGrade"
        :loading="deleting"
      >
        Supprimer
      </BaseButton>
      
      <BaseButton
        type="submit"
        variant="primary"
        :loading="saving"
        :disabled="!isFormValid"
      >
        Modifier la note
      </BaseButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, computed, onMounted, ref } from 'vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import { useGradesStore } from '@/stores/grades'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'

interface Props {
  grade: any
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const gradesStore = useGradesStore()

// État local
const saving = ref(false)
const deleting = ref(false)

// Formulaire
const form = reactive({
  value: '',
  maxValue: '',
  coefficient: '',
  date: '',
  comment: '',
  modificationReason: ''
})

// Computed
const isFormValid = computed(() => {
  return form.value && 
         form.maxValue &&
         form.modificationReason.trim() &&
         parseFloat(form.value) <= parseFloat(form.maxValue) &&
         parseFloat(form.value) >= 0
})

// Méthodes
const handleSubmit = async () => {
  if (!isFormValid.value) return
  
  saving.value = true
  try {
    const gradeData = {
      value: parseFloat(form.value),
      comment: form.comment,
      modification_reason: form.modificationReason,
      modified_at: new Date().toISOString(),
      modified_by: 'current_user' // TODO: Récupérer l'utilisateur actuel
    }
    
    await gradesStore.updateGrade(props.grade.id, gradeData)
    
    emit('saved')
  } catch (error) {
    console.error('Erreur lors de la modification de la note:', error)
  } finally {
    saving.value = false
  }
}

const deleteGrade = async () => {
  if (!confirm('Êtes-vous sûr de vouloir supprimer cette note ? Cette action est irréversible.')) {
    return
  }
  
  deleting.value = true
  try {
    await gradesStore.deleteGrade(props.grade.id)
    emit('saved')
  } catch (error) {
    console.error('Erreur lors de la suppression de la note:', error)
  } finally {
    deleting.value = false
  }
}

// Utilitaires
const getGradeColorClass = (value: number, maxValue: number) => {
  const percentage = (value / maxValue) * 100
  
  if (percentage >= 80) {
    return 'bg-green-100 text-green-800'
  } else if (percentage >= 60) {
    return 'bg-yellow-100 text-yellow-800'
  } else if (percentage >= 40) {
    return 'bg-orange-100 text-orange-800'
  } else {
    return 'bg-red-100 text-red-800'
  }
}

const getPercentage = (value: number, maxValue: number) => {
  return Math.round((value / maxValue) * 100)
}

const getMention = (value: number, maxValue: number) => {
  const percentage = (value / maxValue) * 100
  
  if (percentage >= 90) return 'Excellent'
  if (percentage >= 80) return 'Très bien'
  if (percentage >= 70) return 'Bien'
  if (percentage >= 60) return 'Assez bien'
  if (percentage >= 50) return 'Passable'
  return 'Insuffisant'
}

// Lifecycle
onMounted(() => {
  // Pré-remplir le formulaire avec les données de la note
  Object.assign(form, {
    value: props.grade.value.toString(),
    maxValue: props.grade.max_value.toString(),
    coefficient: props.grade.coefficient.toString(),
    date: props.grade.date,
    comment: props.grade.comment || '',
    modificationReason: ''
  })
})
</script>