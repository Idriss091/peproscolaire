<template>
  <div class="space-y-6">
    <!-- Sélection de l'évaluation -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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
          Classe *
        </label>
        <select
          v-model="form.class"
          @change="loadClassStudents"
          required
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Sélectionner une classe</option>
          <option v-for="cls in classes" :key="cls.id" :value="cls.id">
            {{ cls.name }}
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
    </div>

    <!-- Informations de l'évaluation -->
    <div v-if="selectedEvaluation" class="bg-blue-50 rounded-lg p-4">
      <h4 class="text-sm font-medium text-blue-900 mb-2">{{ selectedEvaluation.name }}</h4>
      <div class="grid grid-cols-3 gap-4 text-sm text-blue-800">
        <div>
          <span class="font-medium">Date:</span> {{ formatDate(selectedEvaluation.date) }}
        </div>
        <div>
          <span class="font-medium">Note sur:</span> {{ selectedEvaluation.max_value }}
        </div>
        <div>
          <span class="font-medium">Coefficient:</span> {{ selectedEvaluation.coefficient }}
        </div>
      </div>
    </div>

    <!-- Actions rapides -->
    <div v-if="classStudents.length > 0" class="flex justify-between items-center">
      <div class="flex gap-2">
        <BaseButton
          variant="outline"
          size="sm"
          @click="fillAllGrades(selectedEvaluation?.max_value || 20)"
        >
          Tous {{ selectedEvaluation?.max_value || 20 }}
        </BaseButton>
        
        <BaseButton
          variant="outline"
          size="sm"
          @click="fillAllGrades(Math.round((selectedEvaluation?.max_value || 20) * 0.5))"
        >
          Tous {{ Math.round((selectedEvaluation?.max_value || 20) * 0.5) }}
        </BaseButton>
        
        <BaseButton
          variant="outline"
          size="sm"
          @click="clearAllGrades"
        >
          Effacer tout
        </BaseButton>
      </div>
      
      <div class="text-sm text-gray-600">
        {{ completedGrades }}/{{ classStudents.length }} notes saisies
      </div>
    </div>

    <!-- Grille de saisie -->
    <div v-if="classStudents.length > 0" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <div class="max-h-96 overflow-y-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50 sticky top-0">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Élève
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Note / {{ selectedEvaluation?.max_value || 20 }}
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Commentaire
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Statut
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="student in classStudents" :key="student.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-8 w-8">
                    <div class="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                      <span class="text-xs font-medium text-gray-700">
                        {{ getStudentInitials(student.first_name, student.last_name) }}
                      </span>
                    </div>
                  </div>
                  <div class="ml-3">
                    <div class="text-sm font-medium text-gray-900">
                      {{ student.first_name }} {{ student.last_name }}
                    </div>
                    <div class="text-xs text-gray-500">
                      {{ student.student_number }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <div class="flex items-center justify-center space-x-2">
                  <BaseInput
                    v-model="studentGrades[student.id].value"
                    type="number"
                    step="0.5"
                    min="0"
                    :max="selectedEvaluation?.max_value || 20"
                    class="w-20 text-center"
                    @input="validateGrade(student.id)"
                  />
                  <span class="text-gray-500">/</span>
                  <span class="font-medium text-gray-900">{{ selectedEvaluation?.max_value || 20 }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <BaseInput
                  v-model="studentGrades[student.id].comment"
                  placeholder="Commentaire..."
                  class="w-full text-sm"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <div v-if="studentGrades[student.id].value">
                  <div class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                       :class="getGradeColorClass(parseFloat(studentGrades[student.id].value), selectedEvaluation?.max_value || 20)">
                    {{ getPercentage(parseFloat(studentGrades[student.id].value), selectedEvaluation?.max_value || 20) }}%
                  </div>
                  <div class="text-xs text-gray-500 mt-1">
                    {{ getMention(parseFloat(studentGrades[student.id].value), selectedEvaluation?.max_value || 20) }}
                  </div>
                </div>
                <div v-else class="text-xs text-gray-400">
                  En attente
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Message si aucun élève -->
    <div v-else-if="form.class" class="text-center py-8 text-gray-500">
      Aucun élève trouvé pour cette classe
    </div>

    <!-- Résumé avant sauvegarde -->
    <div v-if="completedGrades > 0" class="bg-gray-50 rounded-lg p-4">
      <h4 class="text-sm font-medium text-gray-900 mb-3">Résumé de la saisie</h4>
      <div class="grid grid-cols-4 gap-4 text-sm">
        <div class="text-center">
          <div class="text-lg font-semibold text-green-600">{{ gradesStats.excellent }}</div>
          <div class="text-gray-600">Excellent(s)</div>
        </div>
        <div class="text-center">
          <div class="text-lg font-semibold text-blue-600">{{ gradesStats.good }}</div>
          <div class="text-gray-600">Bien</div>
        </div>
        <div class="text-center">
          <div class="text-lg font-semibold text-yellow-600">{{ gradesStats.average }}</div>
          <div class="text-gray-600">Moyen</div>
        </div>
        <div class="text-center">
          <div class="text-lg font-semibold text-red-600">{{ gradesStats.poor }}</div>
          <div class="text-gray-600">Faible</div>
        </div>
      </div>
      <div class="mt-3 text-center">
        <span class="text-sm text-gray-600">
          Moyenne de la classe: 
          <span class="font-semibold">{{ classAverage }}/{{ selectedEvaluation?.max_value || 20 }}</span>
        </span>
      </div>
    </div>

    <!-- Actions -->
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
        variant="primary"
        @click="saveGrades"
        :loading="saving"
        :disabled="completedGrades === 0"
      >
        Enregistrer {{ completedGrades }} note(s)
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
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
  subject: '',
  class: '',
  evaluation: ''
})

