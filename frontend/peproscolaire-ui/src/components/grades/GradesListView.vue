<template>
  <div class="space-y-6">
    <!-- Filtres -->
    <BaseCard>
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Matière
          </label>
          <select
            v-model="filters.subject"
            @change="applyFilters"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Toutes les matières</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
              {{ subject.name }}
            </option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Classe
          </label>
          <select
            v-model="filters.class"
            @change="applyFilters"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Toutes les classes</option>
            <option v-for="cls in classes" :key="cls.id" :value="cls.id">
              {{ cls.name }}
            </option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Période
          </label>
          <select
            v-model="filters.period"
            @change="applyFilters"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Toutes les périodes</option>
            <option value="T1">Trimestre 1</option>
            <option value="T2">Trimestre 2</option>
            <option value="T3">Trimestre 3</option>
          </select>
        </div>
        
        <BaseInput
          v-model="filters.dateFrom"
          type="date"
          label="Date de début"
          @change="applyFilters"
        />
        
        <BaseInput
          v-model="filters.dateTo"
          type="date"
          label="Date de fin"
          @change="applyFilters"
        />
      </div>
      
      <div class="mt-4 flex justify-between items-center">
        <div class="flex gap-2">
          <BaseButton
            variant="primary"
            @click="loadGrades"
            class="flex items-center gap-2"
          >
            <MagnifyingGlassIcon class="w-4 h-4" />
            Rechercher
          </BaseButton>
          
          <BaseButton
            variant="secondary"
            @click="clearFilters"
            class="flex items-center gap-2"
          >
            <XMarkIcon class="w-4 h-4" />
            Effacer
          </BaseButton>
        </div>
        
        <div class="flex gap-2">
          <BaseButton
            variant="secondary"
            @click="exportGrades"
            class="flex items-center gap-2"
          >
            <DocumentArrowDownIcon class="w-4 h-4" />
            Exporter
          </BaseButton>
          
          <BaseButton
            v-if="authStore.hasPermission('teacher_access')"
            variant="outline"
            @click="showBulkGradeModal = true"
            class="flex items-center gap-2"
          >
            <PencilIcon class="w-4 h-4" />
            Saisie groupée
          </BaseButton>
        </div>
      </div>
    </BaseCard>

    <!-- Statistiques rapides -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ChartBarIcon class="h-8 w-8 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Moyenne générale</p>
            <p class="text-2xl font-semibold text-gray-900">{{ gradeStats.average }}/20</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <HashtagIcon class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total notes</p>
            <p class="text-2xl font-semibold text-gray-900">{{ gradeStats.total }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <TrophyIcon class="h-8 w-8 text-yellow-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Excellents</p>
            <p class="text-2xl font-semibold text-gray-900">{{ gradeStats.excellent }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ExclamationTriangleIcon class="h-8 w-8 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Difficultés</p>
            <p class="text-2xl font-semibold text-gray-900">{{ gradeStats.struggling }}</p>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Liste des notes -->
    <BaseCard>
      <div v-if="loading" class="text-center py-8">
        <LoadingSpinner />
        <p class="mt-2 text-gray-600">Chargement des notes...</p>
      </div>
      
      <div v-else-if="filteredGrades.length === 0" class="text-center py-8">
        <AcademicCapIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p class="text-gray-600">Aucune note trouvée</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Élève
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Matière
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Évaluation
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Note
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Coeff.
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
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
            <tr v-for="grade in filteredGrades" :key="grade.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                      <span class="text-sm font-medium text-gray-700">
                        {{ getStudentInitials(grade.student_name) }}
                      </span>
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ grade.student_name }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ grade.class_name }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div
                    class="w-3 h-3 rounded-full mr-2"
                    :style="{ backgroundColor: getSubjectColor(grade.subject_id) }"
                  />
                  <span class="text-sm text-gray-900">{{ grade.subject_name }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ grade.evaluation_name }}</div>
                <div class="text-xs text-gray-500">{{ grade.period }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <div class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                     :class="getGradeColorClass(grade.value, grade.max_value)">
                  {{ grade.value }}/{{ grade.max_value }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span class="text-sm text-gray-900">{{ grade.coefficient }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-900">{{ formatDate(grade.date) }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-500">{{ grade.comment || '-' }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <div class="flex justify-center space-x-2">
                  <BaseButton
                    variant="outline"
                    size="sm"
                    @click="viewGrade(grade)"
                  >
                    Voir
                  </BaseButton>
                  
                  <BaseButton
                    v-if="authStore.hasPermission('teacher_access')"
                    variant="primary"
                    size="sm"
                    @click="editGrade(grade)"
                  >
                    Modifier
                  </BaseButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </BaseCard>

    <!-- Modal de détail -->
    <BaseModal
      v-if="selectedGrade"
      :is-open="!!selectedGrade"
      title="Détail de la note"
      @close="selectedGrade = null"
    >
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="font-medium text-gray-700">Élève:</span>
            <p>{{ selectedGrade.student_name }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Classe:</span>
            <p>{{ selectedGrade.class_name }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Matière:</span>
            <p>{{ selectedGrade.subject_name }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Évaluation:</span>
            <p>{{ selectedGrade.evaluation_name }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Note:</span>
            <div class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                 :class="getGradeColorClass(selectedGrade.value, selectedGrade.max_value)">
              {{ selectedGrade.value }}/{{ selectedGrade.max_value }}
            </div>
          </div>
          <div>
            <span class="font-medium text-gray-700">Coefficient:</span>
            <p>{{ selectedGrade.coefficient }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Date:</span>
            <p>{{ formatDate(selectedGrade.date) }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-700">Période:</span>
            <p>{{ selectedGrade.period }}</p>
          </div>
        </div>
        
        <div v-if="selectedGrade.comment">
          <span class="font-medium text-gray-700">Commentaire:</span>
          <p class="mt-1 text-sm text-gray-600">{{ selectedGrade.comment }}</p>
        </div>
        
        <div class="flex justify-end space-x-3 pt-4 border-t">
          <BaseButton
            variant="outline"
            @click="selectedGrade = null"
          >
            Fermer
          </BaseButton>
        </div>
      </div>
    </BaseModal>

    <!-- Modal de modification -->
    <BaseModal
      v-if="editingGrade"
      :is-open="!!editingGrade"
      title="Modifier la note"
      @close="editingGrade = null"
    >
      <EditGradeForm
        :grade="editingGrade"
        @close="editingGrade = null"
        @saved="handleGradeUpdated"
      />
    </BaseModal>

    <!-- Modal de saisie groupée -->
    <BaseModal
      :is-open="showBulkGradeModal"
      title="Saisie groupée de notes"
      @close="showBulkGradeModal = false"
      size="lg"
    >
      <BulkGradeForm
        @close="showBulkGradeModal = false"
        @saved="handleBulkGradesSaved"
      />
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  MagnifyingGlassIcon,
  XMarkIcon,
  DocumentArrowDownIcon,
  PencilIcon,
  ChartBarIcon,
  HashtagIcon,
  TrophyIcon,
  ExclamationTriangleIcon,
  AcademicCapIcon
} from '@heroicons/vue/24/outline'

import { useAuthStore } from '@/stores/auth'
import { useGradesStore } from '@/stores/grades'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import EditGradeForm from '@/components/grades/EditGradeForm.vue'
import BulkGradeForm from '@/components/grades/BulkGradeForm.vue'

const authStore = useAuthStore()
const gradesStore = useGradesStore()

// État local
const selectedGrade = ref<any>(null)
const editingGrade = ref<any>(null)
const showBulkGradeModal = ref(false)

// Filtres
const filters = reactive({
  subject: '',
  class: '',
  period: '',
  dateFrom: '',
  dateTo: ''
})

// Données simulées
const subjects = ref([
  { id: '1', name: 'Mathématiques', color: '#3B82F6' },
  { id: '2', name: 'Français', color: '#10B981' },
  { id: '3', name: 'Histoire-Géographie', color: '#F59E0B' },
  { id: '4', name: 'Sciences', color: '#8B5CF6' }
])

const classes = ref([
  { id: '1', name: '6ème A' },
  { id: '2', name: '6ème B' },
  { id: '3', name: '5ème A' }
])

const grades = ref([
  {
    id: '1',
    student_name: 'Marie Dubois',
    class_name: '6ème A',
    subject_id: '1',
    subject_name: 'Mathématiques',
    evaluation_name: 'Contrôle Chapitre 1',
    value: 15.5,
    max_value: 20,
    coefficient: 2,
    date: '2024-01-15',
    period: 'T1',
    comment: 'Bon travail, continuez ainsi'
  },
  {
    id: '2',
    student_name: 'Pierre Martin',
    class_name: '6ème A',
    subject_id: '1',
    subject_name: 'Mathématiques',
    evaluation_name: 'Contrôle Chapitre 1',
    value: 12,
    max_value: 20,
    coefficient: 2,
    date: '2024-01-15',
    period: 'T1',
    comment: 'Peut mieux faire'
  }
])

// Computed
const loading = computed(() => gradesStore.loading.grades)

const filteredGrades = computed(() => {
  let filtered = grades.value

  if (filters.subject) {
    filtered = filtered.filter(grade => grade.subject_id === filters.subject)
  }

  if (filters.class) {
    filtered = filtered.filter(grade => grade.class_name.includes(filters.class))
  }

  if (filters.period) {
    filtered = filtered.filter(grade => grade.period === filters.period)
  }

  if (filters.dateFrom) {
    filtered = filtered.filter(grade => grade.date >= filters.dateFrom)
  }

  if (filters.dateTo) {
    filtered = filtered.filter(grade => grade.date <= filters.dateTo)
  }

  return filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
})

const gradeStats = computed(() => {
  const validGrades = filteredGrades.value.filter(g => g.value !== null)
  
  if (validGrades.length === 0) {
    return {
      average: '0.0',
      total: 0,
      excellent: 0,
      struggling: 0
    }
  }

  const sum = validGrades.reduce((acc, grade) => acc + grade.value, 0)
  const average = (sum / validGrades.length).toFixed(1)
  const excellent = validGrades.filter(g => g.value >= 16).length
  const struggling = validGrades.filter(g => g.value < 10).length

  return {
    average,
    total: validGrades.length,
    excellent,
    struggling
  }
})

// Méthodes
const loadGrades = async () => {
  try {
    await gradesStore.fetchGrades(filters)
  } catch (error) {
    console.error('Erreur lors du chargement des notes:', error)
  }
}

const applyFilters = () => {
  // Les filtres sont appliqués automatiquement via computed
}

const clearFilters = () => {
  Object.assign(filters, {
    subject: '',
    class: '',
    period: '',
    dateFrom: '',
    dateTo: ''
  })
}

const exportGrades = async () => {
  try {
    const csvContent = generateGradesCSV()
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `notes-${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Erreur lors de l\'export:', error)
  }
}

const generateGradesCSV = () => {
  const headers = ['Élève', 'Classe', 'Matière', 'Évaluation', 'Note', 'Note max', 'Coefficient', 'Date', 'Période', 'Commentaire']
  const rows = [headers.join(',')]
  
  filteredGrades.value.forEach(grade => {
    const row = [
      grade.student_name,
      grade.class_name,
      grade.subject_name,
      grade.evaluation_name,
      grade.value,
      grade.max_value,
      grade.coefficient,
      grade.date,
      grade.period,
      grade.comment.replace(/,/g, ';')
    ]
    rows.push(row.join(','))
  })
  
  return rows.join('\n')
}

const viewGrade = (grade: any) => {
  selectedGrade.value = grade
}

const editGrade = (grade: any) => {
  editingGrade.value = grade
}

const handleGradeUpdated = () => {
  editingGrade.value = null
  loadGrades()
}

const handleBulkGradesSaved = () => {
  showBulkGradeModal.value = false
  loadGrades()
}

// Utilitaires
const getStudentInitials = (name: string) => {
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
}

const getSubjectColor = (subjectId: string) => {
  return subjects.value.find(s => s.id === subjectId)?.color || '#6B7280'
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

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

// Lifecycle
onMounted(async () => {
  await loadGrades()
})
</script>