<template>
  <div class="space-y-6">
    <!-- Message d'alerte si évaluation commencée -->
    <div v-if="evaluation.status !== 'planned'" class="bg-yellow-50 border border-yellow-200 rounded-md p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <ExclamationTriangleIcon class="h-5 w-5 text-yellow-400" />
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-yellow-800">
            Attention
          </h3>
          <div class="mt-2 text-sm text-yellow-700">
            <p>
              Cette évaluation a déjà commencé ou est terminée. 
              Certaines modifications peuvent affecter les notes déjà saisies.
            </p>
          </div>
        </div>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Nom de l'évaluation *
          </label>
          <BaseInput
            v-model="form.name"
            required
            placeholder="Ex: Contrôle Chapitre 1"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Matière
          </label>
          <BaseInput
            :model-value="evaluation.subject_name"
            readonly
            disabled
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Classe
          </label>
          <BaseInput
            :model-value="evaluation.class_name"
            readonly
            disabled
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Type d'évaluation *
          </label>
          <select
            v-model="form.type"
            required
            :disabled="evaluation.status !== 'planned'"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 disabled:bg-gray-100"
          >
            <option value="controle">Contrôle</option>
            <option value="devoir">Devoir</option>
            <option value="interrogation">Interrogation</option>
            <option value="examen">Examen</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Date *
          </label>
          <BaseInput
            v-model="form.date"
            type="date"
            required
            :disabled="evaluation.status === 'completed'"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Note maximum *
          </label>
          <BaseInput
            v-model="form.maxValue"
            type="number"
            min="1"
            max="100"
            required
            :disabled="evaluation.status !== 'planned'"
          />
          <p v-if="evaluation.status !== 'planned'" class="text-xs text-gray-500 mt-1">
            Ne peut pas être modifié après le début de l'évaluation
          </p>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Coefficient *
          </label>
          <BaseInput
            v-model="form.coefficient"
            type="number"
            min="0.5"
            max="10"
            step="0.5"
            required
            :disabled="evaluation.status !== 'planned'"
          />
          <p v-if="evaluation.status !== 'planned'" class="text-xs text-gray-500 mt-1">
            Ne peut pas être modifié après le début de l'évaluation
          </p>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Durée
          </label>
          <BaseInput
            v-model="form.duration"
            placeholder="Ex: 1h, 45min"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Période *
          </label>
          <select
            v-model="form.period"
            required
            :disabled="evaluation.status !== 'planned'"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 disabled:bg-gray-100"
          >
            <option value="T1">Trimestre 1</option>
            <option value="T2">Trimestre 2</option>
            <option value="T3">Trimestre 3</option>
          </select>
        </div>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          v-model="form.description"
          rows="3"
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          placeholder="Description détaillée de l'évaluation..."
        />
      </div>
      
      <!-- Statut -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Statut
        </label>
        <select
          v-model="form.status"
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="planned">Planifiée</option>
          <option value="in_progress">En cours</option>
          <option value="completed">Terminée</option>
          <option value="cancelled">Annulée</option>
        </select>
      </div>
      
      <!-- Options avancées -->
      <div class="border-t pt-6">
        <h4 class="text-sm font-medium text-gray-900 mb-4">Options</h4>
        
        <div class="space-y-4">
          <div class="flex items-center">
            <input
              id="is-published"
              v-model="form.isPublished"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            >
            <label for="is-published" class="ml-2 block text-sm text-gray-900">
              Visible par les élèves
            </label>
          </div>
          
          <div class="flex items-center">
            <input
              id="allow-retake"
              v-model="form.allowRetake"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            >
            <label for="allow-retake" class="ml-2 block text-sm text-gray-900">
              Autoriser le rattrapage
            </label>
          </div>
        </div>
      </div>
      
      <!-- Statistiques si l'évaluation a commencé -->
      <div v-if="evaluation.status !== 'planned'" class="bg-gray-50 rounded-lg p-4">
        <h4 class="text-sm font-medium text-gray-900 mb-3">Statistiques</h4>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div class="text-center">
            <div class="text-lg font-semibold text-blue-600">
              {{ evaluation.grades_count || 0 }}
            </div>
            <div class="text-gray-600">Notes saisies</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-semibold text-gray-900">
              {{ evaluation.students_count || 0 }}
            </div>
            <div class="text-gray-600">Élèves total</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-semibold text-green-600">
              {{ evaluation.average || 'N/A' }}
            </div>
            <div class="text-gray-600">Moyenne</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-semibold text-purple-600">
              {{ getCompletionPercentage() }}%
            </div>
            <div class="text-gray-600">Complété</div>
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
          v-if="evaluation.status === 'planned'"
          type="button"
          variant="danger"
          @click="deleteEvaluation"
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
          Modifier
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, onMounted, ref } from 'vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import { useGradesStore } from '@/stores/grades'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'

interface Props {
  evaluation: any
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
  name: '',
  type: '',
  date: '',
  maxValue: '',
  coefficient: '',
  duration: '',
  period: '',
  description: '',
  status: '',
  isPublished: false,
  allowRetake: false
})

// Computed
const isFormValid = computed(() => {
  return form.name && 
         form.type && 
         form.date && 
         form.maxValue && 
         form.coefficient &&
         form.period
})

// Méthodes
const handleSubmit = async () => {
  if (!isFormValid.value) return
  
  saving.value = true
  try {
    const evaluationData = {
      name: form.name,
      description: form.description,
      type: form.type,
      date: form.date,
      max_value: parseInt(form.maxValue),
      coefficient: parseFloat(form.coefficient),
      duration: form.duration || null,
      period: form.period,
      status: form.status,
      is_published: form.isPublished,
      allow_retake: form.allowRetake,
      modified_at: new Date().toISOString()
    }
    
    await gradesStore.updateEvaluation(props.evaluation.id, evaluationData)
    
    emit('saved')
  } catch (error) {
    console.error('Erreur lors de la modification de l\'évaluation:', error)
  } finally {
    saving.value = false
  }
}

const deleteEvaluation = async () => {
  if (!confirm('Êtes-vous sûr de vouloir supprimer cette évaluation ? Cette action est irréversible.')) {
    return
  }
  
  deleting.value = true
  try {
    await gradesStore.deleteEvaluation(props.evaluation.id)
    emit('saved')
  } catch (error) {
    console.error('Erreur lors de la suppression de l\'évaluation:', error)
  } finally {
    deleting.value = false
  }
}

const getCompletionPercentage = () => {
  if (!props.evaluation.students_count) return 0
  return Math.round((props.evaluation.grades_count / props.evaluation.students_count) * 100)
}

// Lifecycle
onMounted(() => {
  // Pré-remplir le formulaire avec les données de l'évaluation
  Object.assign(form, {
    name: props.evaluation.name,
    type: props.evaluation.type,
    date: props.evaluation.date,
    maxValue: props.evaluation.max_value.toString(),
    coefficient: props.evaluation.coefficient.toString(),
    duration: props.evaluation.duration || '',
    period: props.evaluation.period,
    description: props.evaluation.description || '',
    status: props.evaluation.status,
    isPublished: props.evaluation.is_published || false,
    allowRetake: props.evaluation.allow_retake || false
  })
})
</script>