// Données
const subjects = ref([
  { id: '1', name: 'Mathématiques' },
  { id: '2', name: 'Français' },
  { id: '3', name: 'Histoire-Géographie' },
  { id: '4', name: 'Sciences' }
])

const classes = ref([
  { id: '1', name: '6ème A' },
  { id: '2', name: '6ème B' },
  { id: '3', name: '5ème A' }
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

const classStudents = ref([])
const studentGrades = ref<Record<string, { value: string; comment: string }>>({})

// Computed
const availableEvaluations = computed(() => {
  if (!form.subject) return []
  return evaluations.value.filter(evaluation => evaluation.subject_id === form.subject)
})

const selectedEvaluation = computed(() => {
  return evaluations.value.find(e => e.id === form.evaluation)
})

const completedGrades = computed(() => {
  return Object.values(studentGrades.value).filter(grade => grade.value && grade.value.trim()).length
})

const gradesStats = computed(() => {
  const grades = Object.values(studentGrades.value)
    .filter(grade => grade.value && grade.value.trim())
    .map(grade => parseFloat(grade.value))
  
  const maxValue = selectedEvaluation.value?.max_value || 20
  
  return {
    excellent: grades.filter(g => (g / maxValue) >= 0.8).length,
    good: grades.filter(g => (g / maxValue) >= 0.6 && (g / maxValue) < 0.8).length,
    average: grades.filter(g => (g / maxValue) >= 0.4 && (g / maxValue) < 0.6).length,
    poor: grades.filter(g => (g / maxValue) < 0.4).length
  }
})

const classAverage = computed(() => {
  const grades = Object.values(studentGrades.value)
    .filter(grade => grade.value && grade.value.trim())
    .map(grade => parseFloat(grade.value))
  
  if (grades.length === 0) return '0.0'
  
  const sum = grades.reduce((acc, grade) => acc + grade, 0)
  return (sum / grades.length).toFixed(1)
})

// Méthodes
const loadSubjectEvaluations = () => {
  form.evaluation = ''
}

const loadClassStudents = async () => {
  try {
    // TODO: Charger les vrais élèves depuis l'API
    classStudents.value = [
      { id: '1', first_name: 'Marie', last_name: 'Dubois', student_number: '001' },
      { id: '2', first_name: 'Pierre', last_name: 'Martin', student_number: '002' },
      { id: '3', first_name: 'Sophie', last_name: 'Blanc', student_number: '003' }
    ]
    
    // Initialiser les notes
    studentGrades.value = {}
    classStudents.value.forEach(student => {
      studentGrades.value[student.id] = { value: '', comment: '' }
    })
  } catch (error) {
    console.error('Erreur lors du chargement des élèves:', error)
  }
}

const updateEvaluationDetails = () => {
  // Les détails sont mis à jour automatiquement via computed
}

const fillAllGrades = (value: number) => {
  Object.keys(studentGrades.value).forEach(studentId => {
    studentGrades.value[studentId].value = value.toString()
  })
}

const clearAllGrades = () => {
  Object.keys(studentGrades.value).forEach(studentId => {
    studentGrades.value[studentId].value = ''
    studentGrades.value[studentId].comment = ''
  })
}

const validateGrade = (studentId: string) => {
  const grade = studentGrades.value[studentId]
  const maxValue = selectedEvaluation.value?.max_value || 20
  
  if (grade.value && parseFloat(grade.value) > maxValue) {
    grade.value = maxValue.toString()
  }
  
  if (grade.value && parseFloat(grade.value) < 0) {
    grade.value = '0'
  }
}

const saveGrades = async () => {
  saving.value = true
  try {
    const gradesToSave = []
    
    Object.entries(studentGrades.value).forEach(([studentId, grade]) => {
      if (grade.value && grade.value.trim()) {
        gradesToSave.push({
          student_id: studentId,
          subject_id: form.subject,
          evaluation_id: form.evaluation,
          class_id: form.class,
          value: parseFloat(grade.value),
          max_value: selectedEvaluation.value?.max_value || 20,
          coefficient: selectedEvaluation.value?.coefficient || 1,
          date: selectedEvaluation.value?.date || new Date().toISOString().split('T')[0],
          period: 'T1', // TODO: Déterminer la période automatiquement
          comment: grade.comment,
          teacher_id: authStore.user?.id
        })
      }
    })
    
    // TODO: Utiliser l'API pour sauvegarder en lot
    await gradesStore.bulkUpdateGrades(form.evaluation, gradesToSave)
    
    emit('saved')
  } catch (error) {
    console.error('Erreur lors de la sauvegarde des notes:', error)
  } finally {
    saving.value = false
  }
}

// Utilitaires
const getStudentInitials = (firstName: string, lastName: string) => {
  return (firstName[0] + lastName[0]).toUpperCase()
}

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

// Watchers
watch(() => form.class, () => {
  if (form.class) {
    loadClassStudents()
  }
})
</script>