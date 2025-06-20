<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Élève *
        </label>
        <select
          v-model="form.student"
          required
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Sélectionner un élève</option>
          <option v-for="student in students" :key="student.id" :value="student.id">
            {{ student.first_name }} {{ student.last_name }} - {{ student.class_name }}
          </option>
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Matière *
        </label>
        <select
          v-model="form.subject"
          @change="loadSubjectEvaluations"
          required
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Sélectionner une matière</option>
          <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
            {{ subject.name }}
          </option>
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Évaluation *
        </label>
        <select
          v-model="form.evaluation"
          @change="updateEvaluationDetails"
          required
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Sélectionner une évaluation</option>
          <option v-for="evaluation in availableEvaluations" :key="evaluation.id" :value="evaluation.id">
            {{ evaluation.name }} - {{ formatDate(evaluation.date) }}
          </option>
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Période *
        </label>
        <select
          v-model="form.period"
          required
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Sélectionner une période</option>
          <option value="T1">Trimestre 1</option>
          <option value="T2">Trimestre 2</option>
          <option value="T3">Trimestre 3</option>
        </select>
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
          placeholder="20"
          readonly
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
          placeholder="1"
          readonly
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
    
    <!-- Aperçu de la note -->
    <div v-if="form.value && form.maxValue" class="bg-gray-50 rounded-lg p-4">
      <h4 class="text-sm font-medium text-gray-900 mb-2">Aperçu de la note</h4>
      <div class="flex items-center space-x-4">
        <div class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
             :class="getGradeColorClass(parseFloat(form.value), parseFloat(form.maxValue))">
          {{ form.value }}/{{ form.maxValue }}
        </div>
        <div class="text-sm text-gray-600">
          Pourcentage: {{ getPercentage(parseFloat(form.value), parseFloat(form.maxValue)) }}%
        </div>
        <div class="text-sm text-gray-600">
          Mention: {{ getMention(parseFloat(form.value), parseFloat(form.maxValue)) }}
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
        type="submit"
        variant="primary"
        :loading="saving"
        :disabled="!isFormValid"
      >
        Ajouter la note
      </BaseButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useGradesStore } from '@/stores/grades'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'

const emit = defineEmits<{
  close: []
  saved: []
}>()

const authStore = useAuthStore()
const gradesStore = useGradesStore()

// État local
const saving = ref(false)

// Formulaire
const form = reactive({
  student: '',
  subject: '',
  evaluation: '',
  period: '',
  value: '',
  maxValue: '20',
  coefficient: '1',
  date: '',
  comment: ''
})

// Données
const students = ref([
  { id: '1', first_name: 'Marie', last_name: 'Dubois', class_name: '6ème A' },
  { id: '2', first_name: 'Pierre', last_name: 'Martin', class_name: '6ème A' },
  { id: '3', first_name: 'Sophie', last_name: 'Blanc', class_name: '6ème B' }
])

const subjects = ref([
  { id: '1', name: 'Mathématiques' },
  { id: '2', name: 'Français' },
  { id: '3', name: 'Histoire-Géographie' },
  { id: '4', name: 'Sciences' }
])

const evaluations = ref([
  {
    id: '1',
    name: 'Contrôle Chapitre 1',
    subject_id: '1',
    date: '2024-01-15',
    max_value: 20,
    coefficient: 2
  },
  {
    id: '2',
    name: 'Devoir Maison',
    subject_id: '1',
    date: '2024-01-10',
    max_value: 20,
    coefficient: 1
  }
])

// Computed
const availableEvaluations = computed(() => {
  if (!form.subject) return []
  return evaluations.value.filter(evaluation => evaluation.subject_id === form.subject)
})

const isFormValid = computed(() => {
  return form.student && 
         form.subject && 
         form.evaluation && 
         form.period && 
         form.value && 
         form.maxValue &&
         parseFloat(form.value) <= parseFloat(form.maxValue)
})

// Méthodes
const loadSubjectEvaluations = () => {
  form.evaluation = ''
  form.maxValue = '20'
  form.coefficient = '1'
  form.date = ''
}

const updateEvaluationDetails = () => {
  const selectedEvaluation = evaluations.value.find(e => e.id === form.evaluation)
  if (selectedEvaluation) {
    form.maxValue = selectedEvaluation.max_value.toString()
    form.coefficient = selectedEvaluation.coefficient.toString()
    form.date = selectedEvaluation.date
  }
}

const handleSubmit = async () => {
  if (!isFormValid.value) return
  
  saving.value = true
  try {
    const gradeData = {
      student_id: form.student,
      subject_id: form.subject,
      evaluation_id: form.evaluation,
      value: parseFloat(form.value),
      max_value: parseFloat(form.maxValue),
      coefficient: parseFloat(form.coefficient),
      period: form.period,
      date: form.date,
      comment: form.comment,
      teacher_id: authStore.user?.id
    }
    
    // TODO: Utiliser le store pour sauvegarder
    await gradesStore.addGrade(gradeData)
    
    emit('saved')
  } catch (error) {
    console.error('Erreur lors de l\'ajout de la note:', error)
  } finally {
    saving.value = false
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

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

// Lifecycle
onMounted(() => {
  // Définir la date par défaut
  form.date = new Date().toISOString().split('T')[0]
})
</script>