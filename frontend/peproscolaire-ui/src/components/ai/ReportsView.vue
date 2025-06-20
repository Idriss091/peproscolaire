<template>
  <div class="space-y-6">
    <!-- Types de rapports -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <BaseCard 
        v-for="reportType in reportTypes" 
        :key="reportType.id"
        class="cursor-pointer hover:shadow-md transition-shadow"
        @click="selectReportType(reportType.id)"
        :class="selectedReportType === reportType.id ? 'ring-2 ring-blue-500' : ''"
      >
        <div class="text-center p-4">
          <div class="flex justify-center mb-3">
            <component :is="reportType.icon" class="w-12 h-12 text-blue-600" />
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">{{ reportType.title }}</h3>
          <p class="text-sm text-gray-600">{{ reportType.description }}</p>
          <div class="mt-4 flex justify-center">
            <BaseBadge :variant="reportType.available ? 'success' : 'secondary'" size="sm">
              {{ reportType.available ? 'Disponible' : 'Bientôt' }}
            </BaseBadge>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Configuration du rapport -->
    <BaseCard v-if="selectedReportType">
      <template #header>
        <h3 class="text-lg font-medium text-gray-900">Configuration du rapport</h3>
      </template>
      
      <form @submit.prevent="generateReport" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Période d'analyse
            </label>
            <select
              v-model="reportConfig.period"
              required
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="week">Cette semaine</option>
              <option value="month">Ce mois</option>
              <option value="quarter">Ce trimestre</option>
              <option value="semester">Ce semestre</option>
              <option value="year">Cette année</option>
              <option value="custom">Période personnalisée</option>
            </select>
          </div>
          
          <div v-if="reportConfig.period === 'custom'">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Date de début
            </label>
            <input
              v-model="reportConfig.startDate"
              type="date"
              required
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
          </div>
          
          <div v-if="reportConfig.period === 'custom'">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Date de fin
            </label>
            <input
              v-model="reportConfig.endDate"
              type="date"
              required
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Niveau de classe
            </label>
            <select
              v-model="reportConfig.classLevel"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Tous les niveaux</option>
              <option value="6">6ème</option>
              <option value="5">5ème</option>
              <option value="4">4ème</option>
              <option value="3">3ème</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Format de sortie
            </label>
            <select
              v-model="reportConfig.format"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="pdf">PDF</option>
              <option value="excel">Excel</option>
              <option value="csv">CSV</option>
            </select>
          </div>
        </div>
        
        <!-- Options spécifiques selon le type de rapport -->
        <div v-if="selectedReportType === 'risk-analysis'" class="border-t pt-6">
          <h4 class="text-sm font-medium text-gray-900 mb-4">Options d'analyse des risques</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-3">
              <div class="flex items-center">
                <input
                  id="include-predictions"
                  v-model="reportConfig.options.includePredictions"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <label for="include-predictions" class="ml-2 block text-sm text-gray-900">
                  Inclure les prédictions IA
                </label>
              </div>
              <div class="flex items-center">
                <input
                  id="include-risk-factors"
                  v-model="reportConfig.options.includeRiskFactors"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <label for="include-risk-factors" class="ml-2 block text-sm text-gray-900">
                  Détailler les facteurs de risque
                </label>
              </div>
            </div>
            <div class="space-y-3">
              <div class="flex items-center">
                <input
                  id="include-interventions"
                  v-model="reportConfig.options.includeInterventions"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <label for="include-interventions" class="ml-2 block text-sm text-gray-900">
                  Inclure les interventions
                </label>
              </div>
              <div class="flex items-center">
                <input
                  id="include-recommendations"
                  v-model="reportConfig.options.includeRecommendations"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <label for="include-recommendations" class="ml-2 block text-sm text-gray-900">
                  Ajouter les recommandations IA
                </label>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="selectedReportType === 'performance'" class="border-t pt-6">
          <h4 class="text-sm font-medium text-gray-900 mb-4">Options de performance</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-3">
              <div class="flex items-center">
                <input
                  id="include-accuracy-metrics"
                  v-model="reportConfig.options.includeAccuracyMetrics"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <label for="include-accuracy-metrics" class="ml-2 block text-sm text-gray-900">
                  Métriques de précision
                </label>
              </div>
              <div class="flex items-center">
                <input
                  id="include-trend-analysis"
                  v-model="reportConfig.options.includeTrendAnalysis"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <label for="include-trend-analysis" class="ml-2 block text-sm text-gray-900">
                  Analyse des tendances
                </label>
              </div>
            </div>
            <div class="space-y-3">
              <div class="flex items-center">
                <input
                  id="include-model-comparison"
                  v-model="reportConfig.options.includeModelComparison"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <label for="include-model-comparison" class="ml-2 block text-sm text-gray-900">
                  Comparaison de modèles
                </label>
              </div>
              <div class="flex items-center">
                <input
                  id="include-feature-importance"
                  v-model="reportConfig.options.includeFeatureImportance"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <label for="include-feature-importance" class="ml-2 block text-sm text-gray-900">
                  Importance des caractéristiques
                </label>
              </div>
            </div>
          </div>
        </div>
        
        <div class="flex justify-end space-x-3">
          <BaseButton
            type="button"
            variant="outline"
            @click="previewReport"
          >
            Aperçu
          </BaseButton>
          
          <BaseButton
            type="submit"
            variant="primary"
            :loading="generating"
          >
            <DocumentChartBarIcon class="w-4 h-4" />
            Générer le rapport
          </BaseButton>
        </div>
      </form>
    </BaseCard>

    <!-- Historique des rapports -->
    <BaseCard>
      <template #header>
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Rapports générés</h3>
          <BaseButton
            variant="outline"
            size="sm"
            @click="refreshHistory"
            :loading="loadingHistory"
          >
            <ArrowPathIcon class="w-4 h-4" />
            Actualiser
          </BaseButton>
        </div>
      </template>
      
      <div v-if="loadingHistory" class="p-8 text-center">
        <div class="inline-flex items-center space-x-2 text-gray-600">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          <span>Chargement de l'historique...</span>
        </div>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type de rapport
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Période
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Généré par
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date de génération
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Statut
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="report in reportHistory"
              :key="report.id"
              class="hover:bg-gray-50"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <component :is="getReportIcon(report.type)" class="w-5 h-5 text-gray-400 mr-3" />
                  <span class="text-sm font-medium text-gray-900">
                    {{ getReportTypeLabel(report.type) }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ report.period }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ report.generated_by }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDateTime(report.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <BaseBadge :variant="getStatusColor(report.status)" size="sm">
                  {{ getStatusLabel(report.status) }}
                </BaseBadge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                  <BaseButton
                    v-if="report.status === 'completed'"
                    variant="outline"
                    size="xs"
                    @click="downloadReport(report.id)"
                  >
                    <DocumentArrowDownIcon class="w-3 h-3" />
                    Télécharger
                  </BaseButton>
                  
                  <BaseButton
                    v-if="report.status === 'completed'"
                    variant="outline"
                    size="xs"
                    @click="shareReport(report.id)"
                  >
                    <ShareIcon class="w-3 h-3" />
                    Partager
                  </BaseButton>
                  
                  <BaseButton
                    variant="outline"
                    size="xs"
                    @click="deleteReport(report.id)"
                    class="text-red-600 hover:text-red-700"
                  >
                    <TrashIcon class="w-3 h-3" />
                  </BaseButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="reportHistory.length === 0" class="text-center py-8 text-gray-500">
          <DocumentChartBarIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>Aucun rapport généré pour le moment</p>
        </div>
      </div>
    </BaseCard>

    <!-- Modal d'aperçu -->
    <BaseModal
      :is-open="showPreviewModal"
      title="Aperçu du rapport"
      @close="showPreviewModal = false"
      size="xl"
    >
      <ReportPreview
        v-if="previewData"
        :report-type="selectedReportType"
        :config="reportConfig"
        :data="previewData"
        @close="showPreviewModal = false"
        @generate="generateReportFromPreview"
      />
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import {
  DocumentChartBarIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  AcademicCapIcon,
  ClipboardDocumentListIcon,
  ArrowPathIcon,
  DocumentArrowDownIcon,
  ShareIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import ReportPreview from '@/components/ai/ReportPreview.vue'

// État local
const generating = ref(false)
const loadingHistory = ref(false)
const selectedReportType = ref('')
const showPreviewModal = ref(false)
const previewData = ref(null)

// Configuration du rapport
const reportConfig = reactive({
  period: 'month',
  startDate: '',
  endDate: '',
  classLevel: '',
  format: 'pdf',
  options: {
    includePredictions: true,
    includeRiskFactors: true,
    includeInterventions: true,
    includeRecommendations: true,
    includeAccuracyMetrics: true,
    includeTrendAnalysis: true,
    includeModelComparison: false,
    includeFeatureImportance: true
  }
})

// Types de rapports
const reportTypes = ref([
  {
    id: 'risk-analysis',
    title: 'Analyse des risques',
    description: 'Rapport détaillé sur les élèves à risque de décrochage avec prédictions IA',
    icon: DocumentChartBarIcon,
    available: true
  },
  {
    id: 'performance',
    title: 'Performance du modèle',
    description: 'Analyse de la performance et de la précision du modèle prédictif',
    icon: ChartBarIcon,
    available: true
  },
  {
    id: 'interventions',
    title: 'Efficacité des interventions',
    description: 'Évaluation de l\'impact des plans d\'intervention mis en place',
    icon: ClipboardDocumentListIcon,
    available: true
  },
  {
    id: 'trends',
    title: 'Tendances et évolutions',
    description: 'Analyse des tendances du décrochage scolaire dans l\'établissement',
    icon: AcademicCapIcon,
    available: false
  },
  {
    id: 'comparative',
    title: 'Analyse comparative',
    description: 'Comparaison avec d\'autres établissements et benchmarks nationaux',
    icon: Cog6ToothIcon,
    available: false
  }
])

// Historique des rapports
const reportHistory = ref([
  {
    id: '1',
    type: 'risk-analysis',
    period: 'Janvier 2024',
    generated_by: 'M. Dupont',
    created_at: '2024-01-15T10:30:00',
    status: 'completed',
    file_size: '2.3 MB'
  },
  {
    id: '2',
    type: 'performance',
    period: 'T1 2023-2024',
    generated_by: 'Mme Martin',
    created_at: '2024-01-10T14:15:00',
    status: 'completed',
    file_size: '1.8 MB'
  },
  {
    id: '3',
    type: 'interventions',
    period: 'Décembre 2023',
    generated_by: 'M. Bernard',
    created_at: '2024-01-08T09:20:00',
    status: 'processing',
    file_size: null
  }
])

// Méthodes
const selectReportType = (typeId: string) => {
  const reportType = reportTypes.value.find(t => t.id === typeId)
  if (reportType && reportType.available) {
    selectedReportType.value = typeId
  }
}

const generateReport = async () => {
  if (!selectedReportType.value) return
  
  generating.value = true
  try {
    // TODO: Appeler l'API pour générer le rapport
    console.log('Génération du rapport:', {
      type: selectedReportType.value,
      config: reportConfig
    })
    
    // Simulation
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    // Ajouter à l'historique
    const newReport = {
      id: Date.now().toString(),
      type: selectedReportType.value,
      period: reportConfig.period,
      generated_by: 'Utilisateur actuel',
      created_at: new Date().toISOString(),
      status: 'processing',
      file_size: null
    }
    
    reportHistory.value.unshift(newReport)
    
    // Réinitialiser la sélection
    selectedReportType.value = ''
  } catch (error) {
    console.error('Erreur lors de la génération:', error)
  } finally {
    generating.value = false
  }
}

const previewReport = async () => {
  if (!selectedReportType.value) return
  
  try {
    // TODO: Générer un aperçu des données
    previewData.value = {
      type: selectedReportType.value,
      config: { ...reportConfig },
      sampleData: {
        studentsAtRisk: 12,
        interventions: 8,
        successRate: 75,
        accuracy: 87.5
      }
    }
    
    showPreviewModal.value = true
  } catch (error) {
    console.error('Erreur lors de l\'aperçu:', error)
  }
}

const generateReportFromPreview = () => {
  showPreviewModal.value = false
  generateReport()
}

const refreshHistory = async () => {
  loadingHistory.value = true
  try {
    // TODO: Recharger l'historique depuis l'API
    await new Promise(resolve => setTimeout(resolve, 1000))
  } catch (error) {
    console.error('Erreur lors du rechargement:', error)
  } finally {
    loadingHistory.value = false
  }
}

const downloadReport = (reportId: string) => {
  // TODO: Télécharger le rapport
  console.log('Télécharger le rapport:', reportId)
}

const shareReport = (reportId: string) => {
  // TODO: Partager le rapport
  console.log('Partager le rapport:', reportId)
}

const deleteReport = (reportId: string) => {
  // TODO: Supprimer le rapport
  const index = reportHistory.value.findIndex(r => r.id === reportId)
  if (index > -1) {
    reportHistory.value.splice(index, 1)
  }
}

// Utilitaires
const getReportIcon = (type: string) => {
  const icons = {
    'risk-analysis': DocumentChartBarIcon,
    'performance': ChartBarIcon,
    'interventions': ClipboardDocumentListIcon,
    'trends': AcademicCapIcon,
    'comparative': Cog6ToothIcon
  }
  return icons[type as keyof typeof icons] || DocumentChartBarIcon
}

const getReportTypeLabel = (type: string) => {
  const labels = {
    'risk-analysis': 'Analyse des risques',
    'performance': 'Performance du modèle',
    'interventions': 'Efficacité des interventions',
    'trends': 'Tendances et évolutions',
    'comparative': 'Analyse comparative'
  }
  return labels[type as keyof typeof labels] || type
}

const getStatusColor = (status: string) => {
  const colors = {
    completed: 'success',
    processing: 'warning',
    failed: 'danger',
    cancelled: 'secondary'
  }
  return colors[status as keyof typeof colors] || 'secondary'
}

const getStatusLabel = (status: string) => {
  const labels = {
    completed: 'Terminé',
    processing: 'En cours',
    failed: 'Échec',
    cancelled: 'Annulé'
  }
  return labels[status as keyof typeof labels] || status
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  refreshHistory()
})
</script>