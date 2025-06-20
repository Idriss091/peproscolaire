<template>
  <div class="space-y-6">
    <!-- En-tête -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Notes et évaluations</h1>
        <p class="text-gray-600">Gestion des notes, évaluations et bulletins</p>
      </div>
      
      <div class="flex gap-3">
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
          variant="primary"
          @click="showAddGradeModal = true"
          class="flex items-center gap-2"
        >
          <PlusIcon class="w-4 h-4" />
          Nouvelle note
        </BaseButton>
      </div>
    </div>

    <!-- Statistiques rapides -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <AcademicCapIcon class="h-8 w-8 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Moyenne générale</p>
            <p class="text-2xl font-semibold text-gray-900">{{ overallStats.average }}/20</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ChartBarIcon class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Notes saisies</p>
            <p class="text-2xl font-semibold text-gray-900">{{ overallStats.total }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <TrophyIcon class="h-8 w-8 text-yellow-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Excellents résultats</p>
            <p class="text-2xl font-semibold text-gray-900">{{ overallStats.excellent }}</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ExclamationTriangleIcon class="h-8 w-8 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">En difficulté</p>
            <p class="text-2xl font-semibold text-gray-900">{{ overallStats.struggling }}</p>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Onglets -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="border-b-2 py-2 px-1 text-sm font-medium"
          :class="activeTab === tab.id
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- Contenu des onglets -->
    <div v-if="activeTab === 'grades'">
      <!-- Onglet Notes -->
      <GradesListView />
    </div>

    <div v-else-if="activeTab === 'evaluations'">
      <!-- Onglet Évaluations -->
      <EvaluationsView />
    </div>

    <div v-else-if="activeTab === 'bulletins'">
      <!-- Onglet Bulletins -->
      <ReportCardsView />
    </div>

    <div v-else-if="activeTab === 'competences'">
      <!-- Onglet Compétences -->
      <CompetencesView />
    </div>

    <!-- Modal d'ajout de note -->
    <BaseModal
      :is-open="showAddGradeModal"
      title="Ajouter une note"
      @close="showAddGradeModal = false"
      size="lg"
    >
      <AddGradeForm
        @close="showAddGradeModal = false"
        @saved="handleGradeSaved"
      />
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  PlusIcon,
  DocumentArrowDownIcon,
  AcademicCapIcon,
  ChartBarIcon,
  TrophyIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'

import { useAuthStore } from '@/stores/auth'
import { useGradesStore } from '@/stores/grades'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import GradesListView from '@/components/grades/GradesListView.vue'
import EvaluationsView from '@/components/grades/EvaluationsView.vue'
import ReportCardsView from '@/components/grades/ReportCardsView.vue'
import CompetencesView from '@/components/grades/CompetencesView.vue'
import AddGradeForm from '@/components/grades/AddGradeForm.vue'

const authStore = useAuthStore()
const gradesStore = useGradesStore()

// État local
const activeTab = ref('grades')
const showAddGradeModal = ref(false)

// Onglets
const tabs = [
  { id: 'grades', name: 'Notes' },
  { id: 'evaluations', name: 'Évaluations' },
  { id: 'bulletins', name: 'Bulletins' },
  { id: 'competences', name: 'Compétences' }
]

// Computed
const overallStats = computed(() => gradesStore.overallStats)

// Méthodes
const exportGrades = async () => {
  try {
    await gradesStore.exportGrades({
      format: 'xlsx',
      includeStats: true
    })
  } catch (error) {
    console.error('Erreur lors de l\'export:', error)
  }
}

const handleGradeSaved = () => {
  showAddGradeModal.value = false
  // Recharger les données si nécessaire
  gradesStore.fetchGrades()
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    gradesStore.fetchGrades(),
    gradesStore.fetchEvaluations(),
    gradesStore.fetchSubjects(),
    gradesStore.fetchClasses()
  ])
})
</script>