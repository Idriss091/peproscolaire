<template>
  <div class="space-y-6">
    <!-- En-tête avec actions -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Évaluations</h1>
        <p class="text-gray-600">Gestion des devoirs, contrôles et examens</p>
      </div>
      
      <div class="flex gap-3">
        <BaseButton
          v-if="authStore.hasPermission('teacher_access')"
          variant="primary"
          @click="showCreateModal = true"
          class="flex items-center gap-2"
        >
          <PlusIcon class="w-4 h-4" />
          Nouvelle évaluation
        </BaseButton>
      </div>
    </div>

    <!-- Filtres -->
    <BaseCard>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <BaseInput
          v-model="filters.search"
          placeholder="Rechercher une évaluation..."
          @input="handleSearch"
        />
        
        <select
          v-model="filters.evaluation_type"
          @change="applyFilters"
          class="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Tous les types</option>
          <option 
            v-for="type in gradesStore.getActiveEvaluationTypes" 
            :key="type.id" 
            :value="type.id"
          >
            {{ type.name }}
          </option>
        </select>
        
        <select
          v-model="filters.subject"
          @change="applyFilters"
          class="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Toutes les matières</option>
          <option 
            v-for="subject in subjects" 
            :key="subject.id" 
            :value="subject.id"
          >
            {{ subject.name }}
          </option>
        </select>
        
        <select
          v-model="filters.is_published"
          @change="applyFilters"
          class="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Tous les statuts</option>
          <option value="true">Publiées</option>
          <option value="false">Brouillons</option>
        </select>
      </div>
    </BaseCard>

    <!-- Liste des évaluations -->
    <BaseCard>
      <div v-if="gradesStore.loading.evaluations" class="text-center py-8">
        <LoadingSpinner />
        <p class="mt-2 text-gray-600">Chargement des évaluations...</p>
      </div>
      
      <div v-else-if="gradesStore.evaluations.length === 0" class="text-center py-8">
        <AcademicCapIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p class="text-gray-600">Aucune évaluation trouvée</p>
        <p class="text-sm text-gray-500 mt-1">
          {{ filters.search || Object.values(filters).some(v => v) 
            ? 'Essayez de modifier vos filtres' 
            : 'Créez votre première évaluation pour commencer' }}
        </p>
      </div>
      
      <div v-else class="space-y-4">
        <div 
          v-for="evaluation in gradesStore.evaluations" 
          :key="evaluation.id"
          class="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
          @click="viewEvaluation(evaluation.id)"
        >
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-lg font-semibold text-gray-900">
                  {{ evaluation.title }}
                </h3>
                <BaseBadge 
                  :variant="evaluation.is_published ? 'success' : 'warning'"
                  size="sm"
                >
                  {{ evaluation.is_published ? 'Publiée' : 'Brouillon' }}
                </BaseBadge>
                <BaseBadge 
                  :variant="getEvaluationTypeColor(evaluation.evaluation_type)"
                  size="sm"
                >
                  {{ evaluation.evaluation_type_name }}
                </BaseBadge>
              </div>
              
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                <div>
                  <span class="font-medium">Matière:</span>
                  {{ evaluation.subject_name }}
                </div>
                <div>
                  <span class="font-medium">Classe:</span>
                  {{ evaluation.class_name }}
                </div>
                <div>
                  <span class="font-medium">Date:</span>
                  {{ formatDate(evaluation.date) }}
                </div>
                <div>
                  <span class="font-medium">Note sur:</span>
                  {{ evaluation.max_score }}
                </div>
              </div>
              
              <p v-if="evaluation.description" class="text-gray-700 mt-2">
                {{ evaluation.description }}
              </p>
              
              <!-- Statistiques si publiée -->
              <div v-if="evaluation.is_published && evaluation.statistics" class="mt-3 flex gap-6 text-sm">
                <div class="text-blue-600">
                  <span class="font-medium">Moyenne:</span>
                  {{ evaluation.statistics.average.toFixed(2) }}
                </div>
                <div class="text-green-600">
                  <span class="font-medium">Max:</span>
                  {{ evaluation.statistics.max_score }}
                </div>
                <div class="text-red-600">
                  <span class="font-medium">Min:</span>
                  {{ evaluation.statistics.min_score }}
                </div>
              </div>
            </div>
            
            <!-- Actions -->
            <div class="flex gap-2 ml-4">
              <BaseButton
                variant="outline"
                size="sm"
                @click.stop="viewGrades(evaluation.id)"
                class="flex items-center gap-1"
              >
                <EyeIcon class="w-4 h-4" />
                Notes
              </BaseButton>
              
              <BaseButton
                v-if="authStore.hasPermission('teacher_access')"
                variant="outline"
                size="sm"
                @click.stop="editEvaluation(evaluation.id)"
                class="flex items-center gap-1"
              >
                <PencilIcon class="w-4 h-4" />
                Modifier
              </BaseButton>
              
              <BaseButton
                v-if="authStore.hasPermission('teacher_access') && !evaluation.is_published"
                variant="danger"
                size="sm"
                @click.stop="confirmDelete(evaluation)"
                class="flex items-center gap-1"
              >
                <TrashIcon class="w-4 h-4" />
                Supprimer
              </BaseButton>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Pagination -->
      <TablePagination
        v-if="gradesStore.pagination.evaluations.count > 0"
        :current-page="currentPage"
        :total-items="gradesStore.pagination.evaluations.count"
        :items-per-page="20"
        @page-change="handlePageChange"
        class="mt-6"
      />
    </BaseCard>

    <!-- Modal de création/édition -->
    <EvaluationFormModal
      v-if="showCreateModal || showEditModal"
      :is-open="showCreateModal || showEditModal"
      :evaluation="selectedEvaluation"
      @close="closeModals"
      @saved="handleEvaluationSaved"
    />

    <!-- Modal de confirmation de suppression -->
    <BaseModal
      v-if="showDeleteModal"
      :is-open="showDeleteModal"
      title="Supprimer l'évaluation"
      @close="showDeleteModal = false"
    >
      <div class="space-y-4">
        <p class="text-gray-700">
          Êtes-vous sûr de vouloir supprimer l'évaluation 
          <strong>{{ evaluationToDelete?.title }}</strong> ?
        </p>
        <p class="text-sm text-red-600">
          Cette action est irréversible et supprimera également toutes les notes associées.
        </p>
        
        <div class="flex justify-end gap-3">
          <BaseButton
            variant="outline"
            @click="showDeleteModal = false"
          >
            Annuler
          </BaseButton>
          <BaseButton
            variant="danger"
            @click="deleteEvaluation"
            :loading="gradesStore.loading.saving"
          >
            Supprimer
          </BaseButton>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { debounce } from 'lodash-es'
