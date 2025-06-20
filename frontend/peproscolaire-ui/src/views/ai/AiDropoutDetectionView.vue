<template>
  <div class="space-y-6">
    <!-- En-tête -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Détection IA du décrochage scolaire</h1>
        <p class="text-gray-600">Système d'intelligence artificielle pour l'identification précoce des élèves à risque</p>
      </div>
      
      <div class="flex gap-3">
        <BaseButton
          variant="secondary"
          @click="exportAnalysis"
          class="flex items-center gap-2"
        >
          <DocumentArrowDownIcon class="w-4 h-4" />
          Exporter l'analyse
        </BaseButton>
        
        <BaseButton
          v-if="authStore.hasPermission('admin_access')"
          variant="primary"
          @click="runAnalysis"
          :loading="analyzing"
          class="flex items-center gap-2"
        >
          <CpuChipIcon class="w-4 h-4" />
          Lancer l'analyse IA
        </BaseButton>
      </div>
    </div>

    <!-- Statistiques globales -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ExclamationTriangleIcon class="h-8 w-8 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Risque élevé</p>
            <p class="text-2xl font-semibold text-gray-900">{{ riskStats.high }}</p>
            <p class="text-xs text-red-600">+{{ riskStats.highTrend }}% ce mois</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ExclamationCircleIcon class="h-8 w-8 text-orange-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Risque modéré</p>
            <p class="text-2xl font-semibold text-gray-900">{{ riskStats.medium }}</p>
            <p class="text-xs text-orange-600">+{{ riskStats.mediumTrend }}% ce mois</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <CheckCircleIcon class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Risque faible</p>
            <p class="text-2xl font-semibold text-gray-900">{{ riskStats.low }}</p>
            <p class="text-xs text-green-600">-{{ riskStats.lowTrend }}% ce mois</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ClockIcon class="h-8 w-8 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Dernière analyse</p>
            <p class="text-lg font-semibold text-gray-900">{{ formatDate(lastAnalysis) }}</p>
            <p class="text-xs text-blue-600">{{ getAnalysisStatus() }}</p>
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
    <div v-if="activeTab === 'dashboard'">
      <!-- Tableau de bord IA -->
      <AiDashboardView />
    </div>

    <div v-else-if="activeTab === 'students'">
      <!-- Liste des élèves à risque -->
      <RiskStudentsView />
    </div>

    <div v-else-if="activeTab === 'predictions'">
      <!-- Prédictions et modèles -->
      <PredictionsView />
    </div>

    <div v-else-if="activeTab === 'interventions'">
      <!-- Plans d'intervention -->
      <InterventionsView />
    </div>

    <div v-else-if="activeTab === 'reports'">
      <!-- Rapports et analyses -->
      <ReportsView />
    </div>

    <!-- Modal de configuration de l'analyse -->
    <BaseModal
      :is-open="showAnalysisModal"
      title="Configuration de l'analyse IA"
      @close="showAnalysisModal = false"
      size="lg"
    >
      <AnalysisConfigForm
        @close="showAnalysisModal = false"
        @saved="handleAnalysisConfigured"
      />
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  DocumentArrowDownIcon,
  CpuChipIcon,
  ExclamationTriangleIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/vue/24/outline'

import { useAuthStore } from '@/stores/auth'
import { useRiskDetectionStore } from '@/stores/risk-detection'
import { useAIModulesStore } from '@/stores/ai-modules'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import AiDashboardView from '@/components/ai/AiDashboardView.vue'
import RiskStudentsView from '@/components/ai/RiskStudentsView.vue'
import PredictionsView from '@/components/ai/PredictionsView.vue'
import InterventionsView from '@/components/ai/InterventionsView.vue'
import ReportsView from '@/components/ai/ReportsView.vue'
import AnalysisConfigForm from '@/components/ai/AnalysisConfigForm.vue'

const authStore = useAuthStore()
const riskDetectionStore = useRiskDetectionStore()
const aiStore = useAIModulesStore()

// État local
const activeTab = ref('dashboard')
const analyzing = ref(false)
const showAnalysisModal = ref(false)
const lastAnalysis = ref('2024-01-15T10:30:00')

// Onglets
const tabs = [
  { id: 'dashboard', name: 'Tableau de bord IA' },
  { id: 'students', name: 'Élèves à risque' },
  { id: 'predictions', name: 'Prédictions' },
  { id: 'interventions', name: 'Interventions' },
  { id: 'reports', name: 'Rapports' }
]

// Statistiques basées sur les vraies données
const riskStats = computed(() => {
  const metrics = aiStore.dashboardMetrics
  if (!metrics?.risk_distribution) {
    return {
      high: 0,
      medium: 0,
      low: 0,
      highTrend: 0,
      mediumTrend: 0,
      lowTrend: 0
    }
  }
  
  const dist = metrics.risk_distribution
  return {
    high: (dist.high || 0) + (dist.critical || 0),
    medium: dist.moderate || 0,
    low: (dist.low || 0) + (dist.very_low || 0),
    highTrend: 15, // TODO: Calculer la tendance réelle
    mediumTrend: 8,
    lowTrend: 5
  }
})

// Méthodes
const runAnalysis = async () => {
  analyzing.value = true
  try {
    // Lancer l'entraînement du modèle de détection de décrochage
    await aiStore.trainModel('dropout_risk', false)
    lastAnalysis.value = new Date().toISOString()
    
    // Rafraîchir les métriques après l'analyse
    await aiStore.fetchDashboardMetrics()
  } catch (error) {
    console.error('Erreur lors de l\'analyse IA:', error)
  } finally {
    analyzing.value = false
  }
}

const exportAnalysis = async () => {
  try {
    await riskDetectionStore.exportAnalysisReport()
  } catch (error) {
    console.error('Erreur lors de l\'export:', error)
  }
}

const handleAnalysisConfigured = () => {
  showAnalysisModal.value = false
  runAnalysis()
}

// Utilitaires
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const getAnalysisStatus = () => {
  const now = new Date()
  const analysisDate = new Date(lastAnalysis.value)
  const diffHours = Math.floor((now.getTime() - analysisDate.getTime()) / (1000 * 60 * 60))
  
  if (diffHours < 1) return 'À jour'
  if (diffHours < 24) return `Il y a ${diffHours}h`
  return `Il y a ${Math.floor(diffHours / 24)} jour(s)`
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    riskDetectionStore.fetchRiskProfiles(),
    riskDetectionStore.fetchPredictions(),
    riskDetectionStore.fetchInterventions(),
    aiStore.fetchModelStatus(),
    aiStore.fetchDashboardMetrics()
  ])
  
  // Démarrer l'auto-refresh des métriques
  aiStore.startMetricsAutoRefresh()
})
</script>