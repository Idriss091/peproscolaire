<template>
  <div class="space-y-6">
    <!-- Filtres et recherche -->
    <div class="bg-white p-4 rounded-lg border border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Rechercher un élève
          </label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Nom, prénom ou numéro"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Niveau de risque
          </label>
          <select
            v-model="selectedRiskLevel"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Tous les niveaux</option>
            <option value="élevé">Risque élevé</option>
            <option value="modéré">Risque modéré</option>
            <option value="faible">Risque faible</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Classe
          </label>
          <select
            v-model="selectedClass"
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
            Statut d'intervention
          </label>
          <select
            v-model="selectedStatus"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Tous les statuts</option>
            <option value="aucune">Aucune intervention</option>
            <option value="planifiée">Intervention planifiée</option>
            <option value="en_cours">Intervention en cours</option>
            <option value="terminée">Intervention terminée</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Actions groupées -->
    <div v-if="selectedStudents.length > 0" class="flex items-center justify-between bg-blue-50 p-4 rounded-lg border border-blue-200">
      <div class="flex items-center space-x-3">
        <span class="text-sm font-medium text-blue-900">
          {{ selectedStudents.length }} élève(s) sélectionné(s)
        </span>
      </div>
      <div class="flex space-x-2">
        <BaseButton
          variant="primary"
          size="sm"
          @click="createBulkIntervention"
        >
          Créer une intervention
        </BaseButton>
        <BaseButton
          variant="outline"
          size="sm"
          @click="exportSelectedStudents"
        >
          Exporter la sélection
        </BaseButton>
        <BaseButton
          variant="secondary"
          size="sm"
          @click="selectedStudents = []"
        >
          Désélectionner
        </BaseButton>
      </div>
    </div>

    <!-- Liste des élèves -->
    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">
            Élèves à risque ({{ filteredStudents.length }})
          </h3>
          <div class="flex items-center space-x-3">
            <div class="flex items-center space-x-2">
              <span class="text-xs text-gray-600">Trier par:</span>
              <select
                v-model="sortBy"
                class="text-xs border-gray-300 rounded"
              >
                <option value="risk_score">Score de risque</option>
                <option value="name">Nom</option>
                <option value="class">Classe</option>
                <option value="last_update">Dernière mise à jour</option>
              </select>
            </div>
            <BaseButton
              variant="outline"
              size="sm"
              @click="refreshData"
              :loading="loading"
            >
              <ArrowPathIcon class="w-4 h-4" />
              Actualiser
            </BaseButton>
          </div>
        </div>
      </div>

      <div v-if="loading" class="p-8 text-center">
        <div class="inline-flex items-center space-x-2 text-gray-600">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          <span>Chargement des données...</span>
        </div>
      </div>

      <div v-else-if="error" class="p-8 text-center">
        <div class="text-red-600 mb-4">
          <ExclamationTriangleIcon class="w-12 h-12 mx-auto mb-2" />
          <p class="font-medium">Erreur lors du chargement</p>
          <p class="text-sm text-gray-600 mt-1">{{ error }}</p>
        </div>
        <BaseButton variant="primary" @click="refreshData" :loading="loading">
          Réessayer
        </BaseButton>
      </div>

      <div v-else-if="filteredStudents.length === 0" class="p-8 text-center text-gray-500">
        <UserGroupIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
        <p>Aucun élève ne correspond aux critères de recherche</p>
      </div>

      <div v-else class="divide-y divide-gray-200">
        <div
          v-for="student in filteredStudents"
          :key="student.id"
          class="px-6 py-4 hover:bg-gray-50"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <input
                v-model="selectedStudents"
                :value="student.id"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              >
              
              <div class="flex-shrink-0">
                <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                  <span class="text-sm font-medium text-gray-700">
                    {{ getStudentInitials(student.first_name, student.last_name) }}
                  </span>
                </div>
              </div>
              
              <div class="flex-1 min-w-0">
                <div class="flex items-center space-x-3">
                  <p class="text-sm font-medium text-gray-900 truncate">
                    {{ student.first_name }} {{ student.last_name }}
                  </p>
                  <BaseBadge :variant="getRiskLevelColor(student.risk_level)" size="sm">
                    {{ student.risk_level }}
                  </BaseBadge>
                </div>
                <div class="flex items-center space-x-4 mt-1">
                  <p class="text-xs text-gray-500">{{ student.class_name }}</p>
                  <p class="text-xs text-gray-500">Score: {{ student.risk_score }}%</p>
                  <p class="text-xs text-gray-500">
                    Dernière analyse: {{ formatDate(student.last_analysis) }}
                  </p>
                </div>
              </div>
            </div>
            
            <div class="flex items-center space-x-4">
              <!-- Indicateurs de risque -->
              <div class="flex space-x-2">
                <div
                  v-if="student.risk_factors.absences"
                  class="flex items-center text-xs text-red-600"
                  title="Problème d'assiduité"
                >
                  <ClockIcon class="w-3 h-3 mr-1" />
                  Absences
                </div>
                <div
                  v-if="student.risk_factors.grades"
                  class="flex items-center text-xs text-orange-600"
                  title="Chute des notes"
                >
                  <ChartBarIcon class="w-3 h-3 mr-1" />
                  Notes
                </div>
                <div
                  v-if="student.risk_factors.behavior"
                  class="flex items-center text-xs text-yellow-600"
                  title="Problème de comportement"
                >
                  <ExclamationTriangleIcon class="w-3 h-3 mr-1" />
                  Comportement
                </div>
              </div>
              
              <!-- Statut d'intervention -->
              <div class="text-xs">
                <span
                  :class="getInterventionStatusColor(student.intervention_status)"
                  class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                >
                  {{ getInterventionStatusLabel(student.intervention_status) }}
                </span>
              </div>
              
              <!-- Actions -->
              <div class="flex space-x-1">
                <BaseButton
                  variant="outline"
                  size="xs"
                  @click="viewStudentDetail(student.id)"
                >
                  Détail
                </BaseButton>
                <BaseButton
                  v-if="!student.intervention_status || student.intervention_status === 'aucune'"
                  variant="primary"
                  size="xs"
                  @click="createIntervention(student.id)"
                >
                  Intervenir
                </BaseButton>
              </div>
            </div>
          </div>
          
          <!-- Prédictions récentes -->
          <div v-if="student.recent_predictions && student.recent_predictions.length > 0" 
               class="mt-3 pl-14">
            <div class="text-xs text-gray-600 mb-2">Prédictions récentes:</div>
            <div class="flex space-x-4">
              <div
                v-for="prediction in student.recent_predictions.slice(0, 3)"
                :key="prediction.id"
                class="text-xs bg-gray-50 rounded px-2 py-1"
              >
                <span class="font-medium">{{ prediction.type }}:</span>
                <span :class="getPredictionColor(prediction.probability)">
                  {{ prediction.probability }}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between">
      <div class="text-sm text-gray-700">
        Affichage de {{ (currentPage - 1) * pageSize + 1 }} à 
        {{ Math.min(currentPage * pageSize, totalStudents) }} sur {{ totalStudents }} élèves
      </div>
      <div class="flex space-x-1">
        <BaseButton
          variant="outline"
          size="sm"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          Précédent
        </BaseButton>
        <BaseButton
          v-for="page in visiblePages"
          :key="page"
          :variant="page === currentPage ? 'primary' : 'outline'"
          size="sm"
          @click="currentPage = page"
        >
          {{ page }}
        </BaseButton>
        <BaseButton
          variant="outline"
          size="sm"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          Suivant
        </BaseButton>
      </div>
    </div>

    <!-- Modal de détail élève -->
    <BaseModal
      :is-open="showStudentModal"
      title="Détail de l'élève à risque"
      @close="showStudentModal = false"
      size="xl"
    >
      <StudentRiskDetail
        v-if="selectedStudentId"
        :student-id="selectedStudentId"
        @close="showStudentModal = false"
        @intervention-created="handleInterventionCreated"
      />
    </BaseModal>

    <!-- Modal de création d'intervention -->
    <BaseModal
      :is-open="showInterventionModal"
      title="Créer une intervention"
      @close="showInterventionModal = false"
      size="lg"
    >
      <CreateInterventionForm
        :student-ids="interventionStudentIds"
        @close="showInterventionModal = false"
        @saved="handleInterventionCreated"
      />
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, watch } from 'vue'
import {
  ArrowPathIcon,
  UserGroupIcon,
  ClockIcon,
  ChartBarIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'

import BaseButton from '@/components/ui/BaseButton.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import StudentRiskDetail from '@/components/ai/StudentRiskDetail.vue'
import CreateInterventionForm from '@/components/ai/CreateInterventionForm.vue'
import { useAIModulesStore } from '@/stores/ai-modules'
import { schoolsApi } from '@/api/schools'
import { aiModulesAPI } from '@/api/ai-modules'

// Stores
const aiStore = useAIModulesStore()

// État local
const loading = ref(false)
const searchQuery = ref('')
const selectedRiskLevel = ref('')
const selectedClass = ref('')
const selectedStatus = ref('')
const selectedStudents = ref<string[]>([])
const sortBy = ref('risk_score')
const currentPage = ref(1)
const pageSize = ref(20)
const showStudentModal = ref(false)
const showInterventionModal = ref(false)
const selectedStudentId = ref<string | null>(null)
const interventionStudentIds = ref<string[]>([])
const error = ref<string | null>(null)

// Données réelles
const classes = ref<Array<{ id: string; name: string }>>([])
const riskProfiles = ref<any[]>([])
const totalStudents = ref(0)

// Computed
const filteredStudents = computed(() => {
  // Transform risk profiles to student-like objects for backward compatibility
  let students = riskProfiles.value.map(profile => getStudentFromProfile(profile))
  
  // Apply client-side sorting since we're not doing it server-side
  students.sort((a, b) => {
    switch (sortBy.value) {
      case 'risk_score':
        return b.risk_score - a.risk_score
      case 'name':
        return `${a.last_name} ${a.first_name}`.localeCompare(`${b.last_name} ${b.first_name}`)
      case 'class':
        return a.class_name.localeCompare(b.class_name)
      case 'last_update':
        return new Date(b.last_analysis).getTime() - new Date(a.last_analysis).getTime()
      default:
        return 0
    }
  })
  
  return students
})

const totalPages = computed(() => Math.ceil(totalStudents.value / pageSize.value))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// Méthodes
const loadClasses = async () => {
  try {
    const response = await schoolsApi.getClasses({ page_size: 100 })
    classes.value = response.results.map(cls => ({
      id: cls.id,
      name: cls.name
    }))
  } catch (err) {
    console.error('Erreur lors du chargement des classes:', err)
  }
}

const loadRiskProfiles = async () => {
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    // Appliquer les filtres de recherche
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    if (selectedRiskLevel.value) {
      params.risk_level = [selectedRiskLevel.value]
    }
    
    // Filtrer par statut d'intervention
    if (selectedStatus.value) {
      switch (selectedStatus.value) {
        case 'aucune':
          params.is_monitored = false
          break
        case 'planifiée':
        case 'en_cours':
        case 'terminée':
          params.is_monitored = true
          break
      }
    }

    const response = await aiModulesAPI.getRiskProfiles(params)
    riskProfiles.value = response.results || []
    totalStudents.value = response.count || 0
    error.value = null
  } catch (err: any) {
    console.error('Erreur lors du chargement des profils de risque:', err)
    error.value = err.response?.data?.error || 'Erreur lors du chargement des données'
    riskProfiles.value = []
    totalStudents.value = 0
  }
}

