<template>
  <div class="space-y-6">
    <!-- En-tête avec navigation -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <BaseButton
          variant="outline"
          @click="$router.back()"
          class="flex items-center gap-2"
        >
          <ArrowLeftIcon class="w-4 h-4" />
          Retour
        </BaseButton>
        
        <div v-if="currentEvaluation">
          <h1 class="text-2xl font-bold text-gray-900">
            {{ currentEvaluation.title }}
          </h1>
          <div class="flex items-center gap-4 text-sm text-gray-600 mt-1">
            <span>{{ currentEvaluation.subject_name }}</span>
            <span>•</span>
            <span>{{ currentEvaluation.class_name }}</span>
            <span>•</span>
            <span>{{ formatDate(currentEvaluation.date) }}</span>
            <span>•</span>
            <span>Note sur {{ currentEvaluation.max_score }}</span>
          </div>
        </div>
      </div>
      
      <div class="flex gap-3">
        <BaseButton
          v-if="currentEvaluation && !currentEvaluation.is_published"
          variant="success"
          @click="publishEvaluation"
          :loading="loading.publishing"
          class="flex items-center gap-2"
        >
          <CheckIcon class="w-4 h-4" />
          Publier les notes
        </BaseButton>
        
        <BaseButton
          variant="primary"
          @click="saveAllGrades"
          :loading="loading.saving"
          :disabled="!hasChanges"
          class="flex items-center gap-2"
        >
          <CheckIcon class="w-4 h-4" />
          Sauvegarder
        </BaseButton>
      </div>
    </div>

    <!-- Statistiques de l'évaluation -->
    <BaseCard v-if="statistics">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div class="text-center">
          <div class="text-2xl font-bold text-blue-600">
            {{ statistics.average.toFixed(2) }}
          </div>
          <div class="text-sm text-gray-600">Moyenne</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-green-600">
            {{ statistics.max_score }}
          </div>
          <div class="text-sm text-gray-600">Note max</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-red-600">
            {{ statistics.min_score }}
          </div>
          <div class="text-sm text-gray-600">Note min</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-600">
            {{ Math.round(statistics.std_deviation * 100) / 100 }}
          </div>
          <div class="text-sm text-gray-600">Écart-type</div>
        </div>
      </div>
    </BaseCard>

    <!-- Actions en lot -->
    <BaseCard>
      <div class="flex justify-between items-center">
        <div class="flex items-center gap-4">
          <h3 class="text-lg font-semibold">Notes des élèves</h3>
          <BaseBadge :variant="getStatusColor()">
            {{ studentsWithGrades.length }}/{{ totalStudents }} saisis
          </BaseBadge>
        </div>
        
        <div class="flex gap-2">
          <BaseButton
            variant="outline"
            size="sm"
            @click="markAllPresent"
            class="flex items-center gap-1"
          >
            <UserGroupIcon class="w-4 h-4" />
            Tous présents
          </BaseButton>
          
          <BaseButton
            variant="outline"
            size="sm"
            @click="showImportModal = true"
            class="flex items-center gap-1"
          >
            <DocumentArrowUpIcon class="w-4 h-4" />
            Importer
          </BaseButton>
          
          <BaseButton
            variant="outline"
            size="sm"
            @click="exportGrades"
            class="flex items-center gap-1"
          >
            <DocumentArrowDownIcon class="w-4 h-4" />
            Exporter
          </BaseButton>
        </div>
      </div>
    </BaseCard>

    <!-- Table des notes -->
    <BaseCard>
      <div v-if="loading.grades" class="text-center py-8">
        <LoadingSpinner />
        <p class="mt-2 text-gray-600">Chargement des notes...</p>
      </div>
      
      <div v-else-if="students.length === 0" class="text-center py-8">
        <UserGroupIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p class="text-gray-600">Aucun élève trouvé pour cette classe</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Élève
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Note / {{ currentEvaluation?.max_score }}
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Statut
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Commentaire
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr 
              v-for="student in students" 
              :key="student.id"
              class="hover:bg-gray-50"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="text-sm font-medium text-gray-900">
                    {{ student.last_name }} {{ student.first_name }}
                  </div>
                </div>
              </td>
              
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <BaseInput
                  v-model.number="getGradeData(student.id).score"
                  type="number"
                  :min="0"
                  :max="currentEvaluation?.max_score"
                  step="0.25"
                  class="w-20 text-center"
                  :disabled="getGradeData(student.id).absent"
                  @input="updateGrade(student.id)"
                />
              </td>
              
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <div class="flex justify-center gap-2">
                  <label class="flex items-center">
                    <input
                      v-model="getGradeData(student.id).absent"
                      type="checkbox"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      @change="updateGrade(student.id)"
                    >
                    <span class="ml-1 text-xs text-gray-600">Absent</span>
                  </label>
                  
                  <label class="flex items-center">
                    <input
                      v-model="getGradeData(student.id).excuse"
                      type="checkbox"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      @change="updateGrade(student.id)"
                    >
                    <span class="ml-1 text-xs text-gray-600">Excusé</span>
                  </label>
                </div>
              </td>
              
              <td class="px-6 py-4 whitespace-nowrap">
                <BaseInput
                  v-model="getGradeData(student.id).comment"
                  placeholder="Commentaire..."
                  class="w-full"
                  @input="updateGrade(student.id)"
                />
              </td>
              
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <BaseBadge 
                  :variant="getGradeStatusColor(student.id)"
                  size="sm"
                >
                  {{ getGradeStatus(student.id) }}
                </BaseBadge>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </BaseCard>

    <!-- Modal d'import -->
    <BaseModal
      v-if="showImportModal"
      :is-open="showImportModal"
      title="Importer les notes"
      @close="showImportModal = false"
    >
      <div class="space-y-4">
        <p class="text-gray-700">
          Importez les notes depuis un fichier CSV ou Excel.
        </p>
        
        <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
          <DocumentArrowUpIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p class="text-gray-600">Glissez-déposez votre fichier ici ou</p>
          <BaseButton
            variant="outline"
            class="mt-2"
            @click="$refs.fileInput?.click()"
          >
            Choisir un fichier
          </BaseButton>
          <input
            ref="fileInput"
            type="file"
            accept=".csv,.xlsx,.xls"
            class="hidden"
            @change="handleFileUpload"
          >
        </div>
        
        <div class="flex justify-end gap-3">
          <BaseButton
            variant="outline"
            @click="showImportModal = false"
          >
            Annuler
          </BaseButton>
        </div>
      </div>
    </BaseModal>

    <!-- Modal de publication -->
    <BaseModal
      v-if="showPublishModal"
      :is-open="showPublishModal"
      title="Publier les notes"
      @close="showPublishModal = false"
    >
      <div class="space-y-4">
        <p class="text-gray-700">
          Êtes-vous sûr de vouloir publier les notes de cette évaluation ?
        </p>
        <p class="text-sm text-amber-600">
          Une fois publiées, les notes seront visibles par les élèves et leurs parents.
        </p>
        
        <div class="flex justify-end gap-3">
          <BaseButton
            variant="outline"
            @click="showPublishModal = false"
          >
            Annuler
          </BaseButton>
          <BaseButton
            variant="success"
            @click="confirmPublish"
            :loading="loading.publishing"
          >
            Publier
          </BaseButton>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { 
  ArrowLeftIcon,
  CheckIcon,
  UserGroupIcon,
  DocumentArrowUpIcon,
  DocumentArrowDownIcon
} from '@heroicons/vue/24/outline'

