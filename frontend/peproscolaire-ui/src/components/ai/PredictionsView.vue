<template>
  <div class="space-y-6">
    <!-- Configuration du modèle -->
    <BaseCard>
      <template #header>
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Configuration du modèle prédictif</h3>
          <BaseButton
            variant="outline"
            size="sm"
            @click="showModelConfig = true"
          >
            <Cog6ToothIcon class="w-4 h-4" />
            Configurer
          </BaseButton>
        </div>
      </template>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="text-center p-4 bg-blue-50 rounded-lg">
          <div class="text-2xl font-bold text-blue-600">{{ modelConfig.accuracy }}%</div>
          <div class="text-sm text-blue-800">Précision du modèle</div>
          <div class="text-xs text-blue-600 mt-1">{{ modelConfig.lastTraining }}</div>
        </div>
        
        <div class="text-center p-4 bg-green-50 rounded-lg">
          <div class="text-2xl font-bold text-green-600">{{ modelConfig.predictions }}</div>
          <div class="text-sm text-green-800">Prédictions aujourd'hui</div>
          <div class="text-xs text-green-600 mt-1">{{ modelConfig.avgConfidence }}% confiance moy.</div>
        </div>
        
        <div class="text-center p-4 bg-purple-50 rounded-lg">
          <div class="text-2xl font-bold text-purple-600">{{ modelConfig.version }}</div>
          <div class="text-sm text-purple-800">Version du modèle</div>
          <div class="text-xs text-purple-600 mt-1">{{ modelConfig.status }}</div>
        </div>
      </div>
    </BaseCard>

    <!-- Filtres et actions -->
    <div class="bg-white p-4 rounded-lg border border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Type de prédiction
          </label>
          <select
            v-model="selectedType"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Tous les types</option>
            <option value="dropout">Décrochage scolaire</option>
            <option value="failure">Risque d'échec</option>
            <option value="behavioral">Problème comportemental</option>
            <option value="academic">Difficulté académique</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Niveau de confiance
          </label>
          <select
            v-model="selectedConfidence"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Tous les niveaux</option>
            <option value="high">Élevé (≥80%)</option>
            <option value="medium">Moyen (60-79%)</option>
            <option value="low">Faible (<60%)</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Période
          </label>
          <select
            v-model="selectedPeriod"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="today">Aujourd'hui</option>
            <option value="week">Cette semaine</option>
            <option value="month">Ce mois</option>
            <option value="quarter">Ce trimestre</option>
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
        
        <div class="flex items-end">
          <BaseButton
            variant="primary"
            @click="runNewPrediction"
            :loading="predicting"
            class="w-full"
          >
            <CpuChipIcon class="w-4 h-4" />
            Nouvelle prédiction
          </BaseButton>
        </div>
      </div>
    </div>

    <!-- Statistiques des prédictions -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ExclamationTriangleIcon class="h-8 w-8 text-red-500" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Prédictions critiques</p>
            <p class="text-2xl font-semibold text-gray-900">{{ predictionStats.critical }}</p>
            <p class="text-xs text-red-600">Confiance ≥90%</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ClockIcon class="h-8 w-8 text-orange-500" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">À surveiller</p>
            <p class="text-2xl font-semibold text-gray-900">{{ predictionStats.moderate }}</p>
            <p class="text-xs text-orange-600">Confiance 70-89%</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <CheckCircleIcon class="h-8 w-8 text-green-500" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Faible risque</p>
            <p class="text-2xl font-semibold text-gray-900">{{ predictionStats.low }}</p>
            <p class="text-xs text-green-600">Confiance <70%</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ChartBarIcon class="h-8 w-8 text-blue-500" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total traité</p>
            <p class="text-2xl font-semibold text-gray-900">{{ predictionStats.total }}</p>
            <p class="text-xs text-blue-600">Élèves analysés</p>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Liste des prédictions -->
    <BaseCard>
      <template #header>
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">
            Prédictions récentes ({{ filteredPredictions.length }})
          </h3>
          <div class="flex items-center space-x-2">
            <BaseButton
              variant="outline"
              size="sm"
              @click="exportPredictions"
            >
              <DocumentArrowDownIcon class="w-4 h-4" />
              Exporter
            </BaseButton>
            <BaseButton
              variant="outline"
              size="sm"
              @click="refreshPredictions"
              :loading="loading"
            >
              <ArrowPathIcon class="w-4 h-4" />
              Actualiser
            </BaseButton>
          </div>
        </div>
      </template>
      
      <div v-if="loading" class="p-8 text-center">
        <div class="inline-flex items-center space-x-2 text-gray-600">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          <span>Chargement des prédictions...</span>
        </div>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Élève
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type de prédiction
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Probabilité
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Confiance
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Facteurs clés
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="prediction in filteredPredictions"
              :key="prediction.id"
              class="hover:bg-gray-50"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-8 w-8">
                    <div class="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                      <span class="text-xs font-medium text-gray-700">
                        {{ getStudentInitials(prediction.student_name) }}
                      </span>
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ prediction.student_name }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ prediction.class_name }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getPredictionTypeColor(prediction.type)">
                  {{ getPredictionTypeLabel(prediction.type) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="text-sm font-medium" :class="getProbabilityColor(prediction.probability)">
                    {{ prediction.probability }}%
                  </div>
                  <div class="ml-2 w-16 bg-gray-200 rounded-full h-1.5">
                    <div 
                      class="h-1.5 rounded-full"
                      :class="getProbabilityBarColor(prediction.probability)"
                      :style="{ width: `${prediction.probability}%` }"
                    />
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ prediction.confidence }}%</div>
                <div class="text-xs text-gray-500">{{ getConfidenceLabel(prediction.confidence) }}</div>
              </td>
              <td class="px-6 py-4">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="factor in prediction.key_factors.slice(0, 3)"
                    :key="factor"
                    class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                  >
                    {{ factor }}
                  </span>
                  <span
                    v-if="prediction.key_factors.length > 3"
                    class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                  >
                    +{{ prediction.key_factors.length - 3 }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDateTime(prediction.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                  <BaseButton
                    variant="outline"
                    size="xs"
                    @click="viewPredictionDetail(prediction.id)"
                  >
                    Détail
                  </BaseButton>
                  <BaseButton
                    v-if="prediction.probability >= 70"
                    variant="primary"
                    size="xs"
                    @click="createAlertFromPrediction(prediction)"
                  >
                    Créer alerte
                  </BaseButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="filteredPredictions.length === 0" class="text-center py-8 text-gray-500">
          <ChartBarIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>Aucune prédiction ne correspond aux critères sélectionnés</p>
        </div>
      </div>
    </BaseCard>

    <!-- Modal de détail de prédiction -->
    <BaseModal
      :is-open="showPredictionModal"
      title="Détail de la prédiction"
      @close="showPredictionModal = false"
      size="lg"
    >
      <PredictionDetail
        v-if="selectedPredictionId"
        :prediction-id="selectedPredictionId"
        @close="showPredictionModal = false"
      />
    </BaseModal>

    <!-- Modal de configuration du modèle -->
    <BaseModal
      :is-open="showModelConfig"
      title="Configuration du modèle prédictif"
      @close="showModelConfig = false"
      size="lg"
    >
      <ModelConfigForm
        @close="showModelConfig = false"
        @saved="handleModelConfigSaved"
      />
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import {
  Cog6ToothIcon,
  CpuChipIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  CheckCircleIcon,
  ChartBarIcon,
  DocumentArrowDownIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'

import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import PredictionDetail from '@/components/ai/PredictionDetail.vue'
import ModelConfigForm from '@/components/ai/ModelConfigForm.vue'

// État local
const loading = ref(false)
const predicting = ref(false)
const selectedType = ref('')
const selectedConfidence = ref('')
const selectedPeriod = ref('week')
const selectedClass = ref('')
const showPredictionModal = ref(false)
const showModelConfig = ref(false)
const selectedPredictionId = ref<string | null>(null)

// Configuration du modèle
const modelConfig = reactive({
  accuracy: 87.5,
  predictions: 42,
  avgConfidence: 78,
  version: 'v2.1.3',
  status: 'Actif',
  lastTraining: 'Il y a 3 jours'
})

// Statistiques
const predictionStats = reactive({
  critical: 8,
  moderate: 15,
  low: 19,
  total: 42
})

// Données
const classes = ref([
  { id: '1', name: '6ème A' },
  { id: '2', name: '6ème B' },
  { id: '3', name: '5ème A' },
  { id: '4', name: '5ème B' }
])

const predictions = ref([
  {
    id: '1',
    student_name: 'Martin Dubois',
    class_name: '6ème A',
    type: 'dropout',
    probability: 92,
    confidence: 89,
    key_factors: ['Absentéisme', 'Chute des notes', 'Isolement social'],
    created_at: '2024-01-15T10:30:00'
  },
  {
    id: '2',
    student_name: 'Sophie Martin',
    class_name: '6ème A',
    type: 'academic',
    probability: 75,
    confidence: 82,
    key_factors: ['Mathématiques', 'Devoirs non rendus'],
    created_at: '2024-01-15T09:15:00'
  },
  {
    id: '3',
    student_name: 'Lucas Bernard',
    class_name: '5ème A',
    type: 'behavioral',
    probability: 68,
    confidence: 75,
    key_factors: ['Sanctions', 'Conflits', 'Manque de respect'],
    created_at: '2024-01-15T08:45:00'
  },
  {
    id: '4',
    student_name: 'Emma Leroy',
    class_name: '6ème B',
    type: 'failure',
    probability: 84,
    confidence: 91,
    key_factors: ['Moyenne générale', 'Participation', 'Motivation'],
    created_at: '2024-01-14T16:20:00'
  }
])

// Computed
const filteredPredictions = computed(() => {
  let filtered = [...predictions.value]

  if (selectedType.value) {
    filtered = filtered.filter(p => p.type === selectedType.value)
  }

  if (selectedConfidence.value) {
    filtered = filtered.filter(p => {
      switch (selectedConfidence.value) {
        case 'high': return p.confidence >= 80
        case 'medium': return p.confidence >= 60 && p.confidence < 80
        case 'low': return p.confidence < 60
        default: return true
      }
    })
  }

  if (selectedClass.value) {
    const className = classes.value.find(c => c.id === selectedClass.value)?.name
    if (className) {
      filtered = filtered.filter(p => p.class_name === className)
    }
  }

  // Tri par probabilité décroissante puis par confiance
  filtered.sort((a, b) => {
    if (a.probability !== b.probability) {
      return b.probability - a.probability
    }
    return b.confidence - a.confidence
  })

  return filtered
})

// Méthodes
const runNewPrediction = async () => {
  predicting.value = true
  try {
    // TODO: Appeler l'API pour lancer une nouvelle prédiction
    await new Promise(resolve => setTimeout(resolve, 3000))
    await refreshPredictions()
  } catch (error) {
    console.error('Erreur lors de la prédiction:', error)
  } finally {
    predicting.value = false
  }
}

const refreshPredictions = async () => {
  loading.value = true
  try {
    // TODO: Charger les prédictions depuis l'API
    await new Promise(resolve => setTimeout(resolve, 1000))
  } catch (error) {
    console.error('Erreur lors du chargement:', error)
  } finally {
    loading.value = false
  }
}

const viewPredictionDetail = (predictionId: string) => {
  selectedPredictionId.value = predictionId
  showPredictionModal.value = true
}

const createAlertFromPrediction = (prediction: any) => {
  // TODO: Créer une alerte à partir de la prédiction
  console.log('Créer alerte pour:', prediction.student_name)
}

const exportPredictions = () => {
  // TODO: Exporter les prédictions
  console.log('Export des prédictions')
}

const handleModelConfigSaved = () => {
  showModelConfig.value = false
  refreshPredictions()
}

// Utilitaires
const getStudentInitials = (name: string) => {
  const parts = name.split(' ')
  return parts.map(p => p[0]).join('').toUpperCase()
}

const getPredictionTypeColor = (type: string) => {
  const colors = {
    dropout: 'bg-red-100 text-red-800',
    failure: 'bg-orange-100 text-orange-800',
    behavioral: 'bg-yellow-100 text-yellow-800',
    academic: 'bg-blue-100 text-blue-800'
  }
  return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800'
}

const getPredictionTypeLabel = (type: string) => {
  const labels = {
    dropout: 'Décrochage',
    failure: 'Échec',
    behavioral: 'Comportement',
    academic: 'Académique'
  }
  return labels[type as keyof typeof labels] || type
}

const getProbabilityColor = (probability: number) => {
  if (probability >= 80) return 'text-red-600'
  if (probability >= 60) return 'text-orange-600'
  if (probability >= 40) return 'text-yellow-600'
  return 'text-green-600'
}

const getProbabilityBarColor = (probability: number) => {
  if (probability >= 80) return 'bg-red-500'
  if (probability >= 60) return 'bg-orange-500'
  if (probability >= 40) return 'bg-yellow-500'
  return 'bg-green-500'
}

const getConfidenceLabel = (confidence: number) => {
  if (confidence >= 90) return 'Très élevée'
  if (confidence >= 80) return 'Élevée'
  if (confidence >= 70) return 'Modérée'
  if (confidence >= 60) return 'Acceptable'
  return 'Faible'
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  refreshPredictions()
})
</script>