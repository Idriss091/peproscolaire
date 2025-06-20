<template>
  <div class="space-y-6">
    <!-- Actions rapides -->
    <div class="flex justify-between items-center">
      <div class="flex gap-3">
        <BaseButton
          v-if="authStore.hasPermission('teacher_access')"
          variant="primary"
          @click="showAddEvaluationModal = true"
          class="flex items-center gap-2"
        >
          <PlusIcon class="w-4 h-4" />
          Nouvelle évaluation
        </BaseButton>
        
        <BaseButton
          variant="secondary"
          @click="exportEvaluations"
          class="flex items-center gap-2"
        >
          <DocumentArrowDownIcon class="w-4 h-4" />
          Exporter
        </BaseButton>
      </div>
      
      <div class="flex items-center gap-2">
        <BaseInput
          v-model="searchTerm"
          placeholder="Rechercher une évaluation..."
          size="sm"
          class="w-64"
        />
      </div>
    </div>

    <!-- Filtres -->
    <BaseCard>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Matière
          </label>
          <select
            v-model="filters.subject"
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
            Type
          </label>
          <select
            v-model="filters.type"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Tous les types</option>
            <option value="controle">Contrôle</option>
            <option value="devoir">Devoir</option>
            <option value="interrogation">Interrogation</option>
            <option value="examen">Examen</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Statut
          </label>
          <select
            v-model="filters.status"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Tous les statuts</option>
            <option value="planned">Planifiée</option>
            <option value="in_progress">En cours</option>
            <option value="completed">Terminée</option>
            <option value="cancelled">Annulée</option>
          </select>
        </div>
      </div>
    </BaseCard>

    <!-- Liste des évaluations -->
    <div class="space-y-4">
      <div v-if="loading" class="text-center py-8">
        <LoadingSpinner />
        <p class="mt-2 text-gray-600">Chargement des évaluations...</p>
      </div>
      
      <div v-else-if="filteredEvaluations.length === 0" class="text-center py-8">
        <ClipboardDocumentIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p class="text-gray-600">Aucune évaluation trouvée</p>
      </div>
      
      <div
        v-for="evaluation in filteredEvaluations"
        :key="evaluation.id"
        class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
        @click="viewEvaluation(evaluation)"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3 mb-2">
              <h3 class="text-lg font-medium text-gray-900">{{ evaluation.name }}</h3>
              <BaseBadge :variant="getStatusColor(evaluation.status)">
                {{ getStatusLabel(evaluation.status) }}
              </BaseBadge>
              <BaseBadge variant="secondary">
                {{ getTypeLabel(evaluation.type) }}
              </BaseBadge>
            </div>
            
            <p v-if="evaluation.description" class="text-sm text-gray-600 mb-3">
              {{ evaluation.description }}
            </p>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span class="font-medium text-gray-700">Matière:</span>
                <div class="flex items-center mt-1">
                  <div
                    class="w-3 h-3 rounded-full mr-2"
                    :style="{ backgroundColor: getSubjectColor(evaluation.subject_id) }"
                  />
                  <span>{{ evaluation.subject_name }}</span>
                </div>
              </div>
              
              <div>
                <span class="font-medium text-gray-700">Classe:</span>
                <p class="mt-1">{{ evaluation.class_name }}</p>
              </div>
              
              <div>
                <span class="font-medium text-gray-700">Date:</span>
                <p class="mt-1">{{ formatDate(evaluation.date) }}</p>
              </div>
              
              <div>
                <span class="font-medium text-gray-700">Durée:</span>
                <p class="mt-1">{{ evaluation.duration || 'Non spécifiée' }}</p>
              </div>
              
              <div>
                <span class="font-medium text-gray-700">Note sur:</span>
                <p class="mt-1">{{ evaluation.max_value }}</p>
              </div>
              
              <div>
                <span class="font-medium text-gray-700">Coefficient:</span>
                <p class="mt-1">{{ evaluation.coefficient }}</p>
              </div>
              
              <div>
                <span class="font-medium text-gray-700">Notes saisies:</span>
                <p class="mt-1">{{ evaluation.grades_count || 0 }}/{{ evaluation.students_count || 0 }}</p>
              </div>
              
              <div>
                <span class="font-medium text-gray-700">Moyenne:</span>
                <p class="mt-1">
                  {{ evaluation.average ? `${evaluation.average}/20` : 'N/A' }}
                </p>
              </div>
            </div>
          </div>
          
          <div class="flex items-center space-x-2 ml-4">
            <BaseButton
              v-if="evaluation.status === 'planned'"
              variant="primary"
              size="sm"
              @click.stop="startEvaluation(evaluation)"
            >
              Commencer
            </BaseButton>
            
            <BaseButton
              v-if="evaluation.status === 'completed'"
              variant="success"
              size="sm"
              @click.stop="viewResults(evaluation)"
            >
              Résultats
            </BaseButton>
            
            <BaseButton
              variant="outline"
              size="sm"
              @click.stop="editEvaluation(evaluation)"
            >
              Modifier
            </BaseButton>
            
            <BaseButton
              v-if="evaluation.status !== 'completed'"
              variant="danger"
              size="sm"
              @click.stop="deleteEvaluation(evaluation.id)"
            >
              Supprimer
            </BaseButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal d'ajout d'évaluation -->
    <BaseModal
      :is-open="showAddEvaluationModal"
      title="Nouvelle évaluation"
      @close="showAddEvaluationModal = false"
      size="lg"
    >
      <AddEvaluationForm
        @close="showAddEvaluationModal = false"
        @saved="handleEvaluationSaved"
      />
    </BaseModal>

    <!-- Modal de modification -->
    <BaseModal
      v-if="editingEvaluation"
      :is-open="!!editingEvaluation"
      title="Modifier l'évaluation"
      @close="editingEvaluation = null"
      size="lg"
    >
      <EditEvaluationForm
        :evaluation="editingEvaluation"
        @close="editingEvaluation = null"
        @saved="handleEvaluationUpdated"
      />
    </BaseModal>

    <!-- Modal de détail -->
    <BaseModal
      v-if="selectedEvaluation"
      :is-open="!!selectedEvaluation"
      :title="selectedEvaluation.name"
      @close="selectedEvaluation = null"
      size="lg"
    >
      <EvaluationDetailView
        :evaluation="selectedEvaluation"
        @close="selectedEvaluation = null"
        @edit="editEvaluation"
        @start="startEvaluation"
        @view-results="viewResults"
      />
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  PlusIcon,
  DocumentArrowDownIcon,
  ClipboardDocumentIcon
} from '@heroicons/vue/24/outline'