import { useGradesStore } from '@/stores/grades'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

import type { User, Grade } from '@/types'

const route = useRoute()
const gradesStore = useGradesStore()

// État local
const loading = ref({
  grades: false,
  saving: false,
  publishing: false
})

const students = ref<User[]>([])
const grades = ref<Record<string, Partial<Grade>>>({})
const hasChanges = ref(false)
const showImportModal = ref(false)
const showPublishModal = ref(false)

// Données calculées
const currentEvaluation = computed(() => gradesStore.currentEvaluation)
const evaluationId = computed(() => route.params.id as string)

const statistics = computed(() => {
  if (!currentEvaluation.value?.statistics) return null
  return currentEvaluation.value.statistics
})

const studentsWithGrades = computed(() => {
  return students.value.filter(student => {
    const grade = grades.value[student.id]
    return grade && (grade.score !== undefined || grade.absent || grade.excuse)
  })
})

const totalStudents = computed(() => students.value.length)

// Gestion des notes
const getGradeData = (studentId: string) => {
  if (!grades.value[studentId]) {
    grades.value[studentId] = {
      student: studentId,
      evaluation: evaluationId.value,
      score: undefined,
      absent: false,
      excuse: false,
      comment: ''
    }
  }
  return grades.value[studentId]
}

const updateGrade = (studentId: string) => {
  hasChanges.value = true
  
  // Si l'élève est marqué absent, effacer la note
  if (grades.value[studentId]?.absent) {
    grades.value[studentId].score = undefined
  }
}

