<template>
  <div class="space-y-6">
    <!-- Métriques de performance du modèle IA -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <BaseCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">Performance du modèle IA</h3>
            <BaseBadge :variant="getModelStatusColor(modelPerformance.status)">
              {{ getModelStatusLabel(modelPerformance.status) }}
            </BaseBadge>
          </div>
        </template>
        
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="text-center p-4 bg-blue-50 rounded-lg">
              <div class="text-2xl font-bold text-blue-600">{{ modelPerformance.accuracy }}%</div>
              <div class="text-sm text-blue-800">Précision</div>
            </div>
            <div class="text-center p-4 bg-green-50 rounded-lg">
              <div class="text-2xl font-bold text-green-600">{{ modelPerformance.recall }}%</div>
              <div class="text-sm text-green-800">Rappel</div>
            </div>
          </div>
          
          <div class="space-y-2">
            <div class="flex justify-between text-sm">
              <span>Score F1</span>
              <span class="font-medium">{{ modelPerformance.f1Score }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-purple-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${modelPerformance.f1Score}%` }"
              />
            </div>
          </div>
          
          <div class="text-xs text-gray-600">
            Dernière mise à jour: {{ formatDateTime(modelPerformance.lastUpdate) }}
          </div>
        </div>
      </BaseCard>

      <BaseCard>
        <template #header>
          <h3 class="text-lg font-medium text-gray-900">Facteurs de risque détectés</h3>
        </template>
        
        <div class="space-y-3">
          <div v-for="factor in riskFactors" :key="factor.name" 
               class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div 
                class="w-3 h-3 rounded-full"
                :class="getRiskFactorColor(factor.impact)"
              />
              <span class="text-sm font-medium">{{ factor.name }}</span>
            </div>
            <div class="flex items-center space-x-2">
              <span class="text-sm text-gray-600">{{ factor.weight }}%</span>
              <div class="w-16 bg-gray-200 rounded-full h-1">
                <div 
                  class="h-1 rounded-full transition-all"
                  :class="getRiskFactorBarColor(factor.impact)"
                  :style="{ width: `${factor.weight}%` }"
                />
              </div>
            </div>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Graphiques de tendances -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <BaseCard>
        <template #header>
          <h3 class="text-lg font-medium text-gray-900">Évolution des prédictions</h3>
        </template>
        
        <div class="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
          <!-- Placeholder pour graphique -->
          <div class="text-center text-gray-500">
            <ChartBarIcon class="w-12 h-12 mx-auto mb-2" />
            <p class="text-sm">Graphique d'évolution des risques</p>
            <p class="text-xs">(À intégrer avec une librairie de graphiques)</p>
          </div>
        </div>
      </BaseCard>

      <BaseCard>
        <template #header>
          <h3 class="text-lg font-medium text-gray-900">Distribution des niveaux de risque</h3>
        </template>
        
        <div class="space-y-4">
          <div v-for="level in riskDistribution" :key="level.name" 
               class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div 
                class="w-4 h-4 rounded"
                :class="level.colorClass"
              />
              <span class="text-sm font-medium">{{ level.name }}</span>
            </div>
            <div class="flex items-center space-x-3">
              <span class="text-sm text-gray-600">{{ level.count }} élèves</span>
              <div class="w-24 bg-gray-200 rounded-full h-2">
                <div 
                  class="h-2 rounded-full transition-all"
                  :class="level.barColor"
                  :style="{ width: `${level.percentage}%` }"
                />
              </div>
              <span class="text-xs text-gray-500 w-8">{{ level.percentage }}%</span>
            </div>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Alertes et recommandations IA -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2">
        <BaseCard>
          <template #header>
            <h3 class="text-lg font-medium text-gray-900">Alertes prioritaires</h3>
          </template>
          
          <div class="space-y-3">
            <div v-if="priorityAlerts.length === 0" class="text-center py-8 text-gray-500">
              <CheckCircleIcon class="w-12 h-12 mx-auto mb-2" />
              <p>Aucune alerte prioritaire</p>
            </div>
            
            <div v-for="alert in priorityAlerts" :key="alert.id" 
                 class="flex items-start space-x-3 p-3 rounded-lg border"
                 :class="getAlertClass(alert.severity)">
              <div class="flex-shrink-0 mt-0.5">
                <ExclamationTriangleIcon 
                  class="h-5 w-5"
                  :class="getAlertIconColor(alert.severity)"
                />
              </div>
              <div class="flex-1">
                <div class="flex items-center justify-between mb-1">
                  <h4 class="text-sm font-medium">{{ alert.student_name }}</h4>
                  <span class="text-xs text-gray-500">{{ formatDate(alert.created_at) }}</span>
                </div>
                <p class="text-sm text-gray-600 mb-2">{{ alert.message }}</p>
                <div class="flex items-center space-x-2">
                  <BaseBadge :variant="getRiskLevelColor(alert.risk_level)" size="sm">
                    Risque {{ alert.risk_level }}
                  </BaseBadge>
                  <span class="text-xs text-gray-500">Confiance: {{ alert.confidence }}%</span>
                </div>
              </div>
              <div class="flex-shrink-0">
                <BaseButton
                  variant="outline"
                  size="sm"
                  @click="viewAlert(alert)"
                >
                  Voir
                </BaseButton>
              </div>
            </div>
          </div>
        </BaseCard>
      </div>

      <div>
        <BaseCard>
          <template #header>
            <h3 class="text-lg font-medium text-gray-900">Recommandations IA</h3>
          </template>
          
          <div class="space-y-3">
            <div v-for="recommendation in aiRecommendations" :key="recommendation.id" 
                 class="p-3 bg-blue-50 rounded-lg border border-blue-200">
              <div class="flex items-start space-x-2">
                <div class="flex-shrink-0">
                  <CpuChipIcon class="h-4 w-4 text-blue-600 mt-0.5" />
                </div>
                <div>
                  <h4 class="text-sm font-medium text-blue-900">{{ recommendation.title }}</h4>
                  <p class="text-xs text-blue-700 mt-1">{{ recommendation.description }}</p>
                  <div class="mt-2 flex items-center space-x-2">
                    <span class="text-xs text-blue-600">Impact estimé: {{ recommendation.impact }}%</span>
                    <BaseButton
                      variant="primary"
                      size="xs"
                      @click="applyRecommendation(recommendation.id)"
                    >
                      Appliquer
                    </BaseButton>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>

    <!-- Actions rapides -->
    <BaseCard>
      <template #header>
        <h3 class="text-lg font-medium text-gray-900">Actions rapides</h3>
      </template>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="text-center p-4 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg text-white">
          <UserGroupIcon class="w-8 h-8 mx-auto mb-2" />
          <h4 class="font-medium mb-1">Analyser une classe</h4>
          <p class="text-sm opacity-90 mb-3">Analyse ciblée d'une classe spécifique</p>
          <BaseButton
            variant="outline"
            size="sm"
            @click="analyzeClass"
            class="text-white border-white hover:bg-white hover:text-blue-600"
          >
            Sélectionner une classe
          </BaseButton>
        </div>
        
        <div class="text-center p-4 bg-gradient-to-r from-green-500 to-green-600 rounded-lg text-white">
          <DocumentChartBarIcon class="w-8 h-8 mx-auto mb-2" />
          <h4 class="font-medium mb-1">Générer un rapport</h4>
          <p class="text-sm opacity-90 mb-3">Rapport détaillé des risques</p>
          <BaseButton
            variant="outline"
            size="sm"
            @click="generateReport"
            class="text-white border-white hover:bg-white hover:text-green-600"
          >
            Générer
          </BaseButton>
        </div>
        
        <div class="text-center p-4 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg text-white">
          <Cog6ToothIcon class="w-8 h-8 mx-auto mb-2" />
          <h4 class="font-medium mb-1">Configurer le modèle</h4>
          <p class="text-sm opacity-90 mb-3">Ajuster les paramètres IA</p>
          <BaseButton
            variant="outline"
            size="sm"
            @click="configureModel"
            class="text-white border-white hover:bg-white hover:text-purple-600"
          >
            Configurer
          </BaseButton>
        </div>
      </div>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  ChartBarIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  CpuChipIcon,
  UserGroupIcon,
  DocumentChartBarIcon,
  Cog6ToothIcon
} from '@heroicons/vue/24/outline'

import { useAIModulesStore } from '@/stores/ai-modules'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'

const aiStore = useAIModulesStore()

// État local
const loading = ref(false)

// Computed properties basées sur les vraies données
const modelPerformance = computed(() => {
  const dropoutModel = aiStore.modelStatus.dropout_risk
  if (!dropoutModel?.performance) {
    return {
      accuracy: 0,
      recall: 0,
      f1Score: 0,
      status: 'loading',
      lastUpdate: new Date().toISOString()
    }
  }
  
  return {
    accuracy: (dropoutModel.performance.accuracy || 0) * 100,
    recall: (dropoutModel.performance.recall || 0) * 100,
    f1Score: (dropoutModel.performance.f1_score || 0) * 100,
    status: dropoutModel.status === 'active' ? 'optimal' : dropoutModel.status,
    lastUpdate: dropoutModel.last_training || new Date().toISOString()
  }
})

const riskFactors = computed(() => {
  // Facteurs de risque calculés à partir des métriques
  const metrics = aiStore.dashboardMetrics
  if (!metrics) return []
  
  return [
    { name: 'Absentéisme', weight: 85, impact: 'high' },
    { name: 'Chute des notes', weight: 78, impact: 'high' },
    { name: 'Retards fréquents', weight: 62, impact: 'medium' },
    { name: 'Sanctions disciplinaires', weight: 71, impact: 'high' },
    { name: 'Manque de participation', weight: 55, impact: 'medium' },
    { name: 'Isolement social', weight: 48, impact: 'medium' }
  ]
})

const riskDistribution = computed(() => {
  const metrics = aiStore.dashboardMetrics
  if (!metrics?.risk_distribution) {
    return [
      { name: 'Risque élevé', count: 0, percentage: 0, colorClass: 'bg-red-500', barColor: 'bg-red-500' },
      { name: 'Risque modéré', count: 0, percentage: 0, colorClass: 'bg-orange-500', barColor: 'bg-orange-500' },
      { name: 'Risque faible', count: 0, percentage: 0, colorClass: 'bg-green-500', barColor: 'bg-green-500' }
    ]
  }
  
  const total = metrics.total_profiles || 1
  const dist = metrics.risk_distribution
  
  return [
    {
      name: 'Risque élevé',
      count: (dist.high || 0) + (dist.critical || 0),
      percentage: Math.round(((dist.high || 0) + (dist.critical || 0)) / total * 100),
      colorClass: 'bg-red-500',
      barColor: 'bg-red-500'
    },
    {
      name: 'Risque modéré',
      count: dist.moderate || 0,
      percentage: Math.round((dist.moderate || 0) / total * 100),
      colorClass: 'bg-orange-500',
      barColor: 'bg-orange-500'
    },
    {
      name: 'Risque faible',
      count: (dist.low || 0) + (dist.very_low || 0),
      percentage: Math.round(((dist.low || 0) + (dist.very_low || 0)) / total * 100),
      colorClass: 'bg-green-500',
      barColor: 'bg-green-500'
    }
  ]
})

// Mock data pour les alertes et recommandations (à remplacer par API plus tard)
const priorityAlerts = ref([])
const aiRecommendations = ref([])

// Méthodes
const getModelStatusColor = (status: string) => {
  const colors = {
    optimal: 'success',
    warning: 'warning',
    critical: 'danger'
  }
  return colors[status as keyof typeof colors] || 'secondary'
}

const getModelStatusLabel = (status: string) => {
  const labels = {
    optimal: 'Optimal',
    warning: 'Attention',
    critical: 'Critique'
  }
  return labels[status as keyof typeof labels] || status
}

const getRiskFactorColor = (impact: string) => {
  const colors = {
    high: 'bg-red-500',
    medium: 'bg-orange-500',
    low: 'bg-green-500'
  }
  return colors[impact as keyof typeof colors] || 'bg-gray-500'
}

const getRiskFactorBarColor = (impact: string) => {
  const colors = {
    high: 'bg-red-500',
    medium: 'bg-orange-500',
    low: 'bg-green-500'
  }
  return colors[impact as keyof typeof colors] || 'bg-gray-500'
}

const getAlertClass = (severity: string) => {
  const classes = {
    high: 'border-red-200 bg-red-50',
    medium: 'border-orange-200 bg-orange-50',
    low: 'border-yellow-200 bg-yellow-50'
  }
  return classes[severity as keyof typeof classes] || 'border-gray-200 bg-gray-50'
}

const getAlertIconColor = (severity: string) => {
  const colors = {
    high: 'text-red-600',
    medium: 'text-orange-600',
    low: 'text-yellow-600'
  }
  return colors[severity as keyof typeof colors] || 'text-gray-600'
}

const getRiskLevelColor = (level: string) => {
  const colors = {
    'élevé': 'danger',
    'modéré': 'warning',
    'faible': 'success'
  }
  return colors[level as keyof typeof colors] || 'secondary'
}

const loadDashboardData = async () => {
  loading.value = true
  try {
    await Promise.all([
      aiStore.fetchModelStatus(),
      aiStore.fetchDashboardMetrics()
    ])
    
    // Auto-refresh des métriques
    aiStore.startMetricsAutoRefresh()
  } catch (error) {
    console.error('Erreur lors du chargement du dashboard:', error)
  } finally {
    loading.value = false
  }
}

const viewAlert = (alert: any) => {
  console.log('Voir alerte:', alert.id)
}

const applyRecommendation = (recommendationId: string) => {
  console.log('Appliquer recommandation:', recommendationId)
}

const analyzeClass = async () => {
  try {
    // Déclenche une analyse de classe
    await aiStore.trainModel('dropout_risk', false)
  } catch (error) {
    console.error('Erreur lors de l\'analyse:', error)
  }
}

const generateReport = () => {
  console.log('Générer un rapport')
}

const configureModel = () => {
  console.log('Configurer le modèle')
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short'
  })
}

// Lifecycle
onMounted(async () => {
  await loadDashboardData()
})
</script>