const refreshData = async () => {
  loading.value = true
  error.value = null
  try {
    await Promise.all([
      loadClasses(),
      loadRiskProfiles()
    ])
  } catch (err) {
    console.error('Erreur lors du chargement des données:', err)
  } finally {
    loading.value = false
  }
}

const viewStudentDetail = (profileId: string) => {
  selectedStudentId.value = profileId
  showStudentModal.value = true
}

const createIntervention = (profileId: string) => {
  interventionStudentIds.value = [profileId]
  showInterventionModal.value = true
}

const createBulkIntervention = () => {
  interventionStudentIds.value = [...selectedStudents.value]
  showInterventionModal.value = true
}

const exportSelectedStudents = () => {
  // TODO: Implémenter l'export
  console.log('Export des élèves:', selectedStudents.value)
}

const handleInterventionCreated = () => {
  showStudentModal.value = false
  showInterventionModal.value = false
  selectedStudents.value = []
  refreshData()
}

// Helper functions for risk profile data structure
const getStudentFromProfile = (profile: any) => {
  return {
    id: profile.id, // Use profile ID for actions
    first_name: profile.student.first_name,
    last_name: profile.student.last_name,
    class_name: profile.student.class_name || 'Non assigné',
    class_id: profile.student.class_id,
    risk_level: profile.risk_level,
    risk_score: Math.round((profile.risk_score || 0) * 100),
    last_analysis: profile.last_analysis || profile.updated_at,
    intervention_status: getInterventionStatus(profile),
    risk_factors: extractRiskFactors(profile),
    recent_predictions: profile.predictions?.slice(0, 3) || []
  }
}

