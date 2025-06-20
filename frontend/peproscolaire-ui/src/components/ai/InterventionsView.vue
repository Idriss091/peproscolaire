<template>
  <div class="space-y-6">
    <!-- Statistiques des interventions -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ClipboardDocumentListIcon class="h-8 w-8 text-blue-500" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Plans actifs</p>
            <p class="text-2xl font-semibold text-gray-900">{{ interventionStats.active }}</p>
            <p class="text-xs text-blue-600">En cours de suivi</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <CheckCircleIcon class="h-8 w-8 text-green-500" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Complétés</p>
            <p class="text-2xl font-semibold text-gray-900">{{ interventionStats.completed }}</p>
            <p class="text-xs text-green-600">Ce mois</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ExclamationTriangleIcon class="h-8 w-8 text-orange-500" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">En retard</p>
            <p class="text-2xl font-semibold text-gray-900">{{ interventionStats.overdue }}</p>
            <p class="text-xs text-orange-600">Actions requises</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ChartBarIcon class="h-8 w-8 text-purple-500" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Taux de réussite</p>
            <p class="text-2xl font-semibold text-gray-900">{{ interventionStats.successRate }}%</p>
            <p class="text-xs text-purple-600">Interventions efficaces</p>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Filtres et actions -->
    <div class="bg-white p-4 rounded-lg border border-gray-200">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-medium text-gray-900">Plans d'intervention</h3>
        <BaseButton
          variant="primary"
          @click="showCreateModal = true"
        >
          <PlusIcon class="w-4 h-4" />
          Nouveau plan
        </BaseButton>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Statut
          </label>
          <select
            v-model="selectedStatus"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Tous les statuts</option>
            <option value="draft">Brouillon</option>
            <option value="active">Actif</option>
            <option value="on-hold">En pause</option>
            <option value="completed">Terminé</option>
            <option value="cancelled">Annulé</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Type d'intervention
          </label>
          <select
            v-model="selectedType"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Tous les types</option>
            <option value="academic">Académique</option>
            <option value="behavioral">Comportemental</option>
            <option value="social">Social</option>
            <option value="psychological">Psychologique</option>
            <option value="family">Familial</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Responsable
          </label>
          <select
            v-model="selectedResponsible"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Tous les responsables</option>
            <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
              {{ teacher.name }}
            </option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Priorité
          </label>
          <select
            v-model="selectedPriority"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Toutes les priorités</option>
            <option value="high">Élevée</option>
            <option value="medium">Moyenne</option>
            <option value="low">Faible</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Recherche
          </label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Nom de l'élève..."
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
        </div>
      </div>
    </div>

    <!-- Liste des interventions -->
    <BaseCard>
      <div v-if="loading" class="p-8 text-center">
        <div class="inline-flex items-center space-x-2 text-gray-600">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          <span>Chargement des interventions...</span>
        </div>
      </div>
      
      <div v-else class="space-y-4">
        <div
          v-for="intervention in filteredInterventions"
          :key="intervention.id"
          class="border border-gray-200 rounded-lg p-6 hover:shadow-sm transition-shadow"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <!-- En-tête de l'intervention -->
              <div class="flex items-center space-x-3 mb-3">
                <div class="flex-shrink-0">
                  <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                    <span class="text-sm font-medium text-gray-700">
                      {{ getStudentInitials(intervention.student_name) }}
                    </span>
                  </div>
                </div>
                <div class="flex-1">
                  <div class="flex items-center space-x-3">
                    <h4 class="text-lg font-medium text-gray-900">{{ intervention.student_name }}</h4>
                    <BaseBadge :variant="getStatusColor(intervention.status)" size="sm">
                      {{ getStatusLabel(intervention.status) }}
                    </BaseBadge>
                    <BaseBadge :variant="getPriorityColor(intervention.priority)" size="sm">
                      {{ getPriorityLabel(intervention.priority) }}
                    </BaseBadge>
                  </div>
                  <div class="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                    <span>{{ intervention.class_name }}</span>
                    <span>{{ getTypeLabel(intervention.type) }}</span>
                    <span>Créé le {{ formatDate(intervention.created_at) }}</span>
                  </div>
                </div>
              </div>
              
              <!-- Objectifs -->
              <div class="mb-4">
                <h5 class="text-sm font-medium text-gray-900 mb-2">Objectifs</h5>
                <p class="text-sm text-gray-700">{{ intervention.objectives }}</p>
              </div>
              
              <!-- Progression -->
              <div class="mb-4">
                <div class="flex items-center justify-between mb-2">
                  <h5 class="text-sm font-medium text-gray-900">Progression</h5>
                  <span class="text-sm text-gray-600">{{ intervention.progress }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    class="h-2 rounded-full transition-all"
                    :class="getProgressColor(intervention.progress)"
                    :style="{ width: `${intervention.progress}%` }"
                  />
                </div>
              </div>
              
              <!-- Actions et échéances -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h5 class="text-sm font-medium text-gray-900 mb-2">Prochaines actions</h5>
                  <div class="space-y-1">
                    <div
                      v-for="action in intervention.next_actions.slice(0, 2)"
                      :key="action.id"
                      class="flex items-center text-sm"
                    >
                      <div
                        class="w-2 h-2 rounded-full mr-2"
                        :class="getActionStatusColor(action.status)"
                      />
                      <span class="text-gray-700">{{ action.title }}</span>
                      <span class="text-gray-500 ml-auto">{{ formatDate(action.due_date) }}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h5 class="text-sm font-medium text-gray-900 mb-2">Équipe d'intervention</h5>
                  <div class="flex items-center space-x-2">
                    <div
                      v-for="member in intervention.team_members.slice(0, 3)"
                      :key="member.id"
                      class="flex items-center text-sm"
                    >
                      <div class="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center mr-1">
                        <span class="text-xs font-medium text-blue-600">
                          {{ getInitials(member.name) }}
                        </span>
                      </div>
                      <span class="text-gray-700 text-xs">{{ member.role }}</span>
                    </div>
                    <span
                      v-if="intervention.team_members.length > 3"
                      class="text-xs text-gray-500"
                    >
                      +{{ intervention.team_members.length - 3 }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Actions -->
            <div class="flex flex-col space-y-2 ml-4">
              <BaseButton
                variant="outline"
                size="sm"
                @click="viewInterventionDetail(intervention.id)"
              >
                Voir détail
              </BaseButton>
              
              <BaseButton
                v-if="intervention.status === 'active'"
                variant="primary"
                size="sm"
                @click="updateProgress(intervention.id)"
              >
                Mettre à jour
              </BaseButton>
              
              <BaseButton
                v-if="intervention.status === 'draft'"
                variant="success"
                size="sm"
                @click="activateIntervention(intervention.id)"
              >
                Activer
              </BaseButton>
            </div>
          </div>
        </div>
        
        <div v-if="filteredInterventions.length === 0" class="text-center py-8 text-gray-500">
          <ClipboardDocumentListIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>Aucun plan d'intervention ne correspond aux critères</p>
        </div>
      </div>
    </BaseCard>

    <!-- Modal de création/édition -->
    <BaseModal
      :is-open="showCreateModal"
      title="Créer un plan d'intervention"
      @close="showCreateModal = false"
      size="xl"
    >
      <CreateInterventionForm
        @close="showCreateModal = false"
        @saved="handleInterventionSaved"
      />
    </BaseModal>

    <!-- Modal de détail -->
    <BaseModal
      :is-open="showDetailModal"
      title="Détail du plan d'intervention"
      @close="showDetailModal = false"
      size="xl"
    >
      <InterventionDetail
        v-if="selectedInterventionId"
        :intervention-id="selectedInterventionId"
        @close="showDetailModal = false"
        @updated="handleInterventionUpdated"
      />
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import {
  ClipboardDocumentListIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  PlusIcon
} from '@heroicons/vue/24/outline'

import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import CreateInterventionForm from '@/components/ai/CreateInterventionForm.vue'
import InterventionDetail from '@/components/ai/InterventionDetail.vue'

// État local
const loading = ref(false)
const searchQuery = ref('')
const selectedStatus = ref('')
const selectedType = ref('')
const selectedResponsible = ref('')
const selectedPriority = ref('')
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const selectedInterventionId = ref<string | null>(null)

// Statistiques
const interventionStats = reactive({
  active: 15,
  completed: 8,
  overdue: 3,
  successRate: 78
})

// Données
const teachers = ref([
  { id: '1', name: 'M. Dupont' },
  { id: '2', name: 'Mme Martin' },
  { id: '3', name: 'M. Bernard' }
])

const interventions = ref([
  {
    id: '1',
    student_name: 'Martin Dubois',
    class_name: '6ème A',
    status: 'active',
    type: 'academic',
    priority: 'high',
    objectives: 'Améliorer les résultats en mathématiques et retrouver la motivation scolaire',
    progress: 65,
    created_at: '2024-01-10',
    next_actions: [
      { id: '1', title: 'Entretien avec les parents', status: 'pending', due_date: '2024-01-20' },
      { id: '2', title: 'Soutien scolaire', status: 'in_progress', due_date: '2024-01-25' }
    ],
    team_members: [
      { id: '1', name: 'M. Dupont', role: 'Responsable' },
      { id: '2', name: 'Mme Martin', role: 'Professeur Math' },
      { id: '3', name: 'M. Bernard', role: 'CPE' }
    ]
  },
  {
    id: '2',
    student_name: 'Sophie Martin',
    class_name: '6ème A',
    status: 'draft',
    type: 'behavioral',
    priority: 'medium',
    objectives: 'Améliorer le comportement en classe et les relations avec les camarades',
    progress: 0,
    created_at: '2024-01-12',
    next_actions: [
      { id: '3', title: 'Observation en classe', status: 'pending', due_date: '2024-01-18' }
    ],
    team_members: [
      { id: '2', name: 'Mme Martin', role: 'Responsable' },
      { id: '3', name: 'M. Bernard', role: 'CPE' }
    ]
  },
  {
    id: '3',
    student_name: 'Lucas Bernard',
    class_name: '5ème A',
    status: 'completed',
    type: 'social',
    priority: 'high',
    objectives: 'Favoriser l\'intégration sociale et lutter contre l\'isolement',
    progress: 100,
    created_at: '2023-12-15',
    next_actions: [],
    team_members: [
      { id: '1', name: 'M. Dupont', role: 'Responsable' },
      { id: '4', name: 'Psychologue', role: 'Support' }
    ]
  }
])

// Computed
const filteredInterventions = computed(() => {
  let filtered = [...interventions.value]

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(intervention =>
      intervention.student_name.toLowerCase().includes(query)
    )
  }

  if (selectedStatus.value) {
    filtered = filtered.filter(intervention => intervention.status === selectedStatus.value)
  }

  if (selectedType.value) {
    filtered = filtered.filter(intervention => intervention.type === selectedType.value)
  }

  if (selectedPriority.value) {
    filtered = filtered.filter(intervention => intervention.priority === selectedPriority.value)
  }

  // Tri par priorité puis par date
  filtered.sort((a, b) => {
    const priorityOrder = { high: 3, medium: 2, low: 1 }
    const aPriority = priorityOrder[a.priority as keyof typeof priorityOrder]
    const bPriority = priorityOrder[b.priority as keyof typeof priorityOrder]
    
    if (aPriority !== bPriority) {
      return bPriority - aPriority
    }
    
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })

  return filtered
})

// Méthodes
const viewInterventionDetail = (interventionId: string) => {
  selectedInterventionId.value = interventionId
  showDetailModal.value = true
}

const updateProgress = (interventionId: string) => {
  // TODO: Implémenter la mise à jour du progrès
  console.log('Mettre à jour l\'intervention:', interventionId)
}

const activateIntervention = (interventionId: string) => {
  // TODO: Activer l'intervention
  const intervention = interventions.value.find(i => i.id === interventionId)
  if (intervention) {
    intervention.status = 'active'
  }
}

const handleInterventionSaved = () => {
  showCreateModal.value = false
  // TODO: Recharger les données
}

const handleInterventionUpdated = () => {
  showDetailModal.value = false
  // TODO: Recharger les données
}

// Utilitaires
const getStudentInitials = (name: string) => {
  const parts = name.split(' ')
  return parts.map(p => p[0]).join('').toUpperCase()
}

const getInitials = (name: string) => {
  const parts = name.split(' ')
  return parts.map(p => p[0]).join('').toUpperCase()
}

const getStatusColor = (status: string) => {
  const colors = {
    draft: 'secondary',
    active: 'primary',
    'on-hold': 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return colors[status as keyof typeof colors] || 'secondary'
}

const getStatusLabel = (status: string) => {
  const labels = {
    draft: 'Brouillon',
    active: 'Actif',
    'on-hold': 'En pause',
    completed: 'Terminé',
    cancelled: 'Annulé'
  }
  return labels[status as keyof typeof labels] || status
}

const getPriorityColor = (priority: string) => {
  const colors = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return colors[priority as keyof typeof colors] || 'secondary'
}

const getPriorityLabel = (priority: string) => {
  const labels = {
    high: 'Élevée',
    medium: 'Moyenne',
    low: 'Faible'
  }
  return labels[priority as keyof typeof labels] || priority
}

const getTypeLabel = (type: string) => {
  const labels = {
    academic: 'Académique',
    behavioral: 'Comportemental',
    social: 'Social',
    psychological: 'Psychologique',
    family: 'Familial'
  }
  return labels[type as keyof typeof labels] || type
}

const getProgressColor = (progress: number) => {
  if (progress >= 80) return 'bg-green-500'
  if (progress >= 60) return 'bg-blue-500'
  if (progress >= 40) return 'bg-yellow-500'
  if (progress >= 20) return 'bg-orange-500'
  return 'bg-red-500'
}

const getActionStatusColor = (status: string) => {
  const colors = {
    pending: 'bg-gray-400',
    in_progress: 'bg-blue-500',
    completed: 'bg-green-500',
    overdue: 'bg-red-500'
  }
  return colors[status as keyof typeof colors] || 'bg-gray-400'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short'
  })
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // TODO: Charger les données depuis l'API
    await new Promise(resolve => setTimeout(resolve, 1000))
  } catch (error) {
    console.error('Erreur lors du chargement:', error)
  } finally {
    loading.value = false
  }
})
</script>