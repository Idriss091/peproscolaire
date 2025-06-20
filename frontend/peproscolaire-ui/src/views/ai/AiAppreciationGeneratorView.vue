<template>
  <div class="space-y-6">
    <!-- En-tête -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Générateur d'appréciations IA</h1>
        <p class="text-gray-600">Génération automatique d'appréciations personnalisées et constructives</p>
      </div>
      
      <div class="flex gap-3">
        <BaseButton
          variant="secondary"
          @click="showTemplatesModal = true"
          class="flex items-center gap-2"
        >
          <DocumentTextIcon class="w-4 h-4" />
          Modèles
        </BaseButton>
        
        <BaseButton
          variant="primary"
          @click="showGenerateModal = true"
          class="flex items-center gap-2"
        >
          <SparklesIcon class="w-4 h-4" />
          Nouvelle génération
        </BaseButton>
      </div>
    </div>

    <!-- Statistiques -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <SparklesIcon class="h-8 w-8 text-purple-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Appréciations générées</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stats.generated }}</p>
            <p class="text-xs text-purple-600">Ce mois</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <CheckCircleIcon class="h-8 w-8 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Validées</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stats.validated }}</p>
            <p class="text-xs text-green-600">{{ stats.validationRate }}% de taux</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <ClockIcon class="h-8 w-8 text-orange-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Temps économisé</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stats.timeSaved }}h</p>
            <p class="text-xs text-orange-600">Estimation</p>
          </div>
        </div>
      </BaseCard>
      
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <StarIcon class="h-8 w-8 text-yellow-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Satisfaction</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stats.satisfaction }}/5</p>
            <p class="text-xs text-yellow-600">Note moyenne</p>
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
            ? 'border-purple-500 text-purple-600'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- Contenu des onglets -->
    <div v-if="activeTab === 'generator'">
      <!-- Générateur d'appréciations -->
      <AppreciationGeneratorView />
    </div>

    <div v-else-if="activeTab === 'history'">
      <!-- Historique des générations -->
      <AppreciationHistoryView />
    </div>

    <div v-else-if="activeTab === 'templates'">
      <!-- Gestion des modèles -->
      <AppreciationTemplatesView />
    </div>

    <div v-else-if="activeTab === 'analytics'">
      <!-- Analyses et performance -->
      <AppreciationAnalyticsView />
    </div>

    <!-- Modal de génération rapide -->
    <BaseModal
      :is-open="showGenerateModal"
      title="Génération rapide d'appréciations"
      @close="showGenerateModal = false"
      size="lg"
    >
      <QuickGenerateForm
        @close="showGenerateModal = false"
        @generated="handleQuickGeneration"
      />
    </BaseModal>

    <!-- Modal de modèles -->
    <BaseModal
      :is-open="showTemplatesModal"
      title="Modèles d'appréciations"
      @close="showTemplatesModal = false"
      size="xl"
    >
      <TemplatesLibraryView
        @close="showTemplatesModal = false"
        @template-selected="handleTemplateSelected"
      />
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import {
  DocumentTextIcon,
  SparklesIcon,
  CheckCircleIcon,
  ClockIcon,
  StarIcon
} from '@heroicons/vue/24/outline'

import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import AppreciationGeneratorView from '@/components/ai/appreciation/AppreciationGeneratorView.vue'
import AppreciationHistoryView from '@/components/ai/appreciation/AppreciationHistoryView.vue'
import AppreciationTemplatesView from '@/components/ai/appreciation/AppreciationTemplatesView.vue'
import AppreciationAnalyticsView from '@/components/ai/appreciation/AppreciationAnalyticsView.vue'
import QuickGenerateForm from '@/components/ai/appreciation/QuickGenerateForm.vue'
import TemplatesLibraryView from '@/components/ai/appreciation/TemplatesLibraryView.vue'

// État local
const activeTab = ref('generator')
const showGenerateModal = ref(false)
const showTemplatesModal = ref(false)

// Onglets
const tabs = [
  { id: 'generator', name: 'Générateur' },
  { id: 'history', name: 'Historique' },
  { id: 'templates', name: 'Modèles' },
  { id: 'analytics', name: 'Analyses' }
]

// Statistiques
const stats = reactive({
  generated: 156,
  validated: 142,
  validationRate: 91,
  timeSaved: 24,
  satisfaction: 4.2
})

// Méthodes
const handleQuickGeneration = () => {
  showGenerateModal.value = false
  activeTab.value = 'history'
}

const handleTemplateSelected = () => {
  showTemplatesModal.value = false
  activeTab.value = 'generator'
}

// Lifecycle
onMounted(async () => {
  // TODO: Charger les statistiques depuis l'API
})
</script>