const getGradeStatus = (studentId: string) => {
  const grade = grades.value[studentId]
  if (!grade) return 'Non saisi'
  if (grade.absent) return 'Absent'
  if (grade.excuse) return 'Excusé'
  if (grade.score !== undefined) return 'Noté'
  return 'Non saisi'
}

const getGradeStatusColor = (studentId: string) => {
  const status = getGradeStatus(studentId)
  switch (status) {
    case 'Noté': return 'success'
    case 'Absent': return 'danger'
    case 'Excusé': return 'warning'
    default: return 'default'
  }
}

const getStatusColor = () => {
  const percentage = (studentsWithGrades.value.length / totalStudents.value) * 100
  if (percentage === 100) return 'success'
  if (percentage >= 50) return 'warning'
  return 'danger'
}

// Actions
const loadData = async () => {
  loading.value.grades = true
  
  try {
    // Charger l'évaluation
    await gradesStore.fetchEvaluation(evaluationId.value)
    
    // Charger les notes existantes
    const existingGrades = await gradesStore.fetchEvaluationGrades(evaluationId.value)
    
    // Charger la liste des élèves de la classe
    // TODO: Implémenter l'API pour récupérer les élèves d'une classe
    // Pour l'instant, utiliser des données mock
    students.value = [
      { id: '1', first_name: 'Jean', last_name: 'Dupont', email: 'jean.dupont@example.com', user_type: 'student', is_active: true, created_at: '', updated_at: '' },
      { id: '2', first_name: 'Marie', last_name: 'Martin', email: 'marie.martin@example.com', user_type: 'student', is_active: true, created_at: '', updated_at: '' },
      { id: '3', first_name: 'Pierre', last_name: 'Bernard', email: 'pierre.bernard@example.com', user_type: 'student', is_active: true, created_at: '', updated_at: '' }
    ]
    
    // Initialiser les notes
    existingGrades.forEach(grade => {
      grades.value[grade.student] = { ...grade }
    })
    
    // Initialiser les élèves sans note
    students.value.forEach(student => {
      if (!grades.value[student.id]) {
        getGradeData(student.id)
      }
    })
    
  } catch (error) {
    console.error('Erreur lors du chargement:', error)
  } finally {
    loading.value.grades = false
  }
}

const saveAllGrades = async () => {
  if (!hasChanges.value) return
  
  loading.value.saving = true
  
  try {
    const gradeUpdates = Object.values(grades.value).filter(grade => 
      grade.score !== undefined || grade.absent || grade.excuse || grade.comment
    )
    
    await gradesStore.bulkUpdateGrades(evaluationId.value, gradeUpdates)
    hasChanges.value = false
    
    // Recharger les statistiques
    await gradesStore.fetchEvaluation(evaluationId.value)
    
  } catch (error) {
    console.error('Erreur lors de la sauvegarde:', error)
  } finally {
    loading.value.saving = false
  }
}

const markAllPresent = () => {
  students.value.forEach(student => {
    const grade = getGradeData(student.id)
    grade.absent = false
    grade.excuse = false
  })
  hasChanges.value = true
}

const publishEvaluation = () => {
  showPublishModal.value = true
}

const confirmPublish = async () => {
  loading.value.publishing = true
  
  try {
    // Sauvegarder d'abord les notes
    if (hasChanges.value) {
      await saveAllGrades()
    }
    
    // Publier l'évaluation
    await gradesStore.updateEvaluation(evaluationId.value, { is_published: true })
    
    showPublishModal.value = false
    
  } catch (error) {
    console.error('Erreur lors de la publication:', error)
  } finally {
    loading.value.publishing = false
  }
}

const exportGrades = () => {
  // TODO: Implémenter l'export
  console.log('Export des notes')
}

const handleFileUpload = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  
  // TODO: Implémenter l'import
  console.log('Import du fichier:', file.name)
  showImportModal.value = false
}

// Utilitaires
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR')
}

// Lifecycle
onMounted(() => {
  loadData()
})

// Navigation guard (prévenir la perte de données)
watch(hasChanges, (newValue) => {
  if (newValue) {
    window.addEventListener('beforeunload', (e) => {
      e.preventDefault()
      e.returnValue = ''
    })
  } else {
    window.removeEventListener('beforeunload', () => {})
  }
})
</script>