const getInterventionStatus = (profile: any) => {
  if (!profile.is_monitored && !profile.active_intervention_plan) {
    return 'aucune'
  }
  if (profile.active_intervention_plan) {
    switch (profile.active_intervention_plan.status) {
      case 'planned': return 'planifiée'
      case 'active': return 'en_cours'
      case 'completed': return 'terminée'
      default: return 'aucune'
    }
  }
  return 'aucune'
}

const extractRiskFactors = (profile: any) => {
  const factors = profile.main_risk_factors || []
  return {
    absences: factors.some((f: any) => f.factor.toLowerCase().includes('absence')),
    grades: factors.some((f: any) => f.factor.toLowerCase().includes('grade') || f.factor.toLowerCase().includes('note')),
    behavior: factors.some((f: any) => f.factor.toLowerCase().includes('behavior') || f.factor.toLowerCase().includes('comportement'))
  }
}

// Utilitaires
const getStudentInitials = (firstName: string, lastName: string) => {
  return (firstName[0] + lastName[0]).toUpperCase()
}

const getRiskLevelColor = (level: string) => {
  const colors = {
    'élevé': 'danger',
    'modéré': 'warning',
    'faible': 'success'
  }
  return colors[level as keyof typeof colors] || 'secondary'
}

const getInterventionStatusColor = (status: string) => {
  const colors = {
    'aucune': 'bg-gray-100 text-gray-800',
    'planifiée': 'bg-blue-100 text-blue-800',
    'en_cours': 'bg-yellow-100 text-yellow-800',
    'terminée': 'bg-green-100 text-green-800'
  }
  return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'
}

const getInterventionStatusLabel = (status: string) => {
  const labels = {
    'aucune': 'Aucune',
    'planifiée': 'Planifiée',
    'en_cours': 'En cours',
    'terminée': 'Terminée'
  }
  return labels[status as keyof typeof labels] || status
}

const getPredictionColor = (probability: number) => {
  if (probability >= 80) return 'text-red-600'
  if (probability >= 60) return 'text-orange-600'
  if (probability >= 40) return 'text-yellow-600'
  return 'text-green-600'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short'
  })
}

// Debounced function for search
let searchTimeout: number | null = null
const debouncedLoadRiskProfiles = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = window.setTimeout(() => {
    loadRiskProfiles()
  }, 300)
}

// Watchers pour recharger les données quand les filtres changent
watch(searchQuery, () => {
  currentPage.value = 1
  debouncedLoadRiskProfiles()
})

watch([selectedRiskLevel, selectedClass, selectedStatus], () => {
  currentPage.value = 1
  loadRiskProfiles()
})

watch(currentPage, () => {
  loadRiskProfiles()
})

watch(sortBy, () => {
  // Le tri est fait côté client, pas besoin de recharger
})

// Lifecycle
onMounted(async () => {
  await refreshData()
})
</script>