import { useAuthStore } from '@/stores/auth'
import { useGradesStore } from '@/stores/grades'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import AddEvaluationForm from '@/components/grades/AddEvaluationForm.vue'
import EditEvaluationForm from '@/components/grades/EditEvaluationForm.vue'
import EvaluationDetailView from '@/components/grades/EvaluationDetailView.vue'

const authStore = useAuthStore()
const gradesStore = useGradesStore()

// État local
const loading = ref(false)
const searchTerm = ref('')
const showAddEvaluationModal = ref(false)
const selectedEvaluation = ref<any>(null)
const editingEvaluation = ref<any>(null)

// Filtres
const filters = reactive({
  subject: '',
  class: '',
  type: '',
  status: ''
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

const evaluations = ref([
  {
    id: '1',
    name: 'Contrôle Chapitre 1 - Les fractions',
    description: 'Évaluation sur les fractions simples et les opérations',
    subject_id: '1',
    subject_name: 'Mathématiques',
    class_id: '1',
    class_name: '6ème A',
    date: '2024-01-15',
    duration: '1h',
    max_value: 20,
    coefficient: 2,
    type: 'controle',
    status: 'completed',
    grades_count: 25,
    students_count: 25,
    average: 13.5
  },
  {
    id: '2',
    name: 'Devoir Maison n°2',
    description: 'Exercices sur les nombres décimaux',
    subject_id: '1',
    subject_name: 'Mathématiques',
    class_id: '1',
    class_name: '6ème A',
    date: '2024-01-20',
    duration: null,
    max_value: 20,
    coefficient: 1,
    type: 'devoir',
    status: 'planned',
    grades_count: 0,
    students_count: 25,
    average: null
  }
])

// Computed
const filteredEvaluations = computed(() => {
  let filtered = evaluations.value

  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase()
    filtered = filtered.filter(evaluation => 
      evaluation.name.toLowerCase().includes(term) ||
      evaluation.description?.toLowerCase().includes(term) ||
      evaluation.subject_name.toLowerCase().includes(term)
    )
  }

  if (filters.subject) {
    filtered = filtered.filter(evaluation => evaluation.subject_id === filters.subject)
  }

  if (filters.class) {
    filtered = filtered.filter(evaluation => evaluation.class_id === filters.class)
  }

  if (filters.type) {
    filtered = filtered.filter(evaluation => evaluation.type === filters.type)
  }

  if (filters.status) {
    filtered = filtered.filter(evaluation => evaluation.status === filters.status)
  }

  return filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
})

// Méthodes
const loadEvaluations = async () => {
  loading.value = true
  try {
    await gradesStore.fetchEvaluations(filters)
  } catch (error) {
    console.error('Erreur lors du chargement des évaluations:', error)
  } finally {
    loading.value = false
  }
}

const viewEvaluation = (evaluation: any) => {
  selectedEvaluation.value = evaluation
}

const editEvaluation = (evaluation: any) => {
  editingEvaluation.value = evaluation
}

const startEvaluation = async (evaluation: any) => {
  try {
    // TODO: Logique pour commencer une évaluation
    console.log('Commencer l\'évaluation:', evaluation.id)
    evaluation.status = 'in_progress'
  } catch (error) {
    console.error('Erreur lors du démarrage de l\'évaluation:', error)
  }
}

const viewResults = (evaluation: any) => {
  // TODO: Rediriger vers la page des résultats
  console.log('Voir les résultats de l\'évaluation:', evaluation.id)
}

const deleteEvaluation = async (evaluationId: string) => {
  if (!confirm('Êtes-vous sûr de vouloir supprimer cette évaluation ?')) {
    return
  }
  
  try {
    await gradesStore.deleteEvaluation(evaluationId)
    const index = evaluations.value.findIndex(e => e.id === evaluationId)
    if (index !== -1) {
      evaluations.value.splice(index, 1)
    }
  } catch (error) {
    console.error('Erreur lors de la suppression:', error)
  }
}

const handleEvaluationSaved = () => {
  showAddEvaluationModal.value = false
  loadEvaluations()
}

const handleEvaluationUpdated = () => {
  editingEvaluation.value = null
  loadEvaluations()
}

const exportEvaluations = async () => {
  try {
    const csvContent = generateEvaluationsCSV()
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `evaluations-${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Erreur lors de l\'export:', error)
  }
}

const generateEvaluationsCSV = () => {
  const headers = ['Nom', 'Matière', 'Classe', 'Date', 'Type', 'Statut', 'Note max', 'Coefficient', 'Notes saisies', 'Moyenne']
  const rows = [headers.join(',')]
  
  filteredEvaluations.value.forEach(evaluation => {
    const row = [
      evaluation.name,
      evaluation.subject_name,
      evaluation.class_name,
      formatDate(evaluation.date),
      getTypeLabel(evaluation.type),
      getStatusLabel(evaluation.status),
      evaluation.max_value,
      evaluation.coefficient,
      `${evaluation.grades_count}/${evaluation.students_count}`,
      evaluation.average || 'N/A'
    ]
    rows.push(row.join(','))
  })
  
  return rows.join('\n')
}

// Utilitaires
const getStatusColor = (status: string) => {
  const colors = {
    planned: 'secondary',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return colors[status as keyof typeof colors] || 'secondary'
}

const getStatusLabel = (status: string) => {
  const labels = {
    planned: 'Planifiée',
    in_progress: 'En cours',
    completed: 'Terminée',
    cancelled: 'Annulée'
  }
  return labels[status as keyof typeof labels] || status
}

const getTypeLabel = (type: string) => {
  const labels = {
    controle: 'Contrôle',
    devoir: 'Devoir',
    interrogation: 'Interrogation',
    examen: 'Examen'
  }
  return labels[type as keyof typeof labels] || type
}

const getSubjectColor = (subjectId: string) => {
  return subjects.value.find(s => s.id === subjectId)?.color || '#6B7280'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

// Lifecycle
onMounted(() => {
  loadEvaluations()
})
</script>