import { 
  PlusIcon, 
  EyeIcon, 
  PencilIcon, 
  TrashIcon,
  AcademicCapIcon 
} from '@heroicons/vue/24/outline'

import { useAuthStore } from '@/stores/auth'
import { useGradesStore } from '@/stores/grades'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import TablePagination from '@/components/ui/TablePagination.vue'
import EvaluationFormModal from '@/components/grades/EvaluationFormModal.vue'

import type { Evaluation, Subject } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const gradesStore = useGradesStore()

// État local
const currentPage = ref(1)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const selectedEvaluation = ref<Evaluation | null>(null)
const evaluationToDelete = ref<Evaluation | null>(null)
const subjects = ref<Subject[]>([])

// Filtres
const filters = ref({
  search: '',
  evaluation_type: '',
  subject: '',
  is_published: ''
})

// Gestion de la recherche avec debounce
const handleSearch = debounce(() => {
  applyFilters()
}, 300)

// Actions
const applyFilters = () => {
  currentPage.value = 1
  loadEvaluations()
}

const loadEvaluations = async () => {
  const params = {
    page: currentPage.value,
    page_size: 20,
    ...Object.fromEntries(
      Object.entries(filters.value).filter(([_, value]) => value !== '')
    )
  }
  
  await gradesStore.fetchEvaluations(params)
}

const viewEvaluation = (id: string) => {
  router.push({ name: 'evaluation-detail', params: { id } })
}

const viewGrades = (id: string) => {
  router.push({ name: 'evaluation-grades', params: { id } })
}

const editEvaluation = (id: string) => {
  selectedEvaluation.value = gradesStore.getEvaluationById.value(id) || null
  showEditModal.value = true
}

const confirmDelete = (evaluation: Evaluation) => {
  evaluationToDelete.value = evaluation
  showDeleteModal.value = true
}

const deleteEvaluation = async () => {
  if (!evaluationToDelete.value) return
  
  try {
    await gradesStore.deleteEvaluation(evaluationToDelete.value.id)
    showDeleteModal.value = false
    evaluationToDelete.value = null
  } catch (error) {
    console.error('Erreur lors de la suppression:', error)
  }
}

const closeModals = () => {
  showCreateModal.value = false
  showEditModal.value = false
  selectedEvaluation.value = null
}

const handleEvaluationSaved = (evaluation: Evaluation) => {
  closeModals()
  loadEvaluations()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadEvaluations()
}

// Utilitaires
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR')
}

const getEvaluationTypeColor = (typeId: string) => {
  const type = gradesStore.getActiveEvaluationTypes.value.find(t => t.id === typeId)
  if (!type) return 'default'
  
  // Couleurs basées sur le nom du type
  if (type.name.toLowerCase().includes('contrôle')) return 'blue'
  if (type.name.toLowerCase().includes('devoir')) return 'green'
  if (type.name.toLowerCase().includes('examen')) return 'red'
  return 'default'
}

// Lifecycle
onMounted(async () => {
  // Charger les données initiales
  await Promise.all([
    gradesStore.fetchEvaluationTypes(),
    loadEvaluations()
  ])
  
  // Charger la liste des matières (à implémenter selon l'API)
  // subjects.value = await timetableApi.getSubjects()
})
</script>